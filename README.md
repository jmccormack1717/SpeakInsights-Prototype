# SpeakInsights – Natural-Language Data Analysis for Any CSV

SpeakInsights is a full-stack web application that enables natural language data analysis. Simply upload a CSV file, ask questions in plain English, and receive tailored charts and narrative insights. The application includes a built-in PIMA diabetes dataset for instant testing and supports importing your own CSV files.

## ✨ Features

- **Natural Language Queries**: Ask questions in plain English—no SQL or coding required
- **Intelligent Analysis**: LLM-powered playbook system that selects appropriate analysis types (overview, correlation, distributions, relationships, segment comparisons)
- **Dynamic Visualizations**: Automatically generated charts including histograms, bar charts, scatter plots, correlation matrices, and more
- **CSV Upload Support**: Import and analyze your own datasets with automatic schema detection
- **Narrative Insights**: AI-generated explanations that translate data findings into business-friendly language
- **User Authentication**: Secure user accounts with JWT-based authentication
- **Live Demo**: Fully deployed and accessible online

## 🏗️ Architecture (High Level)

- **Backend**: FastAPI (Python, async) + SQLAlchemy + Pandas/Numpy
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + Recharts
- **Database**: SQLite per dataset (optimized for small to medium-sized datasets)
- **LLM**: OpenAI model (default: `gpt-4-turbo-preview`, configurable via environment)
- **Charts**: Recharts implementing a small visualization grammar (bar, histogram, scatter, line, correlation matrix, etc.)

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

## ⚡ Quick Start

See [SETUP.md](./SETUP.md) for detailed setup instructions. High level:

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Add your OPENAI_API_KEY to .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to use the application.

- By default the backend will import a cleaned PIMA diabetes CSV into a SQLite DB for the demo dataset.
- In the UI you can either use this built-in dataset or upload your own CSV (recommended size: up to ~50MB / ~100k rows on free hosting).

## 📁 Project Structure

```
speakinsights-prototype/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes (FastAPI endpoints)
│   │   ├── core/         # Core services (LLM, DB, Security)
│   │   ├── services/     # Business logic (playbooks, analysis)
│   │   └── utils/        # Utilities (CSV import, schema parsing)
│   ├── data/             # User databases (SQLite per dataset)
│   ├── tests/            # Backend test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API client
│   │   ├── stores/       # State management (Zustand)
│   │   └── types/        # TypeScript type definitions
│   └── package.json
├── .github/
│   └── workflows/        # CI/CD pipelines
└── README.md
```

## ☁️ Deployment

- **Live demo**: [`https://speakinsights-prototype.onrender.com/`](https://speakinsights-prototype.onrender.com/)
- **Backend**: Render web service (FastAPI + Uvicorn)
- **Frontend**: Static build served via Render
- **Key environment variables**:
  - `OPENAI_API_KEY` – OpenAI API key for LLM calls
  - `VITE_API_URL` – Frontend → backend base URL (e.g. Render backend URL)
- **Note on persistence**: User accounts and datasets are stored in SQLite files on the container filesystem. On free Render tiers, storage is ephemeral and data may reset on redeploys or restarts.

## 🔄 How It Works (Playbooks, Not Raw SQL)

1. **User Query**: User types a natural language question.
2. **Schema Context**: Backend retrieves the dataset schema and basic stats.
3. **Playbook Selection**: LLM chooses an analysis *playbook* (overview, distribution, correlation, relationship, outcome breakdown, segment comparison, etc.) and fills in high-level slots (target, features, segments). It does **not** generate SQL.
4. **Data Fetch**: Backend runs fixed, safe SQL (e.g., `SELECT * FROM main_table LIMIT N`) to fetch the relevant slice of data.
5. **Playbook Execution**: Deterministic Python code computes aggregates, correlations, distributions, etc. and prepares a visualization specification.
6. **Visualization**: Frontend renders the specified chart (bar, histogram, scatter, correlation matrix, table, etc.).
7. **Insights**: LLM generates a narrative over the structured results, in non‑technical language.

## 📊 Example Queries

- "Describe the dataset to me like I’m new to it."
- "Which features are most related to the outcome?"
- "How does glucose relate to the diabetes outcome?"
- "Show the distribution of BMI."
- "Compare patients with diabetes vs without across key metrics."
- "What percentage of patients have the disease?"

## 🛠️ Development Notes

### Backend API

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Testing

#### Backend Tests

```bash
cd backend
# Install test dependencies (already in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_playbooks.py -v
```

#### Frontend Tests

```bash
cd frontend
# Install dependencies (if not already done)
npm install

# Run tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

#### CI/CD

The project includes GitHub Actions workflows that run on every push and pull request:
- Backend tests with pytest and coverage
- Frontend tests with Vitest
- Linting for both backend (flake8, black) and frontend (ESLint)
- Build verification

See `.github/workflows/ci.yml` for details.

### Sample / Demo Data

- A cleaned PIMA diabetes CSV is auto-imported on first backend startup for the default user/dataset (`default_user` / `mvp_dataset`).
- You can also upload your own CSVs via the UI; the backend creates a new SQLite DB per dataset and imports the file using Pandas + SQLAlchemy.

### Project Scope

This project is designed as a portfolio piece demonstrating full-stack development, AI integration, and data analysis capabilities. It focuses on clarity of architecture and code quality rather than large-scale production optimization.

## 📝 License

MIT License

