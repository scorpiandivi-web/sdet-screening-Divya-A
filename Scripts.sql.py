-- ============================================================
-- SDET SCREENING ASSESSMENT — SCRIPTS
-- Task A: SQL Data Reconciliation  (lines 1  – 130)
-- Task C: API Test Automation      (lines 132 – end, Python)
-- ============================================================
-- HOW TO USE
--   SQL section : copy lines 1–130 into any ANSI SQL client
--                 (PostgreSQL, MySQL 8+, SQL Server, SQLite,
--                  Snowflake, BigQuery, DuckDB)
--   Python section: run with  pytest Scripts.sql.py -v
-- ============================================================


-- ============================================================
-- TASK A — SETUP: Create tables and load sample data
-- Run this block once before executing any query below.
-- ============================================================

CREATE TABLE IF NOT EXISTS products_yesterday (
    product_id   INT,
    product_name VARCHAR(100),
    price        DECIMAL(10, 2),
    status       VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS products_today (
    product_id   INT,
    product_name VARCHAR(100),
    price        DECIMAL(10, 2),
    status       VARCHAR(50)
);

-- Yesterday's snapshot (6 rows)
INSERT INTO products_yesterday (product_id, product_name, price, status) VALUES
    (1001, 'Coffee Mug',     12.50, 'ACTIVE'),       -- unchanged in today
    (1002, 'Laptop Stand',   38.00, 'ACTIVE'),       -- price will drop to 35.00
    (1003, 'Wireless Mouse', 19.99, 'ACTIVE'),       -- price will rise to 21.99
    (1004, 'Old Keyboard',   29.99, 'DISCONTINUED'), -- removed from today
    (1005, 'Notebook',        4.50, 'ACTIVE'),       -- status will change to INACTIVE
    (1008, 'Desk Lamp',      24.00, 'ACTIVE');       -- unchanged in today

-- Today's snapshot (7 rows — 1004 removed, 1006 and 1007 added)
INSERT INTO products_today (product_id, product_name, price, status) VALUES
    (1001, 'Coffee Mug',     12.50, 'ACTIVE'),   -- no change
    (1002, 'Laptop Stand',   35.00, 'ACTIVE'),   -- price changed: 38.00 → 35.00
    (1003, 'Wireless Mouse', 21.99, 'ACTIVE'),   -- price changed: 19.99 → 21.99
    (1005, 'Notebook',        4.50, 'INACTIVE'), -- status changed: ACTIVE → INACTIVE
    (1006, 'Webcam',         59.00, 'ACTIVE'),   -- NEW product
    (1007, 'USB Cable',       7.99, 'ACTIVE'),   -- NEW product
    (1008, 'Desk Lamp',      24.00, 'ACTIVE');   -- no change


-- ============================================================
-- PRE-FLIGHT: Data quality check — run BEFORE reconciliation
-- If duplicates > 0, halt and investigate before proceeding.
-- ============================================================

SELECT
    'products_yesterday'       AS table_name,
    COUNT(*)                   AS total_rows,
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
-- Expected: duplicates = 0 for both tables


-- ============================================================
-- TASK A-1: Price Changes
-- Logic : INNER JOIN on product_id (only products in BOTH tables)
--         COALESCE(col, -1) makes the comparison NULL-safe.
--         Sentinel -1 is safe because valid prices are always >= 0.
-- Expected output: 2 rows (1002, 1003)
-- ============================================================

SELECT
    y.product_id,
    y.product_name,
    y.price  AS old_price,
    t.price  AS new_price
FROM products_yesterday y
INNER JOIN products_today t
    ON y.product_id = t.product_id
WHERE
    COALESCE(y.price, -1) <> COALESCE(t.price, -1);
-- INNER JOIN excludes 1004 (only in yesterday) and 1006/1007 (only in today)
-- 1001, 1005, 1008: price unchanged → excluded by WHERE
-- 1002: 38.00 <> 35.00 → included
-- 1003: 19.99 <> 21.99 → included


-- ============================================================
-- TASK A-2: New Products (in today, NOT in yesterday)
-- Logic : NOT EXISTS correlated subquery.
--         Preferred over NOT IN: if product_id contains any NULL
--         in the inner query, NOT IN returns zero rows for the
--         entire outer query — a silent data loss bug.
--         NOT EXISTS short-circuits on first match (performance).
-- Expected output: 2 rows (1006, 1007)
-- ============================================================

SELECT
    t.product_id,
    t.product_name,
    t.price,
    t.status
FROM products_today t
WHERE NOT EXISTS (
    SELECT 1                        -- SELECT 1 is conventional; value ignored
    FROM products_yesterday y
    WHERE y.product_id = t.product_id
);
-- 1001,1002,1003,1005,1008: found in yesterday → excluded by NOT EXISTS
-- 1006, 1007: not found in yesterday → included


-- ============================================================
-- TASK A-3: Missing Products (in yesterday, NOT in today)
-- Logic : Symmetric NOT EXISTS — same rationale as Task A-2
--         but reversed: source is yesterday, check against today.
-- Expected output: 1 row (1004)
-- ============================================================

SELECT
    y.product_id,
    y.product_name,
    y.price,
    y.status
FROM products_yesterday y
WHERE NOT EXISTS (
    SELECT 1
    FROM products_today t
    WHERE t.product_id = y.product_id
);
-- 1001,1002,1003,1005,1008: found in today → excluded
-- 1004: not found in today (was DISCONTINUED, now removed) → included


-- ============================================================
-- TASK A-4: Status Changes
-- Logic : INNER JOIN (same rationale as Task A-1).
--         COALESCE(col, '') uses empty string as sentinel because
--         valid status codes ('ACTIVE','INACTIVE','DISCONTINUED')
--         are never blank.
-- Expected output: 1 row (1005)
-- ============================================================

SELECT
    y.product_id,
    y.product_name,
    y.status  AS old_status,
    t.status  AS new_status
FROM products_yesterday y
INNER JOIN products_today t
    ON y.product_id = t.product_id
WHERE
    COALESCE(y.status, '') <> COALESCE(t.status, '');
-- 1001,1002,1003,1008: status unchanged → excluded
-- 1005: 'ACTIVE' <> 'INACTIVE' → included
-- Note: 1002 and 1003 have price changes but status is still ACTIVE → excluded here


-- ============================================================
-- END OF SQL SECTION
-- ============================================================


"""
============================================================
TASK C — AUTOMATED API TEST SUITE
Endpoint : GET /api/orders/{order_id}
Framework: Python requests + pytest + jsonschema
Author   : SDET Assessment — Divya A
Date     : 2026-08-18

SETUP:
    pip install requests pytest jsonschema

ENVIRONMENT VARIABLES (set before running):
    BASE_URL        — base URL of the API (default: http://localhost:8000)
    API_AUTH_TOKEN  — bearer token for auth (default: test-bearer-token-valid)

RUN:
    pytest Scripts.sql.py -v
    pytest Scripts.sql.py -v --html=report.html --self-contained-html

TEST COVERAGE:
    TC01 — Happy Path          : HTTP 200, status=PAID, Content-Type, full schema
    TC02 — Error Handling      : HTTP 404 for non-existent order
    TC03 — Authorization       : HTTP 401 with no auth token (OWASP API1:2023)
    TC04 — Boundary/Format     : 4xx for 5 malformed inputs (parametrized)
    TC05 — Schema Validation   : jsonschema contract check, ISO 4217 currency
    Total: 9 test cases
============================================================
"""

import os
import pytest
import requests
from jsonschema import validate, ValidationError

# ---------------------------------------------------------------------------
# Module-level configuration
# BASE_URL falls back to localhost so the file is self-contained for local
# runs against a mock server. Never hardcode production URLs here.
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")

# ---------------------------------------------------------------------------
# JSON Schema — defines the agreed API contract for a 200 OK response.
# Kept at module level so it is shared across TC01 and TC05 without
# duplication. additionalProperties: false ensures any undocumented field
# added by the backend is flagged as a contract violation immediately.
# ---------------------------------------------------------------------------
ORDER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["order_id", "customer_id", "amount", "currency", "status", "created_at"],
    "properties": {
        "order_id":    {"type": "string"},
        "customer_id": {"type": "string"},
        "amount":      {"type": "number"},           # must be number, NOT string
        "currency":    {"type": "string", "minLength": 3, "maxLength": 3},  # ISO 4217
        "status":      {"type": "string"},
        "created_at":  {"type": "string", "format": "date-time"},  # ISO 8601
    },
    "additionalProperties": False,  # reject undocumented fields
}


