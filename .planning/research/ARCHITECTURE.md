# Architecture Research

**Domain:** Vietnamese Language Support for AI Content Generation
**Researched:** 2026-04-15
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer (React)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ProjectDetail│  │ Create Post  │  │ PostView     │      │
│  │   .jsx       │  │   Modal      │  │   .jsx       │      │
│  │              │  │              │  │              │      │
│  │ Language     │  │ Language     │  │ Display      │      │
│  │ Selector     │  │ Checkbox     │  │ Language     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend API Layer (FastAPI)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ posts.py     │  │ Post Model   │  │ Project      │      │
│  │ Router       │  │ (Pydantic)   │  │ Model        │      │
│  │              │  │              │  │              │      │
│  │ POST /posts  │  │ language:    │  │ (no change)  │      │
│  │              │  │ str = "vi"   │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                  │                                 │
└─────────┼──────────────────┼────────────────────────────────┘
          │                  │
          ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer (Python)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ai_service   │  │ wp_service   │  │ job_service  │      │
│  │              │  │              │  │              │      │
│  │ research_    │  │ create_wp_  │  │ queue_next_  │      │
│  │ topic()      │  │ post()       │  │ job()        │      │
│  │              │  │              │  │              │      │
│  │ + language   │  │ (no change) │  │ + language   │      │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘      │
│         │                                  │                  │
└─────────┼──────────────────────────────────┼──────────────────┘
          │                                  │
          ↓                                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Worker Layer (Async Tasks)                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ run_         │  │ run_         │  │ run_         │      │
│  │ research()   │  │ outline()    │  │ content()    │      │
│  │              │  │              │  │              │      │
│  │ Pass language│  │ Pass language│  │ Pass language│      │
│  │ to AI service│  │ to AI service│  │ to AI service│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer (MongoDB)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ posts_col    │  │ projects_col │  │ jobs_col     │      │
│  │              │  │              │  │              │      │
│  │ language:    │  │ (no change)  │  │ + language   │      │
│  │ "vi" | "en"  │  │              │  │ (optional)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Post Model** | Store language preference per post | Add `language: str = "vi"` field to `PostCreate` and `PostResponse` |
| **AI Service** | Generate content in specified language | Add `language` parameter to all generation functions, update system prompts |
| **Worker Tasks** | Pass language through pipeline | Extract language from post/job data, pass to AI service calls |
| **Frontend Form** | Allow language selection | Add checkbox/radio after title field, default to Vietnamese |
| **Posts Router** | Accept and persist language | Update `create_post()` to handle language field |
| **Job Service** | Include language in job data | Add language to job payload when queuing |

## Recommended Project Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── post.py              # Add language field to PostCreate/PostResponse
│   │   └── project.py            # No changes needed
│   ├── services/
│   │   ├── ai_service.py        # Add language parameter to all functions
│   │   ├── wp_service.py        # No changes needed
│   │   └── job_service.py       # Add language to job payload
│   ├── routers/
│   │   └── posts.py             # Update create_post() to handle language
│   └── workers/
│       └── tasks.py             # Pass language to AI service calls
frontend/
└── src/
    └── components/
        └── Projects/
            └── ProjectDetail.jsx  # Add language selector to create form
```

### Structure Rationale

- **backend/app/models/post.py:** Language is a post-level attribute, not project-level. Each post can have different language requirements.
- **backend/app/services/ai_service.py:** All AI generation functions need language awareness to produce appropriate content.
- **backend/app/workers/tasks.py:** Worker tasks must pass language through the pipeline to ensure consistent generation.
- **frontend/src/components/Projects/ProjectDetail.jsx:** Create post form is the natural place for language selection.

## Architectural Patterns

### Pattern 1: Parameter Propagation Through Pipeline

**What:** Language parameter flows from user input through all layers of the content generation pipeline.

**When to use:** When a configuration parameter affects multiple stages of an async pipeline.

**Trade-offs:**
- **Pros:** Clear data flow, easy to trace, each stage has all context needed
- **Cons:** More parameters to pass through, potential for parameter drift

**Example:**
```python
# Frontend: User selects language
const [language, setLanguage] = useState('vi')  # Default Vietnamese

# Backend: Router accepts language
class PostCreate(BaseModel):
    language: str = "vi"  # Default Vietnamese

