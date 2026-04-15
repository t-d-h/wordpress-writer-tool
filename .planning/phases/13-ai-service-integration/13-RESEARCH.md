# Phase 13: AI Service Integration - Research

**Researched:** 2026-04-15
**Domain:** AI service language parameter, system prompts, job payload propagation
**Confidence:** HIGH

## Summary

Phase 13 integrates language support into the AI service layer. This involves adding a `language` parameter to all AI service functions, modifying system prompts to include language-specific instructions, and ensuring language flows through the job pipeline from creation to execution. The implementation follows existing patterns in the codebase where parameters like `provider_id` and `model_name` are passed through the pipeline.

The phase requires three key changes: (1) Add `language` parameter to AI service functions (`research_topic`, `generate_outline`, `generate_section_content`, `generate_introduction`), (2) Modify system prompts to include language instruction with cultural context for Vietnamese, and (3) Propagate language from post document through job payload to worker tasks. No new dependencies are required—this is pure parameter passing and prompt modification.

**Primary recommendation:** Add `language: str = "vietnamese"` parameter to all AI service functions, modify system prompts to include language-specific instructions, and extract language from post document in worker tasks before calling AI service functions.

## User Constraints (from CONTEXT.md)

No CONTEXT.md exists for this phase. All decisions are at the planner's discretion based on REQUIREMENTS.md.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LANG-04 | Language Parameter in AI Service | Add `language` parameter to all AI service functions, pass from job payload |
| LANG-05 | Language-Specific System Prompts | Modify system prompts to include language instruction with cultural context |
| LANG-07 | Language in Job Payload | Include language in job payload for all job types, extract from post document |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python 3.11 | Runtime | Backend language | Already in use, no changes needed |
| FastAPI 0.115.0 | REST API framework | Already in use, no changes needed |
| Motor 3.6.0 | Async MongoDB driver | Already in use, no changes needed |
| Redis 5.0.0 | Async Redis client | Already in use, no changes needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None | — | — | No additional libraries needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `language` parameter in each function | Global language variable | Parameter passing is more explicit and testable, follows existing patterns |
| Language-specific prompt templates | Dynamic prompt generation | Static templates are simpler, easier to maintain, sufficient for binary language choice |

**Installation:**
```bash
# No new packages required - all dependencies already in requirements.txt
```

**Version verification:**
```bash
# Verified versions from backend/requirements.txt:
# Python 3.11
# fastapi==0.115.0
# motor==3.6.0
# redis==5.0.0
```

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── services/
│   └── ai_service.py         # Add language parameter to all functions, modify system prompts
worker/app/
├── workers/
│   └── tasks.py              # Extract language from post document, pass to AI service
└── services/
    └── job_service.py       # Include language in job payload (already done in Phase 12)
```

### Pattern 1: Parameter Passing Through Pipeline
**What:** Pass parameters from API layer → job payload → worker tasks → AI service
**When to use:** When a parameter needs to flow through the entire generation pipeline
**Example:**
```python
# Source: backend/app/routers/posts.py (existing pattern in Phase 12)
# API layer includes language in job payload
job_payload = {
    "job_id": job_id,
    "post_id": post_id,
    "project_id": project_id,
    "job_type": "research",
    "language": data.language,  # Already added in Phase 12
}

# Worker task extracts language from post document
post = await posts_col.find_one({"_id": ObjectId(post_id)})
language = post.get("language", "vietnamese")  # Extract from post

# AI service function accepts language parameter
async def research_topic(
    topic: str,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    language: str = "vietnamese",  # Add this parameter
) -> tuple[dict, int]:
```

### Pattern 2: Language-Specific System Prompts
**What:** Modify system prompts based on language parameter
**When to use:** When AI output needs to be in a specific language
**Example:**
```python
# Source: backend/app/services/ai_service.py (existing pattern)
# Current system prompt
system_prompt = "You are an expert SEO content researcher. Respond only in valid JSON."

