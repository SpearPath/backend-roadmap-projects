# REST & Database Standards

## 1. REST API Conventions
- Use standard HTTP methods:
  - `GET` : Read resource(s) (Idempotent, Safe)
  - `POST` : Create new resource
  - `PUT` / `PATCH` : Update entire resource or partial fields
  - `DELETE` : Remove resource (Idempotent)
- Plural resource nouns (e.g., `/tasks`, `/expenses`).
- Appropriate HTTP status codes:
  - `200 OK`, `201 Created`, `204 No Content`
  - `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`
  - `500 Internal Server Error`

## 2. Database & Data Modeling Rules
- Always use auto-incrementing integer or UUID primary keys.
- Store timestamps in UTC ISO-8601 format (`YYYY-MM-DDTHH:MM:SSZ`).
- Never store raw secrets or passwords in the database (use argon2 / bcrypt hashing).
- Use transactions when performing multi-step writes that must remain atomic.
