# SRS Analyzer

A tool that analyzes Software Requirements Specification (SRS) documents and automatically generates a complete FastAPI project structure based on the analysis.

## Features

- Extract API endpoints from SRS documents
- Extract business logic rules
- Extract authentication requirements
- Extract database schema
- Generate a complete FastAPI project structure
- Create database tables automatically
- Generate comprehensive documentation

## Requirements

- Python 3.8+
- PostgreSQL database
- podman

## Required Packages

```bash
pip install fastapi uvicorn python-multipart python-docx sqlalchemy langchain langgraph pydantic graphviz docx2txt langchain_core requests python-dotenv psycopg2-binary
```

## Set up environment variables - create a `.env` file with:

```bash
GROQ_API_KEY=your_groq_api_key 
DB_HOST=localhost 
DB_PORT=5432 
DB_USER=your_db_user 
DB_PASSWORD=your_db_password 
DB_NAME=your_db_name
```

## Usage

1. Start the FastAPI server:
   ```bash uvicorn main:app --reload ```
2. Access the API at http://localhost:8000

3. Use the `/analyze-srs` endpoint to upload and analyze an SRS document:
- The API will extract API endpoints, business logic, authentication requirements, and database schema
- It will generate a project structure in the `generated_project` directory
- It will create documentation in the `docs` directory

## Generated Project

The tool generates a complete FastAPI project with:

- FastAPI application structure
- API routes based on the extracted endpoints
- Database models
- Authentication setup
- Business logic implementation
- Test cases
- Setup scripts
