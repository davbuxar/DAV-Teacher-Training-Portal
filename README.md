# DAV Teacher Training Portal

A teacher registration and training management portal.

## Architecture
- `frontend/`: static HTML/CSS/JavaScript hosted on GitHub Pages.
- `backend/`: FastAPI application hosted separately (for example, Render).
- MySQL: hosted separately (for example, Aiven or another managed MySQL provider).

> GitHub Pages cannot run Python or host MySQL. Never put database credentials or JWT secrets in frontend files or commit them to GitHub.

## Features in this starter
- Teacher registration and login API
- Unique email and mobile validation
- Teacher profiles and Pending-by-default approval
- Admin approval endpoint
- Training-event listing and creation endpoints
- Responsive static frontend starter

## Backend setup
1. Create a MySQL database and note its connection details.
2. Copy `backend/.env.example` to `backend/.env` and fill in the values.
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Run from the repository root: `uvicorn backend.main:app --reload`
5. Open `http://127.0.0.1:8000/docs` to test the API.

## Frontend setup
Open `frontend/index.html` locally, or enable GitHub Pages for the `/frontend` folder using GitHub Actions. Set the API base URL in `frontend/js/config.js` to your deployed backend URL.

## Deployment
- Frontend: GitHub Pages (GitHub Actions workflow can be added after backend URL is known).
- Backend: Render or another Python ASGI host. Set environment variables from `.env.example`.
- Database: managed MySQL provider. Restrict network access where possible.

## Security notes
Use HTTPS, a strong random `JWT_SECRET`, restricted CORS origins, database least-privilege credentials, and production password hashing. Configure an admin account securely before public launch. This starter is a foundation and should be reviewed and tested before production use.
