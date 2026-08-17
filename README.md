# SDET Screening Assessment — Divya A
### Lead QA Engineer / SDET Level

> This README is designed to be **copy-pasted directly into any AI agent** (ChatGPT, Claude, Gemini, Copilot, Kiro, etc.) to fully reproduce both assessments end-to-end. Each task section contains the exact prompt used, the constraints, and the expected deliverables.

---

## Repository Structure

```
sdet-screening-Divya-A/
├── README.md                  ← This file — master prompt & execution guide
├── AI Conversation.md         ← Full session chat history (Task A + Task C)
├── Scripts.sql.py             ← All SQL queries (Task A) + pytest suite (Task C)
└── Output.md                  ← All executed results with detailed inline comments
```

---

## How to Use This README

1. Copy the **complete prompt block** for the task you want to run (Task A or Task C, or both).
2. Paste it into your preferred AI agent or IDE assistant.
3. The agent will generate the SQL queries / test code.
4. Validate results against the **Expected Output** sections in this file.

---

---

# TASK A — SQL Data Reconciliation

## Background

A QA Data Engineer needs to compare two daily product catalog snapshots stored in a relational database. The goal is to detect all meaningful changes between yesterday's and today's snapshot — price movements, new additions, product removals, and status transitions.

---

## Copy-Paste Prompt — Task A

```
Act as a Senior Database Specialist and QA Engineer.

I need you to complete a 5-part SQL data reconciliation exercise comparing
yesterday's and today's product catalog snapshots.

=== SCHEMAS ===

Table 1: products_yesterday
Columns: product_id INT, product_name VARCHAR, price DECIMAL, status VARCHAR

Data:
(1001, 'Coffee Mug',     12.50, 'ACTIVE')
(1002, 'Laptop Stand',   38.00, 'ACTIVE')
(1003, 'Wireless Mouse', 19.99, 'ACTIVE')
(1004, 'Old Keyboard',   29.99, 'DISCONTINUED')
(1005, 'Notebook',        4.50, 'ACTIVE')
(1008, 'Desk Lamp',      24.00, 'ACTIVE')

Table 2: products_today
Columns: product_id INT, product_name VARCHAR, price DECIMAL, status VARCHAR

Data:
(1001, 'Coffee Mug',     12.50, 'ACTIVE')
(1002, 'Laptop Stand',   35.00, 'ACTIVE')
(1003, 'Wireless Mouse', 21.99, 'ACTIVE')
(1005, 'Notebook',        4.50, 'INACTIVE')
(1006, 'Webcam',         59.00, 'ACTIVE')
(1007, 'USB Cable',       7.99, 'ACTIVE')
(1008, 'Desk Lamp',      24.00, 'ACTIVE')

=== TASKS ===

Task 1 — Price Changes
Find products that exist in BOTH tables but whose price has changed.
Required columns: product_id, product_name, old_price, new_price

Task 2 — New Products
Find products present in products_today but NOT in products_yesterday.
Required columns: product_id, product_name, price, status

Task 3 — Missing Products
Find products present in products_yesterday but NOT in products_today.
Required columns: product_id, product_name, price, status

Task 4 — Status Changes
Find products in BOTH tables whose status value has changed.
Required columns: product_id, product_name, old_status, new_status

Task 5 — Technical Explanation (Markdown)
Explain:
  a) Why you chose INNER JOIN vs NOT EXISTS vs NOT IN for each task
  b) What happens if product_id is non-unique (duplicate key impact on QA)
  c) What risks arise if price or status contain NULL values, and how you mitigate them

=== CONSTRAINTS ===
- Use ANSI SQL compatible with PostgreSQL, MySQL 8+, SQL Server, Snowflake
- Use explicit aliases: y = products_yesterday, t = products_today
- Output column names must EXACTLY match the names specified above
- All comparison logic must be NULL-safe (use COALESCE or IS DISTINCT FROM)
- Add inline comments explaining each design decision
```

---

## Task A — Setup Instructions

### Step 1 — Create Tables

```sql
CREATE TABLE products_yesterday (
    product_id   INT,
    product_name VARCHAR(100),
    price        DECIMAL(10, 2),
    status       VARCHAR(50)
);

CREATE TABLE products_today (
    product_id   INT,
    product_name VARCHAR(100),
    price        DECIMAL(10, 2),
    status       VARCHAR(50)
);
```

