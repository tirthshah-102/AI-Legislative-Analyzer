// Global state
const state = {
    user: null,
    token: null,
    currentFile: null,
    documents: []
};

// API Base URL
const API_URL = 'http://localhost:5000/api';

// ==================== AUTHENTICATION ====================

async function handleLogin() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showNotification('Please fill all fields', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showNotification(data.error || 'Login failed', 'error');
            return;
        }

        state.user = data.data;
        state.token = data.data.token;
        localStorage.setItem('token', state.token);
        localStorage.setItem('user', JSON.stringify(state.user));

        showNotification('Login successful!', 'success');
        showAuthScreen(false);
        loadDocuments();

    } catch (error) {
        showNotification('Connection error', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

async function handleRegister() {
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;

    if (!username || !email || !password) {
        showNotification('Please fill all fields', 'error');
        return;
    }

    if (password.length < 8) {
        showNotification('Password must be at least 8 characters', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showNotification(data.error || 'Registration failed', 'error');
            return;
        }

        state.user = data.data;
        state.token = data.data.token;
        localStorage.setItem('token', state.token);
        localStorage.setItem('user', JSON.stringify(state.user));

        showNotification('Registration successful!', 'success');
        showAuthScreen(false);
        loadDocuments();

    } catch (error) {
        showNotification('Connection error', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function handleLogout() {
    state.user = null;
    state.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showAuthScreen(true);
    showNotification('Logged out successfully', 'success');
}

function toggleForms() {
    document.getElementById('loginForm').classList.toggle('hidden');
    document.getElementById('registerForm').classList.toggle('hidden');
}

// ==================== UI FUNCTIONS ====================

function showAuthScreen(show) {
    document.getElementById('authScreen').classList.toggle('hidden', !show);
    document.getElementById('dashboard').classList.toggle('hidden', show);
}

function showLoading(show) {
    document.getElementById('loadingScreen').classList.toggle('hidden', !show);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-blue-500'}`;
    notification.innerHTML = `<i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'} mr-2"></i>${message}`;
    document.body.appendChild(notification);

    setTimeout(() => notification.remove(), 3000);
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('tab-active'));

    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.closest('.tab-btn').classList.add('tab-active');

    if (tabName === 'documents') loadDocuments();
    if (tabName === 'history') loadHistory();
}

// ==================== FILE UPLOAD ====================

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.backgroundColor = 'transparent';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = 'transparent';
        const files = e.dataTransfer.files;
        if (files.length) handleFileUpload(files[0]);
    });

    dropZone.addEventListener('click', () => fileInput.click());
}

if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFileUpload(e.target.files[0]);
    });
}

async function handleFileUpload(file) {
    if (!file.name.endsWith('.pdf')) {
        showNotification('Please upload a PDF file', 'error');
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        showNotification('File size must be less than 50MB', 'error');
        return;
    }

    state.currentFile = file;
    document.getElementById('fileInfo').classList.remove('hidden');
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';

    const formData = new FormData();
    formData.append('file', file);

    showLoading(true);
    document.getElementById('progressSection').classList.remove('hidden');

    try {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            const percentComplete = (e.loaded / e.total) * 100;
            document.getElementById('progressFill').style.width = percentComplete + '%';
            document.getElementById('progressPercent').textContent = Math.round(percentComplete) + '%';
        });

        xhr.addEventListener('load', async () => {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                document.getElementById('analyzeText').value = data.data.text;
                document.getElementById('fileStatus').textContent = 'Uploaded ✓';
                showNotification('File uploaded successfully!', 'success');
                switchTab('analyze');
            } else {
                showNotification('Upload failed', 'error');
            }
            showLoading(false);
        });

        xhr.addEventListener('error', () => {
            showNotification('Upload error', 'error');
            showLoading(false);
        });

        xhr.open('POST', `${API_URL}/documents/upload`);
        xhr.setRequestHeader('Authorization', `Bearer ${state.token}`);
        xhr.send(formData);

    } catch (error) {
        showNotification('Upload failed', 'error');
        console.error(error);
        showLoading(false);
    }
}

// ==================== ANALYSIS ====================

async function handleAnalyze() {
    const text = document.getElementById('analyzeText').value.trim();
    const language = document.getElementById('analysisLanguage').value;

    if (!text) {
        showNotification('Please provide text to analyze', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ text, language })
        });

        const data = await response.json();

        if (!response.ok) {
            showNotification(data.error || 'Analysis failed', 'error');
            return;
        }

        displayResults(data.data);
        showNotification('Analysis complete!', 'success');

    } catch (error) {
        showNotification('Analysis error', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function displayResults(results) {
    document.getElementById('resultsSection').classList.remove('hidden');

    // Display summary
    document.getElementById('summaryContent').innerHTML = marked.parse(results.summary || '');

    // Display metrics
    const metricsDiv = document.getElementById('metricsContent');
    metricsDiv.innerHTML = '';
    if (results.metrics) {
        Object.entries(results.metrics).forEach(([key, value]) => {
            metricsDiv.innerHTML += `
                <div class="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
                    <p class="text-sm text-gray-600">${key}</p>
                    <p class="text-2xl font-bold text-purple-600">${value}</p>
                </div>
            `;
        });
    }
}

// ==================== DOCUMENTS ====================

async function loadDocuments() {
    if (!state.token) return;

    try {
        const response = await fetch(`${API_URL}/documents`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        const data = await response.json();

        if (response.ok) {
            state.documents = data.data.documents;
            const docsList = document.getElementById('documentsList');

            if (state.documents.length === 0) {
                docsList.innerHTML = '<p class="text-gray-500">No documents yet</p>';
            } else {
                docsList.innerHTML = state.documents.map(doc => `
                    <div class="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition">
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="font-semibold text-gray-800">${doc.filename}</p>
                                <p class="text-sm text-gray-500">${doc.file_size} bytes • ${new Date(doc.upload_date).toLocaleDateString()}</p>
                            </div>
                            <button onclick="deleteDocument(${doc.id})" class="text-red-500 hover:text-red-700">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load documents', error);
    }
}

async function loadHistory() {
    if (!state.token) return;

    try {
        const response = await fetch(`${API_URL}/documents`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        const data = await response.json();

        if (response.ok) {
            const historyList = document.getElementById('historyList');
            if (data.data.documents.length === 0) {
                historyList.innerHTML = '<p class="text-gray-500">No history yet</p>';
            }
        }
    } catch (error) {
        console.error('Failed to load history', error);
    }
}

// ==================== EXPORT ====================

async function handleExport(format) {
    const text = document.getElementById('analyzeText').value.trim();
    if (!text) {
        showNotification('No analysis to export', 'error');
        return;
    }

    if (format === 'pdf') {
        const language = document.getElementById('analysisLanguage').value;
        const summary = document.getElementById('summaryContent').innerHTML;

        const response = await fetch(`${API_URL}/export/pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ text: summary, language })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'analysis.pdf';
            a.click();
            showNotification('PDF downloaded', 'success');
        }
    }
}

// ==================== INITIALIZATION ====================

function init() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');

    if (token && user) {
        state.token = token;
        state.user = JSON.parse(user);
        document.getElementById('userDisplay').textContent = `Welcome back, ${state.user.username}!`;
        showAuthScreen(false);
        loadDocuments();
    } else {
        showAuthScreen(true);
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', init);
