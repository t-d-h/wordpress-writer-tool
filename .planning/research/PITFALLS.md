# Pitfalls

## Content Quality Improvements Pitfalls

### HTML Cleaning Issues

- **Warning signs:** AI-generated content contains markdown code blocks, backticks, or other artifacts; content appears broken in WordPress editor; users report content needs manual cleanup; HTML tags are malformed or nested incorrectly
- **Prevention strategy:** Implement BeautifulSoup4 + lxml for robust HTML sanitization; define clear whitelist of allowed HTML tags and attributes; test cleaning with all AI providers; log when cleaning removes content
- **Phase to address:** Phase 1 (HTML Cleaning)
- **Severity:** HIGH - affects core functionality and user experience

### Word Count Validation Failures

- **Warning signs:** Word count validation always fails or passes incorrectly; validation doesn't account for Vietnamese word segmentation; tolerance thresholds are too strict or too loose; users complain about inaccurate word counts
- **Prevention strategy:** Use textstat for accurate word counting; implement tolerance-based validation (±20%); test with both English and Vietnamese content; log validation results for debugging
- **Phase to address:** Phase 2 (Validation Functions)
- **Severity:** HIGH - affects core feature reliability

### Section Count Validation Failures

- **Warning signs:** Section count validation doesn't match actual outline structure; validation counts empty sections or ignores nested sections; tolerance thresholds are inappropriate; users report incorrect section counts
- **Prevention strategy:** Validate section count against outline structure (not content); implement tolerance-based validation (±1 section); handle edge cases (empty sections, nested sections); test with various outline structures
- **Phase to address:** Phase 2 (Validation Functions)
- **Severity:** MEDIUM - affects feature accuracy

### Research Data Not Utilized

- **Warning signs:** Content generation doesn't use research data; content quality is lower than expected; users report content lacks depth; research phase feels disconnected from content
- **Prevention strategy:** Pass research_data to generate_full_content(); update prompts to include research context; test that research data influences content; log when research data is missing or empty
- **Phase to address:** Phase 3 (Research Data Utilization)
- **Severity:** MEDIUM - affects content quality

### Additional Requests Not Honored

- **Warning signs:** AI ignores additional requests; content doesn't reflect user instructions; users report additional requests are ineffective; no mechanism to detect instruction adherence
- **Prevention strategy:** Log when additional_requests provided; add warning if AI output doesn't reflect requests; test with various additional request types; document known limitations
- **Phase to address:** Phase 4 (Additional Requests Validation)
- **Severity:** LOW - affects user experience but not functionality

### Integration Pitfalls with Existing Pipeline

- **Warning signs:** Validation functions break existing pipeline; content generation fails after adding validation; job processing errors increase; performance degrades significantly
- **Prevention strategy:** Add validation as non-blocking checks (log warnings, don't fail); test with existing pipeline; monitor performance impact; ensure backward compatibility
- **Phase to address:** All phases (integration testing)
- **Severity:** HIGH - affects system stability

### Vietnamese Word Counting Accuracy

- **Warning signs:** Word count validation is inaccurate for Vietnamese; textstat doesn't handle Vietnamese word segmentation; users report incorrect word counts for Vietnamese content
- **Prevention strategy:** Test textstat with Vietnamese content; if accuracy is insufficient, consider underthesea or pyvi; document Vietnamese-specific limitations; provide tolerance for Vietnamese content
- **Phase to address:** Phase 2 (Validation Functions)
- **Severity:** MEDIUM - affects feature accuracy for Vietnamese users

### HTML Sanitization Policy Issues

- **Warning signs:** Too much content is removed during sanitization; allowed tags are too restrictive; WordPress formatting is lost; users report content is over-sanitized
- **Prevention strategy:** Define clear whitelist based on WordPress requirements; test sanitization with sample content; allow common formatting tags (h1-h6, p, strong, em, ul, ol, li, a, img); log when content is removed
- **Phase to address:** Phase 1 (HTML Cleaning)
- **Severity:** MEDIUM - affects content quality

### Performance Concerns with Validation

- **Warning signs:** Content generation becomes significantly slower; validation adds noticeable delay; timeouts occur during generation; users report performance degradation
- **Prevention strategy:** Keep validation lightweight (word count, section count, HTML cleaning); avoid complex NLP operations; monitor performance metrics; optimize if needed
- **Phase to address:** All phases (performance monitoring)
- **Severity:** LOW - affects user experience but not functionality

### Backward Compatibility Issues

- **Warning signs:** Existing posts without validation fields; API calls fail for posts without validation; Frontend crashes when displaying validation results; Database queries fail for missing validation fields
- **Prevention strategy:** Handle missing validation fields gracefully; Default validation results to "not_validated"; Update frontend to display validation or default; Add database migration to populate validation fields for existing posts
- **Phase to address:** All phases (backward compatibility)
- **Severity:** MEDIUM - affects existing data

## General Architecture Pitfalls

### Over-Engineering Validation

- **Warning signs:** Complex validation system with multiple layers; Validation rules are configurable per user; Validation requires database lookups; Validation adds significant overhead
- **Prevention strategy:** Keep validation simple and consistent; Use fixed tolerance thresholds; Avoid per-user or per-project validation settings; Validation should be fast and lightweight
- **Phase to address:** All phases (design)
- **Severity:** LOW - affects maintainability

### Strict Enforcement Anti-Pattern

- **Warning signs:** Validation failures block content generation; Content is truncated or padded to meet targets; Users cannot publish content that doesn't meet validation; Validation is enforced rather than advisory
- **Prevention strategy:** Use validation as warnings, not blocks; Allow users to publish content that doesn't meet validation; Provide clear feedback on validation failures; Let users decide whether to regenerate
- **Phase to address:** All phases (design)
- **Severity:** MEDIUM - affects user experience

### Validation Result Storage Anti-Pattern

- **Warning signs:** Validation results stored in separate collection; Complex queries needed to retrieve validation; Validation results are not versioned; Validation results are lost when content is regenerated
- **Prevention strategy:** Store validation results in post document; Include validation timestamp; Allow validation results to be updated; Keep validation results simple (word_count, section_count, html_clean)
- **Phase to address:** Phase 2 (Validation Functions)
- **Severity:** LOW - affects data model

## Sources

- **Existing codebase analysis** — backend/app/services/ai_service.py, backend/app/workers/tasks.py, backend/app/models/post.py - HIGH confidence (direct code inspection)
- **Content quality best practices** — Industry standards for AI content generation - MEDIUM confidence (general knowledge)
- **WordPress content requirements** — WordPress REST API documentation - HIGH confidence (official documentation)
- **AI model limitations** — OpenAI, Gemini, Anthropic documentation - HIGH confidence (official documentation)
- **HTML sanitization best practices** — OWASP guidelines, lxml documentation - HIGH confidence (official documentation)
- **Text analysis libraries** — textstat documentation, BeautifulSoup4 documentation - HIGH confidence (official documentation)
