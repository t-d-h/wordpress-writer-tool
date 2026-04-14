# Concerns

## Technical Debt

### Credential Storage
- **Location**: `backend/app/models/wp_site.py`, `backend/app/routers/wp_sites.py`
- **Issue**: WordPress credentials (username + application password) stored in plain text in MongoDB
- **Impact**: Security risk if database is compromised
- **Recommendation**: Encrypt credentials at rest using encryption keys

### Error Handling
- **Location**: All routers and services
- **Issue**: Inconsistent error handling, some exceptions raised as `Exception` without specific types
- **Impact**: Difficult to debug and handle errors gracefully
- **Recommendation**: Define custom exception classes for common error scenarios

### No App-Level Authentication
- **Location**: `backend/app/main.py`
- **Issue**: No authentication middleware, relies on network-level isolation
- **Impact**: Security risk if exposed to public internet
- **Recommendation**: Add JWT or API key authentication for production use

## Known Issues

### Missing Validation
- **Location**: `backend/app/routers/wp_sites.py`
- **Issue**: WordPress site creation has no validation (URL format, connectivity, credentials)
- **Impact**: Invalid sites can be saved, errors only discovered during publishing
- **Recommendation**: Add validation before saving (URL format, connectivity test, credential verification)

### No Periodic Re-validation
- **Location**: WordPress site management
- **Issue**: Saved WordPress sites are never re-validated
- **Impact**: Credentials may expire or sites may become unreachable
- **Recommendation**: Add periodic re-validation or user-triggered validation

### Token Usage Tracking
- **Location**: `backend/app/models/post.py`, `backend/app/services/ai_service.py`
- **Issue**: Token usage tracked per job but not aggregated at project level
- **Impact**: No visibility into total token usage per project
- **Recommendation**: Add project-level token aggregation and display

## Security Concerns

### CORS Configuration
- **Location**: `backend/app/main.py`
- **Issue**: CORS allows all origins (`allow_origins=["*"]`)
- **Impact**: Any domain can make API requests
- **Recommendation**: Restrict to specific frontend domains in production

### API Key Exposure
- **Location**: `backend/app/routers/ai_providers.py`
- **Issue**: API keys returned in responses (masked with preview pattern)
- **Impact**: Keys visible in API responses (even if masked)
- **Recommendation**: Never return API keys in responses, only store and use internally

### No Rate Limiting
- **Location**: All API endpoints
- **Issue**: No rate limiting on API endpoints
- **Impact**: Vulnerable to abuse and DoS attacks
- **Recommendation**: Add rate limiting middleware

## Performance Concerns

### No Caching
- **Location**: All API endpoints
- **Issue**: No caching layer for frequently accessed data
- **Impact**: Unnecessary database queries and external API calls
- **Recommendation**: Add Redis caching for WordPress site data, AI provider configs

### Synchronous External API Calls
- **Location**: `backend/app/services/wp_service.py`, `backend/app/services/ai_service.py`
- **Issue**: External API calls are synchronous within async functions
- **Impact**: Blocks event loop during long-running requests
- **Recommendation**: Ensure all external calls use async HTTP clients (httpx)

### No Pagination
- **Location**: `backend/app/routers/posts.py`, `backend/app/routers/projects.py`
- **Issue**: List endpoints return all records without pagination
- **Impact**: Performance issues with large datasets
- **Recommendation**: Add pagination with limit/offset parameters

## Fragile Areas

### Job System Error Recovery
- **Location**: `backend/app/workers/tasks.py`
- **Issue**: Failed jobs are marked but no retry mechanism
- **Impact**: Transient failures cause permanent job failure
- **Recommendation**: Add exponential backoff retry for transient failures

### WordPress API Compatibility
- **Location**: `backend/app/services/wp_service.py`
- **Issue**: Assumes WordPress REST API structure, may break with different versions
- **Impact**: Integration failures with non-standard WordPress installations
- **Recommendation**: Add version detection and compatibility checks

### AI Provider Failover
- **Location**: `backend/app/services/ai_service.py`
- **Issue**: No failover if primary AI provider fails
- **Impact**: Single point of failure for AI operations
- **Recommendation**: Add provider failover and load balancing

## Missing Features

### All Posts Tab
- **Location**: Frontend
- **Issue**: No "All Posts" tab to view all WordPress site posts
- **Impact**: Users cannot see existing posts or edit them
- **Recommendation**: Add All Posts component with post listing and edit links

### Post Editing
- **Location**: Frontend
- **Issue**: No ability to edit posts after creation
- **Impact**: Users must use WordPress admin for edits
- **Recommendation**: Add post editing interface or deep links to WordPress admin

### Bulk Operations
- **Location**: Post management
- **Issue**: No bulk post creation or management
- **Impact**: Inefficient for creating multiple posts
- **Recommendation**: Add bulk post creation and management features
