# Architecture Research

**Domain:** Content Quality Improvements for AI Content Generation
**Researched:** 2026-04-16
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer (React)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ProjectDetail│  │ PostView     │  │ PostList     │      │
│  │   .jsx       │  │   .jsx       │  │   .jsx       │      │
│  │              │  │              │  │              │      │
│  │ Display      │  │ Display      │  │ Display      │      │
│  │ Validation   │  │ Validation   │  │ Validation   │      │
│  │ Results      │  │ Results      │  │ Results      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend API Layer (FastAPI)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ posts.py     │  │ Post Model   │  │ Validation   │      │
│  │ Router       │  │ (Pydantic)   │  │ Model        │      │
│  │              │  │              │  │              │      │
│  │ GET /posts   │  │ validation:  │  │ word_count:  │      │
│  │              │  │ dict         │  │ int          │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer (Python)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ai_service   │  │ validation   │  │ wp_service   │      │
│  │              │  │ _service     │  │              │      │
│  │ research_    │  │              │  │ (no change)  │      │
│  │ topic()      │  │ clean_html() │  │              │      │
│  │              │  │ validate_    │  │              │      │
│  │ + HTML       │  │ word_count() │  │              │      │
│  │   cleaning   │  │ validate_    │  │              │      │
│  │ + validation │  │ section_     │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Worker Layer (Async Tasks)                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ run_         │  │ run_         │  │ run_         │      │
│  │ research()   │  │ outline()    │  │ content()    │      │
│  │              │  │              │  │              │      │
│  │ Call AI      │  │ Call AI      │  │ Call AI      │      │
│  │ + Clean HTML │  │ + Validate   │  │ + Validate   │      │
│  │ + Validate   │  │   Section    │  │   Word Count │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────────────────────────────────────────────────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer (MongoDB)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ posts_col    │  │ projects_col │  │ jobs_col     │      │
│  │              │  │              │  │              │      │
│  │ validation:  │  │ (no change)  │  │ (no change)  │      │
│  │ {            │  │              │  │              │      │
│  │   word_      │  │              │  │              │      │
│  │   count: int │  │              │  │              │      │
│  │   section_   │  │              │  │              │      │
│  │   count: int │  │              │  │              │      │
│  │   html_      │  │              │  │              │      │
│  │   clean: bool │  │              │  │              │      │
│  │ }            │  │              │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Validation Service** | Content quality validation and cleaning | Add `validation_service.py` with `clean_html()`, `validate_word_count()`, `validate_section_count()` |
| **AI Service** | Generate content with HTML cleaning and validation | Add HTML cleaning to `generate_section_content()` and `generate_introduction()`; add validation to `generate_outline()` and `generate_full_content()` |
| **Worker Tasks** | Apply validation and cleaning after generation | Call validation functions after AI generation; store validation results in post document |
| **Post Model** | Store validation results | Add `validation: dict` field to `PostResponse` |
| **Frontend** | Display validation results | Show word count, section count, and HTML cleanliness in post detail view |

## Recommended Project Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── post.py              # Add validation field to PostResponse
│   │   └── validation.py        # NEW: Validation result model
│   ├── services/
│   │   ├── ai_service.py        # Add HTML cleaning and validation
│   │   ├── validation_service.py  # NEW: Validation and cleaning functions
│   │   ├── wp_service.py        # No changes needed
│   │   └── job_service.py       # No changes needed
│   ├── routers/
│   │   └── posts.py             # No changes needed
│   └── workers/
│       └── tasks.py             # Add validation calls after generation
frontend/
└── src/
    └── components/
        └── Posts/
            ├── PostView.jsx     # Display validation results
            └── PostList.jsx     # Display validation results
```

### Structure Rationale

- **backend/app/services/validation_service.py:** Centralized location for validation and cleaning functions. Reusable across AI service and worker tasks.
- **backend/app/models/validation.py:** Validation result model for type safety and consistency.
- **backend/app/services/ai_service.py:** AI service should clean and validate content before returning. Ensures quality at generation time.
- **backend/app/workers/tasks.py:** Worker tasks should call validation after generation and store results in post document.
- **frontend/src/components/Posts/PostView.jsx:** Post detail view is natural place to display validation results.

## Architectural Patterns

### Pattern 1: Validation as Non-Blocking Check

**What:** Validation functions return results but don't fail generation. Warnings are logged but content is still saved.

**When to use:** When validation is advisory rather than mandatory. AI models cannot guarantee exact specifications.

**Trade-offs:**
- **Pros:** Doesn't block content generation, users can publish content that doesn't meet validation, clear feedback on quality
- **Cons:** Users may ignore warnings, content may not meet specifications

**Example:**
```python
# Validation returns results, doesn't raise exceptions
validation_result = validate_word_count(content, target_word_count)
if not validation_result["passed"]:
    logger.warning(f"Word count validation failed: {validation_result['actual']} vs {validation_result['target']}")
