# Feature Landscape

**Domain:** Vietnamese language support for AI content generation
**Researched:** 2026-04-15

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Language selection UI (checkbox/radio) | Users need to choose between Vietnamese and English for each post | Low | Simple binary choice, fits existing form pattern |
| Default language setting (Vietnamese) | Vietnamese is the primary target market, should be the default | Low | Global default, no per-user complexity needed |
| Language persistence across sessions | Users shouldn't have to reselect language every time | Low | Store in localStorage or form state |
| Language passed through content pipeline | All AI-generated content (research, outline, content) must respect language choice | Medium | Requires modifying AI service functions to accept language parameter |
| Visual indication of selected language | Users need to see which language is currently selected | Low | Simple UI feedback, checkbox/radio button state |
| Language-specific prompts | AI models need explicit language instructions to generate content correctly | Medium | System prompts need language parameter |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Language-specific SEO optimization | Vietnamese SEO differs from English (keywords, meta descriptions, structure) | High | Requires research into Vietnamese SEO best practices |
| Tone/style customization per language | Vietnamese content may need different tone than English content | High | Cultural nuances, formality levels in Vietnamese |
| Language-specific content length targets | Vietnamese content may require different word counts for equivalent coverage | Medium | Vietnamese is more concise than English |
| Bilingual content generation | Generate both Vietnamese and English versions simultaneously | High | Complex workflow, may confuse users |
| Language quality indicators | Show confidence scores for language quality | Medium | Requires additional AI evaluation |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Per-user language preferences | Over-engineering for MVP, adds database complexity | Use global default with per-post override |
| Per-project language settings | Unnecessary complexity, users can override per-post | Keep language selection at post level only |
| Multi-language dropdown (10+ languages) | Confusing for Vietnamese-focused tool, dilutes value proposition | Binary choice: Vietnamese/English only |
| Language switching mid-generation | Breaks pipeline integrity, creates inconsistent content | Language must be set before generation starts |
| Language-specific AI provider routing | Unnecessary complexity, all providers support both languages | Use same provider for both languages |

## Feature Dependencies

```
Language selection UI → Language parameter in PostCreate model → Language passed to AI service functions → Language-specific system prompts → Content generated in selected language
```

## MVP Recommendation

Prioritize:
1. **Language selection checkbox** (Vietnamese/English) in Create post form after title field
2. **Vietnamese as default language** globally (form initialization)
3. **Language parameter flow** through content pipeline (research → outline → content)
4. **Language-specific system prompts** in AI service functions

Defer:
- Language-specific SEO optimization: Can be added in future milestone
- Tone/style customization: Not needed for MVP
- Bilingual content generation: Over-engineering for current needs

## Implementation Notes

### UI Pattern Recommendation
- **Radio buttons** (not checkbox) for language selection
- Placement: After "Topic" field, before "Additional Requests"
- Default: Vietnamese selected
- Labels: "Tiếng Việt" (Vietnamese) and "English"

### Backend Integration
- Add `language` field to `PostCreate` and `BulkPostCreate` models
- Add `language` parameter to AI service functions:
  - `research_topic()`
  - `generate_outline()`
  - `generate_section_content()`
  - `generate_introduction()`
- Modify system prompts to include language instruction

### System Prompt Pattern
```python
# Vietnamese
system_prompt = "You are an expert blog content writer. Write engaging, detailed, SEO-optimized content in Vietnamese."

# English
system_prompt = "You are an expert blog content writer. Write engaging, detailed, SEO-optimized content in English."
```

### Data Storage
- Store `language` field in MongoDB posts collection
- Values: "vietnamese" or "english"
- Default: "vietnamese"

### Vietnamese-Specific Considerations
- Vietnamese uses diacritics (accented characters)
- Word order differs from English
- Cultural context matters for content
- SEO keywords in Vietnamese may differ from English translations

## Sources

- OpenAI API documentation (text generation, prompt engineering) - HIGH confidence
- Anthropic API documentation (models overview, multilingual capabilities) - HIGH confidence
- Existing WordPress Writer Tool codebase (Create post form, AI service, Post model) - HIGH confidence
- Vietnamese language characteristics (linguistic knowledge) - MEDIUM confidence