# Service: AI service uses language
async def research_topic(topic: str, language: str = "vi", ...) -> tuple[dict, int]:
    system_prompt = _get_system_prompt(language, "research")
    # ... rest of function

# Worker: Passes language to AI service
async def run_research(job_data: dict):
    language = job_data.get("language", "vi")
    research_data, tokens = await ai_service.research_topic(
        topic, additional, provider_id, model_name, language
    )
```

### Pattern 2: Language-Aware System Prompts

**What:** System prompts are dynamically generated based on language parameter.

**When to use:** When AI instructions need to be localized for different languages.

**Trade-offs:**
- **Pros:** Consistent language output, no hardcoded language assumptions
- **Cons:** More complex prompt management, need to maintain multiple prompt templates

**Example:**
```python
def _get_system_prompt(language: str, task_type: str) -> str:
    prompts = {
        "vi": {
            "research": "Bạn là một chuyên gia nghiên cứu nội dung SEO. Chỉ phản hồi bằng JSON hợp lệ.",
            "outline": "Bạn là một chuyên gia chiến lược nội dung SEO. Chỉ phản hồi bằng JSON hợp lệ.",
            "content": "Bạn là một chuyên gia viết nội dung blog. Viết nội dung hấp dẫn, chi tiết, tối ưu hóa SEO."
        },
        "en": {
            "research": "You are an expert SEO content researcher. Respond only in valid JSON.",
            "outline": "You are an expert SEO content strategist. Respond only in valid JSON.",
            "content": "You are an expert blog content writer. Write engaging, detailed, SEO-optimized content."
        }
    }
    return prompts.get(language, {}).get(task_type, prompts["en"][task_type])
```

### Pattern 3: Default Value at Model Level

**What:** Language field defaults to Vietnamese in the Pydantic model, ensuring all posts have a language value.

**When to use:** When a field should always have a value and there's a sensible default.

**Trade-offs:**
- **Pros:** No null/undefined language values, consistent behavior
- **Cons:** Harder to change default later, requires migration if default changes

**Example:**
```python
class PostCreate(BaseModel):
    # ... other fields
    language: str = "vi"  # Vietnamese is default

class PostResponse(BaseModel):
    # ... other fields
    language: str = "vi"  # Vietnamese is default
```

## Data Flow

### Request Flow

```
[User selects Vietnamese in Create Post form]
    ↓
[Frontend sends POST /api/posts with language="vi"]
    ↓
[Backend creates Post document with language="vi"]
    ↓
[Backend queues research job with language="vi"]
    ↓
[Worker picks up research job]
    ↓
[Worker calls ai_service.research_topic(language="vi")]
    ↓
[AI generates research in Vietnamese]
    ↓
[Worker queues outline job with language="vi"]
    ↓
[Worker calls ai_service.generate_outline(language="vi")]
    ↓
[AI generates outline in Vietnamese]
    ↓
[Worker queues content job with language="vi"]
    ↓
[Worker calls ai_service.generate_full_content(language="vi")]
    ↓
[AI generates content in Vietnamese]
    ↓
[Worker queues publish job]
    ↓
[Worker calls wp_service.create_wp_post()]
    ↓
[Post published to WordPress in Vietnamese]
```

### State Management

```
[Post Document in MongoDB]
    ↓ (read by worker)
[Job Data with language="vi"]
    ↓ (passed to AI service)
[AI Service Functions]
    ↓ (use language for system prompts)
[Generated Content in Vietnamese]
    ↓ (stored back to Post)