# Content is still saved, validation result stored in post document
```

### Pattern 2: HTML Cleaning Before Validation

**What:** HTML content is cleaned before validation to ensure accurate word and section counts.

**When to use:** When AI-generated content may contain markdown artifacts or malformed HTML.

**Trade-offs:**
- **Pros:** Accurate validation counts, clean content for WordPress, consistent behavior
- **Cons:** May remove content that user intended to keep, requires careful whitelist definition

**Example:**
```python
# Clean HTML first
cleaned_content = clean_html_content(content)
# Then validate
word_count_result = validate_word_count(cleaned_content, target_word_count)
section_count_result = validate_section_count(cleaned_content, target_section_count)
```

### Pattern 3: Validation Results Stored in Document

**What:** Validation results are stored in the post document for historical tracking and display.

**When to use:** When validation results need to be displayed to users or tracked over time.

**Trade-offs:**
- **Pros:** Historical tracking, easy display in UI, no separate queries needed
- **Cons:** Document size increases, validation results may become stale if content is edited

**Example:**
```python
# Post document structure
{
    "_id": ObjectId("..."),
    "topic": "How to improve website SEO",
    "content": "<h2>Introduction</h2>...",
    "validation": {
        "word_count": {
            "actual": 1200,
            "target": 1500,
            "passed": false,
            "tolerance": 0.2
        },
        "section_count": {
            "actual": 4,
            "target": 5,
            "passed": true,
            "tolerance": 1
        },
        "html_clean": true
    }
}
```

## Data Flow

### Request Flow

```
[User creates post with target_word_count=1500, target_section_count=5]
    ↓
[Frontend sends POST /api/posts with targets]
    ↓
[Backend creates Post document with targets]
    ↓
[Backend queues research job with targets]
    ↓
[Worker picks up research job]
    ↓
[Worker calls ai_service.research_topic()]
    ↓
[AI generates research]
    ↓
[Worker queues outline job with targets]
    ↓
[Worker calls ai_service.generate_outline()]
    ↓
[AI generates outline]
    ↓
[Worker validates section count]
    ↓
[Worker queues content job with targets]
    ↓
[Worker calls ai_service.generate_full_content()]
    ↓
[AI generates content]
    ↓
[Worker cleans HTML content]
    ↓
[Worker validates word count]
    ↓
[Worker stores validation results in Post document]
    ↓
[Post updated with validation results]
```

### State Management

```
[Post Document in MongoDB]
    ↓ (read by worker)
[Job Data with targets]
    ↓ (passed to AI service)
[AI Service Functions]
    ↓ (generate content)
[Generated Content]
    ↓ (cleaned and validated)
[Validation Results]
    ↓ (stored back to Post)
