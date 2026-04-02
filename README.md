#  Dog Breed Explorer

A Flask web application that lets users browse, search, and save dog breeds using [The Dog API](https://thedogapi.com/). Breed data is persisted in a PostgreSQL database.

---

## Features

- Browse 6 randomly selected dog breeds on each visit
- Search for breeds by name
- View detailed breed info (group, origin, temperament, life span, height, weight)
- Save favourite breeds to a PostgreSQL database
- Delete saved breeds
- `/health` and `/status` endpoints for monitoring
- Dockerised for easy deployment
- CI/CD pipeline via GitHub Actions

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | PostgreSQL (psycopg) |
| External API | [The Dog API](https://thedogapi.com/) |
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

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd FlaskProject11
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
THEDOG_API_KEY=your_dog_api_key
DATABASE_URL=your_postgresql_connection_string
```

- Get a free API key at [thedogapi.com](https://thedogapi.com/)
- `DATABASE_URL` should be a valid PostgreSQL connection string (e.g. from Supabase)

### 4. Run the app

```bash
flask run
```

The app will be available at `http://127.0.0.1:5000`

---

## Running with Docker

```bash
docker build -t dog-breed-explorer .
docker run -p 5000:5000 --env-file .env dog-breed-explorer
```

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

### Test coverage

| File | Test |
|---|---|
| `test_integration.py` | `test_returns_joined_result_when_both_sources_available` |
| `test_resilience.py` | `test_graceful_degradation_on_upstream_failure` |
| `test_health.py` | `test_health_endpoint_reports_dependencies` |
| `test_health.py` | `test_status_endpoint_reports_database_and_api` |

---

## CI/CD

GitHub Actions runs automatically on every pull request:
- Linting
- All pytest tests
- Blocks merge on failure

Pipeline config: `.github/workflows/ci.yml`

---

## Requirements

```
flask
psycopg[binary]
requests
python-dotenv
```