# Phase 12: Backend Foundation - Research

**Researched:** 2026-04-15
**Domain:** Pydantic validation, MongoDB backward compatibility, FastAPI request/response models
**Confidence:** HIGH

## Summary

Phase 12 establishes the backend data model and validation infrastructure for language support. This involves adding a `language` field to Post models with Pydantic validation, storing it in MongoDB, and ensuring backward compatibility with existing posts. The implementation follows existing patterns in the codebase, specifically the `provider_type` field validation in `AIProviderCreate` which uses regex pattern matching.

The phase requires three key changes: (1) Add `language` field to `PostCreate` and `BulkPostCreate` Pydantic models with validation, (2) Store the field in MongoDB posts collection, and (3) Handle backward compatibility by defaulting to "english" for existing posts without the field. No new dependencies are required—this is pure configuration and validation logic using existing Pydantic 2.9.0 patterns.

**Primary recommendation:** Use Pydantic's `Field(..., pattern="^(vietnamese|english)$")` for validation, matching the existing `provider_type` pattern in `ai_provider.py`. Use `doc.get("language", "english")` in `format_post()` for backward compatibility.

## User Constraints (from CONTEXT.md)

No CONTEXT.md exists for this phase. All decisions are at the planner's discretion based on REQUIREMENTS.md.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LANG-03 | Language Field in Post Model | Pydantic Field pattern validation, MongoDB storage via Motor |
| LANG-08 | Language Validation | Pydantic automatic 400 error on invalid input, pattern matching |
| LANG-09 | Backward Compatibility | MongoDB schemaless design, `doc.get()` with default pattern |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pydantic | 2.9.0 | Request/response validation | Already in use, provides automatic validation and error responses |
| Motor | 3.6.0 | Async MongoDB driver | Already in use, handles schemaless MongoDB operations |
| FastAPI | 0.115.0 | REST API framework | Already in use, integrates with Pydantic for validation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None | — | — | No additional libraries needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `Field(pattern="...")` | `Literal["vietnamese", "english"]` | Literal provides better type hints but pattern matches existing codebase style |
| `doc.get("language", "english")` | Database migration | Migration is unnecessary for schemaless MongoDB; default pattern is simpler |

**Installation:**
```bash
# No new packages required - all dependencies already in requirements.txt
```

**Version verification:**
```bash
# Verified versions from backend/requirements.txt:
# pydantic==2.9.0
# motor==3.6.0
# fastapi==0.115.0
```

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── models/
│   └── post.py              # Add language field to PostCreate, BulkPostCreate, PostResponse
├── routers/
│   └── posts.py             # Update format_post() for backward compatibility
└── database.py             # No changes needed (schemaless MongoDB)
```

### Pattern 1: Pydantic Field Pattern Validation
**What:** Use regex pattern matching to restrict string field values
**When to use:** When a field must match one of a fixed set of string values
**Example:**
```python
# Source: backend/app/models/ai_provider.py (existing pattern)
from pydantic import BaseModel, Field

class AIProviderCreate(BaseModel):
    provider_type: str = Field(..., pattern="^(openai|gemini|anthropic|openai_compatible)$")

# Apply to language field:
class PostCreate(BaseModel):
    language: str = Field(default="vietnamese", pattern="^(vietnamese|english)$")
```

### Pattern 2: MongoDB Backward Compatibility with Defaults
**What:** Use `doc.get("field", default_value)` to handle missing fields in existing documents
**When to use:** When adding new fields to schemaless MongoDB collections
**Example:**
```python
# Source: backend/app/routers/posts.py (existing pattern in format_post)
def format_post(doc: dict) -> dict:
    return PostResponse(
        # ... existing fields ...
        additional_requests=doc.get("additional_requests", ""),
        auto_publish=doc.get("auto_publish", False),
        # Apply to language field:
        language=doc.get("language", "english"),  # Default for existing posts
    ).model_dump()
```

### Pattern 3: Pydantic Default Values
**What:** Set default values in Pydantic models for new records
**When to use:** When a field should have a default value for new creations
**Example:**
```python
# Source: backend/app/models/post.py (existing pattern)
class PostCreate(BaseModel):
    auto_publish: bool = False
    thumbnail_source: str = "ai"

# Apply to language field:
class PostCreate(BaseModel):
    language: str = "vietnamese"  # Default for new posts