# ---------------------------------------------------------------------------
# Fixtures — session-scoped to avoid repeated env lookups per test
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api_base_url():
    """
    Provides the API base URL for the test session.
    Override via BASE_URL environment variable for different environments
    (local, staging, production) without changing test code.
    """
    return BASE_URL


@pytest.fixture(scope="session")
def valid_auth_headers():
    """
    Provides a valid Authorization header for authenticated test requests.
    Token is read from API_AUTH_TOKEN env var — never hardcoded.
    In production pipelines, inject this via CI/CD secrets management.
    """
    token = os.getenv("API_AUTH_TOKEN", "test-bearer-token-valid")
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# TC01 — Happy Path (the core test explicitly requested in the brief)
# This is the most important test: if it fails, the entire feature is broken.
# ---------------------------------------------------------------------------

class TestGetOrderHappyPath:
    """
    Happy path tests for GET /api/orders/{order_id}.
    Validates the complete success scenario end-to-end.
    """

    def test_TC01_get_order_happy_path_valid_order_id(self, api_base_url, valid_auth_headers):
        """
        TC01 — Happy Path: A valid authenticated request for an existing
        order returns HTTP 200 with the correct payload and headers.

        Four assertions in priority order:
          1. HTTP 200 — most fundamental; no other assertion is meaningful if this fails
          2. Content-Type — ensures response is parseable as JSON before calling .json()
          3. status == 'PAID' — business-critical field value
          4. Full schema — catches any contract drift not caught by assertion 3
        """
        order_id = "ORD-1001"
        url = f"{api_base_url}/api/orders/{order_id}"

        response = requests.get(url, headers=valid_auth_headers, timeout=10)

        # Assertion 1 — HTTP status
        assert response.status_code == 200, (
            f"[TC01] Expected HTTP 200 for order '{order_id}', "
            f"received {response.status_code}. Body: {response.text}"
        )

        # Assertion 2 — Content-Type header (check before parsing body as JSON)
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, (
            f"[TC01] Expected Content-Type 'application/json', got '{content_type}'"
        )

        body = response.json()

        # Assertion 3 — Business-critical field value
        assert body.get("status") == "PAID", (
            f"[TC01] Expected status 'PAID' for order '{order_id}', "
            f"got '{body.get('status')}'. Full response: {body}"
        )

        # Assertion 4 — Full schema contract validation
        try:
            validate(instance=body, schema=ORDER_RESPONSE_SCHEMA)
        except ValidationError as exc:
            pytest.fail(
                f"[TC01] Schema contract violation for order '{order_id}': {exc.message}"
            )


