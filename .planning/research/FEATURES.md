# Feature Research

**Domain:** AI Content Generation Quality Improvements
**Researched:** 2026-04-16
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Clean HTML output** | Users expect AI-generated content to be ready for WordPress without manual cleanup | MEDIUM | Current implementation has basic JSON cleaning but no HTML sanitization. AI often outputs markdown code blocks, backticks, and other artifacts that need removal. |
| **Accurate word count** | Users specify target word counts and expect the output to match | MEDIUM | Current implementation divides target word count by section count but doesn't validate actual output. AI may ignore word count instructions. |
| **Accurate section count** | Users specify target section counts and expect the output to match | LOW | Current implementation passes `target_section_count` to outline generation but doesn't validate actual output. AI may ignore section count instructions. |
| **Research data utilization** | Users expect research phase to inform outline and content generation | MEDIUM | Current implementation passes research data to outline generation but NOT to content generation. Content only uses outline, not original research. |
| **Additional requests honored** | Users expect additional instructions to be applied throughout the pipeline | LOW | Current implementation passes `additional_requests` to all generation functions, but AI may not consistently follow them. |
| **No markdown artifacts** | Users expect clean HTML, not markdown code blocks or backticks | MEDIUM | Current implementation has basic JSON cleaning but no HTML output cleaning. AI often wraps HTML in markdown code blocks. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Content quality validation** | Warn users when content doesn't meet specifications before publishing | MEDIUM | Add validation checks for word count, section count, and HTML cleanliness. Store validation results in post document. |
| **Quality score dashboard** | Visual feedback on content quality metrics (word count accuracy, section count accuracy, HTML cleanliness) | HIGH | Aggregate validation results across posts to show quality trends. Requires frontend UI changes. |
| **Auto-retry on validation failure** | Automatically regenerate content that doesn't meet specifications | HIGH | Adds complexity and cost. For MVP, logging warnings is sufficient. |
| **Content quality reports** | Export quality metrics for analysis and improvement | MEDIUM | Generate reports showing validation results across all posts. Useful for content strategy optimization. |
| **Smart word count distribution** | Distribute word count intelligently based on section importance rather than equal division | HIGH | Requires AI to understand section importance. Current equal division is simpler but may not be optimal. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Strict word count enforcement** | Users want exact word counts | AI models cannot guarantee exact word counts. Enforcement requires truncation or padding, which degrades quality. | Use tolerance-based validation (±20%) and warn users when outside tolerance. |
| **Strict section count enforcement** | Users want exact section counts | AI models cannot guarantee exact section counts. Enforcement requires artificial section splitting or merging, which degrades quality. | Use tolerance-based validation (±1 section) and warn users when outside tolerance. |
| **Real-time quality monitoring** | Users want to see quality metrics as content generates | Adds complexity to async job processing. Requires WebSocket or polling infrastructure. | Show quality metrics after generation completes. |
| **Content regeneration on validation failure** | Users want automatic fixes | Adds cost and complexity. May not converge on valid content. | Log warnings and let users decide whether to regenerate. |
| **Vietnamese-specific word counting** | Users want accurate Vietnamese word counts | Requires NLP libraries (underthesea, pyvi) that add dependencies and complexity. | Use textstat for approximate word counting. Good enough for validation. |

## Feature Dependencies

```
[HTML Cleaning]
    └──requires──> [BeautifulSoup4]
                   └──requires──> [lxml]

[Word Count Validation]
    └──requires──> [textstat]

[Section Count Validation]
    └──requires──> [Outline Structure]

[Content Quality Validation]
    └──requires──> [HTML Cleaning]
    └──requires──> [Word Count Validation]
    └──requires──> [Section Count Validation]

[Research Data Utilization]
    └──enhances──> [Outline Generation]
    └──enhances──> [Content Generation]

[Additional Requests]
    └──enhances──> [All Generation Functions]
```

### Dependency Notes

