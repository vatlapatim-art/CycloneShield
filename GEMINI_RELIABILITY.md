# Gemini reliability and setup

CycloneShield keeps Gemini credentials server-side in `backend/.env`.

Example:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-3.7-flash
GEMINI_RETRY_MODELS=gemini-3.6-flash,gemini-3.5-flash-lite
```

The AI brief endpoint uses the `x-goog-api-key` header. Transient 408, 429 and 5xx responses are retried up to two times per model with bounded exponential backoff. A `Retry-After` response header is honored when provided. The configured primary model, fallback model and optional retry models are tried in order before the application returns its local evidence-based fallback.

A local fallback is intentionally retained so the dashboard can still operate when Gemini is rate-limited or unavailable.

Never commit or expose `backend/.env` or `GEMINI_API_KEY` in the frontend.
