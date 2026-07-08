# API Reference

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs`

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## Auth

### POST /auth/login
```json
{ "email": "john.smith@email.com", "password": "password123" }
```
Response:
```json
{ "access_token": "...", "token_type": "bearer", "customer_id": 2, "is_admin": false, "full_name": "John Smith" }
```

### POST /auth/register
```json
{ "email": "new@email.com", "password": "pass123", "full_name": "New User", "age": 30 }
```

---

## Customers

### GET /customers/me
Returns current customer profile.

### PUT /customers/me
```json
{ "full_name": "Updated Name", "phone": "+1-555-9999" }
```

### GET /customers/ *(admin)*
Returns all customers.

---

## Policies

### GET /policies/
Returns all policies for current customer.

### GET /policies/{id}
Returns single policy details.

### GET /policies/{id}/claims
Returns claims for a policy.

---

## Renewals

### GET /renewals/
Returns all renewals for current customer.

### POST /renewals/recommend/{policy_id}
Triggers AI renewal recommendation. Returns a `Renewal` object with:
- `recommendation_score` — renewal probability (0-1)
- `ai_recommendation` — personalized message
- `new_premium` — recommended premium
- `recommendation_reason` — key reasons

### POST /renewals/{renewal_id}/confirm
Confirms and completes a renewal. Updates policy status to `renewed`.

### POST /renewals/{renewal_id}/decline
Declines a pending renewal.

---

## Chat

### POST /chat/
```json
{ "message": "What does my health insurance cover?", "session_id": "optional-uuid" }
```
Response:
```json
{
  "response": "Your health insurance covers...",
  "intent": "ask_question",
  "session_id": "uuid",
  "sources": ["Health Insurance Policy"]
}
```

---

## Notifications

### GET /notifications/
Returns all notifications (latest 50).

### GET /notifications/unread-count
Returns `{ "count": 3 }`.

### PUT /notifications/{id}/read
Marks a notification as read.

### PUT /notifications/read-all
Marks all notifications as read.

---

## Knowledge *(admin)*

### POST /knowledge/upload-pdf
Multipart form upload of a PDF file. Ingests into ChromaDB RAG.

### POST /knowledge/upload-text
```
?text=<policy text>&source=<source name>
```

---

## Admin *(admin only)*

### GET /admin/stats
Returns `AdminStats` with counts and renewal rate.

### GET /admin/customers
All customers.

### GET /admin/policies
All policies.

### GET /admin/renewals
All renewals ordered by date.

---

## Health

### GET /health
```json
{ "status": "ok", "service": "Policy Renewal Agent" }
```
