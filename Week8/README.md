# Book API Testing Guide

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Newman (Postman CLI)
```bash
npm install -g newman
```

## Running the API

Start the Flask API server:
```bash
python app.py
```
Server runs at `http://localhost:5000`

## Running Tests

### Run All Tests with Newman
```bash
newman run Book_API_Tests.postman_collection.json --environment <environment-file> -r cli
```

### Run Tests with HTML Report
```bash
newman run Book_API_Tests.postman_collection.json -r html --reporter-html-export test-report.html
```

### Run Specific Test Requests
```bash
newman run Book_API_Tests.postman_collection.json --folder "1. Health Check"
```

## Test Coverage

- **Health Check**: API status endpoint
- **GET All Books**: Retrieve book list with array validation
- **POST Create Book**: Create new book, verify response structure
- **GET Book by ID**: Fetch single book, check fields
- **PUT Update Book**: Update book data, verify changes
- **DELETE Book**: Remove book, confirm deletion message
- **GET Search Books**: Filter books by query parameter

## Test Results

- Run Newman with `--reporter json` to save results
- View HTML report generated in test-report.html
- Performance metrics included in detailed reports
