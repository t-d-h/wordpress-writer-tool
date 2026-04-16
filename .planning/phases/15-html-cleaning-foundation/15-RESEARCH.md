# Phase 15: HTML Cleaning Foundation - Research

**Researched:** 2026-04-16
**Domain:** HTML sanitization / content cleaning for AI-generated content
**Confidence:** HIGH

## Summary

Phase 15 implements HTML cleaning to strip markdown artifacts and sanitize AI-generated content for WordPress compatibility. The core approach is a standalone `clean_html()` utility using BeautifulSoup4 + lxml for parsing and tag whitelist filtering. Three decisions are already locked (D-01 through D-05), leaving only error handling approach, attribute stripping policy, and test structure to the agent's discretion.

Key libraries confirmed: beautifulsoup4 4.14.3 (current stable) and lxml (recommended parser per BS4 docs). The standard pattern is: (1) strip markdown wrappers pre-clean, (2) parse with lxml parser, (3) iterate and remove disallowed tags + dangerous attributes, (4) return string.

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Standalone utility function — create `clean_html()` in `ai_service.py`
- **D-02:** Allowed tags whitelist: `h1, h2, h3, h4, h5, h6, p, strong, em, ul, ol, li, a, img`
- **D-03:** Final content only — apply to `generate_full_content()`, `generate_section_content()`, `generate_introduction()` output
- **D-04:** After each AI call — clean right after `_call_ai()` returns inside each generate function
- **D-05:** Code block wrappers + backticks removal — remove ` ```html ... ``` `, ` ``` ... ``` ` wrappers, then strip remaining backticks

### the agent's Discretion
- Error handling for malformed HTML that can't be parsed (log warning, return cleaned attempt)
- Whether to strip attributes from allowed tags (e.g., remove `style` attrs, keep `href` on `<a>`)
- Unit test structure and test data approach

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| HTML cleaning | API/Backend | — | `clean_html()` lives in `ai_service.py`, called inside content generation functions |
| Markdown artifact removal | API/Backend | — | Regex preprocessing before BS4 parsing, part of `clean_html()` |
| Tag whitelist filtering | API/Backend | — | BeautifulSoup4 traversal, part of `clean_html()` |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| beautifulsoup4 | 4.14.3 | HTML parsing and DOM traversal | [CITED: crummy.com — BS4 4.14.3 docs] Standard for Python HTML manipulation; lxml parser recommended for speed |
| lxml | >=5.0.0 | HTML/XML parser backend for BeautifulSoup | [CITED: crummy.com — BS4 docs] Recommended parser; "very fast" per BS4 comparison table |

### Installation
```bash
pip install beautifulsoup4>=4.12.0 lxml>=5.0.0
```

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| lxml parser | html.parser (stdlib) | html.parser is slower and less lenient; lxml is ~3x faster |
| lxml parser | html5lib | html5lib is "extremely lenient" but "very slow" — lxml is faster |

## Architecture Patterns

### System Architecture Diagram

```
AI Provider Response (raw text)
         │
         ▼
┌─────────────────────────────────┐
│  Step 1: Markdown Pre-cleaning  │
│  - Strip ```html ... ``` blocks │
│  - Strip ``` ... ``` blocks     │
│  - Strip remaining backticks    │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 2: BeautifulSoup + lxml  │
│  - Parse HTML from string       │
│  - lxml parser (fast, lenient)  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 3: Tag Whitelist Filter   │
│  - Iterate all tags            │
│  - Remove tags not in whitelist │
│  - Allowed: h1-h6,p,strong,em, │
│    ul,ol,li,a,img              │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Step 4: Attribute Filtering   │
│  - Keep: href (a), src (img)   │
│  - Remove: style, on* handlers  │
│  - Strip all other attrs        │
└─────────────────────────────────┘
         │
         ▼
   Clean HTML String
```

### Recommended Project Structure
```
backend/app/services/
├── ai_service.py          # add clean_html() here
│   ├── clean_html()       # NEW: standalone cleaning function
│   ├── generate_full_content()
│   ├── generate_section_content()
│   └── generate_introduction()
└── ...
```