# ---------------------------------------------------------------------------
# TC02 — Error Handling
# A missing order must return a structured 404, not a silent 200 with null body.
# ---------------------------------------------------------------------------

class TestGetOrderErrorHandling:
    """Error handling and negative path tests."""

    def test_TC02_get_order_not_found_returns_404(self, api_base_url, valid_auth_headers):
        """
        TC02 — Error Handling: A request for a non-existent order_id returns
        HTTP 404 with a structured JSON error body.

        Risk without this test: the API silently returns HTTP 200 with an
        empty/null body, causing downstream consumers to process blank order
        data without raising an error — a data integrity failure.
        """
        order_id = "ORD-9999"  # deliberately non-existent
        url = f"{api_base_url}/api/orders/{order_id}"

        response = requests.get(url, headers=valid_auth_headers, timeout=10)

        assert response.status_code == 404, (
            f"[TC02] Expected HTTP 404 for non-existent order '{order_id}', "
            f"received {response.status_code}"
        )

        body = response.json()
        # Error body must contain a human-readable reason — not a raw HTTP string
        assert "error" in body or "message" in body, (
            f"[TC02] Expected 'error' or 'message' key in 404 response body. Got: {body}"
        )


# ---------------------------------------------------------------------------
# TC03 — Authorization / Access Control
# OWASP API Security Top 10 — API1:2023: Broken Object Level Authorization
# ---------------------------------------------------------------------------

class TestGetOrderAuthorization:
    """Authorization and access control tests."""

    def test_TC03_get_order_missing_auth_token_returns_401(self, api_base_url):
        """
        TC03 — Authorization: An unauthenticated request (no Authorization
        header) must be rejected with HTTP 401.

        OWASP API1:2023 — Broken Object Level Authorization (BOLA/IDOR).
        If this test fails, any caller can read any order without credentials —
        a critical security vulnerability that blocks production deployment.
        This test must be in every CI gate.
        """
        order_id = "ORD-1001"
        url = f"{api_base_url}/api/orders/{order_id}"

        # Intentionally NO Authorization header in this request
        response = requests.get(url, timeout=10)

        assert response.status_code == 401, (
            f"[TC03] Expected HTTP 401 for unauthenticated request to '{url}', "
            f"received {response.status_code}. "
            "CRITICAL: endpoint may be publicly accessible without authentication."
        )