### Step 2 — Load Sample Data

```sql
INSERT INTO products_yesterday (product_id, product_name, price, status) VALUES
    (1001, 'Coffee Mug',     12.50, 'ACTIVE'),
    (1002, 'Laptop Stand',   38.00, 'ACTIVE'),
    (1003, 'Wireless Mouse', 19.99, 'ACTIVE'),
    (1004, 'Old Keyboard',   29.99, 'DISCONTINUED'),
    (1005, 'Notebook',        4.50, 'ACTIVE'),
    (1008, 'Desk Lamp',      24.00, 'ACTIVE');

INSERT INTO products_today (product_id, product_name, price, status) VALUES
    (1001, 'Coffee Mug',     12.50, 'ACTIVE'),
    (1002, 'Laptop Stand',   35.00, 'ACTIVE'),
    (1003, 'Wireless Mouse', 21.99, 'ACTIVE'),
    (1005, 'Notebook',        4.50, 'INACTIVE'),
    (1006, 'Webcam',         59.00, 'ACTIVE'),
    (1007, 'USB Cable',       7.99, 'ACTIVE'),
    (1008, 'Desk Lamp',      24.00, 'ACTIVE');
```

### Step 3 — Run Queries

Open `Scripts.sql.py` and execute the SQL section (lines 1–100). Each task block is clearly labelled.

### Step 4 — Validate Results

| Task | Expected Row Count | Key Affected Rows |
|------|--------------------|-------------------|
| Task 1 — Price Changes | 2 | 1002 Laptop Stand (38.00→35.00), 1003 Wireless Mouse (19.99→21.99) |
| Task 2 — New Products | 2 | 1006 Webcam, 1007 USB Cable |
| Task 3 — Missing Products | 1 | 1004 Old Keyboard |
| Task 4 — Status Changes | 1 | 1005 Notebook (ACTIVE→INACTIVE) |

---

---

# TASK C — API Test Automation

## Background

An SDET needs to design and implement a production-ready automated test suite for a RESTful orders endpoint. The suite must cover the five core QA risk categories: happy path, error handling, authorization, boundary/format, and schema contract validation.

---

## Copy-Paste Prompt — Task C

```
Act as a Lead QA Engineer / SDET.

I need you to complete a 2-part API testing assessment for a RESTful endpoint.

=== ENDPOINT DETAILS ===

Endpoint: GET /api/orders/{order_id}

Success Response — HTTP 200 OK:
{
  "order_id":    "ORD-1001",
  "customer_id": "C001",
  "amount":      100.50,
  "currency":    "GBP",
  "status":      "PAID",
  "created_at":  "2026-05-20T10:30:00Z"
}

=== TASK 1 — TEST CASE DESIGN ===

Provide 5 distinct, high-impact test cases for an automated API test suite.
Test cases must span these 5 categories (one each):
  - Happy Path
  - Error Handling
  - Authorization / Access Control
  - Boundary / Format
  - Schema Validation

For EACH test case provide:
  1. Test Name (descriptive, e.g. TC01_GetOrder_HappyPath_ValidOrderID)
  2. Input (path params, headers, token)
  3. Expected Result (HTTP status + response body / error contract)
  4. Why This Test is Useful (risk-based QA rationale)

=== TASK 2 — AUTOMATED TEST CODE ===

Write production-ready automated test code for:
  - Action  : GET /api/orders/ORD-1001
  - Assert 1: HTTP status code is 200 OK
  - Assert 2: Response body field 'status' equals 'PAID'
  - Assert 3: Content-Type response header contains 'application/json'
  - Assert 4: Full response schema matches the contract above

Framework: Python requests + pytest
Also implement TC02–TC05 as additional test classes in the same file.

=== CONSTRAINTS ===
- Base URL must be read from a BASE_URL environment variable (never hardcoded)
- Auth token must be read from an API_AUTH_TOKEN environment variable
- All assertions must include descriptive failure messages
- Use pytest fixtures (session-scoped) for shared config
- Use jsonschema for contract/schema validation
- Use @pytest.mark.parametrize for boundary input variants
- Every request must have a timeout parameter
- Follow PEP 8 and include module-level docstring with setup/run instructions
```

---

## Task C — Setup Instructions