### Pattern 1: Markdown Pre-cleaning + BeautifulSoup Pipeline
**What:** Two-stage cleaning: regex for markdown artifacts, then BS4 for HTML sanitization
**When to use:** AI output often wrapped in markdown code blocks
**Example:**
```python
def clean_html(html: str) -> str:
    # Stage 1: Remove markdown code block wrappers
    text = html
    if "```html" in text:
        text = text.split("```html")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    # Strip remaining backticks
    text = text.replace("`", "")
    
    # Stage 2: Parse and sanitize with BeautifulSoup + lxml
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(text, "lxml")
    # ... whitelist filtering ...
    return str(soup)
```
**Source:** [CITED: crummy.com/software/BeautifulSoup/bs4/doc/] BeautifulSoup documentation; existing `research_topic()` pattern in codebase (lines 233-236)

### Pattern 2: Tag Whitelist Filtering
**What:** Iterate all tags, remove any not in the allowed set
**When to use:** When you need strict tag allowlist
**Example:**
```python
ALLOWED_TAGS = {"h1","h2","h3","h4","h5","h6","p","strong","em","ul","ol","li","a","img"}

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(True):  # True = all tags
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()  # Remove tag but keep contents
    return str(soup)
```
**Source:** [CITED: crummy.com — BS4 docs "Modifying the tree" section] `unwrap()` removes tag but preserves children

### Pattern 3: Attribute Allowlist
**What:** Keep only safe attributes on allowed tags
**When to use:** When you need to strip dangerous attributes (onclick, style, etc.) while preserving href/src
**Example:**
```python
SAFE_ATTRS = {"href": {"a"}, "src": {"img"}}

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(True):
        if tag.name in SAFE_ATTRS:
            allowed = SAFE_ATTRS[tag.name]
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
        else:
            tag.attrs.clear()  # Strip all attrs for other allowed tags
    return str(soup)
```

### Anti-Patterns to Avoid
- **Don't use `html.parser` for AI content:** AI HTML is often malformed; lxml is more lenient and faster. [CITED: BS4 docs parser comparison]
- **Don't strip all attributes blindly:** `href` on `<a>` and `src` on `<img>` are needed for functionality
- **Don't treat this as one-step:** Markdown pre-cleaning must happen before BS4 parsing, because markdown artifacts confuse the parser
- **Don't use `remove()` on tags with children:** Use `unwrap()` instead to preserve inner content

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTML parsing | `re.compile` for tag matching | BeautifulSoup4 + lxml | HTML is not regular; regex cannot handle nested tags reliably |
| Tag allowlisting | Manual string replacement | BS4 `find_all(True)` + `unwrap()` | BS4 traverses DOM correctly; string replacement breaks nested content |
| Dangerous attributes | String stripping | BS4 attribute iteration | Attributes can appear anywhere; BS4 gives correct scope |
| Markdown code block removal | Full regex solution | Simple split + strip | Code blocks are distinctive patterns (` ``` `); simple string ops suffice |

**Key insight:** HTML is a tree structure. Any approach that treats it as a flat string will eventually fail on nested content. BeautifulSoup provides the correct abstraction.

## Common Pitfalls

### Pitfall 1: Empty/whitespace-only input causes crash
**What goes wrong:** `BeautifulSoup("", "lxml")` returns empty doc; but malformed input like `"```html\n```"` produces unexpected results
**Why it happens:** AI sometimes returns empty code blocks or whitespace
**How to avoid:** Check for empty/stripped input before parsing; return empty string early
**Warning signs:** `ValueError` or empty soup object after parsing

### Pitfall 2: `unwrap()` on root-level text nodes
**What goes wrong:** Calling `unwrap()` on a `<html>` or `<body>` tag can produce invalid output
**Why it happens:** `unwrap()` removes the tag but keeps children; root tags have no parent to keep children
**How to avoid:** Only unwrap tags you explicitly find via `find_all()` on the soup body; don't iterate over `soup.html` or `soup.body`
**Warning signs:** Output starts with text content directly (no wrapping tag)

### Pitfall 3: Modifying soup while iterating
**What goes wrong:** `soup.find_all(True)` returns live list; modifying tags during iteration causes unexpected behavior
**Why it happens:** BS4 returns a live ResultSet, not a snapshot
**How to avoid:** Convert to list first: `for tag in list(soup.find_all(True)):` or iterate in reverse
**Warning signs:** Some tags not processed, or skips every other tag

