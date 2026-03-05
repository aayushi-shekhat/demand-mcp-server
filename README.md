# Demand MCP Server

FastAPI based **Model Context Protocol (MCP) tool server** used by the **Demand Agent** to interact with the PostgreSQL database.

The MCP server exposes tools that allow the AI agent to create and manage recruitment demands.

---

# Purpose

The MCP server acts as a **bridge between the AI agent and the database**.

```
Demand Agent
      │
      ▼
MCP Tools (FastAPI)
      │
      ▼
PostgreSQL Database
```

---

# Tech Stack

```
FastAPI
Python
SQLAlchemy
PostgreSQL
Pydantic
Uvicorn
```

---

# Project Structure

```
demand-mcp-server
│
├── main.py            # FastAPI application entrypoint
├── tools.py           # MCP tools (business logic)
├── schemas.py         # Pydantic request models
├── database.py        # Database connection setup
├── requirements.txt   # Python dependencies
├── .env               # Environment variables
└── README.md
```

---

# MCP Tools

## create_demand

Creates a new demand in the database.

Endpoint

```
POST /create-demand
```

Used by the Demand Agent to store new resource requests.

---

## get_demands

Fetches all existing demands.

Endpoint

```
GET /demands
```

---

## update_demand

Updates the demand status.

Endpoint

```
PUT /update-demand/{demand_id}
```

---

# API Documentation

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# Running the Server

Create virtual environment

```
python -m venv venv
```

Activate

```
venv\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

Run server

```
uvicorn main:app --reload
```

Server runs at

```
http://127.0.0.1:8000
```

---

# Environment Variables

Stored in `.env`

Example:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=recruitment_db
DB_USER=postgres
DB_PASSWORD=password
```

---

# Database Schema

Main table:

```
demands
```

Columns:

```
demand_id
project_name
crm_id
required_count
fulfilled_count
status
external_flag
client_interview_flag
created_at
updated_at
```

---

# Integration with Demand Agent

The Demand Agent calls MCP tools using REST APIs.

Example workflow:

```
User raises demand
       │
Agent collects inputs
       │
Agent calls MCP tool
       │
FastAPI inserts record
       │
PostgreSQL stores demand
```

---

# Maintainer

Aayushi Shekhat
Selena Jasmine
