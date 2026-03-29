# prompts.py
# All AI prompts are stored here for easy management and editing.

# ─────────────────────────────────────────────
# QUESTION GENERATION PROMPTS
# ─────────────────────────────────────────────

def get_question_generation_prompt(role: str, round_type: str, num_questions: int, resume_text: str = "") -> str:
    resume_context = ""
    if resume_text:
        resume_context = f"""
The candidate has uploaded their resume. Here is the content:
---RESUME START---
{resume_text[:2000]}
---RESUME END---
Generate questions that are relevant to their experience and skills mentioned in the resume.
"""

    return f"""You are an expert technical interviewer at a top tech company.

Your task: Generate exactly {num_questions} {round_type} interview questions for a **{role}** position.

{resume_context}

Rules:
- Questions must be specific, relevant, and progressively challenging
- Mix conceptual, practical, and scenario-based questions
- For Technical round: focus on core technical skills, coding concepts, algorithms
- For HR round: focus on behavioral, situational, culture-fit questions
- Do NOT number the questions
- Return ONLY a JSON array of strings, nothing else

Example format:
["Question 1 here?", "Question 2 here?", "Question 3 here?"]

Generate {num_questions} questions now for {role} - {round_type} round:"""


# ─────────────────────────────────────────────
# ANSWER EVALUATION PROMPTS
# ─────────────────────────────────────────────

def get_evaluation_prompt(role: str, question: str, answer: str) -> str:
    return f"""You are a senior interviewer evaluating a candidate for a {role} position.

Question asked: "{question}"

Candidate's answer: "{answer}"

Evaluate this answer strictly and return a JSON object with EXACTLY this structure:
{{
  "score": <integer from 1 to 10>,
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "clarity": "<one sentence about how clearly the answer was communicated>",
  "technical_accuracy": "<one sentence about technical correctness>",
  "weak_skills": ["skill1", "skill2"],
  "brief_feedback": "<2-3 sentence overall feedback>"
}}

Scoring guide:
- 9-10: Exceptional, complete, professional answer
- 7-8: Good answer with minor gaps
- 5-6: Average, missing key points
- 3-4: Weak, significant gaps
- 1-2: Very poor or irrelevant answer

Be honest and strict. Return ONLY the JSON object, no extra text."""


# ─────────────────────────────────────────────
# ANSWER IMPROVEMENT PROMPTS
# ─────────────────────────────────────────────

def get_improvement_prompt(role: str, question: str, answer: str) -> str:
    return f"""You are an expert coach helping a candidate improve their interview answer for a {role} position.

Original Question: "{question}"
Candidate's Original Answer: "{answer}"

Rewrite this into a PERFECT, professional interview answer that:
1. Is structured using the STAR method (Situation, Task, Action, Result) where applicable
2. Uses precise technical terminology appropriate for {role}
3. Is confident, clear, and concise (150-250 words)
4. Highlights key skills and achievements
5. Sounds natural and human, not robotic

Return ONLY the improved answer text, nothing else. Do not include labels like "Improved Answer:" — just the answer itself."""


# ─────────────────────────────────────────────
# FINAL REPORT PROMPTS
# ─────────────────────────────────────────────

def get_final_report_prompt(role: str, qa_pairs: list, scores: list, all_weak_skills: list) -> str:
    qa_summary = ""
    for i, (q, a, s) in enumerate(zip(qa_pairs[0], qa_pairs[1], scores)):
        qa_summary += f"\nQ{i+1} (Score: {s}/10): {q[:100]}...\nAnswer summary: {a[:150]}...\n"

    return f"""You are a career coach generating a comprehensive interview performance report for a {role} candidate.

Interview Summary:
{qa_summary}

Average Score: {sum(scores)/len(scores):.1f}/10
Identified Weak Skills: {', '.join(set(all_weak_skills)) if all_weak_skills else 'None identified'}

Generate a detailed performance report as a JSON object with EXACTLY this structure:
{{
  "overall_assessment": "<2-3 sentence overall performance summary>",
  "top_strengths": ["strength 1", "strength 2", "strength 3"],
  "key_weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "topics_to_improve": [
    {{"topic": "Topic Name", "reason": "Why to study this", "resources": "Books/courses to use"}},
    {{"topic": "Topic Name", "reason": "Why to study this", "resources": "Books/courses to use"}},
    {{"topic": "Topic Name", "reason": "Why to study this", "resources": "Books/courses to use"}}
  ],
  "interview_readiness": "<Not Ready / Needs Work / Almost Ready / Ready>",
  "next_steps": ["step 1", "step 2", "step 3"]
}}

Return ONLY the JSON object."""


# ─────────────────────────────────────────────
# RESUME PARSING PROMPT
# ─────────────────────────────────────────────

def get_resume_analysis_prompt(resume_text: str) -> str:
    return f"""Extract key information from this resume and return a JSON object:

Resume text:
{resume_text[:3000]}

Return ONLY a JSON object:
{{
  "name": "<candidate name or 'Not found'>",
  "skills": ["skill1", "skill2", "skill3"],
  "experience_years": "<estimated years of experience>",
  "top_technologies": ["tech1", "tech2", "tech3"],
  "education": "<highest education level>"
}}"""