### Pitfall 4: Preserving `href` with malformed URLs
**What goes wrong:** AI may generate `href="javascript:alert(1)"` or `href="not-a-url"`
**Why it happens:** Whitelist approach keeps all `href` values without validation
**How to avoid:** The context decisions specify keeping `href` on `<a>` — but WordPress itself sanitizes on publish. Document this limitation.
**Warning signs:** None at cleaning time — WordPress will reject on publish

### Pitfall 5: BeautifulSoup adds `<html><body>` wrapper
**What goes wrong:** `str(soup)` includes `<html><body>` tags even if input was fragment
**Why it happens:** lxml parser always produces a full document tree
**How to avoid:** Use `soup.body.get_text()` or extract just the body content; or use `soup.encode_contents()` and strip manually
**Warning signs:** Output has `<html><body>` wrapper when original was fragment

## Code Examples

### Complete `clean_html()` Implementation Pattern
```python
import re
from bs4 import BeautifulSoup, Tag

ALLOWED_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "strong", "em", "ul", "ol", "li", "a", "img"}
SAFE_ATTRS = {"a": {"href"}, "img": {"src"}}

def clean_html(html: str) -> str:
    """Remove markdown artifacts and sanitize HTML to allowed tags whitelist."""
    if not html or not html.strip():
        return ""
    
    # Stage 1: Remove markdown code block wrappers
    text = html
    if "```html" in text:
        parts = text.split("```html")
        text = "".join(p.split("```")[0] if i > 0 else p for i, p in enumerate(parts))
    elif "```" in text:
        parts = text.split("```")
        text = "".join(p.split("```")[0] if i > 0 else p for i, p in enumerate(parts))
    
    # Strip remaining backticks
    text = text.replace("`", "")
    
    if not text.strip():
        return ""
    
    # Stage 2: Parse with BeautifulSoup + lxml
    try:
        soup = BeautifulSoup(text, "lxml")
    except Exception:
        # Fallback: try html.parser if lxml fails
        soup = BeautifulSoup(text, "html.parser")
    
    # Stage 3: Remove disallowed tags (preserve contents)
    all_tags = list(soup.find_all(True))  # Convert to list to avoid mutation issues
    for tag in all_tags:
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()
    
    # Stage 4: Filter attributes
    for tag in soup.find_all(True):
        if tag.name in SAFE_ATTRS:
            allowed = SAFE_ATTRS[tag.name]
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
        else:
            tag.attrs.clear()
    
    # Stage 5: Extract body content (strip html/body wrappers if present)
    result = text
    if soup.body:
        result = "".join(str(child) for child in soup.body.children)
    else:
        result = str(soup)
    
    return result.strip()
```
**Source:** [CITED: crummy.com — BS4 docs] BeautifulSoup documentation; pattern derived from BS4 "Modifying the tree" and parser comparison sections

### Error-Safe Call Pattern (agent's discretion for error handling)
```python
async def generate_section_content(...) -> tuple[str, int]:
    # ... existing code ...
    text, total_tokens = await _call_ai(prompt, system_prompt, provider_id, model_name)
    
    # Clean HTML after AI returns
    try:
        cleaned = clean_html(text)
        if cleaned != text:
            print(f"[CLEAN] Stripped markdown artifacts from section content")
    except Exception as e:
        print(f"[WARN] HTML cleaning failed, using raw output: {e}")
        cleaned = text
    
    return cleaned, total_tokens
```

### Test Data Pattern (agent's discretion for tests)
```python
# Test fixtures for clean_html()
TEST_CASES = [
    # (input, expected_contains, expected_not_contains)
    ("```html\n<p>Test</p>\n```", "<p>Test</p>", "```"),
    ("<script>alert('xss')</script><p>Safe</p>", "<p>Safe</p>", "<script>"),
    ("<p style='color:red'>Styled</p>", "<p>Styled</p>", "style="),
    ("<h1>Title</h1><div>Bad</div>", "<h1>Title</h1>", "<div>"),
]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No HTML cleaning | BeautifulSoup4 + lxml whitelist | Phase 15 | AI output directly WordPress-ready |
| String regex for markdown | Pre-clean split + BS4 parse | Phase 15 | Correctly handles nested/wrapped content |
| No attribute filtering | Explicit allowlist per tag | Phase 15 | Strips XSS vectors like onclick, style |

