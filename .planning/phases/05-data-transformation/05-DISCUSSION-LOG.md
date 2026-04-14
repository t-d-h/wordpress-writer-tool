# Phase 5: Data Transformation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14
**Phase:** 05-data-transformation
**Areas discussed:** Transformation location, Date format

---

## Transformation Location

| Option | Description | Selected |
|--------|-------------|----------|
| Backend service layer | Backend service layer transforms data before sending to frontend. Aligns with Phase 4 decision D-19. Frontend becomes simpler, just displays what backend sends. | ✓ |
| Frontend only | Frontend continues to transform data as it does now. Backend sends raw WordPress REST API response. Simpler backend, more logic in frontend. | |
| Hybrid | Hybrid approach - backend does basic transformation (extract categories/tags), frontend does formatting (dates, edit URLs). Shared responsibility. | |

**User's choice:** Backend service layer
**Notes:** User chose backend service layer to align with Phase 4 decision D-19 that backend should return properly transformed data.

---

## Date Format

| Option | Description | Selected |
|--------|-------------|----------|
| Browser locale (toLocaleDateString) | Use browser's locale (e.g., "April 14, 2026" in US, "14 April 2026" in UK). User-friendly, adapts to user's location. | |
| Fixed format | Use fixed format like "YYYY-MM-DD" or "MMMM DD, YYYY". Consistent across all users, no locale variations. | |
| Relative time | Use relative time (e.g., "2 hours ago", "yesterday"). More user-friendly but requires updates. | |

**User's choice:** Fixed format
**Notes:** User chose fixed format for consistency across all users.

---

## Fixed Date Format

| Option | Description | Selected |
|--------|-------------|----------|
| MMMM DD, YYYY | Month name, day, year (e.g., "April 14, 2026"). Readable, common in US. | |
| DD MMMM YYYY | Day, month name, year (e.g., "14 April 2026"). Readable, common internationally. | ✓ |
| YYYY-MM-DD | Year-month-day (e.g., "2026-04-14"). Sortable, machine-friendly, less human-readable. | |

**User's choice:** DD MMMM YYYY
**Notes:** User chose DD MMMM YYYY format for international readability.

---

## the agent's Discretion

Areas where user said "you decide" or deferred to the agent:
- Exact implementation location (wp_service.py vs new transformation service)
- Whether to create helper functions or inline transformation
- How to handle edge cases (empty arrays, null values, invalid dates)
- Whether to add logging for transformation steps
- Whether to validate WordPress site URL before generating edit URLs

## Deferred Ideas

None — discussion stayed within phase scope
