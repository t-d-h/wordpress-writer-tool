# Project Research Summary

**Project:** WordPress Writer Tool
**Domain:** AI Content Generation for WordPress
**Researched:** 2026-04-18
**Confidence:** HIGH

## Executive Summary

The WordPress Writer Tool is a full-stack AI content generation platform that enables users to create, validate, and publish content to WordPress sites. The system uses Python/FastAPI with MongoDB and Redis for the backend, and React for the frontend. Research indicates the project should focus on two primary improvement areas: (1) adding user authentication and multi-tenancy to secure the platform, and (2) improving content quality through validation, HTML cleaning, and better research data utilization.

The recommended approach is to implement JWT-based authentication using FastAPI's built-in security utilities, PyJWT for token handling, and pwdlib for password hashing. For content quality, implement BeautifulSoup4 + lxml for HTML sanitization, textstat for word count validation, and tolerance-based validation rather than strict enforcement. Key risks include over-engineering validation systems, breaking existing functionality during authentication integration, and AI models not consistently following word count or section count instructions. Mitigation strategies include using validation as warnings rather than blocks, maintaining backward compatibility, and implementing non-blocking validation checks.

## Key Findings

### Recommended Stack

**Authentication Stack:**
- FastAPI Security (built-in) — OAuth2 password flow and Bearer tokens, integrates with OpenAPI docs
- PyJWT >=2.8.0 — JWT token encoding/decoding, industry standard
- pwdlib >=1.7.0 — Password hashing with Argon2, modern and secure
- MongoDB (existing) — User account storage, async driver
- localStorage — JWT token storage, persists across sessions
- Axios (existing) — API client with token injection via interceptors
- React Router (existing) — Protected routes and login redirect

**Content Quality Stack:**
- lxml 6.0.4 — HTML sanitization and cleaning, production-stable, actively maintained
- BeautifulSoup4 4.14.3 — HTML parsing and text extraction, excellent for parsing HTML
- textstat 0.7.13 — Accurate word counting, handles edge cases better than split()
- Existing AI providers (OpenAI, Gemini, Anthropic) — Content generation

### Expected Features

**Must have (table stakes):**
- Clean HTML output — Users expect AI-generated content ready for WordPress without manual cleanup
- Accurate word count — Users specify target word counts and expect output to match within tolerance
- Accurate section count — Users specify target section counts and expect output to match within tolerance
- Research data utilization — Research phase should inform both outline and content generation
- No markdown artifacts — Users expect clean HTML, not markdown code blocks or backticks
- User authentication — Secure access control with username/password login
- Multi-tenant data isolation — Users can only access their own data

**Should have (competitive):**
- Content quality validation — Warn users when content doesn't meet specifications before publishing
- Quality score dashboard — Visual feedback on content quality metrics across all posts
- Validation result storage — Store validation results in post document for historical tracking

**Defer (v2+):**
- Auto-retry on validation failure — Adds complexity and cost, logging warnings sufficient for MVP
- Smart word count distribution — Requires AI to understand section importance
- Vietnamese-specific word counting — Requires NLP libraries, textstat is good enough
- Real-time quality monitoring — Requires WebSocket infrastructure
- Multi-factor authentication — Not needed for MVP
- Social login — Not in scope for MVP

### Architecture Approach

The system follows a layered architecture with clear separation of concerns. Backend uses FastAPI routers for HTTP endpoints, services for business logic, and Pydantic models for validation. Frontend uses React components with a centralized API client. Authentication adds an AuthContext for state management, ProtectedRoute wrappers for route security, and Axios interceptors for automatic token injection. All data is scoped by user_id to ensure multi-tenant isolation.

**Major components:**
1. AuthContext (Frontend) — Manages authentication state, token storage, login/logout
2. ProtectedRoute (Frontend) — Route wrapper that checks auth before rendering
3. Auth Middleware (Backend) — JWT validation and user context injection via FastAPI Depends()
4. User Service (Backend) — User CRUD, password hashing, authentication logic
5. Validation Service (Backend) — HTML cleaning, word count validation, section count validation
6. Users Collection (Database) — Stores user credentials with hashed passwords
7. All existing collections — Require user_id field for multi-tenant isolation

### Critical Pitfalls

1. **HTML Cleaning Issues** — AI-generated content contains markdown artifacts or malformed HTML. Prevent with BeautifulSoup4 + lxml, define clear whitelist of allowed tags, test with all AI providers.

2. **Word Count Validation Failures** — Validation doesn't account for Vietnamese word segmentation or tolerance thresholds. Prevent with textstat, implement tolerance-based validation (±20%), test with both English and Vietnamese.

3. **Research Data Not Utilized** — Content generation doesn't use research data, reducing content quality. Prevent by passing research_data to generate_full_content(), update prompts to include research context.

4. **Breaking Existing Functionality** — Authentication integration or validation changes break existing pipeline. Add validation as non-blocking checks, test with existing pipeline, maintain backward compatibility.

5. **Over-Engineering Validation** — Complex validation system adds overhead and maintenance burden. Keep validation simple with fixed tolerance thresholds, avoid per-user configuration.