- **[HTML Cleaning] requires [BeautifulSoup4] and [lxml]:** BeautifulSoup4 provides HTML parsing and text extraction. lxml provides HTML sanitization and cleaning. Both are needed for robust content cleaning.
- **[Word Count Validation] requires [textstat]:** textstat provides accurate word counting that handles edge cases (punctuation, hyphens, etc.) better than simple split().
- **[Section Count Validation] requires [Outline Structure]:** Validation counts sections in the outline structure. Requires outline to be generated first.
- **[Content Quality Validation] requires [HTML Cleaning], [Word Count Validation], [Section Count Validation]:** Quality validation combines multiple checks. All must be implemented first.
- **[Research Data Utilization] enhances [Outline Generation] and [Content Generation]:** Research data should inform both outline and content generation. Currently only used for outline.
- **[Additional Requests] enhances [All Generation Functions]:** Additional requests should be applied consistently across all generation functions. Currently passed but not validated.

## MVP Definition

### Launch With (v1.3)

Minimum viable product — what's needed to validate the concept.

- [ ] **HTML Cleaning** — Remove unwanted characters (backticks, markdown artifacts) from AI-generated content. Essential for WordPress compatibility.
- [ ] **Word Count Validation** — Validate actual word count against target with ±20% tolerance. Warn users when outside tolerance.
- [ ] **Section Count Validation** — Validate actual section count against target with ±1 section tolerance. Warn users when outside tolerance.
- [ ] **Research Data Utilization** — Pass research data to content generation (not just outline). Ensures research informs final content.
- [ ] **Additional Requests Validation** — Log when additional requests are provided but AI may not have followed them.

### Add After Validation (v1.4)

Features to add once core is working.

- [ ] **Content Quality Dashboard** — Visual feedback on quality metrics across all posts.
- [ ] **Quality Score Calculation** — Aggregate validation results into a single quality score.
- [ ] **Validation Result Storage** — Store validation results in post document for historical tracking.
- [ ] **Quality Reports** — Export quality metrics for analysis.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Auto-Retry on Validation Failure** — Automatically regenerate content that doesn't meet specifications.
- [ ] **Smart Word Count Distribution** — Distribute word count based on section importance rather than equal division.
- [ ] **Vietnamese-Specific Word Counting** — Use underthesea or pyvi for accurate Vietnamese word segmentation.
- [ ] **Real-Time Quality Monitoring** — Show quality metrics as content generates via WebSocket.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| HTML Cleaning | HIGH | MEDIUM | P1 |
| Word Count Validation | HIGH | MEDIUM | P1 |
| Section Count Validation | HIGH | LOW | P1 |
| Research Data Utilization | MEDIUM | MEDIUM | P1 |
| Additional Requests Validation | MEDIUM | LOW | P2 |
| Content Quality Dashboard | MEDIUM | HIGH | P2 |
| Quality Score Calculation | MEDIUM | MEDIUM | P2 |
| Validation Result Storage | MEDIUM | LOW | P2 |
| Quality Reports | LOW | MEDIUM | P3 |
| Auto-Retry on Validation Failure | LOW | HIGH | P3 |
| Smart Word Count Distribution | LOW | HIGH | P3 |
| Vietnamese-Specific Word Counting | LOW | MEDIUM | P3 |
| Real-Time Quality Monitoring | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch (v1.3)
- P2: Should have, add when possible (v1.4)
- P3: Nice to have, future consideration (v2+)

## Competitor Feature Analysis

| Feature | Competitor A (Jasper) | Competitor B (Copy.ai) | Our Approach |
|---------|--------------|--------------|--------------|
| HTML Cleaning | Built-in content sanitization | Basic markdown removal | BeautifulSoup4 + lxml for robust cleaning |
| Word Count Validation | Exact word count enforcement | Approximate word count | Tolerance-based validation (±20%) |
| Section Count Validation | Not available | Not available | Tolerance-based validation (±1 section) |
| Research Data Utilization | Research phase informs all content | Research phase separate from content | Pass research data to both outline and content |
| Additional Requests | Applied consistently | Applied inconsistently | Log when AI may not have followed requests |
| Quality Dashboard | Advanced quality metrics | Basic quality metrics | Simple validation results display |

## Sources

- **Existing codebase analysis** — backend/app/services/ai_service.py, backend/app/workers/tasks.py, backend/app/models/post.py - HIGH confidence (direct code inspection)
- **Content quality best practices** — Industry standards for AI content generation - MEDIUM confidence (general knowledge)
- **WordPress content requirements** — WordPress REST API documentation - HIGH confidence (official documentation)
- **AI model limitations** — OpenAI, Gemini, Anthropic documentation - HIGH confidence (official documentation)

---
*Feature research for: WordPress Writer Tool v1.3 Content Quality Improvements*
*Researched: 2026-04-16*
