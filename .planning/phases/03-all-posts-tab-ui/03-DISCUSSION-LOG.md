# Phase 3: All Posts Tab UI - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14
**Phase:** 03-all-posts-tab-ui
**Areas discussed:** Post list layout, Visual distinction, Filter UI, Sorting UI, Search UI, Empty state, Pagination

---

## Post list layout

| Option | Description | Selected |
|--------|-------------|----------|
| Cards | Reuses existing Card component with shadow/rounded variants. Consistent with Messages and stat-cards. | ✓ |
| List | Simpler, compact rows. Would be a new pattern in this codebase. | |
| Table | Dense, tabular view. Needs new Table component — none exists yet. | |

**User's choice:** Cards

**Notes:** Reuses existing Card component for consistency with existing patterns.

---

### Card information

| Option | Description | Selected |
|--------|-------------|----------|
| Essential only | Title, status, date, origin badge, edit button. Clean and focused. | ✓ |
| Essential + preview | Title, status, date, origin badge, edit button, word count, thumbnail preview. More informative. | |
| Full detail | Title, status, date, origin badge, edit button, word count, thumbnail preview, excerpt, author. Maximum detail. | |

**User's choice:** Essential only

**Notes:** Keeps it clean and focused with just the essential information.

---

## Visual distinction

| Option | Description | Selected |
|--------|-------------|----------|
| Badge | Small badge on card showing "Tool" or "Existing". Clean and unobtrusive. | ✓ |
| Color | Subtle background color difference (light blue for tool, gray for existing). Easy to scan. | |
| Icon | Icon indicator (sparkle for tool, globe for existing). Visual and semantic. | |
| Border | Left border color (accent color for tool, gray for existing). Subtle but clear. | |

**User's choice:** Badge

**Notes:** Small badge showing "Tool" or "Existing" on each card. Clean and unobtrusive.

---

## Filter UI

| Option | Description | Selected |
|--------|-------------|----------|
| Top bar | Filter dropdown at top of tab, above post list. Standard pattern. | ✓ |
| Sidebar | Filter dropdown in sidebar (if we add one). More space for multiple filters. | |
| Inline | Filter dropdown inline with search bar. Compact. | |

**User's choice:** Top bar

**Notes:** Filter dropdown at the top of the tab, above the post list. Standard pattern.

---

## Sorting UI

| Option | Description | Selected |
|--------|-------------|----------|
| Dropdown | Sort dropdown at top of tab, next to filter. Standard pattern for card layouts. | ✓ |
| Headers | Clickable column headers (if using table layout). Not applicable for cards. | |
| Inline | Sort dropdown inline with search bar. Compact. | |

**User's choice:** Dropdown (after clarification)

**Notes:** Sort dropdown at the top of the tab, next to the filter. Standard pattern for card layouts.

---

## Search UI

| Option | Description | Selected |
|--------|-------------|----------|
| Top bar | Search input at top of tab, next to filter and sort. Standard pattern. | ✓ |
| Inline | Search input inline within the post list area. Compact. | |

**User's choice:** Top bar

**Notes:** Search input at the top of the tab, next to filter and sort. Creates consistent control bar.

---

## Empty state

| Option | Description | Selected |
|--------|-------------|----------|
| Simple message | "No posts yet" message with icon. Simple and clear. | ✓ |
| Message + CTA | "No posts yet" message with icon + "Create your first post" button. Action-oriented. | |
| Full empty state | EmptyState component with illustration, message, and action button. More polished. | |

**User's choice:** Simple message

**Notes:** "No posts yet" with an icon. Keeps it simple and clear.

---

## Pagination

| Option | Description | Selected |
|--------|-------------|----------|
| Infinite scroll | Load more posts as user scrolls down. Seamless experience. | ✓ |
| Page numbers | Show page numbers (1, 2, 3...) at bottom. Traditional pattern. | |
| Load more button | Show "Load more" button at bottom. User-controlled. | |

**User's choice:** Infinite scroll

**Notes:** Load more posts as user scrolls down for a seamless experience.

---

## the agent's Discretion

- Exact badge placement on card (top-right, top-left, etc.)
- Card grid layout (2 columns, 3 columns, responsive)
- Control bar layout (filter, sort, search arrangement)
- Loading state for infinite scroll (spinner, skeleton, etc.)
- Error handling for failed API calls

## Deferred Ideas

None — discussion stayed within phase scope