6. **Missing User Context in Routes** — Routes that don't validate user context allow unauthorized data access. Always use Depends(get_current_user) on protected routes, filter all queries by user_id.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Authentication Foundation
**Rationale:** Authentication is foundational to multi-tenancy and must be implemented before user-scoped data can be enforced. This phase establishes the security infrastructure without breaking existing functionality.
**Delivers:** User service, auth router, JWT token generation, users collection, initial admin account
**Addresses:** User management, secure access control
**Avoids:** Storing passwords in plain text, hardcoded secret keys
**Uses:** FastAPI Security, PyJWT, pwdlib, MongoDB

### Phase 2: Content Quality Validation
**Rationale:** Content quality is the core value proposition. Implementing validation early ensures users get reliable content and provides immediate value.
**Delivers:** HTML cleaning with BeautifulSoup4, word count validation with textstat, section count validation, validation result storage
**Addresses:** Clean HTML output, accurate word/section counts, markdown artifact removal
**Avoids:** Strict enforcement anti-pattern, over-engineering validation
**Uses:** lxml, BeautifulSoup4, textstat

### Phase 3: User-Scoped Data Integration
**Rationale:** Once authentication is in place, all existing data must be migrated to user-scoped queries to ensure proper multi-tenancy.
**Delivers:** User_id field added to all collections, data migration script, updated queries with user_id filters, protected routes
**Addresses:** Data isolation, multi-tenant security
**Avoids:** Missing user context in routes, unauthorized data access
**Implements:** Auth middleware, user-scoped queries

### Phase 4: Research Data Utilization
**Rationale:** Research data should inform both outline and content generation to improve content quality and depth.
**Delivers:** Research data passed to content generation, updated prompts with research context, logging for research data usage
**Addresses:** Research data utilization, content quality improvement
**Avoids:** Research phase feeling disconnected from content

### Phase 5: Quality Dashboard & Reporting
**Rationale:** Once validation is working, provide visibility into quality metrics to help users understand content performance.
**Delivers:** Quality score calculation, validation result display, quality reports export
**Addresses:** Content quality validation, competitive differentiation
**Avoids:** Real-time monitoring complexity

### Phase Ordering Rationale

- Authentication first because it's foundational to multi-tenancy and data isolation
- Content quality validation second because it's the core value proposition and provides immediate user value
- User-scoped data integration third because it depends on authentication being in place
- Research data utilization fourth because it enhances existing functionality without breaking changes
- Quality dashboard fifth because it's a nice-to-have feature that builds on working validation

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (User-Scoped Data Integration):** Complex migration of existing data, needs careful planning to avoid data loss
- **Phase 4 (Research Data Utilization):** Requires prompt engineering research to effectively incorporate research data into content generation

Phases with standard patterns (skip research-phase):
- **Phase 1 (Authentication Foundation):** Well-documented FastAPI security patterns, official examples available
- **Phase 2 (Content Quality Validation):** Established libraries (BeautifulSoup4, textstat) with clear usage patterns
- **Phase 5 (Quality Dashboard):** Standard React dashboard patterns, no novel research needed

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Based on official FastAPI, PyJWT, pwdlib documentation and existing codebase analysis |
| Features | HIGH | Based on existing codebase analysis, WordPress requirements, and AI model limitations documentation |
| Architecture | HIGH | Based on FastAPI official docs, React Context patterns, and established authentication patterns |
| Pitfalls | HIGH | Based on existing codebase analysis, industry best practices, and WordPress content requirements |

**Overall confidence:** HIGH

### Gaps to Address

- **Vietnamese word counting accuracy:** textstat may not handle Vietnamese word segmentation perfectly. Test during implementation and consider underthesea or pyvi if accuracy is insufficient.
- **AI model adherence to instructions:** AI models may not consistently follow word count or section count instructions. Implement tolerance-based validation and log when instructions are not followed.
- **Performance impact of validation:** Monitor performance during implementation to ensure validation doesn't significantly slow down content generation.
- **HTML sanitization policy:** Need to define which HTML tags and attributes are allowed for WordPress content. Current whitelist is conservative.

## Sources

### Primary (HIGH confidence)
- FastAPI Security Tutorial — https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- FastAPI Dependencies — https://fastapi.tiangolo.com/tutorial/dependencies/
- pwdlib Documentation — https://pwdlib.readthedocs.io/
- PyJWT Documentation — https://pyjwt.readthedocs.io/
- React Context API — https://react.dev/learn/scaling-up-with-reducer-and-context
- Axios Interceptors — https://axios-http.com/docs/interceptors
- BeautifulSoup4 Documentation — https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- textstat Documentation — https://github.com/textstat/textstat
- WordPress REST API Documentation — https://developer.wordpress.org/rest-api/
- OpenAI API Documentation — https://platform.openai.com/docs/
- Google Gemini Documentation — https://ai.google.dev/docs
- Anthropic Documentation — https://docs.anthropic.com/
- Existing codebase analysis — backend/app/services/ai_service.py, backend/app/workers/tasks.py, backend/app/models/post.py

### Secondary (MEDIUM confidence)
- Content quality best practices — Industry standards for AI content generation
- HTML sanitization best practices — OWASP guidelines
- MongoDB Indexing — https://www.mongodb.com/docs/manual/indexes/

### Tertiary (LOW confidence)
- Vietnamese word segmentation libraries — underthesea, pyvi (needs validation during implementation)

---
*Research completed: 2026-04-18*
*Ready for roadmap: yes*