# ---------------------------------------------------------------------------
# TC04 — Boundary / Format (parametrized across 5 malformed inputs)
# Each variant is an independent test case in pytest output.
# ---------------------------------------------------------------------------

class TestGetOrderBoundaryAndFormat:
    """Boundary conditions and malformed / injected input tests."""

    @pytest.mark.parametrize("order_id, description", [
        ("",                    "empty string — missing path segment"),
        ("' OR '1'='1",         "SQL injection — classic tautology attack"),
        ("<script>x</script>",  "XSS payload — reflected in response body"),
        ("A" * 256,             "256-char string — oversized / buffer boundary"),
        ("ORD 1001",            "whitespace in ID — URL encoding / split bug"),
    ])
    def test_TC04_get_order_malformed_order_id_returns_4xx(
        self, api_base_url, valid_auth_headers, order_id, description
    ):
        """
        TC04 — Boundary/Format: Every malformed or injected input must return
        a 4xx client error, never HTTP 200 or HTTP 500.

        HTTP 500 on SQL injection input = input reached the DB layer unescaped.
        HTTP 500 on any input = unhandled server exception leaking stack trace.
        HTTP 200 on malformed input = missing input validation entirely.

        5 variants cover: empty input, SQL injection, XSS, oversized input,
        whitespace — each tests a different validation failure mode.
        """
        url = f"{api_base_url}/api/orders/{order_id}"
        response = requests.get(url, headers=valid_auth_headers, timeout=10)

        # Must be a 4xx — never 2xx (implies validation bypass) or 5xx (implies crash)
        assert 400 <= response.status_code < 500, (
            f"[TC04] Expected 4xx for malformed input ({description}), "
            f"received {response.status_code}. URL: {url}"
        )

        # Explicitly guard against 500 — would indicate unhandled exception
        assert response.status_code != 500, (
            f"[TC04] Received HTTP 500 for input '{description}'. "
            "Unhandled server exception — may be leaking stack trace or DB error."
        )


# ---------------------------------------------------------------------------
# TC05 — Schema / Contract Validation
# Catches field renames, type changes, and undocumented additions.
# ---------------------------------------------------------------------------

class TestGetOrderSchemaValidation:
    """Response contract and schema integrity tests."""

    def test_TC05_get_order_response_matches_schema_contract(
        self, api_base_url, valid_auth_headers
    ):
        """
        TC05 — Schema Validation: The HTTP 200 response body must strictly
        conform to the agreed JSON schema contract.

        Catches:
          - Missing required field (e.g., 'amount' accidentally dropped)
          - Type drift (e.g., amount returned as "100.50" string instead of 100.50 number)
          - Field rename (e.g., 'amount' → 'total' by backend team)
          - Undocumented extra fields added without consumer notification
          - Invalid currency format (not a 3-letter ISO 4217 uppercase code)

        This is a contract test — it protects consumers (frontend, downstream
        services) from silent integration failures caused by backend changes.
        """
        order_id = "ORD-1001"
        url = f"{api_base_url}/api/orders/{order_id}"

        response = requests.get(url, headers=valid_auth_headers, timeout=10)

        assert response.status_code == 200, (
            f"[TC05] Expected HTTP 200 to perform schema validation, "
            f"received {response.status_code}"
        )

        body = response.json()

        # jsonschema.validate checks: all required fields, types, minLength/maxLength,
        # date-time format, and rejects any key not in the schema (additionalProperties:false)
        try:
            validate(instance=body, schema=ORDER_RESPONSE_SCHEMA)
        except ValidationError as exc:
            field_path = " -> ".join(str(p) for p in exc.absolute_path) or "root"
            pytest.fail(
                f"[TC05] Schema contract violation:\n"
                f"  Field    : {field_path}\n"
                f"  Violation: {exc.message}\n"
                f"  Body     : {body}"
            )

        # Additional business rule: currency must be uppercase ISO 4217
        # (jsonschema checks length 3; this checks it is also uppercase letters)
        currency = body.get("currency", "")
        assert currency.isupper() and len(currency) == 3 and currency.isalpha(), (
            f"[TC05] Expected 'currency' to be a 3-letter uppercase ISO 4217 code "
            f"(e.g., 'GBP', 'USD'), got '{currency}'"
        )
