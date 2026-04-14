# Feature Landscape

**Domain:** WordPress AI Content Generation Tool
**Researched:** 2026-04-14
**Overall confidence:** HIGH

## Executive Summary

WordPress content management tools have evolved from simple post editors to comprehensive platforms with AI-powered content generation, SEO optimization, and multi-site management. Based on research of leading plugins (Jetpack, Yoast SEO, WP All Import, WordLift) and the WordPress REST API, the feature landscape is well-established.

**Key findings:**
- Table stakes include basic CRUD operations, post listing with filtering, and WordPress integration
- AI content generation is a differentiator but becoming table stakes rapidly
- Token usage tracking is expected in AI tools but often poorly implemented
- All Posts view with visual distinction between tool-created and existing posts is standard
- Bulk operations are table stakes for serious content management

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Post CRUD Operations** | Users must create, read, update, delete posts | Low | Already implemented in codebase |
| **Post Listing with Filtering** | Users need to find posts by status, date, search | Low | Already implemented in AllPosts.jsx |
| **WordPress Site Management** | Users need to configure multiple WordPress sites | Low | Already implemented in WPSites.jsx |
| **AI Provider Configuration** | Users need to set up OpenAI, Gemini, Anthropic | Low | Already implemented in AIProviders.jsx |
| **Project-based Organization** | Users need to group posts by project/campaign | Low | Already implemented in ProjectDetail.jsx |
| **Token Usage Tracking** | Users need to know AI costs per post | Medium | Tracked per job, not aggregated at project level |
| **Post Status Tracking** | Users need to know draft/published/failed status | Low | Already implemented with status badges |
| **Job Progress Monitoring** | Users need to see AI generation progress | Medium | Already implemented with auto-refresh |
| **WordPress REST API Integration** | Users need to publish to WordPress sites | Medium | Already implemented in wp_service.py |
| **Bulk Post Creation** | Users need to create multiple posts at once | Medium | Already implemented in ProjectDetail.jsx |
| **Content Preview** | Users need to see generated content before publishing | Low | Already implemented in PostView.jsx |
| **Edit in WordPress** | Users need to edit posts in WordPress admin | Low | Already implemented in AllPosts.jsx |
| **Post Statistics** | Users need to see published/draft/failed counts | Low | Already implemented in ProjectDetail.jsx |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Token Usage Aggregation** | Complete cost visibility across project | Medium | Calculate on-the-fly from posts collection |
| **Visual Post Origin Distinction** | Clear separation of tool-created vs existing posts | Low | Track post origin in database |
| **Pre-save Connectivity Validation** | Immediate feedback on WordPress site configuration | Medium | Test credentials before saving |
| **AI Pipeline Visualization** | Clear view of research → outline → content → thumbnail | Low | Already implemented with job status badges |
| **Multi-Provider AI Support** | Flexibility to use OpenAI, Gemini, Anthropic | Medium | Already implemented in ai_service.py |
| **Custom Content Length Control** | Target word count and section count | Low | Already implemented in create forms |
| **Thumbnail Generation Options** | AI-generated or upload later | Low | Already implemented in create forms |
| **Auto-publish Toggle** | Control whether posts publish immediately | Low | Already implemented in create forms |
| **Project-level Statistics** | Overview of all posts in a project | Low | Already implemented in ProjectDetail.jsx |
| **Real-time Job Updates** | Auto-refresh while jobs are running | Low | Already implemented with 3s interval |
| **Default Model Configuration** | Set preferred AI models per project | Low | Already implemented in DefaultModels.jsx |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **In-app Post Editor** | WordPress admin is already excellent | Deep link to WordPress admin for editing |
| **Full WordPress Clone** | Reinventing the wheel, maintenance burden | Focus on AI generation, leverage WordPress for editing |
| **Social Media Auto-posting** | Out of scope for MVP, many dedicated tools exist | Use Jetpack Social or dedicated social media tools |
| **SEO Optimization** | Yoast SEO and Rank Math already dominate | Integrate with existing SEO plugins via WordPress admin |
| **Content Calendar** | Complex, many dedicated tools exist | Use WordPress editorial calendar plugins |
| **Multi-user Collaboration** | Requires auth system (out of scope for MVP) | Rely on network-level isolation, defer to later |
| **Advanced Analytics** | Google Analytics and Jetpack Stats already exist | Link to existing analytics tools |
| **Email Notifications** | Requires email infrastructure (out of scope) | Use WordPress notification system or defer |
| **Version Control for Posts** | WordPress has revisions built-in | Use WordPress revision system |
| **Content Syndication** | Complex, many dedicated tools exist | Use RSS feeds or dedicated syndication tools |

## Feature Dependencies

```
WordPress Site Configuration → Post Creation → Content Generation → Publishing
AI Provider Configuration → Token Usage Tracking → Cost Management
Project Creation → Post Organization → Statistics Aggregation
Token Usage Tracking → Project-level Aggregation → Cost Visibility
Post Origin Tracking → All Posts Tab → Visual Distinction
```

## MVP Recommendation

**Prioritize (already implemented):**
1. Post CRUD operations
2. WordPress site management
3. AI provider configuration
4. Project-based organization
5. Post listing with filtering
6. Job progress monitoring
7. Bulk post creation
8. Content preview
9. Edit in WordPress
10. Post statistics

**Active (in progress):**
1. Token usage aggregation display
2. All Posts tab with visual distinction

**Defer (future phases):**
- Advanced filtering and search
- Post scheduling
- Content templates
- Custom AI prompts
- Multi-language support
- Content quality scoring

## Sources

- WordPress REST API Documentation (developer.wordpress.org) - HIGH confidence
- Jetpack Plugin Documentation (wordpress.org/plugins/jetpack) - HIGH confidence
- Yoast SEO Plugin Documentation (wordpress.org/plugins/wordpress-seo) - HIGH confidence
- WP All Import Plugin Documentation (wordpress.org/plugins/wp-all-import) - HIGH confidence
- WordLift Plugin Documentation (wordpress.org/plugins/wordlift) - MEDIUM confidence
- Existing codebase analysis (frontend/src/components/, backend/app/models/) - HIGH confidence
- Project context (.planning/PROJECT.md) - HIGH confidence
- Existing concerns (.planning/codebase/CONCERNS.md) - HIGH confidence