# Modified to include language instruction
async def research_topic(
    topic: str,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    language: str = "vietnamese",
) -> tuple[dict, int]:
    # Language-specific system prompt
    if language == "vietnamese":
        system_prompt = (
            "You are an expert SEO content researcher for Vietnamese content. "
            "Write all content in Vietnamese. Use formal, professional Vietnamese "
            "with appropriate cultural context. Respond only in valid JSON."
        )
    else:  # english
        system_prompt = (
            "You are an expert SEO content researcher. "
            "Write all content in English. Respond only in valid JSON."
        )
```

### Pattern 3: Default Parameter Values
**What:** Set default values for optional parameters
**When to use:** When a parameter should have a sensible default
**Example:**
```python
# Source: backend/app/services/ai_service.py (existing pattern)
async def research_topic(
    topic: str,
    additional_requests: str = "",  # Default empty string
    provider_id: str = None,        # Default None (use first available)
    model_name: str = None,        # Default None (use provider default)
    language: str = "vietnamese",   # Default Vietnamese
) -> tuple[dict, int]:
```

### Anti-Patterns to Avoid
- **Hardcoding language in prompts:** Don't create separate functions for Vietnamese and English—use a single function with language parameter
- **Global language state:** Don't use global variables or module-level constants for language—pass as parameter
- **Skipping language in job payload:** Don't forget to include language in job payload for all job types (research, outline, content, thumbnail, publish)

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Language-specific prompt templates | Separate `research_topic_vietnamese()` and `research_topic_english()` functions | Single function with `language` parameter and conditional prompts | Less code duplication, easier to maintain, follows existing patterns |
| Language extraction in each task | Duplicate `post.get("language", "vietnamese")` in every task | Extract once at task start, pass to AI service | Consistent behavior, easier to test, follows existing patterns |
| Language validation in tasks | Manual `if language not in ["vietnamese", "english"]` checks | Trust Phase 12 validation, use default "vietnamese" | Validation already done at API layer, no need to repeat |

**Key insight:** Language parameter follows the same pattern as `provider_id` and `model_name`—extracted from post document in worker tasks, passed to AI service functions. System prompts are modified conditionally based on language, similar to how different providers might have different prompt requirements.

## Runtime State Inventory

> Not applicable - this is a greenfield phase (adding new parameter, not renaming/refactoring)

## Common Pitfalls

### Pitfall 1: Forgetting to Pass Language to AI Service
**What goes wrong:** Worker task extracts language from post but doesn't pass to AI service function, causing default language to be used
**Why it happens:** Easy to miss when adding new parameter to existing function calls
**How to avoid:** Update all AI service function calls in worker tasks to include language parameter
**Warning signs:** Content always generated in Vietnamese even when English is selected

### Pitfall 2: Inconsistent Language Across Pipeline Stages
**What goes wrong:** Research is in Vietnamese but outline is in English, or content is in different language than outline
**Why it happens:** Language extracted differently in each task, or not passed consistently
**How to avoid:** Extract language once at task start using `post.get("language", "vietnamese")`, pass to all AI service calls
**Warning signs:** Mixed language content in final post

### Pitfall 3: Missing Language in Job Payload
**What goes wrong:** Job payload doesn't include language field, worker can't extract it from post
**Why it happens:** Job creation doesn't include language in extra_data
**How to avoid:** Verify job_service.py includes language in job_message (already done in Phase 12)
**Warning signs:** Worker tasks can't find language field, default to Vietnamese

### Pitfall 4: System Prompts Not Language-Specific
**What goes wrong:** System prompts don't include language instruction, AI generates in wrong language
**Why it happens:** System prompts not modified to include language-specific instructions
**How to avoid:** Add conditional system prompt construction based on language parameter
**Warning signs:** AI generates English content when Vietnamese is selected

## Code Examples

Verified patterns from official sources:

### Parameter Passing Pattern
```python
# Source: backend/app/services/ai_service.py (existing codebase pattern)
async def research_topic(
    topic: str,
    additional_requests: str = "",
    provider_id: str = None,
    model_name: str = None,
    language: str = "vietnamese",  # Add this parameter
) -> tuple[dict, int]:
    # Language-specific system prompt
    if language == "vietnamese":
        system_prompt = (
            "You are an expert SEO content researcher for Vietnamese content. "
            "Write all content in Vietnamese. Use formal, professional Vietnamese "
            "with appropriate cultural context. Respond only in valid JSON."
        )
    else:
        system_prompt = (
            "You are an expert SEO content researcher. "
            "Write all content in English. Respond only in valid JSON."
        )

    prompt = f"""Research the following topic for a WordPress blog post.

Topic: {topic}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Provide your research as JSON with these keys:
{{
    "target_audience": "description of the target audience",
    "keywords": ["list", "of", "seo", "keywords"],
    "key_points": ["point 1 to cover", "point 2 to cover", ...],
    "questions_to_answer": ["question 1", "question 2", ...],
    "competitors_angle": "what competitors typically cover on this topic"
}}"""

    text, total_tokens = await _call_ai(prompt, system_prompt, provider_id, model_name)
    # ... rest of function
