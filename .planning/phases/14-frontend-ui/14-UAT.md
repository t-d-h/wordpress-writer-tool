---
status: complete
phase: 14-frontend-ui
source: [14-01-SUMMARY.md, 14-02-SUMMARY.md, 14-03-SUMMARY.md, 14-04-SUMMARY.md, 14-05-SUMMARY.md, 14-06-SUMMARY.md]
started: 2026-04-16T10:59:25+07:00
updated: 2026-04-16T11:51:23+07:00
---

## Current Test

[testing complete]

## Tests

### 1. Language Selection in Create Post Form
expected: When opening the Create Post modal, radio buttons for language selection are visible with "Tiếng Việt" (Vietnamese) and "English" options. Vietnamese is selected by default.
result: pass
note: "Fixed by plan 14-06 - worker AI service now accepts language parameter"

### 2. Language Persistence Across Form Resets
expected: When selecting a language (e.g., English), closing the modal, and reopening it, the previously selected language is still selected. Language selection also persists when form is submitted with errors.
result: pass

### 3. Language Badge in Post List Table
expected: In the post list table, a "Language" column appears with color-coded badges for each post. Vietnamese posts show a green badge with "Tiếng Việt", English posts show a blue badge with "English".
result: pass

### 4. Language Badge in Post Detail View
expected: When viewing a post's detail page, a language badge appears in the header area showing the post's language with color coding (green for Vietnamese, blue for English).
result: pass

### 5. Language Preference Saved to localStorage
expected: When changing the language selection in the Create Post form, the preference is saved to browser localStorage. Reopening the modal restores the saved preference instead of defaulting to Vietnamese.
result: pass

### 6. Language Field Included in API Requests
expected: When submitting a post (single or bulk), the language field is included in the API request with the selected value ("vietnamese" or "english").
result: skipped
reason: "User cannot verify API requests directly"

### 7. Missing Language Field Handled Gracefully
expected: Posts without a language field in the database display an English badge (blue) in both the post list table and post detail view, rather than showing an error or missing badge.
result: pass
note: "Verified via Playwright - all 25 posts display language badges correctly, no errors or missing badges"

## Summary

total: 7
passed: 6
issues: 0
pending: 0
skipped: 1

## Gaps

[none - all issues resolved]
