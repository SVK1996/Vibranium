# Vibranium

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Setup and Run](#setup-and-run)
4. [Enhancements](#enhancements)

## Introduction

Vibranium is a RESTful web service that manages financial transactions with support for parent-child relationships, transaction types, and sum calculations. The service is built using FastAPI and PostgreSQL, providing a robust and scalable solution for transaction management.

## Features
 - Create and retrieve transactions
 - Support for transaction types and parent-child relationships
 - Calculate transaction sums including linked transactions
 - Query transactions by type
 - Redis caching for improved performance
 - Docker support for easy deployment
 - Comprehensive test coverage

## Setup and Run

To set up and run the application, follow these steps:

1. **Prerequisites:**
   - Ensure you have Python 3.11 or higher installed on your system.
   - Install PostgreSQL and Redis servers if not already installed.
   - Docker and Docker Compose

2. **Virtual Environment:**
   - Create a virtual environment for the application to manage dependencies and isolate them from the system-wide Python environment.
        ```
        python3 -m venv venv
        source venv/bin/activate
        ```

3. **Install Dependencies:**
   - Install the required Python packages by running:
     ```
     pip install -r requirements.txt
     ```

4. **Environment Variables:**
    - Edit .env with your configuration
    ```
    cp .env.example .env
    ```
5. **Database Setup:**
   - Run the database migration sql scripts manually in terminal from `alembic upgrade head` to create the necessary tables and schemas.

6. **Start the Application:**
   - Start the application server:
     ```
    uvicorn app.main:app --reload
     ```

Feel free to explore and implement these enhancements to improve the functionality and performance of the Backend Application.
