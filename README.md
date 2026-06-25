# 🏋️ AI Fitness Tracker

A multilingual, AI-powered fitness tracking application built with Streamlit. Track meals, workouts, progress, and get personalized AI coaching — all in your native language.

## ✨ Features

| Feature | Description |
|---|---|
| 🌍 **Global Multilingual UI** | One-tap language switching (English, हिन्दी, తెలుగు, தமிழ்) |
| 🍽️ **Meal Tracker** | Log breakfast, lunch, dinner & snacks with calorie tracking |
| 💪 **Workout Streak** | Daily workout logging with streak motivation banners |
| 📈 **Progress Charts** | Weight, BMI & calorie trend charts using Plotly |
| 🤖 **AI Diet Planner** | Personalized meal plans via GPT-4, Gemini, or local Ollama |
| 🏃 **AI Workout Planner** | Custom exercise routines tailored to your goals |
| 🧠 **RAG Fitness Assistant** | Upload PDFs and ask questions using LangChain + FAISS |
| 👁️ **Llava Vision Models** | Analyze food photos using local Llava (via Ollama) |
| 🔐 **Auth** | Secure login/signup with SQLite-backed user accounts |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://code.swecha.org/<your-username>/fitness-tracker.git
cd fitness-tracker

# 2. Create a virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# 3. Install development tools
uv pip install ruff mypy vulture bandit pytest pre-commit

# 4. Install git pre-commit hooks
pre-commit install

# 5. Run the app
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔧 AI Configuration

Go to **AI Settings** in the sidebar to configure your preferred AI provider:

| Provider | Models | Setup Required |
|---|---|---|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | `OPENAI_API_KEY` env var |
| **Gemini** | Gemini Pro, Flash | `GEMINI_API_KEY` env var |
| **Ollama (Local)** | Llama3, Llava, Mistral, … | [Install Ollama](https://ollama.ai) |
| **BYOK** | Any OpenAI-compatible endpoint | Custom base URL + key |

---

## 🧪 Development

### Run Tests
```bash
pytest tests/ -v
```

### Lint & Format
```bash
ruff check .          # lint
ruff format .         # format
```

### Type Check
```bash
mypy . --ignore-missing-imports
```

### Dead Code
```bash
vulture . --min-confidence=80 --exclude .venv,tests
```

### Security Check
```bash
bandit -r . -x .venv,tests --skip B101,B311
```

### Package Audit
```bash
pip-audit -r requirements.txt
```

### Run All Pre-commit Checks
```bash
pre-commit run --all-files
```

---

## 🏗️ Project Structure

```
fitness-tracker/
├── app.py                    # Main entry point (login / signup)
├── pages/
│   ├── dashboard.py          # Home dashboard with daily stats
│   ├── meals.py              # Meal logging
│   ├── workout-streak.py     # Workout streak tracker
│   ├── progress.py           # Weight & BMI progress
│   ├── profile.py            # User profile & goals
│   ├── ai_diet plan.py       # AI-powered diet planner
│   ├── ai_workout planner.py # AI-powered workout planner
│   ├── rag_fitness_assistant.py  # PDF RAG chatbot
│   ├── ai-coach.py           # Unified AI chat coach
│   └── i18n/                 # Translation JSON files
│       ├── en.json
│       ├── hi.json
│       ├── te.json
│       └── ta.json
├── utils/
│   └── navigation.py         # Shared sidebar layout & language switching
├── ai_helper.py              # Unified LLM provider interface
├── database.py               # SQLite database helpers
├── tests/
│   ├── test_ai_helper.py
│   └── test_i18n.py
├── .pre-commit-config.yaml   # Git pre-commit hooks
├── .gitlab-ci.yml            # GitLab CI/CD pipeline
├── pyproject.toml            # Tool configuration (ruff, mypy, pytest)
└── requirements.txt          # Runtime dependencies
```

---

## 🔄 CI/CD Pipeline

The GitLab CI pipeline runs automatically on every push and merge request:

| Stage | Tool | Blocks merge? |
|---|---|---|
| **lint** | ruff | ✅ Yes |
| **format-check** | ruff format | ✅ Yes |
| **type-check** | mypy | ⚠️ Advisory |
| **dead-code** | vulture | ⚠️ Advisory |
| **security** | bandit | ⚠️ Advisory |
| **audit** | uv pip audit | ⚠️ Advisory |
| **test** | pytest | ✅ Yes |
| **deploy** | manual trigger | 🚀 Manual (main only) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
