# SERM Monitoring System

SERM Monitoring System automates the detection of negative mentions about a person or brand within search engine result pages. It combines a REST API, a Telegram bot and PDF report generation to deliver actionable monitoring insights.

## What's new

- Modernised Flask application factory with a `/health` endpoint.
- Fully validated REST API with JSON responses and richer error handling.
- New `/api/search` endpoint that can optionally generate PDF reports on demand.
- Keyword management now supports create, list and delete operations.
- Updated dependencies and improved PDF generation.

## Project layout

```
.
├── app.py                 # Development entrypoint
├── api.py                 # REST resources registered under /api
├── bot_telegram/          # Telegram bot code
├── models/                # SQLAlchemy models and database setup
├── pdf_loader.py          # PDF report helpers
├── reports/               # Generated reports (created at runtime)
├── services.py            # Service layer shared by the API
├── xmlproxy.py            # XMLProxy wrapper
└── docs/
    ├── architecture.md    # C4 model documentation
    └── openapi.yaml       # OpenAPI description for the HTTP API
```

## Requirements

- Python 3.10+
- PostgreSQL 13+
- (Optional) Docker & Docker Compose

All Python dependencies are pinned in [`requirements.txt`](requirements.txt).

## Configuration

| Environment variable | Description | Default |
| -------------------- | ----------- | ------- |
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql+psycopg2://pashkan:password@deleteme_db:5432/deleteme` |
| `XMLPROXY_URL` | Base URL for the XMLProxy search API | `http://xmlproxy.ru/search/` |

Create a `.env` file (or export the variables) before running the services.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\\Scripts\\activate`
pip install -r requirements.txt
flask --app app db upgrade  # Make sure the database exists beforehand
python app.py
```

The API will be available at `http://localhost:8200/api`. The Telegram bot can be started separately using `python main.py` once you configure the bot token in `bot_telegram/config.py`.

### Docker Compose

The repository includes a `docker-compose.yml` that wires together PostgreSQL and the application container:

```bash
docker-compose up --build
```

## REST API

The API is documented in [`docs/openapi.yaml`](docs/openapi.yaml). A short summary of the most important endpoints:

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/api/register` | Register a user sent by the Telegram bot |
| `POST` | `/api/check-user` | Check whether a Telegram user exists |
| `POST` | `/api/check-keywords` | Attach keywords to a user |
| `GET` | `/api/check-keywords` | List keywords for a user |
| `DELETE` | `/api/check-keywords` | Remove keywords from a user |
| `POST` | `/api/search` | Perform a monitoring search and optionally generate a PDF |
| `GET` | `/api/user-data` | Return basic user profile information |
| `DELETE` | `/api/user` | Remove a user and their associations |

## PDF reports

The helper in [`pdf_loader.py`](pdf_loader.py) stores generated reports in the `reports/` directory. Reports contain the headline, URL and snippet for each search result returned by the XMLProxy provider.

## Architecture

A C4 model describing the system and the interactions between the API, the Telegram bot, the database and external services is available in [`docs/architecture.md`](docs/architecture.md).

## Contributing

1. Fork the repository and create a feature branch.
2. Install dependencies and configure the environment variables.
3. Add tests or scripts when adding new features.
4. Submit a pull request.

## License

This project is released under the MIT License.
