---
status: testing
phase: 14-frontend-ui
source: [14-01-SUMMARY.md, 14-02-SUMMARY.md, 14-03-SUMMARY.md, 14-04-SUMMARY.md, 14-05-SUMMARY.md]
started: 2026-04-16T10:59:25+07:00
updated: 2026-04-16T11:12:51+07:00
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

number: 2
name: Language Persistence Across Form Resets
expected: |
  When selecting a language (e.g., English), closing the modal, and reopening it, the previously selected language is still selected. Language selection also persists when form is submitted with errors.
awaiting: user response

## Tests

### 1. Language Selection in Create Post Form
expected: When opening the Create Post modal, radio buttons for language selection are visible with "Tiếng Việt" (Vietnamese) and "English" options. Vietnamese is selected by default.
result: issue
reported: "research_topic() takes from 1 to 4 positional arguments but 5 were given"
severity: blocker

### 2. Language Persistence Across Form Resets
expected: When selecting a language (e.g., English), closing the modal, and reopening it, the previously selected language is still selected. Language selection also persists when form is submitted with errors.
result: pending

### 3. Language Badge in Post List Table
expected: In the post list table, a "Language" column appears with color-coded badges for each post. Vietnamese posts show a green badge with "Tiếng Việt", English posts show a blue badge with "English".
result: pending

### 4. Language Badge in Post Detail View
expected: When viewing a post's detail page, a language badge appears in the header area showing the post's language with color coding (green for Vietnamese, blue for English).
result: pending

### 5. Language Preference Saved to localStorage
expected: When changing the language selection in the Create Post form, the preference is saved to browser localStorage. Reopening the modal restores the saved preference instead of defaulting to Vietnamese.
result: pending

### 6. Language Field Included in API Requests
expected: When submitting a post (single or bulk), the language field is included in the API request with the selected value ("vietnamese" or "english").
result: pending

### 7. Missing Language Field Handled Gracefully
expected: Posts without a language field in the database display an English badge (blue) in both the post list table and post detail view, rather than showing an error or missing badge.
result: pending

## Summary

total: 7
passed: 0
issues: 1
pending: 6
skipped: 0

## Gaps

- truth: "research_topic() function should accept the correct number of arguments"
  status: failed
  reason: "User reported: research_topic() takes from 1 to 4 positional arguments but 5 were given"
  severity: blocker
  test: 1
  artifacts: ["worker/app/services/ai_service.py", "worker/app/workers/tasks.py"]
  missing: ["language parameter in worker's research_topic() function", "language-specific system prompt logic in worker's research_topic()"]
