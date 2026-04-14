# Pitfalls

## Token Usage Display Pitfalls

### Performance Degradation with Large Projects
- **Warning signs**: Page load time increases significantly as post count grows, MongoDB queries take >1 second
- **Prevention strategy**: Use MongoDB aggregation pipeline with `$group` and `$sum` operators, add database indexes on `project_id` and `token_usage` fields, implement query result caching for frequently accessed projects
- **Phase to address**: Phase 1 (Token Usage Display)
- **Severity**: HIGH - affects user experience with real projects

### Incorrect Token Aggregation
- **Warning signs**: Token totals don't match individual post totals, missing token types in breakdown
- **Prevention strategy**: Validate aggregation pipeline against individual post calculations, write unit tests for aggregation logic, include deleted posts in aggregation query explicitly
- **Phase to address**: Phase 1 (Token Usage Display)
- **Severity**: MEDIUM - data accuracy issue

### Race Conditions in Token Updates
- **Warning signs**: Token counts fluctuate unexpectedly, concurrent job updates cause inconsistent totals
- **Prevention strategy**: Use MongoDB atomic operations for token updates, implement optimistic locking or versioning for post documents, ensure aggregation reads from consistent snapshot
- **Phase to address**: Phase 1 (Token Usage Display)
- **Severity**: MEDIUM - data consistency issue

## All Posts Tab Pitfalls

### WordPress API Rate Limiting
- **Warning signs**: API calls fail with 429 errors, post listing becomes slow or incomplete
- **Prevention strategy**: Implement request throttling and exponential backoff, cache WordPress post data in MongoDB, use pagination to limit API calls per request
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: HIGH - affects core functionality

### Inconsistent Post Origin Tracking
- **Warning signs**: Posts show wrong origin type, tool-created posts not distinguished from existing posts
- **Prevention strategy**: Store post origin flag in database when posts are created, implement merge logic to combine WordPress API data with database records, add validation to ensure origin tracking is consistent
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: MEDIUM - user experience issue

### Security Risks with WordPress Credentials
- **Warning signs**: WordPress credentials exposed in API responses, credentials stored in plain text
- **Prevention strategy**: Never expose WordPress credentials in API responses, encrypt credentials at rest, use application-specific passwords with limited permissions, implement credential rotation
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: CRITICAL - security vulnerability

### Performance Issues with Large Post Lists
- **Warning signs**: Page becomes unresponsive with >100 posts, filtering/sorting is slow
- **Prevention strategy**: Implement server-side pagination, use TanStack Table with virtualization for large datasets, add database indexes on post fields used for filtering/sorting, implement debouncing for search queries
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: HIGH - affects user experience

## General Architecture Pitfalls

### Tight Coupling Between Features
- **Warning signs**: Changes to token usage display break All Posts tab, shared state causes unexpected side effects
- **Prevention strategy**: Keep features in separate components with clear interfaces, use React context or state management for shared data, implement feature flags for gradual rollout
- **Phase to address**: All phases
- **Severity**: MEDIUM - maintainability issue

### Missing Error Handling
- **Warning signs**: Unhandled exceptions cause page crashes, error messages are not user-friendly
- **Prevention strategy**: Implement comprehensive error boundaries in React, add try-catch blocks around all async operations, provide meaningful error messages to users, log errors for debugging
- **Phase to address**: All phases
- **Severity**: MEDIUM - user experience issue

### Inconsistent State Management
- **Warning signs**: UI shows stale data, state updates don't reflect in all components
- **Prevention strategy**: Use single source of truth for state, implement proper state synchronization, add loading states to prevent race conditions, use React's built-in state management patterns
- **Phase to address**: All phases
- **Severity**: MEDIUM - data consistency issue

## WordPress Integration Pitfalls

### Authentication Failures
- **Warning signs**: WordPress API calls fail with 401 errors, credentials become invalid
- **Prevention strategy**: Implement credential validation before use, add automatic credential refresh, provide clear error messages when authentication fails, implement retry logic for transient auth failures
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: HIGH - affects core functionality

### API Version Compatibility
- **Warning signs**: WordPress API changes break integration, features work on some WordPress versions but not others
- **Prevention strategy**: Detect WordPress version and adapt API calls accordingly, implement feature detection rather than version detection, test with multiple WordPress versions, provide graceful degradation for unsupported features
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: MEDIUM - compatibility issue

### Network Timeout Issues
- **Warning signs**: API calls hang indefinitely, slow WordPress sites cause poor UX
- **Prevention strategy**: Implement reasonable timeout values for API calls, provide loading indicators for long-running operations, allow users to cancel pending requests, implement offline mode with cached data
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: MEDIUM - user experience issue

## Data Consistency Pitfalls

### Orphaned Post Records
- **Warning signs**: Posts exist in database but not in WordPress, deleted posts still counted in totals
- **Prevention strategy**: Implement sync mechanism to reconcile database with WordPress, add soft delete flag instead of hard delete, run periodic cleanup jobs, provide manual sync option for users
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: MEDIUM - data accuracy issue

### Duplicate Post Creation
- **Warning signs**: Same post created multiple times, duplicate entries in post lists
- **Prevention strategy**: Implement idempotent post creation, check for existing posts before creating, use WordPress post ID as unique identifier, add deduplication logic in merge operations
- **Phase to address**: Phase 2 (All Posts Tab)
- **Severity**: MEDIUM - data integrity issue

### Inconsistent Token Tracking
- **Warning signs**: Token counts don't match actual API usage, missing token types
- **Prevention strategy**: Validate token tracking against AI provider APIs, implement comprehensive logging for token usage, add reconciliation jobs to detect discrepancies, provide manual correction interface
- **Phase to address**: Phase 1 (Token Usage Display)
- **Severity**: MEDIUM - data accuracy issue

## Testing Pitfalls

### Missing Integration Tests
- **Warning signs**: Features work in isolation but fail when integrated, regressions introduced by changes
- **Prevention strategy**: Write integration tests for critical user flows, test with real WordPress instances, implement end-to-end testing for complete workflows, use test data that mirrors production
- **Phase to address**: All phases
- **Severity**: MEDIUM - quality assurance issue

### Inadequate Error Scenario Testing
- **Warning signs**: Application crashes on edge cases, error handling not tested
- **Prevention strategy**: Test with invalid WordPress credentials, simulate network failures, test with large datasets, test with malformed API responses, implement chaos testing for resilience
- **Phase to address**: All phases
- **Severity**: MEDIUM - reliability issue

### Performance Testing Gaps
- **Warning signs**: Performance degrades in production, slow queries not detected in development
- **Prevention strategy**: Implement performance benchmarks, test with realistic data volumes, profile database queries, monitor API response times, implement performance regression tests
- **Phase to address**: All phases
- **Severity**: MEDIUM - performance issue
