# Requirements: v1.3 Content Quality Improvements

**Milestone**: v1.3
**Status**: Defined
**Last Updated**: 2026-04-16

## Overview

Fix content generation issues to improve output quality and ensure AI-generated content meets user specifications. This milestone focuses on HTML cleaning, validation (word count and section count), and pipeline integration (research data utilization).

## In-Scope Requirements

### HTML Cleaning

#### HTML-01: Clean HTML Output
**Priority**: High
**Description**: Remove unwanted characters (backticks, markdown artifacts) from AI-generated content
**Acceptance Criteria**:
- System removes backticks from AI-generated content
- System removes markdown code blocks wrapping HTML
- System removes markdown artifacts from final content
- Content is ready for WordPress without manual cleanup
- HTML cleaning applied to all AI-generated content (research, outline, content)
**Notes**: Use BeautifulSoup4 + lxml for robust HTML sanitization

#### HTML-02: No Markdown Artifacts
**Priority**: High
**Description**: Ensure content doesn't contain markdown code blocks or backticks
**Acceptance Criteria**:
- Final content doesn't contain markdown code blocks (```html or ```)
- Final content doesn't contain backticks wrapping HTML
- Content displays correctly in WordPress editor
- No manual cleanup needed by users
**Notes**: AI often wraps HTML in markdown code blocks that need removal

#### HTML-03: HTML Sanitization
**Priority**: Medium
**Description**: Implement HTML sanitization with allowed tags whitelist
**Acceptance Criteria**:
- System sanitizes HTML content before saving
- Whitelist of allowed HTML tags defined (h1-h6, p, strong, em, ul, ol, li, a, img)
- Malicious or unwanted tags removed
- Content structure preserved
**Notes**: Define whitelist based on WordPress requirements

### Validation

#### VAL-01: Word Count Validation
**Priority**: High
**Description**: Validate actual word count against target word count
**Acceptance Criteria**:
- System calculates actual word count using textstat
- System compares actual word count to target word count
- Validation uses ±20% tolerance
- System warns user when outside tolerance
- Validation results stored in post document
**Notes**: Use textstat for accurate word counting

#### VAL-02: Section Count Validation
**Priority**: High
**Description**: Validate actual section count against target section count
**Acceptance Criteria**:
- System counts sections in outline structure
- System compares actual section count to target section count
- Validation uses ±1 section tolerance
- System warns user when outside tolerance
- Validation results stored in post document
**Notes**: Validate section count against outline structure (not content)

#### VAL-03: Validation Results Display
**Priority**: Medium
**Description**: Display validation results to users
**Acceptance Criteria**:
- Word count validation results shown in post detail view
- Section count validation results shown in post detail view
- HTML cleanliness status shown in post detail view
- Clear visual indication when validation fails
- Users can see actual vs target values
**Notes**: Validation is advisory, not blocking

#### VAL-04: Validation Warnings
**Priority**: Medium
**Description**: Log warnings when content doesn't meet validation criteria
**Acceptance Criteria**:
- System logs warning when word count validation fails
- System logs warning when section count validation fails
- System logs warning when HTML cleaning removes content
- Warnings include actual vs target values
- Warnings stored in job logs for debugging
**Notes**: Validation is non-blocking, content is still saved

#### VAL-05: Tolerance-Based Validation
**Priority**: Medium
**Description**: Implement tolerance-based validation instead of strict enforcement
**Acceptance Criteria**:
- Word count validation uses ±20% tolerance
- Section count validation uses ±1 section tolerance
- Validation passes when within tolerance
- Validation fails when outside tolerance
- Users can publish content that doesn't meet validation
**Notes**: AI models cannot guarantee exact specifications

### Pipeline Integration

#### PIPE-01: Research Data Utilization
**Priority**: High
**Description**: Pass research data to content generation (not just outline)
**Acceptance Criteria**:
- System passes research_data to generate_full_content()
- Content generation prompts include research context
- Research data influences final content generation
- Content quality improves with research data
**Notes**: Currently research data only used for outline generation

#### PIPE-02: Research Context in Prompts
**Priority**: Medium
**Description**: Update prompts to include research context
**Acceptance Criteria**:
- Content generation prompts include research summary
- Prompts reference research findings
- AI uses research data to inform content
- Content depth improves with research context
**Notes**: Test that research data actually influences content

