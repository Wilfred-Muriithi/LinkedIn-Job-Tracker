## LinkedIn Job Tracker – Backend + GitHub Pages Frontend

This repo now has two parts:

1. **Flask backend (`app.py`)** – scrapes LinkedIn, logs jobs to Google Sheets, and emails matches.
2. **Static frontend (`frontend/`)** – a single-page app you can host on GitHub Pages that calls the backend API.

### 1. Backend (Flask API)

#### Environment

Copy `.env.example` (if you have one) or create `.env` with:

```
EMAIL_ENABLED=true
EMAIL_FROM=you@gmail.com
EMAIL_PASSWORD=app-password
EMAIL_TO=default@recipient.com  # used if frontend doesn't send a custom email
```

Place your Google service account JSON as `credentials.json` and ensure the sheet name in `sheet_writer.py` matches the one in Google Sheets.

#### Install & run locally

```powershell
Traack_venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

- Health check: `GET http://localhost:5000/health`
- Job search: `POST http://localhost:5000/api/search`

Payload example:

```json
{
  "skills": "Microsoft Fabric, Power BI",
  "locations": "Remote, Kenya",
  "email": "alerts@example.com"
}
```

The endpoint responds with `{ "total_new": 4, "email_sent": true, "combinations_checked": [...] }`.

#### Deploying the backend

You can deploy the Flask API to any host that supports Python. Two common options:

- **Render**
  1. Create a new “Web Service”, connect this repo.
  2. Environment: `Python 3.11`.
  3. Start command: `gunicorn app:app`.
  4. Add the same environment variables (`EMAIL_*`) plus any Secrets for Google credentials (Render supports mounting files or using environment variables).

- **Railway / Fly.io / Azure App Service**
  - Create Dockerfile or use buildpack; ensure port 5000 is exposed and env vars are set.

Remember to use secret storage for email password and Google credentials. Never commit these values.

### 2. GitHub Pages Frontend

The `frontend/` folder contains the static assets.

#### Configure the API endpoint

1. Copy `frontend/config.example.js` to `frontend/config.js`.
2. Set the deployed backend URL:

```js
window.BACKEND_URL = "https://your-backend.onrender.com/api/search";
```

For local testing, the default `http://localhost:5000/api/search` already works.

#### Preview locally

Open `frontend/index.html` directly in a browser, or serve the folder with any static server:

```powershell
cd frontend
python -m http.server 8000
```

Visit `http://localhost:8000` – the page will call whatever URL is in `config.js`.

#### Publish with GitHub Pages

1. Create a new branch or repo dedicated to Pages (optional but clean).
2. Copy the `frontend/` contents to that repo or configure GitHub Pages to use `/frontend`.
3. In GitHub → Settings → Pages:
   - Source: `Deploy from a branch`
   - Branch: `main` (or whichever) / `/frontend` folder
4. Push changes; GitHub will serve the static site at `https://<username>.github.io/<repo>/`.

Whenever you update the frontend, push again and Pages will redeploy.

### Architecture recap

- GitHub Pages hosts the **static UI** (`frontend/index.html`).
- Users submit skills/locations/email; the UI calls your **Flask backend** (`/api/search`).
- The backend performs LinkedIn scraping, dedupes against Google Sheets, appends new jobs, and (if jobs found) sends an email to the requested address.

### Next steps / ideas

- Add auth/token to `/api/search` to avoid abuse from the public internet.
- Queue searches (Celery/Redis) if you expect high traffic.
- Allow recurring alerts per user instead of manual triggers.


