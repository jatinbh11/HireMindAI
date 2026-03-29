# utils.py
# All backend logic functions — API calls, parsing, history saving, PDF reading.
# Using Groq (free) with LLaMA 3.3 70B model

import os
import json
import re
import time
import datetime
import pandas as pd
from groq import Groq
from prompts import (
    get_question_generation_prompt,
    get_evaluation_prompt,
    get_improvement_prompt,
    get_final_report_prompt,
    get_resume_analysis_prompt,
)

# ─────────────────────────────────────────────
# GROQ CLIENT SETUP (Free — LLaMA 3.3 70B)
# ─────────────────────────────────────────────

def get_client():
    """Initialize and return Groq client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please check your .env file.")
    return Groq(api_key=api_key)


def call_llm(prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
    """
    Central function to call the Groq API.
    Uses LLaMA 3.3 70B — completely free, very fast, GPT-4 level accuracy.
    Returns the text content of the response.
    """
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # Best free model on Groq
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def safe_parse_json(text: str) -> dict | list | None:
    """
    Safely parse JSON from LLM response.
    Handles cases where the model wraps JSON in markdown code blocks.
    """
    # Remove markdown code fences if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from the text using regex
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except Exception:
                return None
    return None


# ─────────────────────────────────────────────
# QUESTION GENERATION
# ─────────────────────────────────────────────

def generate_questions(role: str, round_type: str, num_questions: int = 5, resume_text: str = "") -> list[str]:
    """
    Generate interview questions for the selected role and round type.
    Returns a list of question strings.
    """
    prompt = get_question_generation_prompt(role, round_type, num_questions, resume_text)
    response = call_llm(prompt, max_tokens=1000, temperature=0.8)
    questions = safe_parse_json(response)

    if isinstance(questions, list) and len(questions) > 0:
        return questions[:num_questions]

    # Fallback: try to split by newlines if JSON parsing fails
    lines = [line.strip().lstrip("0123456789.-) ") for line in response.split("\n") if line.strip() and "?" in line]
    return lines[:num_questions] if lines else ["Tell me about yourself?", "What are your strengths?"]


# ─────────────────────────────────────────────
# ANSWER EVALUATION
# ─────────────────────────────────────────────

def evaluate_answer(role: str, question: str, answer: str) -> dict:
    """
    Evaluate a candidate's answer and return structured feedback.
    Returns a dict with score, strengths, weaknesses, etc.
    """
    if not answer or len(answer.strip()) < 5:
        return {
            "score": 1,
            "strengths": ["Attempted to answer"],
            "weaknesses": ["Answer was too short or empty"],
            "clarity": "No clarity — answer was not provided.",
            "technical_accuracy": "Cannot assess — no answer given.",
            "weak_skills": ["Communication"],
            "brief_feedback": "Please provide a detailed answer to get proper feedback."
        }

    prompt = get_evaluation_prompt(role, question, answer)
    response = call_llm(prompt, max_tokens=800, temperature=0.3)
    result = safe_parse_json(response)

    if isinstance(result, dict) and "score" in result:
        # Ensure score is an integer in range 1-10
        result["score"] = max(1, min(10, int(result.get("score", 5))))
        return result

    # Fallback evaluation
    return {
        "score": 5,
        "strengths": ["Answer was provided"],
        "weaknesses": ["Could not fully analyze the answer"],
        "clarity": "Unable to assess clarity.",
        "technical_accuracy": "Unable to assess technical accuracy.",
        "weak_skills": [],
        "brief_feedback": "Your answer was received but couldn't be fully evaluated. Please try again."
    }


# ─────────────────────────────────────────────
# ANSWER IMPROVEMENT
# ─────────────────────────────────────────────

def improve_answer(role: str, question: str, answer: str) -> str:
    """
    Rewrite the user's answer into a professional, polished version.
    Returns the improved answer as a string.
    """
    prompt = get_improvement_prompt(role, question, answer)
    response = call_llm(prompt, max_tokens=600, temperature=0.5)
    return response.strip()


# ─────────────────────────────────────────────
# FINAL REPORT GENERATION
# ─────────────────────────────────────────────

def generate_final_report(role: str, questions: list, answers: list, scores: list, all_weak_skills: list) -> dict:
    """
    Generate a comprehensive final performance report after all questions.
    Returns structured report data.
    """
    prompt = get_final_report_prompt(role, [questions, answers], scores, all_weak_skills)
    response = call_llm(prompt, max_tokens=1200, temperature=0.4)
    result = safe_parse_json(response)

    if isinstance(result, dict) and "overall_assessment" in result:
        return result

    # Fallback report
    avg = sum(scores) / len(scores) if scores else 0
    return {
        "overall_assessment": f"You completed the {role} interview with an average score of {avg:.1f}/10.",
        "top_strengths": ["Completed the interview", "Attempted all questions"],
        "key_weaknesses": ["Report generation encountered an issue"],
        "topics_to_improve": [{"topic": "Core Concepts", "reason": "Practice fundamentals", "resources": "Official documentation"}],
        "interview_readiness": "Needs Work" if avg < 6 else "Almost Ready",
        "next_steps": ["Review your weak areas", "Practice more questions", "Take mock interviews"]
    }


# ─────────────────────────────────────────────
# PDF RESUME PARSING
# ─────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from an uploaded PDF resume.
    Returns plain text string.
    """
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def analyze_resume(resume_text: str) -> dict:
    """
    Use AI to extract structured info from resume text.
    """
    if not resume_text or len(resume_text) < 50:
        return {}
    prompt = get_resume_analysis_prompt(resume_text)
    response = call_llm(prompt, max_tokens=500, temperature=0.3)
    result = safe_parse_json(response)
    return result if isinstance(result, dict) else {}


