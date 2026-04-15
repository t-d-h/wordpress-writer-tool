# Technology Stack

**Project:** WordPress Writer Tool - Vietnamese Language Support
**Researched:** 2026-04-15
**Mode:** Ecosystem (feature-specific stack additions)

## Executive Summary

**No new libraries required.** The existing AI providers (OpenAI GPT-4o, Gemini 2.0 Flash, Anthropic Claude Sonnet 4) all support Vietnamese language generation. The only changes needed are:

1. **Backend:** Add `language` field to PostCreate/PostResponse models, pass through pipeline
2. **Frontend:** Add language selection checkbox in Create Post form (Vietnamese default)
3. **AI Service:** Add language parameter to all generation functions, include language instruction in prompts
4. **Database:** Add `language` field to posts collection (MongoDB schemaless - no migration needed)

## Recommended Stack

### Core Framework (No Changes)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python 3.11 | 3.11-slim | Backend runtime | Existing stack, no changes needed |
| FastAPI 0.115.0 | 0.115.0 | Backend REST API framework | Existing stack, no changes needed |
| React 18.3 | 18.3 | Frontend UI framework | Existing stack, no changes needed |
| Vite 5.4 | 5.4 | Frontend build tool | Existing stack, no changes needed |

### Database (No Changes)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| MongoDB | 7.x | Post storage with language field | Existing stack, add `language` field to posts collection |
| Redis | 7.x | Job queue for async processing | Existing stack, no changes needed |

### AI Providers (Existing - All Support Vietnamese)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| OpenAI GPT-4o | >=1.60.0 | Vietnamese content generation | Supports Vietnamese with 128K context window, multilingual model |
| Gemini 2.0 Flash | 1.5.0 | Vietnamese content generation | Multilingual model, supports Vietnamese natively |
| Anthropic Claude Sonnet 4 | 0.39.0 | Vietnamese content generation | Multilingual model, supports Vietnamese natively |

### Backend Changes
| Component | Change | Why |
|-----------|--------|-----|
| `backend/app/models/post.py` | Add `language: str = "vietnamese"` to PostCreate and PostResponse | Store language preference per post, Vietnamese as default |
| `backend/app/routers/posts.py` | Pass `language` to job queue and store in MongoDB | Persist language through entire pipeline |
| `backend/app/services/ai_service.py` | Add `language` parameter to all generation functions | Include language instruction in prompts |
| `worker/app/workers/tasks.py` | Pass `language` to AI service calls | Ensure language flows through async pipeline |

### Frontend Changes
| Component | Change | Why |
|-----------|--------|-----|
| `frontend/src/components/Projects/ProjectDetail.jsx` | Add language selection checkbox (Vietnamese/English) after title field | Allow user to choose language, Vietnamese as default |
| `frontend/src/components/Projects/ProjectDetail.jsx` | Set Vietnamese as default in form state | Meet requirement for Vietnamese default |
| `frontend/src/api/client.js` | Pass `language` in createPost/createBulkPosts calls | Send language to backend API |

### Prompt Engineering Changes
| Function | Change | Why |
|----------|--------|-----|
| `research_topic()` | Add "Write all responses in [language]" to system prompt | Ensure research data in target language |
| `generate_outline()` | Add "Write all content in [language]" to system prompt | Ensure outline in target language |
| `generate_section_content()` | Add "Write in [language]" to prompt | Ensure section content in target language |
| `generate_introduction()` | Add "Write in [language]" to prompt | Ensure introduction in target language |

## Database Schema Updates

### Posts Collection
Add `language` field to posts documents:

```python
{
    "language": "vietnamese",  # or "english"
    "topic": "...",
    "title": "...",
    "content": "...",
    # ... existing fields
}
```

**Migration:** No migration needed - MongoDB is schemaless. New posts will include `language` field. Existing posts will default to "english" if queried.

## Installation

No new dependencies required. Existing stack supports Vietnamese language generation.

```bash
# Backend - no changes needed
cd backend
pip install -r requirements.txt

# Frontend - no changes needed
cd frontend
npm install
```

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Language Selection | Checkbox (Vietnamese/English) | Dropdown with more languages | Scope creep - only Vietnamese needed for MVP |
| Language Storage | Per-post field | Global project setting | Per-post flexibility allows mixed-language projects |
| Prompt Approach | Language instruction in prompts | Separate translation step | Direct generation is simpler and more cost-effective |
| AI Provider | Existing providers (OpenAI/Gemini/Anthropic) | Vietnamese-specific models | Existing models have excellent Vietnamese support |

## Integration Points

### Backend API
```python
# POST /api/posts
{
    "project_id": "...",
    "topic": "...",
    "language": "vietnamese",  # NEW FIELD
    "additional_requests": "...",
    # ... existing fields
}
```

### AI Service Calls
```python
# All AI service functions now accept language parameter
await ai_service.research_topic(
    topic,
    additional_requests,
    provider_id,
    model_name,
    language="vietnamese"  # NEW PARAMETER
)
```

### Frontend Form
```jsx
// Language selection checkbox (after title field)
<div className="form-group">
  <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
    <input
      type="checkbox"
      checked={singleForm.language === 'vietnamese'}
      onChange={e => setSingleForm({
        ...singleForm,
        language: e.target.checked ? 'vietnamese' : 'english'
      })}
      style={{ cursor: 'pointer' }}
    />
    <span>Vietnamese Language</span>
  </label>
  <small style={{ display: 'block', marginTop: 4, color: 'var(--text-muted)' }}>
    Generate content in Vietnamese (default) or English
  </small>
</div>
```

