# Phase 1: Token Usage Display - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14T10:44:00+07:00
**Phase:** 01-token-usage-display
**Areas discussed:** Visual Presentation, Information Hierarchy, Data Format, Loading State, Error Handling, Performance, Data Query
**Mode:** Auto (YOLO) - All decisions auto-selected

---

## Visual Presentation

| Option | Description | Selected |
|--------|-------------|----------|
| Card-based layout (reuses existing stat-card CSS) | Consistent with existing design, minimal new CSS | ✓ |
| Table layout | More structured, but requires new CSS pattern | |
| List layout | Simpler, but less visual hierarchy | |

**User's choice:** Card-based layout (reuses existing stat-card CSS) - Auto-selected (recommended default)
**Notes:** Matches existing `.stat-card` class and `.stats-grid` container pattern from ProjectDetail.jsx

---

## Information Hierarchy

| Option | Description | Selected |
|--------|-------------|----------|
| Total tokens prominent, breakdown below | Clear visual hierarchy, users see totals first | ✓ |
| Breakdown prominent, totals below | More detail-focused, but totals less visible | |
| Equal prominence | Balanced, but less clear hierarchy | |

**User's choice:** Total tokens prominent, breakdown below - Auto-selected (recommended default)
**Notes:** Primary display shows total input/output tokens, secondary shows breakdown by type

---

## Data Format

| Option | Description | Selected |
|--------|-------------|----------|
| Numbers with commas, "tokens" label | Readable, clear units (e.g., "15,432 tokens") | ✓ |
| Numbers only (no formatting) | Simple, but harder to read large numbers | |
| Abbreviated (15.4K) | Compact, but less precise for cost tracking | |

**User's choice:** Numbers with commas, "tokens" label - Auto-selected (recommended default)
**Notes:** Full precision important for cost tracking, no abbreviations

---

## Loading State

| Option | Description | Selected |
|--------|-------------|----------|
| Loading spinner + skeleton | Clear feedback, matches existing pattern | ✓ |
| Loading spinner only | Simple, but less context | |
| Text only ("Loading...") | Minimal, but less visual feedback | |

**User's choice:** Loading spinner + skeleton - Auto-selected (recommended default)
**Notes:** Matches existing loading pattern in ProjectDetail.jsx

---

## Error Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Error message + "N/A" fallback | User-friendly, graceful degradation | ✓ |
| Error message only | Clear, but shows broken state | |
| Silent failure | Poor UX, users don't know something's wrong | |

**User's choice:** Error message + "N/A" fallback - Auto-selected (recommended default)
**Notes:** Console logging for debugging, user sees helpful error message

---

## Performance

| Option | Description | Selected |
|--------|-------------|----------|
| MongoDB aggregation + indexes | Standard approach, well-documented | ✓ |
| Pre-computed totals | Faster reads, but requires cache invalidation | |
| Client-side aggregation | Simpler backend, but poor performance with large datasets | |

**User's choice:** MongoDB aggregation + indexes - Auto-selected (recommended default)
**Notes:** On-the-fly calculation for MVP, indexes for optimization

---

## Data Query

| Option | Description | Selected |
|--------|-------------|----------|
| All posts (no status filter) | Includes deleted posts as required | ✓ |
| Active posts only | Excludes deleted, violates requirement | |
| Published posts only | Too restrictive, misses draft costs | |

**User's choice:** All posts (no status filter) - Auto-selected (required by specification)
**Notes:** Requirement TOKEN-05 explicitly requires including deleted posts

---

## the agent's Discretion

- **Visual styling**: Match existing stat-card design (colors, spacing, typography)
- **Placement**: Above existing stats-grid in general tab
- **Zero values**: Show or hide at agent's discretion

## Deferred Ideas

None — discussion stayed within phase scope