[Post Document Updated with Vietnamese Content]
```

### Key Data Flows

1. **Language Selection Flow:** User selects language in form → Frontend state → API request → Post document → Job data → AI service calls
2. **Content Generation Flow:** Research (Vietnamese) → Outline (Vietnamese) → Content (Vietnamese) → Thumbnail (language-agnostic) → Publish
3. **Default Language Flow:** Pydantic model default → Frontend form default → All new posts default to Vietnamese

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Current architecture is sufficient. Language parameter adds minimal overhead. |
| 1k-100k users | Consider caching language-specific prompts. Add language-specific model selection if needed. |
| 100k+ users | Consider separate worker pools per language. Add language-specific rate limiting. |

### Scaling Priorities

1. **First bottleneck:** AI API rate limits. Language parameter doesn't change this, but Vietnamese generation may have different token costs.
2. **Second bottleneck:** MongoDB query performance. Adding language field doesn't significantly impact queries, but could add index if filtering by language becomes common.

## Anti-Patterns

### Anti-Pattern 1: Hardcoding Language in System Prompts

**What people do:** Keep English system prompts and rely on AI to infer language from topic.

**Why it's wrong:** AI may generate mixed language content, inconsistent output, poor Vietnamese quality.

**Do this instead:** Explicitly pass language parameter and use language-specific system prompts.

### Anti-Pattern 2: Storing Language at Project Level

**What people do:** Add language field to Project model and assume all posts in a project use the same language.

**Why it's wrong:** Users may want mixed-language posts within a single project (e.g., bilingual blog).

**Do this instead:** Store language at Post level, allowing per-post language selection.

### Anti-Pattern 3: Not Passing Language Through Worker Pipeline

**What people do:** Store language in Post document but don't pass it to worker jobs, expecting workers to read from Post document.

**Why it's wrong:** Workers may not have access to Post document at all times, adds unnecessary database reads, breaks job isolation.

**Do this instead:** Include language in job payload when queuing, pass explicitly to AI service calls.

### Anti-Pattern 4: Using English as Default Without User Awareness

**What people do:** Default to English but don't show language selector, users assume content will be in Vietnamese.

**Why it's wrong:** Poor UX, users surprised by English content, violates requirement that Vietnamese is default.

**Do this instead:** Default to Vietnamese, show language selector clearly, make default visible to users.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI API | Pass language in system prompt | OpenAI models support Vietnamese well, no special handling needed |
| Gemini API | Pass language in system prompt | Gemini models support Vietnamese, ensure prompts are clear |
| Anthropic API | Pass language in system prompt | Claude models support Vietnamese, may need more explicit instructions |
| WordPress REST API | No language parameter needed | WordPress stores content as-is, language is content metadata only |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ Backend API | HTTP POST with language field | Add `language` to request body, include in response |
| Backend Router ↔ Service Layer | Function parameter | Pass language as explicit parameter to AI service functions |
| Service Layer ↔ Worker Layer | Job payload | Include language in job data when queuing via Redis |
| Worker ↔ AI Service | Function parameter | Extract language from job data, pass to AI service calls |
| Worker ↔ MongoDB | Document field | Read/write language field in Post document |

## Build Order

Based on dependencies and integration points, recommended build order:

### Phase 1: Backend Model and API (Foundation)
1. **Update Post Model** (`backend/app/models/post.py`)
   - Add `language: str = "vi"` to `PostCreate`
   - Add `language: str = "vi"` to `PostResponse`
   - Add `language: str = "vi"` to `BulkPostCreate`

2. **Update Posts Router** (`backend/app/routers/posts.py`)
   - Update `create_post()` to handle language field
   - Update `create_bulk_posts()` to handle language field
   - Update `format_post()` to include language in response
   - Pass language to job payload in `publish_job()`

### Phase 2: AI Service Integration (Core Logic)
3. **Update AI Service** (`backend/app/services/ai_service.py`)
   - Add `language` parameter to `research_topic()`
   - Add `language` parameter to `generate_outline()`
   - Add `language` parameter to `generate_section_content()`
   - Add `language` parameter to `generate_introduction()`
   - Add `language` parameter to `generate_full_content()`
   - Implement `_get_system_prompt(language, task_type)` helper
   - Update all system prompts to be language-aware

4. **Update Job Service** (`backend/app/services/job_service.py`)
   - Add language to job payload when queuing

### Phase 3: Worker Pipeline Integration (Async Processing)
5. **Update Worker Tasks** (`worker/app/workers/tasks.py`)
   - Update `run_research()` to pass language to AI service
   - Update `run_outline()` to pass language to AI service
   - Update `run_content()` to pass language to AI service
   - Extract language from job data or post document

### Phase 4: Frontend UI (User Interface)
6. **Update Create Post Form** (`frontend/src/components/Projects/ProjectDetail.jsx`)
   - Add language state to `singleForm` and `bulkForm`
   - Add language selector (checkbox/radio) after title field
   - Default to Vietnamese (`"vi"`)
   - Pass language in API calls
   - Display language in post list/table

### Phase 5: Testing and Validation
7. **End-to-End Testing**
   - Test Vietnamese content generation
   - Test English content generation
   - Verify language persistence in database
   - Verify language flows through entire pipeline

## Data Model Changes

### Post Model Changes

```python
# backend/app/models/post.py

