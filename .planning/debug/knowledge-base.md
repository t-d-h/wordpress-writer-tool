# GSD Debug Knowledge Base

Resolved debug sessions. Used by `gsd-debugger` to surface known-pattern hypotheses at the start of new investigations.

---

## all-posts-blinking — Table blinks on and off repeatedly when clicking All Posts tab in ProjectDetail
- **Date:** 2026-04-15
- **Error patterns:** blinking, table, auto-refresh, useEffect, polling
- **Root cause:** useEffect dependency array included project object, which changes on every load() call. When there are active jobs, load() is called every 3 seconds, causing repeated effect triggers and loading spinner blinking.
- **Fix:** Removed the auto-refresh useEffect and added manual refresh buttons to both Content and All Posts tab toolbars
- **Files changed:** frontend/src/components/Projects/ProjectDetail.jsx

---