#### PIPE-03: Research Data Flow
**Priority**: Medium
**Description**: Ensure research data flows through entire pipeline
**Acceptance Criteria**:
- Research data stored in post document
- Research data passed to outline generation
- Research data passed to content generation
- Research data logged at each stage for debugging
- Research data not lost between pipeline stages
**Notes**: Research data must be consistent across all stages

## Future Requirements (Deferred)

### HTML Cleaning (Deferred)

#### HTML-F01: Content Quality Dashboard
**Priority**: Low
**Description**: Visual feedback on quality metrics across all posts
**Notes**: Aggregate validation results across posts to show quality trends. Requires frontend UI changes.

#### HTML-F02: Quality Score Calculation
**Priority**: Low
**Description**: Aggregate validation results into a single quality score
**Notes**: Combine word count, section count, and HTML cleanliness into a score.

#### HTML-F03: Validation Result Storage
**Priority**: Low
**Description**: Store validation results in post document for historical tracking
**Notes**: Track validation results over time for quality analysis.

### Validation (Deferred)

#### VAL-F01: Auto-Retry on Validation Failure
**Priority**: Low
**Description**: Automatically regenerate content that doesn't meet specifications
**Notes**: Adds complexity and cost. For MVP, logging warnings is sufficient.

#### VAL-F02: Smart Word Count Distribution
**Priority**: Low
**Description**: Distribute word count based on section importance rather than equal division
**Notes**: Requires AI to understand section importance. Current equal division is simpler.

#### VAL-F03: Vietnamese-Specific Word Counting
**Priority**: Low
**Description**: Use underthesea or pyvi for accurate Vietnamese word segmentation
**Notes**: textstat may not handle Vietnamese word segmentation perfectly.

### Pipeline Integration (Deferred)

#### PIPE-F01: Additional Requests Validation
**Priority**: Low
**Description**: Log when additional requests are provided but AI may not have followed them
**Notes**: Add warning if AI output doesn't reflect requests.

#### PIPE-F02: Real-Time Quality Monitoring
**Priority**: Low
**Description**: Show quality metrics as content generates via WebSocket
**Notes**: Adds complexity to async job processing. Show after generation completes.

## Out of Scope

### HTML-O01: Strict Word Count Enforcement
**Reason**: AI models cannot guarantee exact word counts. Enforcement requires truncation or padding, which degrades quality.
**Alternative**: Use tolerance-based validation (±20%) and warn users when outside tolerance.

### HTML-O02: Strict Section Count Enforcement
**Reason**: AI models cannot guarantee exact section counts. Enforcement requires artificial section splitting or merging, which degrades quality.
**Alternative**: Use tolerance-based validation (±1 section) and warn users when outside tolerance.

### HTML-O03: Real-Time Quality Monitoring
**Reason**: Adds complexity to async job processing. Requires WebSocket or polling infrastructure.
**Alternative**: Show quality metrics after generation completes.

### HTML-O04: Content Regeneration on Validation Failure
**Reason**: Adds cost and complexity. May not converge on valid content.
**Alternative**: Log warnings and let users decide whether to regenerate.

### HTML-O05: Vietnamese-Specific Word Counting
**Reason**: Requires NLP libraries (underthesea, pyvi) that add dependencies and complexity.
**Alternative**: Use textstat for approximate word counting. Good enough for validation.

## Traceability

| Requirement ID | Phase | Status |
|----------------|-------|--------|
| HTML-01 | TBD | Pending |
| HTML-02 | TBD | Pending |
| HTML-03 | TBD | Pending |
| VAL-01 | TBD | Pending |
| VAL-02 | TBD | Pending |
| VAL-03 | TBD | Pending |
| VAL-04 | TBD | Pending |
| VAL-05 | TBD | Pending |
| PIPE-01 | TBD | Pending |
| PIPE-02 | TBD | Pending |
| PIPE-03 | TBD | Pending |

## Notes

- Three new libraries required: lxml 6.0.4 (HTML sanitization), BeautifulSoup4 4.14.3 (HTML parsing), textstat 0.7.13 (word counting)
- Current implementation has gaps: research data not passed to content generation, no validation for word/section counts, incomplete HTML cleaning
- Validation is advisory, not blocking. Users can publish content that doesn't meet validation criteria.
- HTML cleaning must come before validation to ensure accurate counts.
- Research data utilization enhances content quality by providing context to AI.
- Vietnamese word counting may need underthesea or pyvi if textstat proves inaccurate.