```

### Anti-Patterns to Avoid
- **Hardcoding validation in routers:** Don't manually check `if language not in ["vietnamese", "english"]`—let Pydantic handle it
- **Database migrations:** Don't create migration scripts for MongoDB schemaless design—use default values instead
- **Separate validation functions:** Don't create custom validators when Pydantic's built-in pattern validation suffices

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| String enum validation | Custom `if language in [...]` checks | Pydantic `Field(pattern="...")` | Automatic 400 error, consistent with existing codebase |
| Backward compatibility logic | Database migration scripts | `doc.get("language", "english")` | MongoDB is schemaless, no migration needed |
| Default value handling | Manual default assignment in routers | Pydantic `default="vietnamese"` | Declarative, validated at model level |

**Key insight:** Pydantic's pattern validation provides automatic 400 errors with clear messages, eliminating the need for manual validation logic in routers. MongoDB's schemaless design means we can add fields without migrations—just use default values when reading.

## Runtime State Inventory

> Not applicable - this is a greenfield phase (adding new field, not renaming/refactoring)

## Common Pitfalls

### Pitfall 1: Forgetting to Update format_post()
**What goes wrong:** New posts have `language` field, but `format_post()` doesn't extract it, causing 500 errors when reading posts
**Why it happens:** `format_post()` manually maps MongoDB documents to Pydantic models; missing fields cause KeyError
**How to avoid:** Add `language=doc.get("language", "english")` to `format_post()` immediately after adding field to models
**Warning signs:** 500 errors on GET /posts/{id} or GET /posts/by-project/{project_id}

### Pitfall 2: Wrong Default for Backward Compatibility
**What goes wrong:** Existing posts default to "vietnamese" instead of "english", breaking user expectations
**Why it happens:** Confusion between default for new posts ("vietnamese") vs. existing posts ("english")
**How to avoid:** Use `default="vietnamese"` in Pydantic model (new posts) and `doc.get("language", "english")` in `format_post()` (existing posts)
**Warning signs:** Old posts suddenly showing as Vietnamese language

### Pitfall 3: Missing Field in BulkPostCreate
**What goes wrong:** Bulk post creation fails validation because `BulkPostCreate` doesn't have `language` field
**Why it happens:** `BulkPostCreate` is a separate model from `PostCreate`, both need the field
**How to avoid:** Add `language` field to both `PostCreate` and `BulkPostCreate` models
**Warning signs:** 400 errors on POST /posts/bulk endpoint

### Pitfall 4: Case Sensitivity in Validation
**What goes wrong:** Users send "Vietnamese" or "ENGLISH" and get 400 errors
**Why it happens:** Regex pattern is case-sensitive by default
**How to avoid:** Use case-insensitive regex or document that values must be lowercase
**Warning signs:** Validation errors for valid language names with different casing

## Code Examples

Verified patterns from official sources:

### Pydantic Pattern Validation
```python
# Source: https://docs.pydantic.dev/latest/api/pydantic/standard_library_types/#strings
# Pattern constraint for strings
from pydantic import BaseModel, Field

class PostCreate(BaseModel):
    language: str = Field(
        default="vietnamese",
        pattern="^(vietnamese|english)$",
        description="Language for content generation"
    )
```

### MongoDB Backward Compatibility
```python
# Source: backend/app/routers/posts.py (existing codebase pattern)
def format_post(doc: dict) -> dict:
    return PostResponse(
        # ... existing fields ...
        language=doc.get("language", "english"),  # Backward compatibility
    ).model_dump()
```

### Pydantic Default Values
```python
# Source: https://docs.pydantic.dev/latest/concepts/fields/#default-values
class PostCreate(BaseModel):
    language: str = "vietnamese"  # Default for new posts
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual validation in routers | Pydantic automatic validation | Pydantic V2 (2023) | Cleaner code, automatic error responses |
| Database migrations for schema changes | Schemaless with defaults | MongoDB adoption | No downtime for schema changes |

**Deprecated/outdated:**
- Pydantic V1 patterns: Implicit `None` defaults for `Optional` fields (removed in V2)
- Manual validation: `if field not in allowed_values` checks (use Pydantic instead)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Pydantic 2.9.0 supports `pattern` parameter in `Field()` | Standard Stack | Pattern validation might not work, requiring alternative approach |
| A2 | MongoDB schemaless design allows adding fields without migration | Architecture Patterns | Might need migration script if MongoDB has schema constraints |
| A3 | FastAPI automatically returns 400 errors on Pydantic validation failure | Common Pitfalls | Might need manual error handling if automatic errors don't work |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions (RESOLVED)

1. **Case sensitivity for language values** (RESOLVED)
   - What we know: Regex pattern `^(vietnamese|english)$` is case-sensitive
   - What's unclear: Should we accept "Vietnamese" or "VIETNAMESE"?
   - **Decision:** Keep case-sensitive for now (matches existing `provider_type` pattern), document clearly in API spec
   - **Rationale:** Consistent with existing codebase patterns, simpler validation, no need for case conversion

