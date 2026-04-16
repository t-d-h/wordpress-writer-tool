# Technology Stack

**Project:** WordPress Writer Tool - v1.3 Content Quality Improvements
**Researched:** 2026-04-16
**Confidence:** HIGH

## Executive Summary

**Three new libraries required** for content quality improvements. The existing AI pipeline generates content but lacks validation and cleaning. The additions needed are:

1. **lxml 6.0.4** - HTML sanitization and cleaning (replaces deprecated bleach)
2. **BeautifulSoup4 4.14.3** - HTML parsing and text extraction
3. **textstat 0.7.13** - Word count validation and text analysis

These libraries will enable:
- Removal of unwanted characters (backticks, markdown artifacts)
- HTML sanitization and validation
- Word count validation against targets
- Section count validation against targets
- Content quality checks before saving

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **lxml** | 6.0.4 | HTML sanitization and cleaning | Production-stable, actively maintained (Apr 2026), BSD-3-Clause license. Provides robust HTML cleaning via `html-clean` extra. Alternative to deprecated bleach. |
| **BeautifulSoup4** | 4.14.3 | HTML parsing and manipulation | Production-stable (Nov 2025), MIT license. Excellent for parsing HTML, extracting text, removing unwanted characters, and fixing malformed HTML. |
| **textstat** | 0.7.13 | Text analysis and word counting | Production-stable (Feb 2026), MIT license. Provides accurate word counting, readability analysis, and text statistics for validating content quality. |

### Existing Stack (No Changes)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python 3.11 | 3.11-slim | Backend runtime | Existing stack, no changes needed |
| FastAPI 0.115.0 | 0.115.0 | Backend REST API framework | Existing stack, no changes needed |
| React 18.3 | 18.3 | Frontend UI framework | Existing stack, no changes needed |
| MongoDB | 7.x | Post storage | Existing stack, no changes needed |
| Redis | 7.x | Job queue | Existing stack, no changes needed |
| OpenAI GPT-4o | >=1.60.0 | Content generation | Existing stack, no changes needed |
| Gemini 2.0 Flash | 1.5.0 | Content generation | Existing stack, no changes needed |
| Anthropic Claude Sonnet 4 | 0.39.0 | Content generation | Existing stack, no changes needed |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **lxml[html-clean]** | 6.0.4 | HTML sanitization with allowed tags | Use when sanitizing AI-generated HTML content to remove malicious or unwanted tags while preserving allowed formatting. |
| **re** (stdlib) | Built-in | Pattern matching and text cleaning | Use for removing unwanted characters like backticks, markdown code blocks, and other artifacts from AI output. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **pytest** | Testing content validation functions | Already in project (>=7.4.0). Use for testing validation logic. |
| **pytest-asyncio** | Async testing support | Already in project (>=0.21.0). Required for testing async AI service functions. |

## Installation

```bash
# Core HTML processing and text analysis
pip install lxml==6.0.4 beautifulsoup4==4.14.3 textstat==0.7.13

# HTML sanitization (lxml extra)
pip install 'lxml[html-clean]==6.0.4'
```

Update `backend/requirements.txt`:

```txt
# Existing dependencies...
fastapi==0.115.0
uvicorn==0.30.0
motor==3.6.0
pymongo>=4.7,<4.10
redis==5.0.0
google-genai==1.5.0
anthropic==0.39.0
openai>=1.60.0
python-multipart==0.0.9
Pillow==10.4.0
pydantic==2.9.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.24.0

# NEW: Content quality improvements
lxml==6.0.4
beautifulsoup4==4.14.3
textstat==0.7.13
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **lxml** | bleach | NEVER use bleach - deprecated as of 2023-01-23. Use lxml with html-clean extra instead. |
| **BeautifulSoup4** | html5lib | Use html5lib only if you need strict HTML5 compliance. BeautifulSoup4 is more flexible and has better Pythonic API. |
| **textstat** | Custom word counting | Use custom counting only if you need language-specific word counting that textstat doesn't support (e.g., Vietnamese word segmentation). |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **bleach** | Deprecated as of 2023-01-23. No longer maintained, security vulnerabilities may not be fixed. | **lxml** with `html-clean` extra for HTML sanitization. |
| **nltk** | Overkill for simple word counting. Heavy dependency, requires downloading language models. | **textstat** for word counting and text analysis. |
| **html5lib** | Slower than lxml, less flexible API. | **BeautifulSoup4** for HTML parsing and manipulation. |
| **Custom regex for HTML cleaning** | Error-prone, difficult to maintain, doesn't handle edge cases. | **lxml** or **BeautifulSoup4** for robust HTML processing. |
| **Vietnamese-specific NLP libraries** (underthesea, pyvi) | Not needed for content quality validation. | **textstat** for word counting (works with any language). |

## Stack Patterns by Variant

**If cleaning AI-generated HTML:**
- Use `lxml.html.clean` with allowed tags whitelist
- Because it provides security-focused sanitization and removes malicious content
- Example: `lxml.html.clean.clean_html(html, tags={'h1', 'h2', 'h3', 'p', 'strong', 'em', 'ul', 'ol', 'li', 'a'})`

**If removing unwanted characters from text:**
- Use BeautifulSoup4 to extract text from HTML, then regex for character cleanup
- Because BeautifulSoup4 handles HTML parsing correctly, regex handles character patterns
- Example: `soup.get_text()` followed by `re.sub(r'`[^`]*`', '', text)` to remove backtick-enclosed content

**If validating word counts:**
- Use textstat for accurate word counting
- Because it handles edge cases (punctuation, hyphens, etc.) better than simple split()
- Example: `textstat.lexicon_count(text, removepunct=True)`

**If validating section counts:**
- Use BeautifulSoup4 to count H2/H3 tags in HTML
- Because it correctly parses HTML structure
- Example: `len(soup.find_all(['h2', 'h3']))`

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| lxml==6.0.4 | Python >=3.8 | Requires Python 3.8 or higher. Compatible with Python 3.11 (project version). |
| beautifulsoup4==4.14.3 | Python >=3.7 | Compatible with Python 3.11 (project version). |
| textstat==0.7.13 | Python >=3.6 | Compatible with Python 3.11 (project version). |
| lxml[html-clean] | lxml==6.0.4 | Extra requires lxml core package. |

## Integration Points

### AI Service Layer (`backend/app/services/ai_service.py`)

**Add new validation and cleaning functions:**

```python
from bs4 import BeautifulSoup
import textstat
import re
from lxml import html as lxml_html