# ─────────────────────────────────────────────
# INTERVIEW HISTORY (SAVE / LOAD)
# ─────────────────────────────────────────────

HISTORY_FILE = "interview_history.json"


def save_interview_history(role: str, round_type: str, questions: list, answers: list, scores: list, report: dict):
    """Save completed interview to a local JSON history file."""
    history = load_all_history()

    entry = {
        "id": len(history) + 1,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "role": role,
        "round_type": round_type,
        "num_questions": len(questions),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "scores": scores,
        "questions": questions,
        "answers": answers,
        "report": report,
    }

    history.append(entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    return entry["id"]


def load_all_history() -> list:
    """Load all past interview sessions from history file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def get_history_dataframe() -> pd.DataFrame:
    """Return interview history as a pandas DataFrame for display."""
    history = load_all_history()
    if not history:
        return pd.DataFrame()

    rows = []
    for h in history:
        rows.append({
            "ID": h.get("id", ""),
            "Date": h.get("date", ""),
            "Role": h.get("role", ""),
            "Round": h.get("round_type", ""),
            "Questions": h.get("num_questions", 0),
            "Avg Score": h.get("average_score", 0),
            "Readiness": h.get("report", {}).get("interview_readiness", "N/A"),
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# SCORE COLOR HELPER
# ─────────────────────────────────────────────

def score_to_color(score: int) -> str:
    """Return a hex color based on score range."""
    if score >= 8:
        return "#22c55e"   # green
    elif score >= 6:
        return "#f59e0b"   # amber
    elif score >= 4:
        return "#f97316"   # orange
    else:
        return "#ef4444"   # red


def score_to_label(score: int) -> str:
    """Return a text label based on score."""
    if score >= 9:
        return "Excellent ⭐"
    elif score >= 7:
        return "Good 👍"
    elif score >= 5:
        return "Average 📊"
    elif score >= 3:
        return "Weak ⚠️"
    else:
        return "Poor ❌"


# ─────────────────────────────────────────────
# TIMER HELPER
# ─────────────────────────────────────────────

def format_time(seconds: int) -> str:
    """Format seconds into MM:SS string."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"
