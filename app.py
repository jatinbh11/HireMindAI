# app.py
# Main Streamlit application — AI Interview Coach

import os
import time
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils import (
    generate_questions,
    evaluate_answer,
    improve_answer,
    generate_final_report,
    extract_text_from_pdf,
    analyze_resume,
    save_interview_history,
    get_history_dataframe,
    load_all_history,
    score_to_color,
    score_to_label,
    format_time,
)

# ─────────────────────────────────────────────
# PAGE CONFIG & GLOBAL STYLES
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="HireMind AI - Ai Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for professional styling
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #0a0f1e;
    --bg-card: #111827;
    --bg-card2: #1a2235;
    --accent: #6366f1;
    --accent2: #8b5cf6;
    --accent3: #06b6d4;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
    --text-primary: #f1f5f9;
    --text-muted: #94a3b8;
    --border: rgba(99,102,241,0.2);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1424 0%, #111827 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* Keep header visible so sidebar toggle works */
header {
    visibility: visible !important;
    background: transparent !important;
}
/* Hide only the deploy button and footer */
.stDeployButton, footer, #MainMenu {
    visibility: hidden !important;
    display: none !important;
}
/* Ensure hamburger menu remains clickable */
button[kind="header"] {
    visibility: visible !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.8rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.25) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent3)) !important;
    border-radius: 10px !important;
}
.stProgress > div > div {
    background: var(--bg-card2) !important;
    border-radius: 10px !important;
}

/* ── Cards ── */
.coach-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.coach-card-accent {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-label {
    font-size: 0.82rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Question bubble ── */
.question-bubble {
    background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.1));
    border-left: 4px solid var(--accent);
    border-radius: 0 14px 14px 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.6;
}

/* ── Score badge ── */
.score-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 100px;
    font-weight: 700;
    font-size: 0.9rem;
}

