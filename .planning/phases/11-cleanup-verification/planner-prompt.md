<planning_context>
**Phase:** 11
**Mode:** standard

<files_to_read>
- .planning/STATE.md (Project State)
- .planning/ROADMAP.md (Roadmap)
- .planning/REQUIREMENTS.md (Requirements)
- .planning/phases/07-cleanup/07-01-SUMMARY.md (Phase 7 Plan 1 Summary - PostCard removal)
- .planning/phases/07-cleanup/07-02-SUMMARY.md (Phase 7 Plan 2 Summary - Infinite scroll removal)
- .planning/phases/07-cleanup/07-03-SUMMARY.md (Phase 7 Plan 3 Summary - CSS cleanup including origin badges)
- .planning/phases/07-cleanup/07-03-PLAN.md (Phase 7 Plan 3 - Origin badge removal plan)
</files_to_read>

**Phase requirement IDs (every ID MUST appear in a plan's `requirements` field):** CLEANUP-02

**Project instructions:** Read ./AGENTS.md if exists — follow project-specific guidelines
**Project skills:** Check .kilo/skills/ or .kilo/skills/ directory (if either exists) — read SKILL.md files, plans should account for project skill rules

</planning_context>

<downstream_consumer>
Output consumed by /gsd-execute-phase. Plans need:
- Frontmatter (wave, depends_on, files_modified, autonomous)
- Tasks in XML format with read_first and acceptance_criteria fields (MANDATORY on every task)
- Verification criteria
- must_haves for goal-backward verification
</downstream_consumer>

<deep_work_rules>
## Anti-Shallow Execution Rules (MANDATORY)

Every task MUST include these fields — they are NOT optional:

1. **`<read_first>`** — Files the executor MUST read before touching anything. Always include:
   - The file being modified (so executor sees current state, not assumptions)
   - Any "source of truth" file referenced in CONTEXT.md (reference implementations, existing patterns, config files, schemas)
   - Any file whose patterns, signatures, types, or conventions must be replicated or respected

2. **`<acceptance_criteria>`** — Verifiable conditions that prove the task was done correctly. Rules:
   - Every criterion must be checkable with grep, file read, test command, or CLI output
   - NEVER use subjective language ("looks correct", "properly configured", "consistent with")
   - ALWAYS include exact strings, patterns, values, or command outputs that must be present
   - Examples:
     - Code: `auth.py contains def verify_token(` / `test_auth.py exits 0`
     - Config: `.env.example contains DATABASE_URL=` / `Dockerfile contains HEALTHCHECK`
     - Docs: `README.md contains '## Installation'` / `API.md lists all endpoints`
     - Infra: `deploy.yml has rollback step` / `docker-compose.yml has healthcheck for db`

3. **`<action>`** — Must include CONCRETE values, not references. Rules:
   - NEVER say "align X with Y", "match X to Y", "update to be consistent" without specifying the exact target state
   - ALWAYS include the actual values: config keys, function signatures, SQL statements, class names, import paths, env vars, etc.
   - If CONTEXT.md has a comparison table or expected values, copy them into the action verbatim
   - The executor should be able to complete the task from the action text alone, without needing to read CONTEXT.md or reference files (read_first is for verification, not discovery)

**Why this matters:** Executor agents work from the plan text. Vague instructions like "update the config to match production" produce shallow one-line changes. Concrete instructions like "add DATABASE_URL=postgresql://... , set POOL_SIZE=20, add REDIS_URL=redis://..." produce complete work. The cost of verbose plans is far less than the cost of re-doing shallow execution.
</deep_work_rules>

<quality_gate>
- [ ] PLAN.md files created in phase directory
- [ ] Each plan has valid frontmatter
- [ ] Tasks are specific and actionable
- [ ] Every task has `<read_first>` with at least the file being modified
- [ ] Every task has `<acceptance_criteria>` with grep-verifiable conditions
- [ ] Every `<action>` contains concrete values (no "align X with Y" without specifying what)
- [ ] Dependencies correctly identified
- [ ] Waves assigned for parallel execution
- [ ] must_haves derived from phase goal
</quality_gate>

<objective>
Create a plan for Phase 11: Cleanup Verification

**Phase Goal:** Create VERIFICATION.md for Phase 7 to formally verify cleanup requirements

**Context:**
- Phase 7 completed cleanup work including removal of PostCard component, infinite scroll logic, and unused CSS classes
- Phase 7 Plan 03 specifically removed origin-badge CSS classes (CLEANUP-02)
- The work was completed and committed (commit d600c14)
- This phase needs to create a VERIFICATION.md file to formally verify that CLEANUP-02 was completed correctly

**Requirements to verify:**
- CLEANUP-02: Origin badges are removed from All Posts tab

**What the plan should accomplish:**
Create a VERIFICATION.md file for Phase 7 that:
1. Documents the verification approach for CLEANUP-02
2. Provides evidence that origin badges were removed
3. Confirms the verification status as "passed"

**Expected output:**
A single plan (11-01-PLAN.md) that creates the VERIFICATION.md file for Phase 7
</objective>
