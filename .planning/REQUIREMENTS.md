# Requirements: v1.2 Vietnamese Language Support

**Milestone**: v1.2
**Status**: Defined
**Last Updated**: 2026-04-15

## Overview

Add Vietnamese language support to the AI content generation pipeline. Users can choose between Vietnamese and English for each post, with Vietnamese as the default. All AI-generated content (research, outline, content) respects the language choice.

## In-Scope Requirements

### UI Requirements

#### LANG-01: Language Selection UI
**Priority**: High
**Description**: Add language selection radio buttons to the Create Post form
**Acceptance Criteria**:
- Radio buttons displayed after "Topic" field, before "Additional Requests"
- Two options: "Tiếng Việt" (Vietnamese) and "English"
- Vietnamese is selected by default
- Visual indication of selected language (radio button state)
**Notes**: Radio buttons (not checkbox) for mutually exclusive choice

#### LANG-02: Language Display in Post List
**Priority**: Medium
**Description**: Display language indicator in post list and detail views
**Acceptance Criteria**:
- Language badge shown in post list table
- Language badge shown in post detail view
- Badge uses color coding (e.g., green for Vietnamese, blue for English)
- Badge shows language name or icon
**Notes**: Helps users identify post language at a glance

### Backend Requirements

#### LANG-03: Language Field in Post Model
**Priority**: High
**Description**: Add `language` field to Post model and database
**Acceptance Criteria**:
- `language` field added to `PostCreate` Pydantic model
- `language` field added to `BulkPostCreate` Pydantic model
- `language` field stored in MongoDB posts collection
- Valid values: "vietnamese" or "english"
- Default value: "vietnamese"
- Existing posts without language field default to "english" for backward compatibility
**Notes**: MongoDB is schemaless, no migration needed

#### LANG-04: Language Parameter in AI Service
**Priority**: High
**Description**: Pass language parameter to all AI service functions
**Acceptance Criteria**:
- `research_topic()` accepts `language` parameter
- `generate_outline()` accepts `language` parameter
- `generate_section_content()` accepts `language` parameter
- `generate_introduction()` accepts `language` parameter
- Language parameter passed from job payload to AI service functions
- Language parameter logged at each stage for debugging
**Notes**: Language must flow through entire pipeline

#### LANG-05: Language-Specific System Prompts
**Priority**: High
**Description**: Modify system prompts to include language instruction
**Acceptance Criteria**:
- System prompts include explicit language instruction
- Vietnamese prompt: "Write all content in Vietnamese"
- English prompt: "Write all content in English"
- Prompts include cultural context for Vietnamese
- Prompts specify formality level (formal for Vietnamese)
- All AI providers (OpenAI, Gemini, Anthropic) use language-specific prompts
**Notes**: Test prompts with each AI provider

### Data Requirements

#### LANG-06: Language Persistence
**Priority**: Medium
**Description**: Persist language selection across form submissions
**Acceptance Criteria**:
- Language selection persists when form is submitted with errors
- Language selection persists when user navigates away and returns
- Language selection stored in localStorage or form state
- Language selection resets to default (Vietnamese) on page refresh
**Notes**: Simple localStorage implementation sufficient

#### LANG-07: Language in Job Payload
**Priority**: High
**Description**: Include language in job payload for all job types
**Acceptance Criteria**:
- `language` field included in research job payload
- `language` field included in outline job payload
- `language` field included in content job payload
- `language` field included in thumbnail job payload
- `language` field included in section_images job payload
- `language` field included in publish job payload
- Language field validated in job payload
**Notes**: Ensures language consistency across all stages

### Integration Requirements

#### LANG-08: Language Validation
**Priority**: Medium
**Description**: Validate language parameter in API endpoints
**Acceptance Criteria**:
- API validates language is "vietnamese" or "english"
- Invalid language returns 400 error with clear message
- Validation applied to POST /posts endpoint
- Validation applied to POST /posts/bulk endpoint
- Validation applied to PUT /posts/{id} endpoint
**Notes**: Use Pydantic validation

#### LANG-09: Backward Compatibility
**Priority**: Medium
**Description**: Handle existing posts without language field gracefully
**Acceptance Criteria**:
- API responses default to "english" for posts without language field
- Frontend displays "English" for posts without language field
- No errors when querying posts without language field
- No errors when updating posts without language field
**Notes**: MongoDB schemaless, no migration needed

## Future Requirements (Deferred)

### LANG-F01: Language-Specific SEO Optimization
**Priority**: Low
**Description**: Optimize content for Vietnamese SEO
**Notes**: Vietnamese SEO differs from English (keywords, meta descriptions, structure). Requires research into Vietnamese SEO best practices.

### LANG-F02: Tone/Style Customization per Language
**Priority**: Low
**Description**: Allow users to customize tone and style per language
**Notes**: Vietnamese content may need different tone than English content. Cultural nuances, formality levels in Vietnamese.

### LANG-F03: Language-Specific Content Length Targets
**Priority**: Low
**Description**: Adjust content length targets based on language
**Notes**: Vietnamese is more concise than English. May require different word counts for equivalent coverage.

### LANG-F04: Bilingual Content Generation
**Priority**: Low
**Description**: Generate both Vietnamese and English versions simultaneously
**Notes**: Complex workflow, may confuse users. Consider if users request this feature.

### LANG-F05: Language Quality Indicators
**Priority**: Low
**Description**: Show confidence scores for language quality
**Notes**: Requires additional AI evaluation. May be useful for quality assurance.

## Out of Scope

### LANG-O01: Per-User Language Preferences
**Reason**: Over-engineering for MVP, adds database complexity
**Alternative**: Use global default with per-post override

### LANG-O02: Per-Project Language Settings
**Reason**: Unnecessary complexity, users can override per-post
**Alternative**: Keep language selection at post level only

### LANG-O03: Multi-Language Dropdown (10+ Languages)
**Reason**: Confusing for Vietnamese-focused tool, dilutes value proposition
**Alternative**: Binary choice: Vietnamese/English only

### LANG-O04: Language Switching Mid-Generation
**Reason**: Breaks pipeline integrity, creates inconsistent content
**Alternative**: Language must be set before generation starts

### LANG-O05: Language-Specific AI Provider Routing
**Reason**: Unnecessary complexity, all providers support both languages
**Alternative**: Use same provider for both languages

## Traceability

| Requirement ID | Phase | Status |
|----------------|-------|--------|
| LANG-01 | TBD | Pending |
| LANG-02 | TBD | Pending |
| LANG-03 | TBD | Pending |
| LANG-04 | TBD | Pending |
| LANG-05 | TBD | Pending |
| LANG-06 | TBD | Pending |
| LANG-07 | TBD | Pending |
| LANG-08 | TBD | Pending |
| LANG-09 | TBD | Pending |

## Notes

- Vietnamese is a "low-resource" language with unique challenges (tonal structure, cultural context, limited training data)
- All existing AI providers (OpenAI GPT-4o, Gemini 2.0 Flash, Anthropic Claude Sonnet 4) support Vietnamese natively
- No new libraries required - implementation is configuration changes only
- Direct generation in target language (no translation workflow) is simpler and more cost-effective
- Test with Vietnamese speakers for cultural appropriateness