def clean_html_content(html: str) -> str:
    """Remove unwanted characters and clean HTML from AI output."""
    # Remove markdown code blocks
    html = re.sub(r'```json[^`]*```', '', html)
    html = re.sub(r'```html[^`]*```', '', html)
    html = re.sub(r'```[^`]*```', '', html)
    html = re.sub(r'`[^`]*`', '', html)

    # Parse and clean with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    return str(soup)

def sanitize_html(html: str) -> str:
    """Sanitize HTML to remove malicious tags while preserving allowed formatting."""
    from lxml.html.clean import clean_html, Cleaner

    cleaner = Cleaner(
        tags={'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'em', 'u', 'a',
              'ul', 'ol', 'li', 'br', 'hr', 'blockquote', 'code', 'pre'},
        attributes={'a': ['href', 'title'], 'img': ['src', 'alt']},
        styles=False,
        links=False,
        forms=False,
        remove_tags=['script', 'style', 'meta', 'link'],
        safe_attrs_only=True,
    )
    return cleaner.clean(html)

def validate_word_count(content: str, target: int, tolerance: float = 0.2) -> tuple[bool, int]:
    """Validate word count is within tolerance of target.
    Returns (is_valid, actual_word_count).
    """
    # Extract text from HTML for accurate word count
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()

    actual = textstat.lexicon_count(text, removepunct=True)
    if target is None:
        return True, actual

    min_words = int(target * (1 - tolerance))
    max_words = int(target * (1 + tolerance))
    is_valid = min_words <= actual <= max_words
    return is_valid, actual

def validate_section_count(outline: dict, target: int, tolerance: int = 1) -> tuple[bool, int]:
    """Validate section count is within tolerance of target.
    Returns (is_valid, actual_section_count).
    """
    sections = outline.get('sections', [])
    actual = len(sections)
    if target is None:
        return True, actual

    is_valid = abs(actual - target) <= tolerance
    return is_valid, actual
```

**Update existing generation functions to use validation:**

```python
async def generate_outline(
    topic: str,
    research_data: dict,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    target_section_count: int = None,
    language: str = "vietnamese",
) -> tuple[dict, int]:
    """Generate a post outline: SEO title, meta description, intro, sections."""
    # ... existing code ...

    text, total_tokens = await _call_ai(prompt, system_prompt, provider_id, model_name)
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        import re
        text = re.sub(r"//.*", "", text)
        data = json.loads(text.strip())
    except json.JSONDecodeError:
        data = {"raw_outline": text}

    # NEW: Validate section count
    if target_section_count:
        is_valid, actual = validate_section_count(data, target_section_count)
        if not is_valid:
            logger.warning(
                f"Section count mismatch: {actual} vs target {target_section_count}. "
                f"AI may not have followed instructions."
            )

    return data, total_tokens
```

### Worker Tasks (`backend/app/workers/tasks.py`)

**Add validation before saving results:**

```python
from app.services.ai_service import (
    clean_html_content,
    sanitize_html,
    validate_word_count,
    validate_section_count,
)

async def run_content_task(post_id: str, job_id: str):
    """Generate full content for a post."""
    try:
        # ... existing code to get post data ...

        # Generate content
        content, sections, tokens = await generate_full_content(
            topic=topic,
            outline=outline,
            additional_requests=additional_requests,
            provider_id=ai_provider_id,
            model_name=model_name,
            target_word_count=target_word_count,
            language=language,
        )

        # NEW: Clean content
        cleaned_content = clean_html_content(content)

        # NEW: Sanitize HTML
        sanitized_content = sanitize_html(cleaned_content)

        # NEW: Validate word count
        if target_word_count:
            is_valid, actual = validate_word_count(sanitized_content, target_word_count)
            if not is_valid:
                logger.warning(
                    f"Word count mismatch for post {post_id}: {actual} vs target {target_word_count}. "
                    f"Content may not meet user expectations."
                )
                # Optionally: Store validation result in post document
                await posts_col.update_one(
                    {"_id": ObjectId(post_id)},
                    {"$set": {"word_count_validation": {"valid": is_valid, "actual": actual, "target": target_word_count}}}
                )

        # Save cleaned and sanitized content
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$set": {
                    "content": sanitized_content,
                    "sections": sections,
                    "content_done": True,
                }
            }
        )

        # ... rest of existing code ...
