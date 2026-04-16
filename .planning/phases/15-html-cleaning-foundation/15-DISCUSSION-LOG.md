# Phase 15: HTML Cleaning Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-16
**Phase:** 15-html-cleaning-foundation
**Areas discussed:** Integration, Tag Whitelist, Scope, Cleaning Timing, Markdown Handling

---

## Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone utility function | Create clean_html() utility in ai_service.py, called after each generate function | ✓ |
| Inline in each generate function | Add cleaning logic directly inside generate functions | |
| In the worker pipeline only | Clean HTML only at the worker level after all AI calls complete | |

**User's choice:** Standalone utility function (Recommended)
**Notes:** Keeps cleaning logic separate and testable.

---

## Tag Whitelist

| Option | Description | Selected |
|--------|-------------|----------|
| Requirements-defined set | h1-h6, p, strong, em, ul, ol, li, a, img — as specified in HTML-03 | ✓ |
| WordPress Extended set | Add blockquote, table, code, pre, br, span, div | |
| Minimal set only | Just p, h2-h4, strong, em, ul, ol, li, a | |

**User's choice:** Requirements-defined set (Recommended)
**Notes:** Keeps content focused and WordPress-safe.

---

## Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Final content only | Clean only generate output, not research/outline | ✓ |
| All AI outputs | Also clean research_data and outline HTML fields | |

**User's choice:** Final content only (Recommended)
**Notes:** Research and outline are internal JSON, not displayed in WordPress.

---

## Cleaning Timing

| Option | Description | Selected |
|--------|-------------|----------|
| After each AI call | Clean right after each AI call returns inside generate functions | ✓ |
| After full assembly | Clean once at the end of generate_full_content | |

**User's choice:** After each AI call (Recommended)
**Notes:** Dirty intermediate data never stored.

---

## Markdown Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Code block wrappers + backticks | Remove ```html...``` and ```...``` wrappers, strip remaining backticks | ✓ |
| Full markdown stripping | Also strip **bold**, *italic*, # headers, [links](...) | |

**User's choice:** Code block wrappers + backticks (Recommended)
**Notes:** Covers the main issue from requirements without over-stripping.

---

## Agent's Discretion

- Error handling for malformed HTML (log warning, return cleaned attempt)
- Whether to strip attributes from allowed tags
- Unit test structure and test data approach

## Deferred Ideas

None — discussion stayed within phase scope.
