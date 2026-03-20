import streamlit as st
import os
from gtts import gTTS
from src.utils.pdf_handler import extract_text_from_pdf
from src.utils.analyzer import LegislativeAnalyzer
from src.utils.report_gen import ReportGenerator

st.set_page_config(
    page_title="AI Legislative Analyzer – Pro Dashboard",
    page_icon="⚖️",
    layout="wide"
)

# Initialize Session State
if 'history' not in st.session_state: st.session_state.history = []
if 'summary' not in st.session_state: st.session_state.summary = ""
if 'glossary' not in st.session_state: st.session_state.glossary = ""
if 'metrics' not in st.session_state: st.session_state.metrics = {}
if 'source_text' not in st.session_state: st.session_state.source_text = ""

# Custom CSS for Premium Design
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; transition: 0.3s; width: 100%; border: none; padding: 10px; font-weight: bold; }
    .stButton>button:hover { background-color: #45a049; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(76,175,80,0.3); }
    .metric-card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border-left: 5px solid #4CAF50; }
    .chat-bubble { padding: 12px; border-radius: 15px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); }
    .user-bubble { background: rgba(76,175,80,0.1); border-left: 4px solid #4CAF50; }
    .ai-bubble { background: rgba(255,255,255,0.02); border-left: 4px solid #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ AI Legislative Analyzer – Pro")
st.caption("Advanced Context Compression & Citizen-Friendly Intelligence")

analyzer = LegislativeAnalyzer()
reporter = ReportGenerator()

# Sidebar
with st.sidebar:
    st.header("🌐 Language Settings")
    selected_language = st.selectbox("Output Language", ["English", "Hindi", "Gujarati"])
    
    st.divider()
    st.header("🔍 Citizen Assistant")
    user_question = st.text_input("Ask a specific question:")
    ask_button = st.button("Analyze & Answer")
    
    if st.session_state.history:
        st.divider()
        st.subheader("💬 Chat History")
        for chat in reversed(st.session_state.history):
            with st.expander(f"Q: {chat['q'][:30]}..."):
                st.write(f"**Question:** {chat['q']}")
                st.write(f"**Answer:** {chat['a']}")

# Main Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Legislative PDF Document", type="pdf")

    if uploaded_file:
        # Save temp file
        temp_path = os.path.join("tmp", uploaded_file.name)
        os.makedirs("tmp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("⚡ Process Document") or st.session_state.source_text == "":
            with st.spinner("Compressing context..."):
                text = extract_text_from_pdf(temp_path)
                if text:
                    st.session_state.source_text = text
                    st.session_state.summary, st.session_state.metrics = analyzer.generate_summary(text, language=selected_language)
                    st.session_state.glossary = analyzer.extract_glossary(text, language=selected_language)
                    st.success("Analysis Complete!")
                else:
                    st.error("Text extraction failed.")

        if st.session_state.summary:
            st.header(f"📋 Simplified Summary ({selected_language})")
            
            # TTS Feature
            if st.button("📢 Listen to Summary"):
                lang_code = analyzer.lang_map.get(selected_language, 'en')
                tts = gTTS(text=st.session_state.summary, lang=lang_code)
                tts_path = os.path.join("tmp", "summary.mp3")
                tts.save(tts_path)
                st.audio(tts_path)
            
            st.markdown(st.session_state.summary)
            
            # Download Feature
            pdf_path = reporter.generate_summary_pdf(st.session_state.summary, selected_language)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download Report (PDF)", f, file_name="Summary.pdf", mime="application/pdf")

with col2:
    if st.session_state.metrics:
        st.header("💰 Efficiency Hub")
        orig = st.session_state.metrics.get('original_tokens', 0)
        comp = st.session_state.metrics.get('compressed_tokens', 0)
        saving = orig - comp
        cost_saved = (saving / 1000000) * 10 # Estimate $10 per 1M tokens
        
        st.markdown(f"""
            <div class="metric-card">
                <h3>Token Savings</h3>
                <h2 style="color:#4CAF50;">{saving:,} Tokens</h2>
                <p>Saved using ScaleDown Compression</p>
            </div>
        """, unsafe_allow_html=True)
        st.metric("Estimated Cost Saved", f"${cost_saved:.4f}")
        st.metric("Compression Ratio", f"{st.session_state.metrics.get('ratio', 1.0):.2f}x")

    if st.session_state.glossary:
        st.divider()
        st.header("📜 Smart Glossary")
        st.info("Key legal terms simplified for you.")
        st.markdown(st.session_state.glossary)

# Q&A Handling
if ask_button and user_question and st.session_state.source_text:
    with col1:
        st.divider()
        st.markdown(f'<div class="chat-bubble user-bubble"><b>Q:</b> {user_question}</div>', unsafe_allow_html=True)
        with st.spinner("Finding answer in compressed context..."):
            answer, _ = analyzer.ask_question(st.session_state.source_text, user_question, language=selected_language)
            st.markdown(f'<div class="chat-bubble ai-bubble"><b>A:</b> {answer}</div>', unsafe_allow_html=True)
            st.session_state.history.append({"q": user_question, "a": answer})

st.divider()
st.caption("Powered by ScaleDown API & DeepMind Antigravity Intelligence")