```

### Backend API (`backend/app/routers/posts.py`)

**Add validation status to response:**

```python
class PostResponse(BaseModel):
    # ... existing fields ...
    word_count_validation: Optional[dict] = None  # NEW: Validation results
    section_count_validation: Optional[dict] = None  # NEW: Validation results
```

## Database Schema Updates

### Posts Collection
Add validation result fields to posts documents:

```python
{
    "word_count_validation": {
        "valid": true,
        "actual": 1250,
        "target": 1500
    },
    "section_count_validation": {
        "valid": true,
        "actual": 6,
        "target": 5
    },
    # ... existing fields
}
```

**Migration:** No migration needed - MongoDB is schemaless. New posts will include validation fields. Existing posts will not have these fields (null/missing).

## Testing Strategy

### Unit Tests for Validation Functions

```python
# tests/test_content_validation.py
import pytest
from app.services.ai_service import (
    clean_html_content,
    sanitize_html,
    validate_word_count,
    validate_section_count,
)

def test_clean_html_content_removes_backticks():
    html = "<p>Some `code` here</p>"
    cleaned = clean_html_content(html)
    assert "`code`" not in cleaned

def test_clean_html_content_removes_markdown_blocks():
    html = "<p>```json\n{\"key\": \"value\"}\n```</p>"
    cleaned = clean_html_content(html)
    assert "```json" not in cleaned
    assert "```" not in cleaned

def test_validate_word_count_within_tolerance():
    content = "<p>This is a test with ten words exactly.</p>"
    is_valid, actual = validate_word_count(content, target=10, tolerance=0.2)
    assert is_valid is True
    assert actual == 10

def test_validate_word_count_outside_tolerance():
    content = "<p>This is a test with ten words exactly.</p>"
    is_valid, actual = validate_word_count(content, target=20, tolerance=0.2)
    assert is_valid is False
    assert actual == 10

def test_validate_section_count_within_tolerance():
    outline = {"sections": [{"title": "1"}, {"title": "2"}, {"title": "3"}]}
    is_valid, actual = validate_section_count(outline, target=3, tolerance=1)
    assert is_valid is True
    assert actual == 3

def test_validate_section_count_outside_tolerance():
    outline = {"sections": [{"title": "1"}, {"title": "2"}, {"title": "3"}]}
    is_valid, actual = validate_section_count(outline, target=6, tolerance=1)
    assert is_valid is False
    assert actual == 3
```

## Sources

- **lxml 6.0.4** — https://pypi.org/project/lxml/ (verified Apr 12, 2026) - HIGH confidence (official PyPI)
- **BeautifulSoup4 4.14.3** — https://pypi.org/project/beautifulsoup4/ (verified Nov 30, 2025) - HIGH confidence (official PyPI)
- **textstat 0.7.13** — https://pypi.org/project/textstat/ (verified Feb 18, 2026) - HIGH confidence (official PyPI)
- **bleach 6.3.0** — https://pypi.org/project/bleach/ (verified deprecated status, Oct 27, 2025) - HIGH confidence (official PyPI, deprecation notice)
- **Existing codebase** — backend/app/services/ai_service.py, backend/app/workers/tasks.py, backend/requirements.txt - HIGH confidence (direct code inspection)

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack Selection | HIGH | All libraries are production-stable, actively maintained, with recent releases. |
| lxml vs bleach | HIGH | Bleach is officially deprecated (2023-01-23). lxml is the recommended alternative. |
| BeautifulSoup4 | HIGH | Industry standard for HTML parsing, widely used and well-documented. |
| textstat | HIGH | Production-stable, handles word counting edge cases better than custom solutions. |
| Integration Points | HIGH | Clear integration points identified in AI service and worker tasks. |
| Version Compatibility | HIGH | All libraries compatible with Python 3.11 (project version). |
| Testing Strategy | HIGH | Straightforward unit tests for validation functions. |

## Gaps to Address

- **Vietnamese word counting:** textstat may not handle Vietnamese word segmentation perfectly. Consider using `underthesea` or `pyvi` if Vietnamese word counting proves inaccurate.
- **HTML sanitization policy:** Need to define which HTML tags and attributes are allowed for WordPress content. Current whitelist is conservative.
- **Retry logic:** If validation fails, should we retry generation? This adds complexity and cost. For MVP, logging warnings is sufficient.
- **User feedback:** Consider adding UI indicators when content doesn't meet validation criteria (e.g., "Word count: 1200/1500").

---
*Stack research for: WordPress Writer Tool v1.3 Content Quality Improvements*
*Researched: 2026-04-16*
