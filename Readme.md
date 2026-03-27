# Backend Data Pipeline

This project simulates a real-world data pipeline using Flask, FastAPI, and PostgreSQL, all running with Docker.

Flask acts as a mock API serving customer data, while FastAPI ingests this data and stores it in PostgreSQL.

To run the project:
1. Make sure Docker Desktop is running
2. Run: docker-compose up --build

Access APIs:
- Flask: http://localhost:5000/api/customers
- FastAPI: http://localhost:8000/api/customers

Use POST /api/ingest to load data into the database.

This project demonstrates API integration, data ingestion, and containerized backend architecture.