class PostCreate(BaseModel):
    project_id: str
    topic: str
    additional_requests: Optional[str] = ""
    ai_provider_id: Optional[str] = None
    model_name: Optional[str] = None
    auto_publish: bool = False
    thumbnail_source: str = "ai"
    thumbnail_provider_id: Optional[str] = None
    thumbnail_model_name: Optional[str] = None
    target_word_count: Optional[int] = None
    target_section_count: Optional[int] = None
    language: str = "vi"  # NEW: Vietnamese is default

class BulkPostCreate(BaseModel):
    project_id: str
    topics: List[str]
    additional_requests: Optional[str] = ""
    ai_provider_id: Optional[str] = None
    model_name: Optional[str] = None
    auto_publish: bool = False
    thumbnail_source: str = "ai"
    thumbnail_provider_id: Optional[str] = None
    thumbnail_model_name: Optional[str] = None
    target_word_count: Optional[int] = None
    target_section_count: Optional[int] = None
    language: str = "vi"  # NEW: Vietnamese is default

class PostResponse(BaseModel):
    id: str
    project_id: str
    topic: str
    additional_requests: str
    ai_provider_id: Optional[str] = None
    model_name: Optional[str] = None
    auto_publish: bool = False
    thumbnail_source: str = "ai"
    thumbnail_provider_id: Optional[str] = None
    thumbnail_model_name: Optional[str] = None
    target_word_count: Optional[int] = None
    target_section_count: Optional[int] = None
    language: str = "vi"  # NEW: Vietnamese is default
    title: Optional[str] = None
    meta_description: Optional[str] = None
    outline: Optional[Dict[str, Any]] = None
    sections: List[Section] = []
    content: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str = "draft"
    research_data: Optional[Dict[str, Any]] = None
    research_done: bool = False
    content_done: bool = False
    thumbnail_done: bool = False
    token_usage: TokenUsage = TokenUsage()
    jobs: List[JobInfo] = []
    created_at: datetime
    wp_post_id: Optional[int] = None
    wp_post_url: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    origin: str = "tool"
```

### Database Schema Changes

```python
# backend/app/database.py

# No index changes needed for language field
# Language is stored as a simple string field in Post documents
# Example Post document structure:
{
    "_id": ObjectId("..."),
    "project_id": "...",
    "topic": "How to improve website SEO",
    "language": "vi",  # NEW: "vi" for Vietnamese, "en" for English
    "additional_requests": "",
    "ai_provider_id": "...",
    "model_name": "gpt-4o",
    "auto_publish": false,
    "thumbnail_source": "ai",
    "target_word_count": 500,
    "target_section_count": 4,
    "title": "Cách cải thiện SEO website",
    "meta_description": "Hướng dẫn chi tiết...",
    "outline": {...},
    "sections": [...],
    "content": "<h2>Giới thiệu</h2>...",
    "thumbnail_url": "/tmp/wp_images/...",
    "status": "draft",
    "research_data": {...},
    "research_done": true,
    "content_done": true,
    "thumbnail_done": true,
    "token_usage": {...},
    "jobs": [...],
    "created_at": datetime(...),
    "wp_post_id": 123,
    "wp_post_url": "https://example.com/?p=123"
}
```

## Sources

- Existing codebase analysis: `backend/app/models/post.py`, `backend/app/services/ai_service.py`, `worker/app/workers/tasks.py`, `frontend/src/components/Projects/ProjectDetail.jsx`
- Project requirements: `.planning/PROJECT.md` (v1.2 Vietnamese Language Support milestone)
- FastAPI documentation: https://fastapi.tiangolo.com/
- Pydantic documentation: https://docs.pydantic.dev/
- React documentation: https://react.dev/

---
*Architecture research for: Vietnamese Language Support in WordPress Writer Tool*
*Researched: 2026-04-15*