/* ── Timer ── */
.timer-display {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem;
    font-weight: 600;
    color: var(--accent3);
    text-align: center;
    letter-spacing: 0.1em;
}
.timer-warning {
    color: var(--warning) !important;
}
.timer-danger {
    color: var(--danger) !important;
    animation: pulse 1s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ── Section headers ── */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
    background: linear-gradient(135deg, #f1f5f9, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.section-sub {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
}

/* ── Tags / chips ── */
.skill-chip {
    display: inline-block;
    background: rgba(99,102,241,0.18);
    border: 1px solid rgba(99,102,241,0.35);
    color: #a5b4fc;
    border-radius: 100px;
    padding: 0.25rem 0.8rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 0.2rem;
}
.weak-chip {
    background: rgba(239,68,68,0.15);
    border-color: rgba(239,68,68,0.35);
    color: #fca5a5;
}
.strong-chip {
    background: rgba(34,197,94,0.15);
    border-color: rgba(34,197,94,0.35);
    color: #86efac;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 12px !important;
}

/* ── Hide empty ghost boxes ── */
.element-container:empty { display: none !important; }
.stMarkdown:empty { display: none !important; }
.stMarkdown p:empty { display: none !important; margin: 0 !important; padding: 0 !important; }
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 0.3rem !important;
    gap: 0.2rem !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--bg-card2) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* ── Feature Grid (Home Page) ── */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1rem 0 2rem 0;
}
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: transform 0.2s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
}
.feature-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.feature-title {
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 0.3rem;
    color: var(--text-primary);
}
.feature-desc {
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.4;
}
@media (max-width: 768px) {
    .feature-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────

def init_session():
    defaults = {
        "page": "home",
        "role": None,
        "round_type": "Technical",
        "questions": [],
        "current_q_idx": 0,
        "answers": [],
        "evaluations": [],
        "improved_answers": {},
        "all_weak_skills": [],
        "scores": [],
        "final_report": None,
        "resume_text": "",
        "resume_info": {},
        "interview_started": False,
        "interview_complete": False,
        "timer_start": None,
        "num_questions": 5,
        "time_per_question": 120,
        "show_improved": False,
        "last_answered_idx": -1,
        "last_evaluation": None,
        "last_answer_text": "",
        "pending_improve": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0; text-align: center;">
            <div style="font-size: 2.5rem;">🎯</div>
            <div style="font-size: 1.2rem; font-weight: 800; background: linear-gradient(135deg, #6366f1, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                HireMind AI
            </div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.2rem;">
                Agentic Interview Coach
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown('<div style="font-size:0.75rem; color:#64748b; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; padding: 0 0.5rem 0.5rem;">Navigation</div>', unsafe_allow_html=True)

        pages = [
            ("🏠", "Home", "home"),
            ("🎤", "Interview", "interview"),
            ("📊", "Report", "report"),
            ("📁", "History", "history"),
        ]

        for icon, label, page_key in pages:
            is_active = st.session_state.page == page_key
            btn_style = "primary" if is_active else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True, type=btn_style):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("---")

        if st.session_state.interview_started and not st.session_state.interview_complete:
            st.markdown('<div style="font-size:0.75rem; color:#64748b; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; padding: 0 0.5rem 0.5rem;">Session</div>', unsafe_allow_html=True)

            q_idx = st.session_state.current_q_idx
            total = len(st.session_state.questions)
            progress = q_idx / total if total > 0 else 0

            st.markdown(f"""
            <div style="background:#1a2235; border-radius:12px; padding:1rem; border: 1px solid rgba(99,102,241,0.2);">
                <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.3rem;">Progress</div>
                <div style="font-size:1.5rem; font-weight:800; color:#6366f1;">{q_idx}/{total}</div>
                <div style="font-size:0.8rem; color:#64748b;">Questions</div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(progress)

            if st.session_state.role:
                st.markdown(f"""
                <div style="margin-top: 0.8rem;">
                    <span class="skill-chip">{st.session_state.role}</span>
                    <span class="skill-chip">{st.session_state.round_type}</span>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🛑 End Interview", use_container_width=True):
                if len(st.session_state.answers) > 0:
                    st.session_state.interview_complete = True
                    st.session_state.page = "report"
                    st.rerun()

        if st.session_state.scores:
            avg = sum(st.session_state.scores) / len(st.session_state.scores)
            color = score_to_color(int(avg))
            st.markdown(f"""
            <div style="background:#1a2235; border-radius:12px; padding:1rem; border: 1px solid rgba(99,102,241,0.2); margin-top:0.5rem;">
                <div style="font-size:0.8rem; color:#94a3b8;">Avg Score</div>
                <div style="font-size:2rem; font-weight:800; color:{color};">{avg:.1f}<span style="font-size:1rem; color:#64748b;">/10</span></div>
            </div>
            """, unsafe_allow_html=True)

        # st.markdown("---")
        st.markdown('<div style="font-size:1rem; color:#334155; text-align:center; padding:0.5rem;">Developed by Jatin Bhargav 🚀</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: HOME / SETUP
# ─────────────────────────────────────────────

def page_home():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1.5rem 0;">
        <div style="font-size: 3.5rem; margin-bottom: 0.5rem;">🎯</div>
        <h1 style="font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 50%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; line-height: 1.1;">
           HireMind AI- Ai Interview Coach
        </h1>
        <p style="color: #64748b; font-size: 1.1rem; margin-top: 0.8rem; font-weight: 400;">
            Agentic AI-powered interview simulator · Real feedback · Real growth
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature grid (CSS Grid ensures equal widths regardless of sidebar)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Questions</div>
            <div class="feature-desc">Role-specific questions generated in real-time</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Smart Evaluation</div>
            <div class="feature-desc">Score + strengths + weaknesses per answer</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">✨</div>
            <div class="feature-title">Answer Coach</div>
            <div class="feature-desc">AI rewrites your answer to perfection</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Report Dashboard</div>
            <div class="feature-desc">Full performance analysis with charts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Setup Form
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<div class="section-header">⚙️ Configure Your Interview</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Set up your session before starting</div>', unsafe_allow_html=True)


        st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#94a3b8; margin-bottom:0.4rem;">🎭 Target Role</div>', unsafe_allow_html=True)
        role = st.selectbox(
            label="Target Role",
            label_visibility="collapsed",
            options=[
                "Data Scientist",
                "AI / ML Engineer",
                "Web Developer (Frontend)",
                "Web Developer (Backend)",
                "Full Stack Developer",
                "Data Analyst",
                "DevOps Engineer",
                "Software Engineer",
                "Product Manager",
                "Business Analyst",
            ],
            index=0,
        )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#94a3b8; margin-bottom:0.4rem;">🔄 Interview Round</div>', unsafe_allow_html=True)
            round_type = st.selectbox(
                label="Interview Round",
                label_visibility="collapsed",
                options=["Technical", "HR / Behavioral", "Mixed (HR + Technical)"],
                index=0,
            )
        with col_r2:
            st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#94a3b8; margin-bottom:0.4rem;">❓ Number of Questions</div>', unsafe_allow_html=True)
            num_questions = st.slider(
                label="Number of Questions",
                label_visibility="collapsed",
                min_value=3,
                max_value=10,
                value=5,
                step=1,
            )

        st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#94a3b8; margin-bottom:0.4rem; margin-top:0.5rem;">⏱️ Time per Question (seconds)</div>', unsafe_allow_html=True)
        time_per_q = st.slider(
            label="Time per Question",
            label_visibility="collapsed",
            min_value=60,
            max_value=300,
            value=120,
            step=30,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-header">📎 Upload Resume (Optional)</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Questions will be tailored to your resume</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload your resume (PDF)",
            type=["pdf"],
            help="Optional: upload your resume for personalized questions"
        )

        if uploaded_file:
            with st.spinner("📖 Parsing resume..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                resume_info = analyze_resume(resume_text)
                st.session_state.resume_text = resume_text
                st.session_state.resume_info = resume_info

            if resume_info:
                st.success("✅ Resume parsed successfully!")
                chips = ""
                for skill in resume_info.get("skills", [])[:6]:
                    chips += f'<span class="skill-chip strong-chip">{skill}</span>'
                st.markdown(f"""
                <div class="coach-card" style="margin-top:0.5rem;">
                    <div style="font-weight:700; margin-bottom:0.5rem;">👤 {resume_info.get('name', 'Candidate')}</div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.5rem;">
                        {resume_info.get('experience_years', '?')} experience · {resume_info.get('education', '?')}
                    </div>
                    <div>{chips}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Start Interview Session", use_container_width=True, type="primary"):
            st.session_state.role = role
            st.session_state.round_type = round_type
            st.session_state.num_questions = num_questions
            st.session_state.time_per_question = time_per_q
            st.session_state.questions = []
            st.session_state.current_q_idx = 0
            st.session_state.answers = []
            st.session_state.evaluations = []
            st.session_state.improved_answers = {}
            st.session_state.all_weak_skills = []
            st.session_state.scores = []
            st.session_state.final_report = None
            st.session_state.interview_started = True
            st.session_state.interview_complete = False
            st.session_state.timer_start = time.time()
            st.session_state.page = "interview"

            with st.spinner(f"🤖 Generating {num_questions} {round_type} questions for {role}..."):
                questions = generate_questions(
                    role=role,
                    round_type=round_type,
                    num_questions=num_questions,
                    resume_text=st.session_state.resume_text,
                )
                st.session_state.questions = questions

            st.rerun()

    with col_right:
        st.markdown('<div class="section-header">📋 How It Works</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Your journey to interview success</div>', unsafe_allow_html=True)

        steps = [
            ("1", "#6366f1", "Configure", "Choose your role, round type, and number of questions"),
            ("2", "#8b5cf6", "Interview", "Answer AI-generated questions one at a time with a timer"),
            ("3", "#06b6d4", "Get Feedback", "Receive instant scoring and detailed analysis per answer"),
            ("4", "#22c55e", "Improve", "Let AI rewrite your answer into a perfect response"),
            ("5", "#f59e0b", "Report", "View full dashboard with charts, weak areas, and next steps"),
        ]

        for num, color, title, desc in steps:
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; gap:1rem; margin-bottom:1rem; background:#111827; border-radius:12px; padding:1rem; border: 1px solid rgba(255,255,255,0.06);">
                <div style="width:32px; height:32px; border-radius:50%; background:{color}; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:0.9rem; flex-shrink:0;">{num}</div>
                <div>
                    <div style="font-weight:700; font-size:0.95rem;">{title}</div>
                    <div style="font-size:0.82rem; color:#64748b; line-height:1.4; margin-top:0.2rem;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.1)); border:1px solid rgba(99,102,241,0.4); border-radius:16px; padding:1.5rem; margin-top:0.5rem;">
            <div style="font-weight:700; margin-bottom:0.5rem;">💡 Pro Tips</div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.8;">
                • Answer in full sentences<br>
                • Use STAR method for behavioral questions<br>
                • Always mention specific technologies<br>
                • Upload resume for tailored questions<br>
                • Try both Technical and HR rounds
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: INTERVIEW
# ─────────────────────────────────────────────

def page_interview():
    if not st.session_state.interview_started or not st.session_state.questions:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem;">
            <div style="font-size:3rem;">🎤</div>
            <div style="font-size:1.3rem; font-weight:700; margin:1rem 0 0.5rem;">No Active Interview</div>
            <div style="color:#64748b;">Go to Home to set up and start your interview session.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Go to Home", type="primary"):
            st.session_state.page = "home"
            st.rerun()
        return

    if st.session_state.interview_complete:
        st.markdown("""
        <div style="text-align:center; padding:3rem 2rem;">
            <div style="font-size:3rem;">✅</div>
            <div style="font-size:1.3rem; font-weight:700; margin:1rem 0 0.5rem;">Interview Complete!</div>
            <div style="color:#64748b;">View your full performance report.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 View Report", type="primary"):
            st.session_state.page = "report"
            st.rerun()
        return

    questions = st.session_state.questions
    q_idx = st.session_state.current_q_idx
    total = len(questions)

    if q_idx >= total:
        st.session_state.interview_complete = True
        if not st.session_state.final_report:
            with st.spinner("🤖 Generating your performance report..."):
                report = generate_final_report(
                    role=st.session_state.role,
                    questions=st.session_state.questions,
                    answers=st.session_state.answers,
                    scores=st.session_state.scores,
                    all_weak_skills=st.session_state.all_weak_skills,
                )
                st.session_state.final_report = report
                save_interview_history(
                    role=st.session_state.role,
                    round_type=st.session_state.round_type,
                    questions=st.session_state.questions,
                    answers=st.session_state.answers,
                    scores=st.session_state.scores,
                    report=report,
                )
        st.session_state.page = "report"
        st.rerun()
        return

    current_question = questions[q_idx]

    col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
    with col_h1:
        st.markdown(f"""
        <div>
            <span style="font-size:0.8rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.08em;">
                {st.session_state.role} · {st.session_state.round_type}
            </span>
            <div class="section-header" style="margin-top:0.2rem;">Question {q_idx + 1} of {total}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#6366f1;">{q_idx}/{total}</div>
            <div class="metric-label">Done</div>
        </div>
        """, unsafe_allow_html=True)
    with col_h3:
        avg = sum(st.session_state.scores) / len(st.session_state.scores) if st.session_state.scores else 0
        color = score_to_color(int(avg)) if avg else "#6366f1"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color};">{avg:.1f}</div>
            <div class="metric-label">Avg Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.progress(q_idx / total)
    st.markdown("<br>", unsafe_allow_html=True)

    time_limit = st.session_state.time_per_question
    timer_placeholder = st.empty()
    if time_limit > 0:
        if st.session_state.timer_start is None:
            st.session_state.timer_start = time.time()
        elapsed = int(time.time() - st.session_state.timer_start)
        remaining = max(0, time_limit - elapsed)
        t_color = '#ef4444' if remaining < 20 else '#f59e0b' if remaining < 60 else '#06b6d4'
        timer_placeholder.markdown(f"""
        <div class="coach-card" style="text-align:center; padding:0.8rem;">
            <span style="font-size:0.8rem; color:#64748b; text-transform:uppercase; letter-spacing:0.08em;">⏱ Time Remaining</span>
            <div style="font-family:'JetBrains Mono',monospace; font-size:2.2rem; font-weight:700; color:{t_color}; letter-spacing:0.12em;">{format_time(remaining)}</div>
        </div>
        """, unsafe_allow_html=True)
        if remaining == 0 and st.session_state.last_answered_idx < q_idx:
            st.warning("⏰ Time's up! Moving to next question.")
            st.session_state.answers.append("[Time expired]")
            st.session_state.scores.append(0)
            st.session_state.evaluations.append(None)
            st.session_state.current_q_idx += 1
            st.session_state.timer_start = time.time()
            st.rerun()

    st.markdown(f"""
    <div class="question-bubble">
        <div style="font-size:0.78rem; color:#6366f1; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.6rem;">
            🤖 Interviewer
        </div>
        {current_question}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-weight:600; font-size:0.9rem; margin-bottom:0.5rem; color:#94a3b8;">✍️ Your Answer</div>', unsafe_allow_html=True)
    user_answer = st.text_area(
        label="",
        placeholder="Type your answer here... Be specific, use examples, and structure your response clearly.",
        height=160,
        key=f"answer_input_{q_idx}",
        label_visibility="collapsed"
    )

    word_count = len(user_answer.split()) if user_answer.strip() else 0
    wc_color = "#22c55e" if word_count >= 50 else "#f59e0b" if word_count >= 20 else "#ef4444"
    st.markdown(f'<div style="font-size:0.8rem; color:{wc_color}; margin-top:-0.5rem; margin-bottom:1rem;">📝 {word_count} words {"(Good length)" if word_count >= 50 else "(Try to write more)"}</div>', unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        already_answered = st.session_state.last_answered_idx >= q_idx
        if not already_answered:
            submit = st.button("📤 Submit Answer & Get Feedback", use_container_width=True, type="primary")
        else:
            submit = False
    with col_btn2:
        skip = st.button("⏭️ Skip Question", use_container_width=True)

    if skip and not already_answered:
        st.session_state.answers.append("[Skipped]")
        st.session_state.scores.append(0)
        st.session_state.evaluations.append(None)
        st.session_state.last_answered_idx = q_idx
        st.session_state.current_q_idx += 1
        st.session_state.timer_start = time.time()
        st.session_state.pending_improve = False
        st.rerun()

    if submit:
        if not user_answer.strip():
            st.warning("⚠️ Please write an answer before submitting.")
        else:
            with st.spinner("🤖 Evaluating your answer..."):
                evaluation = evaluate_answer(
                    role=st.session_state.role,
                    question=current_question,
                    answer=user_answer,
                )
            st.session_state.answers.append(user_answer)
            st.session_state.scores.append(evaluation["score"])
            st.session_state.evaluations.append(evaluation)
            st.session_state.all_weak_skills.extend(evaluation.get("weak_skills", []))
            st.session_state.last_evaluation = evaluation
            st.session_state.last_answer_text = user_answer
            st.session_state.last_answered_idx = q_idx
            st.session_state.pending_improve = False
            st.rerun()

    if st.session_state.last_answered_idx >= q_idx and st.session_state.last_evaluation:
        evaluation = st.session_state.last_evaluation
        score = evaluation["score"]
        color = score_to_color(score)
        label = score_to_label(score)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="coach-card" style="border-color: {color}40;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
                <div style="font-size:1.1rem; font-weight:700;">📊 Evaluation Result</div>
                <div style="background:{color}22; border:1px solid {color}66; border-radius:100px; padding:0.4rem 1.2rem; font-weight:800; color:{color}; font-size:1.1rem;">
                    {score}/10 · {label}
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            strengths = evaluation.get("strengths", [])
            st.markdown('<div style="font-weight:700; color:#22c55e; margin-bottom:0.5rem;">✅ Strengths</div>', unsafe_allow_html=True)
            for s in strengths:
                st.markdown(f'<div style="font-size:0.88rem; color:#94a3b8; padding:0.3rem 0; border-bottom:1px solid #1e293b;">• {s}</div>', unsafe_allow_html=True)
        with col_e2:
            weaknesses = evaluation.get("weaknesses", [])
            st.markdown('<div style="font-weight:700; color:#ef4444; margin-bottom:0.5rem;">⚠️ Weaknesses</div>', unsafe_allow_html=True)
            for w in weaknesses:
                st.markdown(f'<div style="font-size:0.88rem; color:#94a3b8; padding:0.3rem 0; border-bottom:1px solid #1e293b;">• {w}</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div style="margin-top:1rem; background:#1a2235; border-radius:10px; padding:1rem;">
                <div style="font-size:0.8rem; color:#6366f1; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">Clarity</div>
                <div style="font-size:0.9rem; color:#94a3b8; margin-top:0.3rem;">{evaluation.get('clarity', 'N/A')}</div>
            </div>
            <div style="margin-top:0.7rem; background:#1a2235; border-radius:10px; padding:1rem;">
                <div style="font-size:0.8rem; color:#06b6d4; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">Technical Accuracy</div>
                <div style="font-size:0.9rem; color:#94a3b8; margin-top:0.3rem;">{evaluation.get('technical_accuracy', 'N/A')}</div>
            </div>
            <div style="margin-top:0.7rem; background:rgba(99,102,241,0.1); border-radius:10px; padding:1rem; border:1px solid rgba(99,102,241,0.2);">
                <div style="font-size:0.8rem; color:#a5b4fc; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">💬 Coach Feedback</div>
                <div style="font-size:0.9rem; color:#cbd5e1; margin-top:0.3rem;">{evaluation.get('brief_feedback', '')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_imp1, col_imp2 = st.columns(2)

        with col_imp1:
            if q_idx not in st.session_state.improved_answers:
                if st.button("✨ Show AI-Improved Answer", use_container_width=True, key=f"improve_btn_{q_idx}"):
                    st.session_state.pending_improve = True
            else:
                st.success("✅ AI Answer Generated Below")

        with col_imp2:
            if q_idx < total - 1:
                if st.button("➡️ Next Question", use_container_width=True, type="primary", key=f"next_btn_{q_idx}"):
                    st.session_state.current_q_idx += 1
                    st.session_state.timer_start = time.time()
                    st.session_state.last_evaluation = None
                    st.session_state.pending_improve = False
                    st.rerun()
            else:
                if st.button("🏁 Finish & View Report", use_container_width=True, type="primary", key=f"finish_btn_{q_idx}"):
                    with st.spinner("🤖 Generating performance report..."):
                        report = generate_final_report(
                            role=st.session_state.role,
                            questions=st.session_state.questions,
                            answers=st.session_state.answers,
                            scores=st.session_state.scores,
                            all_weak_skills=st.session_state.all_weak_skills,
                        )
                        st.session_state.final_report = report
                        save_interview_history(
                            role=st.session_state.role,
                            round_type=st.session_state.round_type,
                            questions=st.session_state.questions,
                            answers=st.session_state.answers,
                            scores=st.session_state.scores,
                            report=report,
                        )
                    st.session_state.interview_complete = True
                    st.session_state.page = "report"
                    st.rerun()

        if q_idx in st.session_state.improved_answers:
            st.markdown(f"""
            <div class="coach-card-accent" style="margin-top:1rem;">
                <div style="font-size:0.8rem; color:#a5b4fc; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.7rem;">✨ AI-Crafted Perfect Answer</div>
                <div style="font-size:0.95rem; color:#e2e8f0; line-height:1.7;">{st.session_state.improved_answers[q_idx]}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.pending_improve and q_idx not in st.session_state.improved_answers:
        answer_for_improve = st.session_state.last_answer_text
        question_for_improve = st.session_state.questions[q_idx] if q_idx < len(st.session_state.questions) else current_question
        if answer_for_improve and answer_for_improve not in ("[Skipped]", "[Time expired]", ""):
            with st.spinner("✨ Crafting your perfect answer... please wait"):
                improved = improve_answer(
                    role=st.session_state.role,
                    question=question_for_improve,
                    answer=answer_for_improve,
                )
            st.session_state.improved_answers[q_idx] = improved
            st.session_state.pending_improve = False
            st.rerun()
        else:
            st.session_state.pending_improve = False
            st.warning("⚠️ No answer found to improve. Please submit your answer first.")

    if time_limit > 0 and st.session_state.last_answered_idx < q_idx and not st.session_state.pending_improve:
        elapsed = int(time.time() - (st.session_state.timer_start or time.time()))
        if elapsed < time_limit:
            time.sleep(1)
            st.rerun()


# ─────────────────────────────────────────────
# PAGE: REPORT
# ─────────────────────────────────────────────

def page_report():
    if not st.session_state.scores:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem;">
            <div style="font-size:3rem;">📊</div>
            <div style="font-size:1.3rem; font-weight:700; margin:1rem 0 0.5rem;">No Report Available</div>
            <div style="color:#64748b;">Complete an interview session to see your report.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Go to Home", type="primary"):
            st.session_state.page = "home"
            st.rerun()
        return

    report = st.session_state.final_report or {}
    scores = st.session_state.scores
    avg_score = sum(scores) / len(scores)
    readiness = report.get("interview_readiness", "Needs Work")

    readiness_colors = {
        "Not Ready": "#ef4444",
        "Needs Work": "#f59e0b",
        "Almost Ready": "#06b6d4",
        "Ready": "#22c55e",
    }
    readiness_color = readiness_colors.get(readiness, "#6366f1")

    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <div class="section-header" style="font-size:2rem;">📊 Performance Report</div>
        <div class="section-sub">{st.session_state.role} · {st.session_state.round_type} Round · {len(scores)} Questions</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    kpis = [
        (f"{avg_score:.1f}/10", "Average Score", score_to_color(int(avg_score))),
        (f"{len(scores)}", "Questions Answered", "#6366f1"),
        (readiness, "Interview Readiness", readiness_color),
        (f"{len(set(st.session_state.all_weak_skills))}", "Weak Areas", "#f59e0b"),
    ]
    for col, (val, label, color) in zip([col1, col2, col3, col4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-color:{color}33;">
                <div class="metric-value" style="color:{color}; font-size:1.8rem;">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Score Analysis", "📝 Q&A Review", "🎯 Insights", "🔧 Improvement Plan"])

    with tab1:
        col_c1, col_c2 = st.columns(2, gap="large")

        with col_c1:
            q_labels = [f"Q{i+1}" for i in range(len(scores))]
            colors_list = [score_to_color(s) for s in scores]

            fig_bar = go.Figure(data=[
                go.Bar(
                    x=q_labels,
                    y=scores,
                    marker_color=colors_list,
                    text=[f"{s}/10" for s in scores],
                    textposition="outside",
                    textfont=dict(color="white", size=12),
                )
            ])
            fig_bar.update_layout(
                title=dict(text="Score Per Question", font=dict(color="#f1f5f9", size=16)),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(17,24,39,0.8)",
                font=dict(color="#94a3b8"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
                yaxis=dict(range=[0, 11], gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
                margin=dict(t=50, b=20, l=20, r=20),
                height=300,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_c2:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_score,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Overall Score", "font": {"color": "#f1f5f9", "size": 16}},
                number={"suffix": "/10", "font": {"color": "#f1f5f9", "size": 36}},
                gauge={
                    "axis": {"range": [0, 10], "tickcolor": "#64748b"},
                    "bar": {"color": score_to_color(int(avg_score))},
                    "bgcolor": "rgba(17,24,39,0.5)",
                    "bordercolor": "#1e293b",
                    "steps": [
                        {"range": [0, 4], "color": "rgba(239,68,68,0.2)"},
                        {"range": [4, 7], "color": "rgba(245,158,11,0.2)"},
                        {"range": [7, 10], "color": "rgba(34,197,94,0.2)"},
                    ],
                    "threshold": {"line": {"color": "white", "width": 3}, "thickness": 0.8, "value": avg_score},
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                margin=dict(t=30, b=10, l=20, r=20),
                height=300,
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        if len(scores) > 2:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=q_labels, y=scores,
                mode="lines+markers",
                line=dict(color="#6366f1", width=3),
                marker=dict(size=10, color=colors_list, line=dict(color="white", width=2)),
                fill="tozeroy",
                fillcolor="rgba(99,102,241,0.1)",
            ))
            fig_line.add_hline(y=avg_score, line_dash="dash", line_color="#f59e0b",
                               annotation_text=f"Avg: {avg_score:.1f}", annotation_font_color="#f59e0b")
            fig_line.update_layout(
                title=dict(text="Score Progression", font=dict(color="#f1f5f9", size=16)),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(17,24,39,0.8)",
                font=dict(color="#94a3b8"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(range=[0, 11], gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=50, b=20, l=20, r=20),
                height=280,
            )
            st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        for i, (q, a, score) in enumerate(zip(
            st.session_state.questions,
            st.session_state.answers,
            st.session_state.scores
        )):
            color = score_to_color(score)
            label = score_to_label(score)
            with st.expander(f"Q{i+1}: {q[:80]}... — {score}/10 {label}"):
                st.markdown(f"""
                <div style="background:#0f172a; border-radius:10px; padding:1rem; margin-bottom:0.8rem; border-left:3px solid #6366f1;">
                    <div style="font-size:0.75rem; color:#6366f1; font-weight:700; text-transform:uppercase; margin-bottom:0.4rem;">Question</div>
                    <div style="color:#e2e8f0; line-height:1.6;">{q}</div>
                </div>
                <div style="background:#0f172a; border-radius:10px; padding:1rem; margin-bottom:0.8rem; border-left:3px solid #22c55e;">
                    <div style="font-size:0.75rem; color:#22c55e; font-weight:700; text-transform:uppercase; margin-bottom:0.4rem;">Your Answer</div>
                    <div style="color:#94a3b8; line-height:1.6;">{a}</div>
                </div>
                <div style="background:{color}11; border-radius:10px; padding:0.8rem; border:1px solid {color}33;">
                    <div style="font-size:1.2rem; font-weight:800; color:{color};">Score: {score}/10 · {label}</div>
                </div>
                """, unsafe_allow_html=True)

                if i < len(st.session_state.evaluations) and st.session_state.evaluations[i]:
                    ev = st.session_state.evaluations[i]
                    col_s, col_w = st.columns(2)
                    with col_s:
                        st.markdown("**✅ Strengths**")
                        for s in ev.get("strengths", []):
                            st.markdown(f"- {s}")
                    with col_w:
                        st.markdown("**⚠️ Weaknesses**")
                        for w in ev.get("weaknesses", []):
                            st.markdown(f"- {w}")

                if i in st.session_state.improved_answers:
                    st.markdown(f"""
                    <div class="coach-card-accent" style="margin-top:0.7rem;">
                        <div style="font-size:0.75rem; color:#a5b4fc; font-weight:700; text-transform:uppercase; margin-bottom:0.5rem;">✨ AI Perfect Answer</div>
                        <div style="font-size:0.9rem; color:#e2e8f0; line-height:1.7;">{st.session_state.improved_answers[i]}</div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab3:
        col_i1, col_i2 = st.columns(2, gap="large")

        with col_i1:
            st.markdown('<div style="font-weight:700; font-size:1.05rem; margin-bottom:1rem;">💪 Top Strengths</div>', unsafe_allow_html=True)
            for s in report.get("top_strengths", []):
                st.markdown(f'<div style="background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.25); border-radius:10px; padding:0.7rem 1rem; margin-bottom:0.5rem; color:#86efac; font-size:0.9rem;">✅ {s}</div>', unsafe_allow_html=True)

            st.markdown('<div style="font-weight:700; font-size:1.05rem; margin:1.2rem 0 0.8rem;">🎯 Next Steps</div>', unsafe_allow_html=True)
            for i, step in enumerate(report.get("next_steps", []), 1):
                st.markdown(f'<div style="background:#1a2235; border-radius:10px; padding:0.7rem 1rem; margin-bottom:0.5rem; font-size:0.9rem; color:#94a3b8;"><span style="color:#6366f1; font-weight:700;">{i}.</span> {step}</div>', unsafe_allow_html=True)

        with col_i2:
            st.markdown('<div style="font-weight:700; font-size:1.05rem; margin-bottom:1rem;">⚠️ Key Weaknesses</div>', unsafe_allow_html=True)
            for w in report.get("key_weaknesses", []):
                st.markdown(f'<div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.25); border-radius:10px; padding:0.7rem 1rem; margin-bottom:0.5rem; color:#fca5a5; font-size:0.9rem;">❌ {w}</div>', unsafe_allow_html=True)

            weak_skills = list(set(st.session_state.all_weak_skills))
            if weak_skills:
                st.markdown('<div style="font-weight:700; font-size:1.05rem; margin:1.2rem 0 0.8rem;">🔴 Detected Weak Skills</div>', unsafe_allow_html=True)
                chips = "".join([f'<span class="skill-chip weak-chip">⚠️ {skill}</span>' for skill in weak_skills[:8]])
                st.markdown(f'<div>{chips}</div>', unsafe_allow_html=True)

        if report.get("overall_assessment"):
            st.markdown(f"""
            <div class="coach-card-accent" style="margin-top:1.5rem;">
                <div style="font-weight:700; color:#a5b4fc; margin-bottom:0.5rem;">🤖 AI Coach Assessment</div>
                <div style="font-size:0.95rem; color:#e2e8f0; line-height:1.7;">{report.get("overall_assessment", "")}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        topics = report.get("topics_to_improve", [])
        if topics:
            for i, topic in enumerate(topics):
                st.markdown(f"""
                <div class="coach-card" style="margin-bottom:1rem;">
                    <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.8rem;">
                        <div style="width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg,#6366f1,#8b5cf6); display:flex; align-items:center; justify-content:center; font-weight:800; flex-shrink:0;">{i+1}</div>
                        <div style="font-size:1.05rem; font-weight:700;">{topic.get("topic", "Topic")}</div>
                    </div>
                    <div style="background:#0f172a; border-radius:10px; padding:0.8rem; margin-bottom:0.6rem;">
                        <div style="font-size:0.75rem; color:#6366f1; font-weight:700; text-transform:uppercase; margin-bottom:0.3rem;">Why Study This</div>
                        <div style="font-size:0.9rem; color:#94a3b8;">{topic.get("reason", "")}</div>
                    </div>
                    <div style="background:#0f172a; border-radius:10px; padding:0.8rem;">
                        <div style="font-size:0.75rem; color:#06b6d4; font-weight:700; text-transform:uppercase; margin-bottom:0.3rem;">📚 Resources</div>
                        <div style="font-size:0.9rem; color:#94a3b8;">{topic.get("resources", "")}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific improvement topics identified. Great performance!")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Start New Interview", use_container_width=True, type="primary"):
            for key in ["interview_started", "interview_complete", "questions", "answers",
                        "scores", "evaluations", "all_weak_skills", "final_report",
                        "improved_answers", "current_q_idx"]:
                if key in st.session_state:
                    del st.session_state[key]
            init_session()
            st.session_state.page = "home"
            st.rerun()


# ─────────────────────────────────────────────
# PAGE: HISTORY
# ─────────────────────────────────────────────

def page_history():
    st.markdown('<div class="section-header">📁 Interview History</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">All your past interview sessions</div>', unsafe_allow_html=True)

    history = load_all_history()

    if not history:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; background:#111827; border-radius:16px; border:1px dashed #1e293b;">
            <div style="font-size:3rem;">📂</div>
            <div style="font-size:1.1rem; font-weight:700; margin:1rem 0 0.5rem;">No History Yet</div>
            <div style="color:#64748b;">Complete your first interview to see it here.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    all_scores = [h.get("average_score", 0) for h in history]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:#6366f1;">{len(history)}</div><div class="metric-label">Total Sessions</div></div>""", unsafe_allow_html=True)
    with col2:
        avg = sum(all_scores)/len(all_scores) if all_scores else 0
        st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:{score_to_color(int(avg))};">{avg:.1f}</div><div class="metric-label">Overall Avg Score</div></div>""", unsafe_allow_html=True)
    with col3:
        best = max(all_scores) if all_scores else 0
        st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:#22c55e;">{best:.1f}</div><div class="metric-label">Best Session Score</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    df = get_history_dataframe()
    if not df.empty:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Avg Score": st.column_config.ProgressColumn("Avg Score", min_value=0, max_value=10),
            }
        )

    if len(history) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        dates = [h.get("date", f"Session {h.get('id',i)}") for i, h in enumerate(history)]
        scores = [h.get("average_score", 0) for h in history]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=scores,
            mode="lines+markers+text",
            line=dict(color="#6366f1", width=3),
            marker=dict(size=10, color=[score_to_color(int(s)) for s in scores], line=dict(color="white", width=2)),
            text=[f"{s}/10" for s in scores],
            textposition="top center",
            textfont=dict(color="white"),
        ))
        fig.update_layout(
            title=dict(text="Score Trend Across Sessions", font=dict(color="#f1f5f9", size=16)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,24,39,0.8)",
            font=dict(color="#94a3b8"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(range=[0, 11], gridcolor="rgba(255,255,255,0.05)"),
            margin=dict(t=50, b=40, l=20, r=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# MAIN APP ROUTER
# ─────────────────────────────────────────────

def main():
    render_sidebar()

    page = st.session_state.page

    if page == "home":
        page_home()
    elif page == "interview":
        page_interview()
    elif page == "report":
        page_report()
    elif page == "history":
        page_history()
    else:
        page_home()


if __name__ == "__main__":
    main()