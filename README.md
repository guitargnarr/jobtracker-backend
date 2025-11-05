# Job Tracker Backend - "Synergy Dashboard™ 3000"

FastAPI backend for job application tracking with corporate satire branding.

## Features

- 📊 Full CRUD for job applications
- 📧 Gmail IMAP integration (auto-scan for job emails)
- 🎭 Demo mode with fake data
- 🔒 Real mode with actual CSV data
- 🚨 Phishing detection
- 📈 Analytics & stats dashboard

## Tech Stack

- FastAPI 0.115+
- Python 3.14
- pandas for CSV handling
- IMAP for Gmail scanning
- Deployed on Render.com

## Local Development

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Visit API docs
http://localhost:8000/docs
```

## API Endpoints

- `GET /` - API info with corporate humor
- `GET /health` - Health check
- `GET /api/applications` - List all applications
- `POST /api/applications` - Create new application
- `PUT /api/applications/{id}` - Update application
- `DELETE /api/applications/{id}` - Delete application
- `POST /api/gmail/scan` - Trigger Gmail scan
- `GET /api/stats/overview` - Dashboard statistics
- `POST /api/auth/mode` - Toggle demo/real mode
- `GET /api/phishing/alerts` - Get phishing attempts

## Environment Variables

```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
CSV_PATH=/path/to/JOB_TRACKER_LIVE.csv
```

## Deployment (Render)

1. Push to GitHub
2. Connect to Render.com
3. Set environment variables
4. Deploy with:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

Part of Matthew Scott's portfolio - Louisville AI Consultant
**Frontend:** Coming soon
**Portfolio:** https://jaspermatters.com
**GitHub:** https://github.com/guitargnarr
