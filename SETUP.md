# Intelligent Task Assignment System — Run Guide

## 1. Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Set the database in `backend/.env`:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/task-assi-sys
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

To try it without Postgres, use SQLite instead:

```
DATABASE_URL=sqlite:///./app.db
```

Optionally load a small demo dataset (skipped automatically if the
database already has employees):

```bash
python -m app.etl.seed_demo
```

For the full research dataset, use the existing CSV loaders:

```bash
python -m app.etl.load_all
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Docs: http://127.0.0.1:8000/docs

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

`frontend/.env` controls the API base URL:

```
VITE_API_URL=http://127.0.0.1:8000
```

## 3. Verification scripts

With the API running on port 8010:

```bash
cd backend
DATABASE_URL="sqlite:///./dev_local.db" python e2e_check.py
python page_flow_check.py
```

`e2e_check.py` walks the whole API journey.
`page_flow_check.py` replays each frontend page's request sequence and
validates CORS preflight plus response shape.

## 4. Notes

- Neo4j is optional. If the driver is missing or the server is down, the
  `/graph/*` routes are skipped and the rest of the API still starts.
- The ML model is loaded once per process from
  `ml/models/xgboost_assignment_model.pkl`. If it cannot be loaded, the
  API falls back to a weighted rule-based score and reports
  `scoring_method: "rule_based_fallback"` in the response.