2. **Language field in PostUpdate model** (RESOLVED)
   - What we know: LANG-08 mentions validation for PUT /posts/{id} endpoint
   - What's unclear: Should `PostUpdate` include optional `language` field for updates?
   - **Decision:** Add `language: Optional[str] = Field(None, pattern="^(vietnamese|english)$")` to `PostUpdate` to allow language changes
   - **Rationale:** Users may want to change language after creation, optional field maintains backward compatibility

## Environment Availability

> Skip this section if the phase has no external dependencies (code/config-only changes).

**Step 2.6: SKIPPED (no external dependencies identified)**

This phase involves only code changes to existing Python files (Pydantic models and FastAPI routers). No external tools, services, or runtimes are required beyond what's already in the project.

## Validation Architecture

> Skip this section entirely if workflow.nyquist_validation is explicitly set to false in .planning/config.json. If the key is absent, treat as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected (Wave 0 required) |
| Config file | None — see Wave 0 |
| Quick run command | `pytest tests/ -x` (after Wave 0 setup) |
| Full suite command | `pytest tests/` (after Wave 0 setup) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LANG-03 | Language field in PostCreate/BulkPostCreate models | unit | `pytest tests/test_models.py::test_post_create_language -x` | ❌ Wave 0 |
| LANG-03 | Language field stored in MongoDB | integration | `pytest tests/test_posts.py::test_create_post_with_language -x` | ❌ Wave 0 |
| LANG-08 | API validates language is "vietnamese" or "english" | unit | `pytest tests/test_posts.py::test_invalid_language_rejected -x` | ❌ Wave 0 |
| LANG-08 | Invalid language returns 400 error | unit | `pytest tests/test_posts.py::test_invalid_language_400 -x` | ❌ Wave 0 |
| LANG-09 | API responses default to "english" for posts without language | integration | `pytest tests/test_posts.py::test_backward_compatibility_default -x` | ❌ Wave 0 |
| LANG-09 | No errors when querying posts without language field | integration | `pytest tests/test_posts.py::test_query_posts_without_language -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_models.py tests/test_posts.py -x`
- **Per wave merge:** `pytest tests/`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_models.py` — Pydantic model validation tests
- [ ] `tests/test_posts.py` — API endpoint tests
- [ ] `tests/conftest.py` — Shared fixtures (MongoDB test database, test client)
- [ ] `pytest.ini` or `pyproject.toml` — Test configuration
- [ ] Framework install: `pip install pytest pytest-asyncio httpx` — if none detected

*(If no gaps: "None — existing test infrastructure covers all phase requirements")*

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Omit only if explicitly `false` in config.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Pydantic pattern validation for language field |
| V2 Authentication | no | Not applicable (no auth changes) |
| V3 Session Management | no | Not applicable (no session changes) |
| V4 Access Control | no | Not applicable (no access control changes) |
| V6 Cryptography | no | Not applicable (no crypto changes) |

### Known Threat Patterns for Pydantic/FastAPI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Injection via language field | Tampering | Pydantic pattern validation restricts to "vietnamese" or "english" only |
| Regex DoS via pattern validation | Denial of Service | Simple regex `^(vietnamese|english)$` has no catastrophic backtracking risk |
| Data injection via MongoDB | Tampering | Motor driver handles escaping, Pydantic validates input |

## Sources

### Primary (HIGH confidence)
- [Pydantic 2.9.0 Documentation - Fields](https://docs.pydantic.dev/latest/concepts/fields/) - Field constraints, default values, pattern validation
- [Pydantic 2.9.0 Documentation - Standard Library Types](https://docs.pydantic.dev/latest/api/pydantic/standard_library_types/) - String constraints including pattern parameter
- [backend/app/models/ai_provider.py](file:///root/vscode/wordpress-writer-tool/backend/app/models/ai_provider.py) - Existing pattern validation example
- [backend/app/routers/posts.py](file:///root/vscode/wordpress-writer-tool/backend/app/routers/posts.py) - Existing backward compatibility pattern
- [backend/requirements.txt](file:///root/vscode/wordpress-writer-tool/backend/requirements.txt) - Verified package versions

### Secondary (MEDIUM confidence)
- [FastAPI Documentation - Request Bodies](https://fastapi.tiangolo.com/tutorial/body/) - How Pydantic integrates with FastAPI validation
- [MongoDB Documentation - Schemaless Design](https://www.mongodb.com/docs/manual/core/data-model-architecture/) - Schemaless database principles

### Tertiary (LOW confidence)
- None - All findings verified from primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified from requirements.txt and official documentation
- Architecture: HIGH - Based on existing codebase patterns and verified Pydantic documentation
- Pitfalls: HIGH - Identified from code review and common FastAPI/Pydantic mistakes

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 (30 days - Pydantic 2.9 is stable, MongoDB patterns are long-standing)
