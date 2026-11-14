# ServiceWatch – Service Monitoring & Incident Management System

## Project Overview

ServiceWatch is a Python-based service monitoring and incident management application that monitors website availability, records response times, detects service failures, and tracks incidents.

The application monitors 10 real-world web endpoints at 60-second intervals and stores monitoring results in a MySQL database.

## Key Features

- **Automated Health Monitoring:** Checks 10 website endpoints every 60 seconds.
- **Response Time Tracking:** Records HTTP status codes and response times.
- **Incident Detection:** Creates incidents after 3 consecutive service failures.
- **Severity Classification:** Categorizes incidents based on severity.
- **Incident Management:** Supports assignment, status updates, escalation tracking, and resolution.
- **REST APIs:** Provides endpoints for service monitoring, incident management, and metrics.
- **Performance Metrics:** Calculates uptime percentage, P95 response time, and Mean Time to Resolve (MTTR).
- **Dashboard:** Displays service health, monitoring metrics, and incident summaries.
- **Troubleshooting Documentation:** Includes five Linux troubleshooting scenarios.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Database | MySQL |
| API | REST API |
| Containerization | Docker, Docker Compose |
| Query Language | SQL |
| Testing | Pytest |
| API Testing | PowerShell |
| Operating System Concepts | Linux |

## System Architecture

1. Flask application retrieves active services from MySQL.
2. The monitoring scheduler checks services every 60 seconds.
3. HTTP status codes and response times are stored in MySQL.
4. Three consecutive failures trigger incident creation.
5. Incidents can be assigned, escalated, updated, and resolved.
6. REST APIs provide monitoring and incident information.
7. The dashboard displays service health and performance metrics.

## Monitored Services

The application currently monitors:

- Google
- Cloudflare
- GitHub Status
- RFC Editor
- Python
- Microsoft
- Mozilla
- Docker
- Postman
- Debian

## Project Structure

```text
Service-Watch/
│
├── app.py
├── db.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
├── troubleshooting.md
│
├── templates/
│   └── dashboard.html
│
└── test/
    └── test_api.py
```

## Installation and Setup

### Prerequisites

- Python 3.10+
- Docker Desktop
- MySQL Server
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Sathyanarayanan2002/Service-Watch.git
cd Service-Watch
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
MYSQL_PASSWORD=your_mysql_password
```

Configure the remaining database settings in `docker-compose.yml` as required by your environment.

Do not commit your `.env` file or database credentials to GitHub.

### 3. Start the Application

```bash
docker compose up -d --build
```

### 4. Access the Dashboard

Open:

```text
http://localhost:5000/dashboard
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application health check |
| GET | `/api/services` | Retrieve services |
| GET | `/api/incidents` | Retrieve incidents |
| GET | `/api/metrics` | Retrieve monitoring metrics |
| PATCH | `/api/incidents/{incident_id}` | Update incident status and assignment |

## Testing

Automated API tests are implemented using Pytest.

Run tests using:

```bash
python -m pytest -v
```

**Latest test result:** 7 tests passed.

## Troubleshooting

Refer to `troubleshooting.md` for documented troubleshooting scenarios covering:

- Docker container issues
- Application port issues
- Application logs
- MySQL connectivity
- DNS and network connectivity

## Project Objective

To demonstrate practical knowledge of Python application development, database integration, REST APIs, automated monitoring, incident management, Docker deployment, SQL performance metrics, and troubleshooting.