```

### Worker Task Language Extraction
```python
# Source: worker/app/workers/tasks.py (existing codebase pattern)
async def run_research(job_data: dict):
    """Research a topic using AI."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        logger.info(f"[RESEARCH] Starting research for post {post_id}")

        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        topic = post["topic"]
        additional = post.get("additional_requests", "")
        provider_id = post.get("ai_provider_id")
        model_name = post.get("model_name")
        language = post.get("language", "vietnamese")  # Extract language

        logger.info(f"[RESEARCH] Topic: {topic}")
        logger.info(f"[RESEARCH] Language: {language}")  # Log language
        logger.info(f"[RESEARCH] Using AI provider: {provider_id}")
        logger.info(f"[RESEARCH] Calling AI model: {model_name}")

        research_data, total_tokens = await ai_service.research_topic(
            topic, additional, provider_id, model_name, language  # Pass language
        )

        # ... rest of function
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded language in prompts | Language parameter with conditional prompts | This phase | Supports multiple languages, easier to maintain |
| No language in job payload | Language in job payload (Phase 12) | Phase 12 | Language flows through pipeline consistently |

**Deprecated/outdated:**
- Hardcoded language prompts: "Write in English" or "Write in Vietnamese" without parameterization
- Separate functions for each language: `research_topic_vietnamese()`, `research_topic_english()`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AI providers (OpenAI, Gemini, Anthropic) support Vietnamese natively | Standard Stack | Vietnamese content generation might not work, requiring translation workflow |
| A2 | System prompt language instruction is sufficient for Vietnamese generation | Architecture Patterns | Might need additional techniques (few-shot examples, temperature tuning) |
| A3 | Language parameter default "vietnamese" is appropriate for this user base | User Constraints | Users might prefer English as default, requiring configuration change |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions (RESOLVED)

1. **Should language be included in thumbnail generation prompts?** (RESOLVED)
   - What we know: LANG-07 mentions language in job payload for thumbnail job
   - What's unclear: Should thumbnail prompts include language instruction?
   - **Decision:** No, thumbnail generation is visual, not text-based. Language parameter not needed for image generation.
   - **Rationale:** Image generation prompts describe visual content, not text. Language parameter only relevant for text generation functions.

2. **Should language be included in publish job?** (RESOLVED)
   - What we know: LANG-07 mentions language in job payload for publish job
   - What's unclear: What does language mean for publishing to WordPress?
   - **Decision:** Include language in publish job payload for consistency, but don't use it in publish logic.
   - **Rationale:** WordPress doesn't have a language field in post API. Language is for content generation, not publishing. Include for job payload consistency only.

3. **What cultural context should be included in Vietnamese prompts?** (RESOLVED)
   - What we know: LANG-05 requires cultural context for Vietnamese
   - What's unclear: What specific cultural context to include?
   - **Decision:** Include general instruction for formal, professional Vietnamese with appropriate cultural context.
   - **Rationale:** Specific cultural references depend on topic. General instruction for formality and cultural appropriateness is sufficient for MVP.

## Environment Availability

> Skip this section if the phase has no external dependencies (code/config-only changes).

**Step 2.6: SKIPPED (no external dependencies identified)**

This phase involves only code changes to existing Python files (AI service functions and worker tasks). No external tools, services, or runtimes are required beyond what's already in the project.

## Validation Architecture

> Skip this section entirely if workflow.nyquist_validation is explicitly set to false in .planning/config.json. If the key is absent, treat as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already set up in Phase 12) |
| Config file | backend/pytest.ini (already created in Phase 12) |
| Quick run command | `pytest tests/ -x` |
| Full suite command | `pytest tests/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LANG-04 | research_topic accepts language parameter | unit | `pytest tests/test_ai_service.py::test_research_topic_language -x` | ❌ Need to create |
| LANG-04 | generate_outline accepts language parameter | unit | `pytest tests/test_ai_service.py::test_generate_outline_language -x` | ❌ Need to create |
| LANG-04 | generate_section_content accepts language parameter | unit | `pytest tests/test_ai_service.py::test_generate_section_content_language -x` | ❌ Need to create |
| LANG-04 | generate_introduction accepts language parameter | unit | `pytest tests/test_ai_service.py::test_generate_introduction_language -x` | ❌ Need to create |
| LANG-05 | System prompts include language instruction | unit | `pytest tests/test_ai_service.py::test_system_prompt_language -x` | ❌ Need to create |
| LANG-07 | Language in job payload for research job | integration | `pytest tests/test_jobs.py::test_research_job_language -x` | ❌ Need to create |
| LANG-07 | Language in job payload for outline job | integration | `pytest tests/test_jobs.py::test_outline_job_language -x` | ❌ Need to create |
| LANG-07 | Language in job payload for content job | integration | `pytest tests/test_jobs.py::test_content_job_language -x` | ❌ Need to create |

### Sampling Rate
- **Per task commit:** `pytest tests/test_ai_service.py tests/test_jobs.py -x`
- **Per wave merge:** `pytest tests/`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_ai_service.py` — AI service language parameter tests
- [ ] `tests/test_jobs.py` — Job payload language tests
- [ ] Framework already set up in Phase 12 (pytest, conftest, etc.)

*(If no gaps: "None — existing test infrastructure covers all phase requirements")*

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Omit only if explicitly `false` in config.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Language parameter already validated in Phase 12 (Pydantic pattern validation) |
| V2 Authentication | no | Not applicable (no auth changes) |
| V3 Session Management | no | Not applicable (no session changes) |
| V4 Access Control | no | Not applicable (no access control changes) |
| V6 Cryptography | no | Not applicable (no crypto changes) |

### Known Threat Patterns for AI Service

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection via language parameter | Tampering | Language parameter already validated in Phase 12 (restricted to "vietnamese" or "english") |
| Language parameter bypassing validation | Tampering | Pydantic validation at API layer, no user input in worker tasks |

## Sources

### Primary (HIGH confidence)
- [backend/app/services/ai_service.py](file:///root/vscode/wordpress-writer-tool/backend/app/services/ai_service.py) - Existing AI service functions
- [worker/app/workers/tasks.py](file:///root/vscode/wordpress-writer-tool/worker/app/workers/tasks.py) - Existing worker task implementations
- [backend/app/services/job_service.py](file:///root/vscode/wordpress-writer-tool/backend/app/services/job_service.py) - Job creation with language payload (Phase 12)
- [backend/app/routers/posts.py](file:///root/vscode/wordpress-writer-tool/backend/app/routers/posts.py) - API endpoints with language field (Phase 12)
- [backend/requirements.txt](file:///root/vscode/wordpress-writer-tool/backend/requirements.txt) - Verified package versions

### Secondary (MEDIUM confidence)
- [OpenAI Documentation - System Messages](https://platform.openai.com/docs/guides/system-prompts) - How to use system prompts for language instruction
- [Google Gemini Documentation - System Instructions](https://ai.google.dev/gemini-api/docs/system-instructions) - System prompt patterns for Gemini
- [Anthropic Documentation - System Prompts](https://docs.anthropic.com/claude/docs/system-prompts) - System prompt patterns for Claude

### Tertiary (LOW confidence)
- None - All findings verified from primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified from requirements.txt and existing codebase
- Architecture: HIGH - Based on existing parameter passing patterns in codebase
- Pitfalls: HIGH - Identified from code review and common parameter passing mistakes

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 (30 days - AI service patterns are stable, no external dependencies)
