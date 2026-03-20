// --- Application Logic ---
document.addEventListener('DOMContentLoaded', () => {

    // Selectors
    const fileUpload = document.getElementById('file-upload');
    const processBtn = document.getElementById('process-btn');
    const askBtn = document.getElementById('ask-btn');
    const summaryContent = document.getElementById('summary-content');
    const glossaryContent = document.getElementById('glossary-content');
    const chatMessages = document.getElementById('chat-messages');
    const toggleAssistant = document.getElementById('toggle-assistant');
    
    // UI Panels & Buttons
    const loader = document.getElementById('loader');
    const loaderText = document.getElementById('loader-text');
    const listenBtn = document.getElementById('listen-btn');
    const audioPlayer = document.getElementById('audio-player');

    // Chart Variables
    let riskChart = null;

    // Tab Switching Logic
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab') + '-tab';
            
            // Toggle Buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle Contents
            tabContents.forEach(c => c.classList.remove('active'));
            const targetContent = document.getElementById(targetId);
            if (targetContent) targetContent.classList.add('active');

            // Initialize Assistant Greeting if it's the first time
            if (targetId === 'assistant-tab' && chatMessages.children.length === 0) {
                addMessage("Hello! I'm your Legislative Assistant. Upload a document and ask me anything about its legal aspects.", 'ai');
            }
        });
    });

    // Custom Language Dropdown Logic
    const langBtn = document.getElementById('language-dropdown-btn');
    const langMenu = document.getElementById('language-menu');
    const langOptions = document.querySelectorAll('.language-option');
    const langSelectedText = document.getElementById('language-selected-text');
    const langHiddenInput = document.getElementById('language-select');
    const langChevron = document.getElementById('language-chevron');

    if (langBtn && langMenu) {
        langBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isExpanded = langMenu.classList.contains('opacity-100');
            
            if (isExpanded) {
                // Close menu
                langMenu.classList.remove('opacity-100', 'visible', 'scale-100');
                langMenu.classList.add('opacity-0', 'invisible', 'scale-95');
                langChevron.classList.remove('rotate-180');
            } else {
                // Open menu
                langMenu.classList.remove('opacity-0', 'invisible', 'scale-95');
                langMenu.classList.add('opacity-100', 'visible', 'scale-100');
                langChevron.classList.add('rotate-180');
            }
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!langBtn.contains(e.target) && !langMenu.contains(e.target)) {
                langMenu.classList.remove('opacity-100', 'visible', 'scale-100');
                langMenu.classList.add('opacity-0', 'invisible', 'scale-95');
                langChevron.classList.remove('rotate-180');
            }
        });

        // Handle option selection
        langOptions.forEach(option => {
            option.addEventListener('click', () => {
                const value = option.getAttribute('data-value');
                const flag = option.getAttribute('data-flag');
                
                // Update UI and hidden input
                langSelectedText.textContent = `${flag} ${value}`;
                langHiddenInput.value = value;
                
                // Close menu
                langMenu.classList.remove('opacity-100', 'visible', 'scale-100');
                langMenu.classList.add('opacity-0', 'invisible', 'scale-95');
                langChevron.classList.remove('rotate-180');
            });
        });
    }

    let extractedText = "";
    let summaryText = "";

    const suggestedQuestionsCont = document.getElementById('suggested-questions');
    
    const suggestions = [
        "What are the main penalties?",
        "Who is most affected?",
        "What are the key deadlines?",
        "Explain this bill's impact."
    ];

    function initSuggestions() {
        suggestedQuestionsCont.innerHTML = "";
        suggestions.forEach(q => {
            const chip = document.createElement('div');
            chip.className = 'px-3 py-1.5 bg-white border border-slate-200 rounded-full text-xs font-medium text-slate-500 cursor-pointer hover:border-indigo-400 hover:text-indigo-600 transition-colors shadow-sm';
            chip.innerText = q;
            chip.onclick = () => {
                document.getElementById('user-question').value = q;
                askBtn.click();
            };
            suggestedQuestionsCont.appendChild(chip);
        });
    }

    initSuggestions();

    // The Assistant is now a main tab, no sliding logic needed.

    // File Upload Handling
    fileUpload.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            processBtn.disabled = false;
            processBtn.innerHTML = `<svg class="w-5 h-5 mr-1 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg> Process ${e.target.files[0].name.substring(0, 15)}...`;
        }
    });

    // Process Document
    processBtn.addEventListener('click', async () => {
        const file = fileUpload.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        console.log("Starting upload process for:", file.name);
        showLoader("Extracting Legislative Text...");

        try {
            // Step 1: Upload & Extract
            const uploadRes = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!uploadRes.ok) {
                const errData = await uploadRes.json();
                throw new Error(errData.error || "Upload failed");
            }
            
            const uploadData = await uploadRes.json();
            console.log("Upload successful, text extracted");
            extractedText = uploadData.text;

            // Step 2: Analyze
            showLoader("Compressing Context & Summarizing...");
            const lang = document.getElementById('language-select').value;
            
            const analyzeRes = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: extractedText, 
                    language: lang
                })
            });

            if (!analyzeRes.ok) {
                const errData = await analyzeRes.json();
                throw new Error(errData.error || "Analysis failed");
            }

            const analyzeData = await analyzeRes.json();
            console.log("Analysis complete");
            updateUI(analyzeData);
            
            // Step 3: Fetch Extras (Compliance, Citations, Timeline, Entities)
            fetchComplianceAndCitations(extractedText, lang);
            fetchVisualData(extractedText, lang);
            
            hideLoader();
        } catch (error) {
            console.error("Pipeline error:", error);
            alert("Error: " + error.message);
            hideLoader();
        }
    });

    // --- Bill Comparison Logic ---
    const fileV1 = document.getElementById('file-v1');
    const fileV2 = document.getElementById('file-v2');
    const compareRunBtn = document.getElementById('compare-run-btn');
    const v1Name = document.getElementById('v1-name');
    const v2Name = document.getElementById('v2-name');

    let textV1 = "";
    let textV2 = "";

    fileV1.addEventListener('change', async (e) => {
        if (e.target.files[0]) {
            v1Name.innerText = e.target.files[0].name;
            textV1 = await extractFileText(e.target.files[0]);
            checkCompareStatus();
        }
    });

    fileV2.addEventListener('change', async (e) => {
        if (e.target.files[0]) {
            v2Name.innerText = e.target.files[0].name;
            textV2 = await extractFileText(e.target.files[0]);
            checkCompareStatus();
        }
    });

    function checkCompareStatus() {
        if (textV1 && textV2) {
            compareRunBtn.disabled = false;
        }
    }

    async function extractFileText(file) {
        const formData = new FormData();
        formData.append('file', file);
        showLoader(`Processing ${file.name}...`);
        try {
            const res = await fetch('/upload', { method: 'POST', body: formData });
            const data = await res.json();
            hideLoader();
            return data.text;
        } catch (e) {
            alert("Failed to extract text from " + file.name);
            hideLoader();
            return "";
        }
    }

    compareRunBtn.addEventListener('click', async () => {
        const lang = document.getElementById('language-select').value;
        showLoader("Generating Comparative Analysis...");
        try {
            const res = await fetch('/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text1: textV1, text2: textV2, language: lang })
            });
            const data = await res.json();
            const compContent = document.getElementById('comparison-content');
            compContent.innerHTML = formatMarkdown(data.comparison);
            compContent.classList.remove('dashed-box');
            const compInsights = document.getElementById('compare-insights');
            compInsights.innerHTML = `<p>Analysis complete. ${textV2.length - textV1.length > 0 ? 'Document size increased.' : 'Document size decreased or stayed same.'}</p>`;
            compInsights.classList.remove('dashed-box');
        } catch (e) {
            alert("Comparison failed: " + e.message);
        }
        hideLoader();
    });

    // Q&A Handling
    askBtn.addEventListener('click', async () => {
        const question = document.getElementById('user-question').value;
        const lang = document.getElementById('language-select').value;

        if (!question) return;
        
        if (!extractedText) {
            alert("Please upload a document first.");
            return;
        }

        addMessage(question, 'user');
        document.getElementById('user-question').value = "";

        try {
            const res = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: extractedText,
                    question: question,
                    language: lang
                })
            });
            const data = await res.json();
            addMessage(data.answer, 'ai');
        } catch (error) {
            addMessage("Sorry, I couldn't process that question.", 'ai');
        }
    });

    // TTS Handling
    listenBtn.addEventListener('click', async () => {
        if (!summaryText || summaryText === "No summary available.") {
            alert("Please process a document first to generate a summary.");
            return;
        }
        
        try {
            listenBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Loading...';
            const lang = document.getElementById('language-select').value;
            const res = await fetch('/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: summaryText, language: lang })
            });
            const data = await res.json();

            if (data.error) throw new Error(data.error);
            
            audioPlayer.src = `data:audio/mp3;base64,${data.audio}`;
            audioPlayer.load(); // must call load() before play() on some browsers
            audioPlayer.play().catch(err => {
                console.error("Audio play error:", err);
                alert("Could not play audio automatically. Please try again.");
            });
            listenBtn.innerHTML = '<i class="fas fa-volume-up mr-2"></i> Listen';
        } catch (error) {
            console.error("TTS error:", error);
            alert("Audio generation failed: " + error.message);
            listenBtn.innerHTML = '<i class="fas fa-volume-up mr-2"></i> Listen';
        }
    });

    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.addEventListener('click', async () => {
        if (!summaryText || summaryText === "No summary available.") return;

        try {
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            const lang = document.getElementById('language-select').value;
            
            const res = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: summaryText, language: lang })
            });

            if (!res.ok) throw new Error("PDF generation failed");

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "Legislative_Summary.pdf";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            downloadBtn.innerHTML = '<i class="fas fa-download mr-2"></i> Download';
        } catch (error) {
            alert("Download failed: " + error.message);
            downloadBtn.innerHTML = '<i class="fas fa-download mr-2"></i> Download';
        }
    });

    function updateUI(data) {
        if (!data) return;

        summaryText = data.summary || "No summary available.";
        summaryContent.innerHTML = formatMarkdown(summaryText);
        summaryContent.classList.remove('dashed-box');
        
        glossaryContent.innerHTML = formatMarkdown(data.glossary || "No glossary items found.");
        glossaryContent.classList.remove('dashed-box');

        // Update Radar Chart
        if (data.risk_data) {
            renderRiskChart(data.risk_data);
        }

        // Metrics with defensive checks
        const metrics = data.metrics || { original_tokens: 0, compressed_tokens: 0, ratio: 1.0 };
        const original = metrics.original_tokens || 0;
        const compressed = metrics.compressed_tokens || 0;
        const ratio = metrics.ratio || 1.0;
        const savings = Math.max(0, original - compressed);

        document.getElementById('token-savings').innerText = savings.toLocaleString();
        document.getElementById('cost-saved').innerText = `$${(savings / 1000000 * 10).toFixed(4)}`;
        document.getElementById('comp-ratio').innerText = `${ratio.toFixed(2)}x`;
    }

    async function fetchComplianceAndCitations(text, lang) {
        try {
            // Compliance Checklist
            const compRes = await fetch('/compliance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, language: lang })
            });
            const compData = await compRes.json();
            const compEl = document.getElementById('compliance-content');
            if (compData.checklist) {
                // Convert list items to pretty boxes
                let html = formatMarkdown(compData.checklist);
                // Simple hack to convert [ ] into styled list items if marked doesn't do it
                compEl.innerHTML = html;
                compEl.classList.remove('dashed-box');
            }

            // Citations
            const citeRes = await fetch('/citations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, language: lang })
            });
            const citeData = await citeRes.json();
            const citeEl = document.getElementById('citations-content');
            if (citeData.citations) {
                citeEl.innerHTML = formatMarkdown(citeData.citations);
                citeEl.classList.remove('dashed-box');
            }
        } catch (e) {
            console.error("Extras fetch failed:", e);
        }
    }

    async function fetchVisualData(text, lang) {
        try {
            // Timeline
            const timeRes = await fetch('/timeline', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, language: lang })
            });
            const timeData = await timeRes.json();
            if (timeData.timeline) {
                renderTimeline(timeData.timeline);
                document.getElementById('timeline-content').classList.remove('dashed-box');
            }

            // Entities
            const entRes = await fetch('/entities', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, language: lang })
            });
            const entData = await entRes.json();
            if (entData.entities) renderEntityMap(entData.entities);
        } catch (e) {
            console.error("Visual data fetch failed:", e);
        }
    }

    function renderTimeline(events) {
        const cont = document.getElementById('timeline-content');
        cont.innerHTML = "";
        if (!events || events.length === 0) {
            cont.innerHTML = "<p>No timeline data found.</p>";
            return;
        }

        const timelineList = document.createElement('div');
        timelineList.className = 'timeline-list';
        
        events.forEach(ev => {
            const item = document.createElement('div');
            item.className = 'timeline-item';
            item.innerHTML = `
                <div class="timeline-date">${ev.date}</div>
                <div class="timeline-marker"></div>
                <div class="timeline-event">${ev.event}</div>
            `;
            timelineList.appendChild(item);
        });
        cont.appendChild(timelineList);
    }

    function renderEntityMap(links) {
        const cont = document.getElementById('visuals-tab').querySelector('.side-panels');
        // We'll create a new section for the Entity Map
        let mapSec = document.getElementById('entity-map-section');
        if (!mapSec) {
            mapSec = document.createElement('section');
            mapSec.id = 'entity-map-section';
            mapSec.className = 'glossary-panel glass';
            mapSec.innerHTML = '<h3>🗺️ Entity Relationship Map</h3><div id="entity-map-svg" style="height: 300px; width: 100%;"></div>';
            cont.appendChild(mapSec);
        }

        const width = 300;
        const height = 300;
        const svgArea = document.getElementById('entity-map-svg');
        svgArea.innerHTML = "";

        const svg = d3.select("#entity-map-svg")
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", `0 0 ${width} ${height}`);

        // Very simple Force Graph logic
        const nodes = Array.from(new Set(links.flatMap(l => [l.source, l.target])), id => ({id}));
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke-width", 1);

        const node = svg.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", 5)
            .attr("fill", "#5c8d89");

        node.append("title").text(d => d.id);

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });
    }

    function renderRiskChart(riskData) {
        const ctx = document.getElementById('riskRadarChart').getContext('2d');
        const isDark = document.body.classList.contains('dark-mode');
        const textColor = isDark ? '#94a3b8' : '#707793';
        const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

        if (riskChart) riskChart.destroy();

        riskChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Complexity', 'Burdens', 'Legal Risk', 'Rights Prot.'],
                datasets: [{
                    label: 'Legislative Scores',
                    data: [riskData.complexity, riskData.burden, riskData.risk, riskData.protection],
                    backgroundColor: 'rgba(92, 141, 137, 0.2)',
                    borderColor: '#5c8d89',
                    pointBackgroundColor: '#5c8d89',
                    borderWidth: 2
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: { color: gridColor },
                        grid: { color: gridColor },
                        pointLabels: { color: textColor, font: { size: 12 } },
                        ticks: { display: false },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    function addMessage(text, type) {
        const div = document.createElement('div');
        div.className = `bubble ${type === 'user' ? 'user-msg' : 'ai-msg'}`;
        
        if (type === 'ai') {
            div.innerHTML = `
                <div class="msg-content text-sm text-slate-700 space-y-2">${formatMarkdown(text)}</div>
                <div class="mt-3 pt-2 border-t border-slate-200 flex gap-2">
                    <button class="copy-btn text-xs font-semibold text-slate-500 hover:text-indigo-600 flex items-center gap-1 transition-colors"><i class="fas fa-copy"></i> Copy Answer</button>
                </div>
            `;
            const copyBtn = div.querySelector('.copy-btn');
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(text);
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy Answer';
                }, 2000);
            };
        } else {
            div.innerText = text;
        }
        
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showLoader(text) {
        console.log("SHOW LOADER:", text);
        if (!loader) {
            console.error("Loader element NOT FOUND in DOM!");
            return;
        }
        loaderText.innerText = text;
        loader.style.display = 'flex';
        loader.style.opacity = '1';
    }

    function hideLoader() {
        console.log("HIDE LOADER");
        if (loader) {
            loader.style.display = 'none';
        }
    }

    // Use marked library for robust markdown rendering
    function formatMarkdown(text) {
        if (!text) return "";
        // Optional: configure marked options if needed
        return marked.parse(text);
    }


});