### Step 1 — Install Dependencies

```bash
pip install requests pytest jsonschema
# Optional: for HTML test reports
pip install pytest-html
```

### Step 2 — Configure Environment

```bash
# Local development
export BASE_URL=http://localhost:8000
export API_AUTH_TOKEN=your-local-token

# Or create a .env file (add .env to .gitignore — never commit tokens)
BASE_URL=http://localhost:8000
API_AUTH_TOKEN=your-local-token
```

### Step 3 — Run the Tests

```bash
# Basic run with verbose output
pytest Scripts.sql.py -v -k "TestGet"

# Run against staging
BASE_URL=https://api-staging.example.com \
API_AUTH_TOKEN=your-staging-token \
pytest Scripts.sql.py -v

# Generate HTML report
pytest Scripts.sql.py -v --html=report.html --self-contained-html
```

### Step 4 — Validate Results

| Test ID | Test Name | Category | Expected Outcome |
|---------|-----------|----------|-----------------|
| TC01 | `test_TC01_get_order_happy_path_valid_order_id` | Happy Path | PASS — HTTP 200, status=PAID, schema valid |
| TC02 | `test_TC02_get_order_not_found_returns_404` | Error Handling | PASS — HTTP 404, error key in body |
| TC03 | `test_TC03_get_order_missing_auth_token_returns_401` | Authorization | PASS — HTTP 401 |
| TC04 | `test_TC04_...[×5 variants]` | Boundary/Format | PASS — HTTP 4xx, never 500 |
| TC05 | `test_TC05_get_order_response_matches_schema_contract` | Schema Validation | PASS — all fields, types, ISO codes valid |

**Total test cases: 9** (TC04 is parametrized across 5 malformed input variants)

---

---

# Combined QA Engineering Reference

## Key Technical Decisions

| Decision | Task A | Task C |
|---|---|---|
| Primary technique | INNER JOIN (change detection), NOT EXISTS (set difference) | pytest + requests + jsonschema |
| NULL safety | COALESCE(col, sentinel) on all comparisons | N/A (JSON values) |
| Duplicate key handling | Pre-flight COUNT vs COUNT DISTINCT check | N/A |
| Security coverage | NULL injection via price/status | OWASP API1:2023 BOLA/IDOR (TC03) |
| Contract validation | IS DISTINCT FROM alternative | jsonschema with additionalProperties: false |
| CI/CD integration | Any SQL runner | pytest with env var injection |

## Pre-Flight Data Quality Check (Task A)

Always run this before executing reconciliation queries to detect duplicate keys:

```sql
-- Run for both tables before reconciliation
SELECT
    'products_yesterday'     AS table_name,
    COUNT(*)                 AS total_rows,
    COUNT(DISTINCT product_id) AS unique_ids,
    COUNT(*) - COUNT(DISTINCT product_id) AS duplicates
FROM products_yesterday
UNION ALL
SELECT
    'products_today',
    COUNT(*),
    COUNT(DISTINCT product_id),
    COUNT(*) - COUNT(DISTINCT product_id)
FROM products_today;
-- If duplicates > 0, halt and investigate before reconciling
```

## CI/CD Pipeline Integration (Task C)

```yaml
# GitHub Actions — add to .github/workflows/api-tests.yml
name: API Test Suite
on: [push, pull_request]
jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install requests pytest jsonschema pytest-html
      - name: Run API Tests
        env:
          BASE_URL: ${{ secrets.STAGING_API_URL }}
          API_AUTH_TOKEN: ${{ secrets.STAGING_API_TOKEN }}
        run: pytest Scripts.sql.py -v --tb=short --html=report.html --self-contained-html
      - uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: report.html
```

---

## Compatibility Matrix

| Tool / Platform | Task A (SQL) | Task C (API Tests) |
|---|---|---|
| PostgreSQL 12+ | ✅ | — |
| MySQL 8+ | ✅ | — |
| SQL Server 2016+ | ✅ | — |
| SQLite 3.35+ | ✅ | — |
| Snowflake | ✅ | — |
| BigQuery | ✅ | — |
| Python 3.8+ | — | ✅ |
| pytest 7+ | — | ✅ |
| jsonschema 4+ | — | ✅ |
| Any CI/CD (GitHub Actions, GitLab CI, Jenkins) | ✅ | ✅ |