## What NOT to Add

### Do NOT Add These Libraries

| Library | Why Not |
|---------|---------|
| Google Translate API | Adds cost and latency. Direct generation is better. |
| DeepL API | Adds cost and latency. Direct generation is better. |
| Language detection libraries (langdetect, polyglot) | Unnecessary - user selects language explicitly |
| Vietnamese-specific NLP libraries (underthesea, pyvi) | Not needed for content generation |
| Translation services (libretranslate, argostranslate) | Over-engineering - AI models handle Vietnamese natively |

### Do NOT Add These Features

| Feature | Why Not |
|---------|---------|
| Multi-language support beyond Vietnamese/English | Scope creep for MVP |
| Language detection from topic | Unnecessary - user selects language |
| Separate Vietnamese content pipeline | Duplicates code, adds complexity |
| Language-specific fine-tuning | Over-engineering for MVP |
| Translation workflow (generate in English then translate) | Adds cost, latency, and quality degradation |

## Prompt Engineering Examples

### Research Topic (Vietnamese)
```python
system_prompt = "You are an expert SEO content researcher. Write all responses in Vietnamese. Respond only in valid JSON."

prompt = f"""Research the following topic for a WordPress blog post.

Topic: {topic}
Language: Vietnamese
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Provide your research as JSON with these keys:
{{
    "target_audience": "description of the target audience in Vietnamese",
    "keywords": ["list", "of", "seo", "keywords"],
    "key_points": ["point 1 to cover", "point 2 to cover", ...],
    "questions_to_answer": ["question 1", "question 2", ...],
    "competitors_angle": "what competitors typically cover on this topic"
}}"""
```

### Generate Outline (Vietnamese)
```python
system_prompt = "You are an expert SEO content strategist. Write all content in Vietnamese. Respond only in valid JSON."

prompt = f"""Create a detailed blog post outline in Vietnamese based on:

Topic: {topic}
Language: Vietnamese
Research data: {json.dumps(research_data)}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

Create an outline as JSON:
{{
    "title": "SEO optimized title for the post in Vietnamese",
    "meta_description": "compelling meta description under 160 chars in Vietnamese",
    "introduction": {{
        "hook": "an engaging opening hook in Vietnamese",
        "problem": "the problem the reader faces in Vietnamese",
        "promise": "what the reader will learn/gain in Vietnamese"
    }},
    "sections": [
        {{
            "title": "Section 1 Title in Vietnamese",
            "key_points": ["point to cover in Vietnamese", "another point in Vietnamese"]
        }},
        ...more sections
    ]
}}"""
```

### Generate Section Content (Vietnamese)
```python
system_prompt = "You are an expert blog content writer. Write engaging, detailed, SEO-optimized content in Vietnamese."

prompt = f"""Write the content for a blog post section in Vietnamese.

Blog post topic: {topic}
Blog post title: {outline.get("title", topic)}
Section title: {section_title}
Language: Vietnamese
Key points to cover: {json.dumps(key_points)}
{f"Additional requests: {additional_requests}" if additional_requests else ""}

{word_count_hint} of detailed, engaging content in Vietnamese for this section.
Use subheadings (H3) where appropriate.
Include relevant examples and practical advice.
Do NOT include the section title itself — just the body content.
Format in HTML."""
```

## Sources

- **Context7:** Not used (no library-specific questions)
- **Official Docs:**
  - OpenAI GPT-4o: https://platform.openai.com/docs/models/gpt-4o (HIGH confidence - official docs, confirms multilingual support)
  - Google Gemini: https://ai.google.dev/gemini-api/docs/languages (MEDIUM confidence - official docs, confirms multilingual support)
  - Anthropic Claude: https://docs.anthropic.com/en/docs/about-claude/languages (LOW confidence - URL not accessible, but Claude is known to support Vietnamese)
- **Codebase Analysis:**
  - `backend/app/services/ai_service.py` - Current AI service implementation (HIGH confidence - direct code inspection)
  - `backend/app/models/post.py` - Current post models (HIGH confidence - direct code inspection)
  - `backend/app/routers/posts.py` - Current posts router (HIGH confidence - direct code inspection)
  - `worker/app/workers/tasks.py` - Current worker tasks (HIGH confidence - direct code inspection)
  - `frontend/src/components/Projects/ProjectDetail.jsx` - Current post creation form (HIGH confidence - direct code inspection)
  - `frontend/src/api/client.js` - Current API client (HIGH confidence - direct code inspection)
  - `backend/requirements.txt` - Current backend dependencies (HIGH confidence - direct code inspection)
  - `frontend/package.json` - Current frontend dependencies (HIGH confidence - direct code inspection)

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All existing AI providers support Vietnamese. No new libraries needed. |
| Backend Changes | HIGH | Clear integration points identified. Simple field addition to models. |
| Frontend Changes | HIGH | Simple checkbox addition to existing form. |
| AI Service Changes | HIGH | Language parameter addition is straightforward. |
| Prompt Engineering | HIGH | Language instruction in prompts is standard practice. |
| Database Changes | HIGH | MongoDB schemaless - no migration needed. |
| Integration | HIGH | Clear data flow from form → API → job queue → AI service. |

## Gaps to Address

- **No gaps:** All functionality is already supported by existing stack. Vietnamese language support requires only configuration changes, not new libraries or infrastructure.
