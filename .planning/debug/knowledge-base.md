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

## research-topic-args-error — Research job fails with "takes from 1 to 4 positional arguments but 5 were given"
- **Date:** 2026-04-16
- **Error patterns:** research_topic, positional arguments, 5, 4, job fails, __pycache__, stale bytecode
- **Root cause:** Stale Python bytecode cache in worker/app/services/__pycache__/ai_service.cpython-311.pyc caused worker to load old version of ai_service.py without language parameter
- **Fix:** Cleared all __pycache__ directories in worker and restarted worker container to force recompilation with updated source code
- **Files changed:** []

---
