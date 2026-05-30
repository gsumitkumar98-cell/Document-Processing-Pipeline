# Document Processing Pipeline

A production-ready Python document processing system built using Object-Oriented Programming (OOP), Clean Architecture, Dependency Injection, and SOLID design principles.

The application loads documents, splits them into chunks, stores them in a repository, and retrieves relevant chunks based on search queries.

---

# Features

* Object-Oriented Design
* SOLID Principles
* Dependency Injection
* Clean Architecture
* Pydantic Configuration Management
* Environment Variable Support
* Structured JSON Logging
* Rotating Log Files
* Custom Exception Handling
* Repository Pattern
* Document Chunking
* Keyword-Based Retrieval
* Unit Testing with Pytest
* Docker Support
* GitHub Actions CI/CD
* Type Hints Throughout Application

---

# Technology Stack

| Technology         | Purpose                  |
| ------------------ | ------------------------ |
| Python 3.11+       | Programming Language     |
| FastAPI            | API Framework            |
| Uvicorn            | ASGI Server              |
| Pydantic Settings  | Configuration Management |
| Pytest             | Testing                  |
| Docker             | Containerization         |
| GitHub Actions     | CI/CD                    |
| Python JSON Logger | Structured Logging       |

---

# Project Structure

```text
document-processing-pipeline/
│
├── app/
│   └── main.py
│
├── src/
│
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── exceptions.py
│   │   └── constants.py
│   │
│   ├── models/
│   │   ├── document.py
│   │   ├── chunk.py
│   │   ├── retrieval_result.py
│   │   └── search_response.py
│   │
│   ├── interfaces/
│   │   ├── document_loader_interface.py
│   │   ├── chunker_interface.py
│   │   ├── retriever_interface.py
│   │   └── repository_interface.py
│   │
│   ├── repositories/
│   │   └── chunk_repository.py
│   │
│   ├── services/
│   │   ├── document_loader.py
│   │   ├── text_chunker.py
│   │   ├── keyword_retriever.py
│   │   └── pipeline_service.py
│   │
│   ├── dependency/
│   │   └── container.py
│   │
│   └── utils/
│       ├── validators.py
│       └── file_helper.py
│
├── documents/
│   ├── python.txt
│   ├── ai.txt
│   └── microservices.txt
│
├── tests/
│
├── logs/
│
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── README.md
└── DESIGN_NOTE.md
```

---

# Application Flow

```text
Documents
    │
    ▼
Document Loader
    │
    ▼
Document Objects
    │
    ▼
Text Chunker
    │
    ▼
Chunks
    │
    ▼
Chunk Repository
    │
    ▼
Keyword Retriever
    │
    ▼
Search Results
```

---

# Architecture Overview

The project follows Clean Architecture principles.

```text
Presentation Layer
      │
      ▼
Pipeline Service
      │
      ▼
Interfaces
      │
      ▼
Implementations
      │
      ▼
Repository
```

Benefits:

* Loose Coupling
* High Testability
* Easy Maintenance
* Easy Extensibility
* Production Ready

---

# Configuration

Configuration is managed through environment variables.

## .env

```env
APP_NAME=Document Processing Pipeline
LOG_LEVEL=INFO
CHUNK_SIZE=50
MAX_RESULTS=5
DOCUMENT_PATH=documents
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>

cd document-processing-pipeline
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running Application

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

Application URL:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc Documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# API Endpoints

## Health Check

### Request

```http
GET /
```

### Response

```json
{
  "message": "Document Processing Pipeline Running"
}
```

---

## Search Documents

### Request

```http
GET /search?query=python backend
```

### Response

```json
{
  "query": "python backend",
  "total_results": 1,
  "results": [
    {
      "document": "python.txt",
      "chunk_id": 1,
      "text": "Python is widely used for backend development."
    }
  ]
}
```

---

# Sample Documents

## python.txt

```text
Python is widely used for backend development.
Python powers REST APIs.
Python is easy to learn.
```

## ai.txt

```text
Artificial intelligence automates tasks.
Machine learning is a subset of AI.
AI is transforming industries.
```

## microservices.txt

```text
Microservices improve scalability.
Services can be deployed independently.
Microservices are common in cloud systems.
```

---

# Logging

Application uses structured JSON logging.

Log File:

```text
logs/app.log
```

Example:

```json
{
  "asctime": "2026-05-31 10:00:00",
  "levelname": "INFO",
  "name": "document_loader",
  "message": "Document loaded successfully"
}
```

Features:

* Structured JSON Logs
* Rotating File Handler
* Console Logging
* Production Monitoring Friendly

---

# Testing

Run all tests:

```bash
pytest
```

Run coverage:

```bash
pytest --cov=src
```

Example:

```text
5 passed in 0.30s
```

---

# Docker

## Build Image

```bash
docker build -t document-pipeline .
```

## Run Container

```bash
docker run -p 8000:8000 document-pipeline
```

---

# Docker Compose

```bash
docker-compose up --build
```

---

# CI/CD

GitHub Actions automatically:

* Install dependencies
* Run tests
* Generate coverage
* Build Docker image

Pipeline:

```text
Push Code
    │
    ▼
GitHub Actions
    │
    ├── Install Dependencies
    ├── Run Tests
    ├── Generate Coverage
    └── Build Docker Image
```

---

# Design Decisions

## Why Interfaces?

Interfaces provide abstraction and support Dependency Inversion Principle.

Benefits:

* Easy Testing
* Replace Implementations Easily
* Better Maintainability

---

## Why Repository Pattern?

Repository abstracts storage.

Current:

```text
In-Memory Storage
```

Future:

```text
Redis
MongoDB
PostgreSQL
Vector Database
```

without changing business logic.

---

## Why Dependency Injection?

Reduces coupling between components.

Benefits:

* Easier Unit Testing
* Better Scalability
* Cleaner Architecture

---

# Future Improvements

* Semantic Search
* OpenAI Embeddings
* FAISS Vector Search
* Pinecone Integration
* PDF Processing
* DOCX Processing
* OCR Support
* S3 Storage
* Authentication & Authorization
* Kubernetes Deployment

---

# Author

**Sumit Kumar Gupta**

Python Backend Developer

Technologies:

* Python
* FastAPI
* REST APIs
* Docker
* Pytest
* Clean Architecture
* Dependency Injection
* Data Processing
