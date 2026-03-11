## Sales Insight Automator

Full-stack project for generating executive sales summaries from CSV data using Gemini and emailing the results.

### Project structure

- **backend**: FastAPI application exposing `/upload`
- **frontend**: React single-page app for CSV upload and email input
- **docker-compose.yml**: Orchestrates backend and frontend
- **.env.example**: Sample environment variables

### Backend (FastAPI)

- **Endpoint**: `POST /upload`
  - Accepts multipart form data:
    - `file`: CSV file with sales data
    - `email`: destination email address
  - Uses `pandas` to parse the CSV
  - Sends a prompt with a CSV preview to the Gemini API
  - Emails the generated executive summary via SMTP
  - Returns a JSON confirmation

FastAPI automatically exposes Swagger documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

#### Running backend locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example ../.env  # then edit values

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React + Vite)

The React app provides:

- CSV file chooser (`.csv` only)
- Email input field
- Submit button that posts to the backend `/upload` endpoint

Configure the backend URL via `VITE_API_BASE_URL` (defaults to `http://localhost:8000`).

#### Running frontend locally

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

### Environment variables

Copy `.env.example` to `.env` and fill in:

- **GEMINI_API_KEY**: Your Gemini API key
- **GEMINI_MODEL**: Gemini model name (e.g. `gemini-1.5-flash`)
- **SMTP_HOST**: SMTP server hostname
- **SMTP_PORT**: SMTP port (e.g. `587`)
- **SMTP_USER** / **SMTP_PASSWORD**: SMTP credentials
- **SMTP_FROM**: From address for the summary email
- **FRONTEND_ORIGIN**: Frontend origin for CORS (e.g. `http://localhost:5173`)

### Docker & docker-compose

To run both services with Docker:

```bash
cp .env.example .env  # then edit values
docker compose up --build
```

Services:

- **backend**: `http://localhost:8000`
  - Swagger at `http://localhost:8000/docs`
- **frontend**: `http://localhost:5173`

### GitHub Actions CI

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on pushes/PRs to `main`/`master`:

- Backend:
  - Installs dependencies
  - Runs `python -m compileall` for a basic syntax check
- Frontend:
  - Installs dependencies
  - Runs `npm run build`