[Post Document Updated with Validation Results]
```

### Key Data Flows

1. **Target Flow:** User input → API request → Post document → Job data → AI service calls → Validation
2. **Content Flow:** AI generation → HTML cleaning → Validation → Storage
3. **Validation Flow:** Validation functions → Validation results → Post document → Frontend display

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Current architecture is sufficient. Validation adds minimal overhead. |
| 1k-100k users | Consider caching validation results. Add validation result indexing if filtering by validation status becomes common. |
| 100k+ users | Consider separate validation service. Add validation result aggregation for quality dashboards. |

### Scaling Priorities

1. **First bottleneck:** AI API rate limits. Validation doesn't change this, but HTML cleaning adds minimal overhead.
2. **Second bottleneck:** MongoDB document size. Adding validation results increases document size but not significantly.

## Anti-Patterns

### Anti-Pattern 1: Validation as Blocking Check

**What people do:** Validation failures raise exceptions and block content generation.

**Why it's wrong:** AI models cannot guarantee exact specifications. Blocking generation frustrates users and wastes tokens.

**Do this instead:** Use validation as advisory checks. Log warnings and store results, but don't block generation.

### Anti-Pattern 2: Validation After Storage

**What people do:** Store content first, then validate separately.

**Why it's wrong:** Validation results may not be associated with content. Content may be published before validation completes.

**Do this instead:** Validate before storage. Store validation results with content in same document.

### Anti-Pattern 3: HTML Cleaning After Validation

**What people do:** Validate word count first, then clean HTML.

**Why it's wrong:** Word count may be inaccurate if HTML contains markdown artifacts or code blocks.

**Do this instead:** Clean HTML first, then validate. Ensures accurate validation counts.

### Anti-Pattern 4: Strict Enforcement Without Tolerance

**What people do:** Validation requires exact word count and section count.

**Why it's wrong:** AI models cannot guarantee exact specifications. Strict enforcement leads to frequent failures.

**Do this instead:** Use tolerance-based validation (±20% for word count, ±1 section for section count).

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI API | No changes | AI generation unchanged, validation added after |
| Gemini API | No changes | AI generation unchanged, validation added after |
| Anthropic API | No changes | AI generation unchanged, validation added after |
| WordPress REST API | No changes | Content is cleaned before publishing, but WordPress API unchanged |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| AI Service ↔ Validation Service | Function call | AI service calls validation functions after generation |
| Worker ↔ Validation Service | Function call | Worker calls validation functions after AI generation |
| Worker ↔ MongoDB | Document field | Worker stores validation results in post document |
| Frontend ↔ Backend API | HTTP response | Backend includes validation results in PostResponse |

## Build Order

Based on dependencies and integration points, recommended build order:

### Phase 1: HTML Cleaning (Foundation)
1. **Add Validation Service** (`backend/app/services/validation_service.py`)
   - Implement `clean_html_content()` using BeautifulSoup4 + lxml
   - Implement `sanitize_html()` with whitelist of allowed tags
   - Add tests for HTML cleaning

2. **Update AI Service** (`backend/app/services/ai_service.py`)
   - Add HTML cleaning to `generate_section_content()`
   - Add HTML cleaning to `generate_introduction()`
   - Test cleaning with all AI providers

### Phase 2: Validation Functions (Core Logic)
3. **Update Validation Service** (`backend/app/services/validation_service.py`)
   - Implement `validate_word_count()` using textstat
   - Implement `validate_section_count()` using outline structure
   - Add tolerance-based validation (±20% word count, ±1 section)

4. **Update AI Service** (`backend/app/services/ai_service.py`)
   - Add validation to `generate_outline()`
   - Add validation to `generate_full_content()`
   - Return validation results from AI service functions

5. **Update Worker Tasks** (`backend/app/workers/tasks.py`)
   - Call validation functions after AI generation
   - Store validation results in post document
   - Log validation warnings

### Phase 3: Research Data Utilization (Enhancement)
6. **Update AI Service** (`backend/app/services/ai_service.py`)
   - Pass `research_data` to `generate_full_content()`
   - Update prompts to include research context
   - Test that research data influences content

### Phase 4: Additional Requests Validation (Nice-to-have)
7. **Update Worker Tasks** (`backend/app/workers/tasks.py`)
   - Log when `additional_requests` provided
   - Add warning if AI output doesn't reflect requests
   - Document known limitations

### Phase 5: Frontend Display (User Interface)
8. **Update Post Model** (`backend/app/models/post.py`)
   - Add `validation: dict` field to `PostResponse`
   - Define validation result structure

9. **Update Frontend** (`frontend/src/components/Posts/PostView.jsx`)
   - Display word count validation results
   - Display section count validation results
   - Display HTML cleanliness status

## Data Model Changes

### Post Model Changes

```python
# backend/app/models/post.py

class PostResponse(BaseModel):
    # ... existing fields ...
    validation: Optional[Dict[str, Any]] = None  # NEW: Validation results
```

### Validation Result Structure

```python
# backend/app/models/validation.py

from pydantic import BaseModel
from typing import Optional

class WordCountValidation(BaseModel):
    actual: int
    target: int
    passed: bool
    tolerance: float = 0.2  # ±20%

class SectionCountValidation(BaseModel):
    actual: int
    target: int
    passed: bool
    tolerance: int = 1  # ±1 section

class ValidationResult(BaseModel):
    word_count: Optional[WordCountValidation] = None
    section_count: Optional[SectionCountValidation] = None
    html_clean: bool = False
```

### Database Schema Changes

```python
# backend/app/database.py

# No index changes needed for validation field
# Validation is stored as a simple dict field in Post documents
# Example Post document structure:
{
    "_id": ObjectId("..."),
    "project_id": "...",
    "topic": "How to improve website SEO",
    "content": "<h2>Introduction</h2>...",
    "validation": {  # NEW: Validation results
        "word_count": {
            "actual": 1200,
            "target": 1500,
            "passed": false,
            "tolerance": 0.2
        },
        "section_count": {
            "actual": 4,
            "target": 5,
            "passed": true,
            "tolerance": 1
        },
        "html_clean": true
    },
    # ... other fields ...
}
```

## Sources

- Existing codebase analysis: `backend/app/services/ai_service.py`, `backend/app/workers/tasks.py`, `backend/app/models/post.py`
- Project requirements: `.planning/PROJECT.md` (v1.3 Content Quality Improvements milestone)
- FastAPI documentation: https://fastapi.tiangolo.com/
- Pydantic documentation: https://docs.pydantic.dev/
- React documentation: https://react.dev/
- BeautifulSoup4 documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- lxml documentation: https://lxml.de/
- textstat documentation: https://github.com/textstat/textstat

---
*Architecture research for: WordPress Writer Tool v1.3 Content Quality Improvements*
*Researched: 2026-04-16*