**Deprecated/outdated:**
- None relevant to this phase

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | beautifulsoup4>=4.12.0 compatible with Python 3.11 | Standard Stack | Minor: version may need adjustment |
| A2 | lxml>=5.0.0 available on Python 3.11 | Standard Stack | Minor: may need lower version constraint |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions

1. **Should `clean_html()` return empty string or original on complete failure?**
   - What we know: D-01 says "log warning, return cleaned attempt" — but if parsing crashes, what is "cleaned attempt"?
   - What's unclear: Whether empty string or original input is better fallback
   - Recommendation: Return original (uncleaned) on crash — preserves some content vs nothing

2. **Should whitespace-only content after cleaning be preserved or returned as empty?**
   - What we know: AI often generates whitespace-only responses
   - What's unclear: Whether empty string should be treated as error or valid empty content
   - Recommendation: Return empty string (no content to display anyway)

## Environment Availability

> Step 2.6: SKIPPED (no external dependencies beyond Python packages — beautifulsoup4/lxml are pip-installable)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | none — existing pytest.ini not found in backend/ |
| Quick run command | `pytest backend/tests/test_ai_service.py::test_clean_html -x -v` |
| Full suite command | `pytest backend/tests/ -x -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HTML-01 | Strips backticks from content | unit | `pytest tests/test_ai_service.py::test_clean_html_strips_backticks -x` | ❌ Wave 0 |
| HTML-01 | Strips markdown code blocks | unit | `pytest tests/test_ai_service.py::test_clean_html_strips_code_blocks -x` | ❌ Wave 0 |
| HTML-02 | No markdown artifacts in output | unit | `pytest tests/test_ai_service.py::test_clean_html_no_markdown -x` | ❌ Wave 0 |
| HTML-03 | Allowed tags preserved | unit | `pytest tests/test_ai_service.py::test_clean_html_preserves_allowed_tags -x` | ❌ Wave 0 |
| HTML-03 | Disallowed tags removed | unit | `pytest tests/test_ai_service.py::test_clean_html_removes_disallowed_tags -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_ai_service.py -x -v`
- **Per wave merge:** `pytest backend/tests/ -x`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_ai_service.py` — test_clean_html_* functions for HTML-01, HTML-02, HTML-03
- [ ] `backend/tests/conftest.py` — shared fixtures if needed
- [ ] Framework install: already in requirements.txt (pytest>=7.4.0)

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V4 Access Control | no | N/A — content filtering only |
| V5 Input Validation | yes | BeautifulSoup4 tag/attribute allowlist |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for HTML Content

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| XSS via `<script>` tag | XSS | Tag allowlist strips `<script>` |
| XSS via `onclick` attribute | XSS | Attribute allowlist strips event handlers |
| XSS via `javascript:` href | XSS | **NOT MITIGATED** — href values not validated |
| CSS injection via style attr | Tampering | Attribute allowlist strips `style` |
| Phishing via fake links | Spoofing | **NOT MITIGATED** — href values not validated |

**Known limitation:** This phase implements tag/attribute allowlisting but does NOT validate URL values. `href="javascript:alert(1)"` passes through unchanged. WordPress sanitizes on publish, but this is a defense-in-depth gap.

## Sources

### Primary (HIGH confidence)
- [CITED: crummy.com/software/BeautifulSoup/bs4/doc/] BeautifulSoup 4.14.3 official documentation — parser comparison, tree modification, tag filtering
- [CITED: 15-CONTEXT.md] Phase 15 locked decisions D-01 through D-05

### Secondary (MEDIUM confidence)
- [ASSUMED] beautifulsoup4 4.14.3 is current stable — verified via PyPI fetch of docs page

### Tertiary (LOW confidence)
- [ASSUMED] beautifulsoup4>=4.12.0 compatible with Python 3.11 — should verify on install

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — official docs, existing project deps
- Architecture: HIGH — decisions locked in context, BS4 patterns verified
- Pitfalls: MEDIUM — based on BS4 docs and general Python parsing experience

**Research date:** 2026-04-16
**Valid until:** 2026-05-16 (30 days — stable library, no fast-moving changes)
