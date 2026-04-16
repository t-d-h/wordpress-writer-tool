---
status: awaiting_human_verify
trigger: "Investigate issue: research-topic-args-error"
created: 2026-04-16T12:25:54+07:00
updated: 2026-04-16T12:25:54+07:00
---

## Current Focus
hypothesis: Stale Python bytecode cache - worker loading old version of ai_service.py without language parameter
test: Check __pycache__ timestamps and compare to source file timestamps
expecting: Find that ai_service.cpython-311.pyc is older than ai_service.py
next_action: Request human verification

## Symptoms
expected: Research fails with different error
actual: Research job fails immediately
errors: research_topic() takes from 1 to 4 positional arguments but 5 were given
reproduction: Use existing project
timeline: Worked before (regression)

## Eliminated

## Evidence
- timestamp: 2026-04-16T12:25:54+07:00
  checked: Function signature in worker/app/services/ai_service.py
  found: research_topic() has 5 parameters: topic, additional_requests, provider_id, model_name, language
  implication: Function should accept 5 positional arguments

- timestamp: 2026-04-16T12:25:54+07:00
  checked: Call site in worker/app/workers/tasks.py
  found: Calls research_topic(topic, additional, provider_id, model_name, language) with 5 positional arguments
  implication: Call matches function signature

- timestamp: 2026-04-16T12:25:54+07:00
  checked: __pycache__ directory timestamps
  found: ai_service.cpython-311.pyc dated Apr 10 15:51, but ai_service.py modified Apr 16 11:37
  implication: Stale bytecode cache - worker loading old version without language parameter

- timestamp: 2026-04-16T12:25:54+07:00
  checked: Cleared __pycache__ directories and restarted worker
  found: Worker restarted successfully, __pycache__ regenerated with correct code
  implication: Worker now loads correct version of ai_service.py

- timestamp: 2026-04-16T12:25:54+07:00
  checked: Function signature inside running worker container
  found: research_topic() has 5 parameters including language with default 'vietnamese'
  implication: Worker loaded correct version after restart

- timestamp: 2026-04-16T12:25:54+07:00
  checked: Function binding test with 5 positional arguments
  found: Successfully bound 5 positional arguments to function signature
  implication: Function accepts the call pattern used in tasks.py

## Resolution
root_cause: Stale Python bytecode cache in worker/app/services/__pycache__/ai_service.cpython-311.pyc caused worker to load old version of ai_service.py without language parameter
fix: Cleared all __pycache__ directories in worker and restarted worker container to force recompilation with updated source code
verification: Verified function signature in running worker container has 5 parameters and successfully binds 5 positional arguments
files_changed: []
