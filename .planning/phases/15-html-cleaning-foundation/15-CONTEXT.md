# Phase 15: HTML Cleaning Foundation - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove markdown artifacts and sanitize AI-generated HTML content so it's WordPress-ready without manual cleanup. Three requirements: HTML-01 (clean output), HTML-02 (no markdown artifacts), HTML-03 (HTML sanitization).

This phase handles FINAL CONTENT ONLY — research_data and outline are internal JSON, not displayed in WordPress.

</domain>

<decisions>
## Implementation Decisions

### HTML Cleaning Architecture
- **D-01:** Standalone utility function — create `clean_html()` in `ai_service.py`, called after each AI content generation call. Keeps cleaning logic separate, reusable, and independently testable.

### Allowed HTML Tags Whitelist
- **D-02:** Requirements-defined set — `h1, h2, h3, h4, h5, h6, p, strong, em, ul, ol, li, a, img`. Matches HTML-03. All other tags stripped.

### Cleaning Scope
- **D-03:** Final content only — apply cleaning to `generate_full_content()`, `generate_section_content()`, `generate_introduction()` output. Do NOT clean research_data or outline JSON (internal pipeline data, not displayed).

### Cleaning Timing
- **D-04:** After each AI call — clean right after `_call_ai()` returns inside each generate function. Dirty intermediate data never stored.

### Markdown Artifact Handling
- **D-05:** Code block wrappers + backticks — remove ` ```html ... ``` `, ` ``` ... ``` ` wrappers, then strip remaining backticks. Do NOT strip other markdown syntax (bold, italic, headers, links).

### the agent's Discretion
- Error handling for malformed HTML that can't be parsed (log warning, return cleaned attempt)
- Whether to strip attributes from allowed tags (e.g., remove `style` attrs, keep `href` on `<a>`)
- Unit test structure and test data approach

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §HTML-01, HTML-02, HTML-03 — acceptance criteria for HTML cleaning

### Codebase
- `backend/app/services/ai_service.py` — target file: `generate_full_content()` (line 402), `generate_section_content()` (line 314), `generate_introduction()` (line 361), `research_topic()` (line 195, has partial markdown stripping pattern)
- `backend/app/workers/tasks.py` — pipeline orchestration, where jobs are dispatched
- `.planning/codebase/CONVENTIONS.md` — naming patterns, import order, error handling
- `.planning/codebase/STACK.md` — dependency management (pip requirements.txt)

### Dependencies
- `requirements.txt` — need to add: `beautifulsoup4>=4.12.0`, `lxml>=5.0.0`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `research_topic()` (ai_service.py:195) — already has markdown code block stripping pattern (`if "```json" in text`), can reference this pattern for HTML cleaning
- `_call_ai()` — returns `(text, total_tokens)`, text is raw AI output that needs cleaning

### Established Patterns
- Functions return `tuple[str, int]` for content + tokens
- Services use `raise Exception("...")` for errors, routers use `HTTPException`
- No custom exception classes — use built-in FastAPI exceptions
- Private functions prefixed with underscore: `_call_ai()`, `_get_*_key()`

### Integration Points
- `generate_full_content()` calls `generate_introduction()` and `generate_section_content()` — cleaning happens inside each
- Worker tasks dispatch to ai_service functions — no changes needed in worker layer
- Post model has `research_data: Optional[Dict]` — no changes needed (not cleaning research output)

</code_context>

<specifics>
## Specific Ideas

No specific references — open to standard approaches for HTML sanitization with BeautifulSoup4 + lxml.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 15-html-cleaning-foundation*
*Context gathered: 2026-04-16*
