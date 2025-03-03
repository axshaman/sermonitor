# SERM Monitoring System

## Overview

SERM Monitoring System is an automated service for monitoring and detecting negative mentions in the top X pages of search engine results. The system helps users track their name or brand presence in online search results and generates detailed reports based on the collected data.

## Features

- **User Registration:** Users register through a Telegram bot.
- **Keyword Monitoring:** Users specify keywords for tracking.
- **Automated Search:** The system retrieves search results for specified keywords.
- **Report Generation:** Results are compiled into a PDF report.
- **Data Storage:** User information and keywords are stored in a PostgreSQL database.
- **Containerized Deployment:** The system is fully containerized with Docker.

---

## Project Structure

```
SERM-Monitoring/
│── bot_telegram/             # Telegram bot logic
│   ├── handlers/             # Message handlers
│   ├── keyboards/            # Custom keyboards
│   ├── loader.py             # Bot initialization
│   ├── config.py             # Configuration file
│   ├── states.py             # User state management
│── api/                      # REST API backend
│   ├── api.py                # Main API endpoints
│   ├── api_queries.py        # API request handling
│   ├── services.py           # Helper functions
│── models/                   # Database models
│   ├── models.py             # User and keyword models
│── database/                 # Database-related files
│── reports/                  # Report generation module
│   ├── pdf_loader.py         # PDF report creation
│── migrations/               # Alembic migration scripts
│── create_advertisement.py   # Ad management module
│── main.py                   # Telegram bot startup script
│── app.py                    # Flask API application entry point
│── docker-compose.yml        # Docker Compose configuration
│── requirements.txt          # Project dependencies
│── .env                      # Environment variables configuration
```

---

## Technologies Used

- **Backend:** Flask, Flask-RESTful, Flask-SQLAlchemy
- **Database:** PostgreSQL
- **Bot Framework:** Aiogram
- **PDF Reports:** ReportLab
- **Containerization:** Docker, Docker Compose

---

## Installation & Setup

### 1. Clone the Repository

```sh
git clone https://github.com/axshaman/sermonitor.git
cd sermonitor
```

### 2. Install Dependencies

Create a virtual environment and install dependencies:

```sh
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file and add the following parameters:

```env
POSTGRES_DB=db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

### 4. Run with Docker

To start all services using Docker Compose:

```sh
docker-compose up --build
```

### 5. Run Manually (Without Docker)

#### 5.1 Start PostgreSQL

Ensure PostgreSQL is installed and running:

```sh
sudo service postgresql start
```

Create the database and user:

```sql
CREATE DATABASE deleteme;
CREATE USER pashkan WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE deleteme TO pashkan;
```

#### 5.2 Start API

```sh
python app.py
```

#### 5.3 Start Telegram Bot

```sh
python main.py
```

---

## API Endpoints

| Method  | URL              | Description |
|---------|-----------------|-------------|
| `POST`  | `/register`     | Registers a new user |
| `POST`  | `/check-user`   | Checks if a user exists |
| `POST`  | `/check-keywords` | Adds keywords for monitoring |
| `GET`   | `/check-keywords` | Searches for specified keywords |
| `GET`   | `/result`       | Retrieves all searched keywords |
| `GET`   | `/user-data`    | Fetches user data |

---

## PDF Report Generation

Reports are generated using `ReportLab`. The `pdf_loader.py` module compiles search results into structured PDF documents containing URLs and relevant snippets.

---