# d_task_manage_svc

## Overview

d_task_manage_svc is a task management service that provides RESTful APIs for task management operations. This service now integrates with an external authentication system to ensure that all API requests are securely validated using session tokens.

## Authentication Integration

### Purpose
All API requests now require a valid 'session_token' in the request header. This token is used to authenticate the request before processing.

### Middleware Details
The authentication middleware, defined in `src/d_task_manage_svc/middleware/auth.py`, intercepts every incoming request. Its responsibilities include:

- Extracting the `session_token` from the request headers.
- Sending an asynchronous HTTP request to the demo-backend endpoint using `httpx` to validate the token.
- Returning a **401 Unauthorized** response if the token is missing, invalid, or expired.
- Returning a **500 Internal Server Error** if an exception occurs during token validation.

### Configuration Instructions
To configure the authentication integration:

- Set the `DEMO_BACKEND_URL` environment variable to point to your demo-backend authentication endpoint (for example, `http://demo-backend`).
- This configuration is managed in the `src/d_task_manage_svc/config.py` file.

### Error Responses
- **401 Unauthorized:** Returned when the `session_token` header is missing or the token is invalid/expired.
- **500 Internal Server Error:** Returned when an unexpected error occurs during token validation.

### Dependency
This integration introduces a dependency on `httpx` for asynchronous HTTP calls.

### Example Usage
When making an API request, include the `session_token` in the request header as shown below:

```
curl -H "session_token: your_valid_token" http://localhost:8000/your_api_endpoint
```

## Additional Information
Ensure that your environment is properly configured with the necessary environment variables and dependencies for the authentication integration to work correctly.
