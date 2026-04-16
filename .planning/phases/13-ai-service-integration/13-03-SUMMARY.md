# Plan 13-03: Update Worker Tasks to Extract and Pass Language

**Status:** Complete
**Completed:** 2026-04-15

## Summary

Updated worker tasks to extract language from post document and pass it to AI service functions. All three worker tasks (run_research, run_outline, run_content) now extract the language parameter from the post document and pass it to the corresponding AI service functions.

## Changes Made

### Task 1: Update run_research()
- Added `language = job_data.get("language", "vietnamese")` extraction
- Added logging: `logger.info(f"[RESEARCH] Language: {language}")`
- Updated `ai_service.research_topic()` call to include `language` parameter

### Task 2: Update run_outline()
- Added `language = post.get("language", "vietnamese")` extraction
- Added logging: `logger.info(f"[OUTLINE] Language: {language}")`
- Updated `ai_service.generate_outline()` call to include `language` parameter

### Task 3: Update run_content()
- Added `language = post.get("language", "vietnamese")` extraction
- Added logging: `logger.info(f"[CONTENT] Language: {language}")`
- Updated `ai_service.generate_full_content()` call to include `language` parameter

## Verification

- ✅ `run_research()` extracts language from post and passes to `ai_service.research_topic()`
- ✅ `run_outline()` extracts language from post and passes to `ai_service.generate_outline()`
- ✅ `run_content()` extracts language from post and passes to `ai_service.generate_full_content()`
- ✅ Language is logged in all three tasks for debugging
- ✅ Language defaults to "vietnamese" if not found in post

## Files Modified

- `worker/app/workers/tasks.py` - Updated 3 worker task functions

## Commits

- `52749d3`: feat(13-03): update run_research() to extract and pass language
- `8c5bca1`: feat(13-03): update run_outline() to extract and pass language
- `d95cf44`: feat(13-03): update run_content() to extract and pass language

## Requirements Coverage

- LANG-04: Language Parameter in AI Service ✅
- LANG-07: Language in Job Payload ✅

## Notes

All worker tasks now properly extract and pass the language parameter through the entire content generation pipeline. The language parameter flows from:
1. Post document (MongoDB)
2. Job payload (Redis)
3. Worker task extraction
4. AI service function call
5. AI content generation

This completes the end-to-end language support for Vietnamese and English content generation.
