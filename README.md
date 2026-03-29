# 🎯 HireMindAI - Ai Interview Coach  
> A production-grade AI-powered interview coaching platform built with Streamlit and OpenAI GPT.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)


## ✨ Features

| Feature | Description |
|---|---|
| 🎭 Role-Based Questions | AI generates tailored questions for 10+ tech roles |
| 🤖 Smart Evaluation | Score (1–10) + strengths, weaknesses, clarity, technical accuracy |
| ✨ Answer Improvement | AI rewrites your answer into a professional, STAR-method response |
| 📊 Performance Dashboard | Charts, KPI cards, score progression, readiness meter |
| 🔴 Weak Area Detection | Identifies specific skill gaps (ML, SQL, DSA, etc.) |
| ⏱️ Timer-Based Mode | Countdown timer per question for realistic pressure |
| 📎 Resume Upload | Upload PDF resume for personalized questions |
| 💾 Interview History | All sessions saved locally with trend charts |
| 🔄 HR + Technical Rounds | Choose round type or mix both |

---


## 📁 Project Structure

```
ai-interview-coach/
├── app.py               # Main Streamlit app (pages, UI, routing)
├── utils.py             # Backend logic (API calls, PDF parsing, history)
├── prompts.py           # All AI prompts (easy to customize)
├── requirements.txt     # Python dependencies
├── .env                 # API key configuration (you fill this)
├── .gitignore           # Files to exclude from git
└── README.md            # This file
```

---

## ⚙️ Setup & Installation

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-interview-coach.git
cd ai-interview-coach
```

### Step 2 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure your API key
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up free (no credit card needed)
3. Click **API Keys → Create API Key**
4. Open the `.env` file and replace the placeholder:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 5 — Run the app
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 🌐 Deployment on Streamlit Cloud (Free)

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New App" → connect your GitHub repo
4. In **Advanced Settings → Secrets**, add:
```toml
GROQ_API_KEY = "gsk_your-key-here"
```
5. Click **Deploy** — your app will be live in ~2 minutes!

---

## 🔧 Customization

### Add new roles
In `app.py`, find the `st.selectbox` for "Target Role" and add to the list:
```python
options=["Your New Role", "Data Scientist", ...]
```

### Change AI model
In `utils.py`, find the `call_llm` function. You can swap models freely:
```python
model="llama-3.3-70b-versatile"   # Default — best quality (free)
model="llama3-8b-8192"            # Faster, lighter
model="mixtral-8x7b-32768"        # Great for long answers
```

### Modify prompts
All prompts are in `prompts.py` — edit them to change how questions are generated and answers evaluated.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit with custom CSS (dark theme, animations)
- **AI**: Groq LLaMA 3.3 70B (free, fast, GPT-4 level accuracy)
- **Charts**: Plotly (bar, gauge, line charts)
- **PDF Parsing**: PyPDF2
- **Data**: Pandas for history management
- **Config**: python-dotenv for environment variables

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests welcome. Please open an issue first to discuss changes.

---

## 📬 Contact

Built with Jatin Bhargav❤️ using Streamlit + OpenAI. Star ⭐ this repo if you found it helpful!
