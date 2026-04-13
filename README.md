# Dog Breed Explorer
### IS2209 DeployHub Project

**Live URL:** https://flaskproject11-xnta.onrender.com/
**GitHub Repo:** https://github.com/Evan3129/FlaskProject11

---

## Group Information

**Group Number:** Group 29

| Name | Student Number  |
|---|-----------------|
| Jack Hanley| 124322031       |
| Evan O'Toole| 124357173       |
| Shane Hartnett | 124376781       |

---

## Overview

A Flask web application that allows users to browse, search, and save dog breeds. Breed data is fetched from The Dog API and persisted in a PostgreSQL database hosted on Supabase.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | PostgreSQL (psycopg) |
| External API | The Dog API |
| Environment | python-dotenv |
| Containerisation | Docker |
| CI/CD | GitHub Actions |

---

## Project Structure

```
FlaskProject11/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── static/
│   └── style.css               # App styling
├── templates/
│   ├── index.html              # Home page
│   ├── dogs.html               # Browse/search breeds
│   └── saved.html              # Saved breeds page
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared pytest fixtures
│   ├── test_health.py          # Health endpoint tests
│   ├── test_integration.py     # Integration tests
│   └── test_resilience.py      # Graceful degradation tests
├── .env                        # Environment variables (not committed)
├── .env.example                # Example environment variables
├── .gitignore
├── app.py                      # Main Flask application
├── Dockerfile                  # Docker configuration
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <https://github.com/Evan3129/FlaskProject11>
cd FlaskProject11
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template:

```env
SECRET_KEY=your_secret_key
THEDOG_API_KEY=your_dog_api_key
DATABASE_URL=your_postgresql_connection_string
```

### 4. Run the application

```bash
flask run
```

The app will be available locally at `http://127.0.0.1:5000`

Or visit the live deployment at https://flaskproject11-xnta.onrender.com/

---

## Features

- Browse 6 randomly selected dog breeds on each visit
- Search for breeds by name
- View detailed breed info (group, origin, temperament, life span, height, weight)
- Save favourite breeds to a PostgreSQL database
- Delete saved breeds
- `/health` and `/status` endpoints for monitoring
- Structured logging with request IDs and timing on every request
- Retry/back-off logic when the Dog API is unavailable

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/` | Home page |
| GET | `/dogs-page` | Browse random dog breeds |
| GET | `/search?q=<query>` | Search breeds by name |
| GET | `/saved` | View saved breeds |
| POST | `/save_dog` | Save a breed to the database |
| GET | `/delete_dog/<id>` | Delete a saved breed |
| GET | `/dogs` | JSON — random breed data |
| GET | `/health` | JSON — app health check |
| GET | `/status` | JSON — database and API status |

---

## Running Tests

```bash
pip install pytest
pytest -v
```

### Test Coverage

| File | Test |
|---|---|
| `test_integration.py` | `test_returns_joined_result_when_both_sources_available` |
| `test_resilience.py` | `test_graceful_degradation_on_upstream_failure` |
| `test_health.py` | `test_health_endpoint_reports_dependencies` |
| `test_health.py` | `test_status_endpoint_reports_database_and_api` |

---

## CI/CD Pipeline

GitHub Actions is configured to run automatically on every pull request. The pipeline will:
- Run all pytest tests
- Block merging if any tests fail

Pipeline config: `.github/workflows/ci.yml`

---

## Observability

The app logs every request to stdout with a unique request ID and response time:

If the Dog API is unavailable the app retries 3 times with back-off (1s, 2s, 4s) before returning an error.

The `/status` endpoint reports live database and API connectivity.

---

## Docker

```bash
docker build -t dog-breed-explorer .
docker run -p 5000:5000 --env-file .env dog-breed-explorer
```