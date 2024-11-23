# Vibranium

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Setup and Run](#setup-and-run)
4. [Performance and Asymptotic Analysis](#peformance)

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

## Performance and Asymptotic Analysis

### Time Complexity Analysis

| Operation | Time Complexity | Description |
|-----------|----------------|-------------|
| Create Transaction | O(1) | Direct database insertion with constant-time parent validation |
| Get Transaction | O(1) | Direct lookup by transaction ID using database index |
| Get Transactions by Type | O(n) | Linear scan of transactions with type index, where n is the number of transactions of given type |
| Get Transaction Sum | O(h) | Traversal of transaction tree, where h is the height of the transaction hierarchy |


Feel free to explore and implement further enhancements to improve the functionality and performance of the Backend Application.
