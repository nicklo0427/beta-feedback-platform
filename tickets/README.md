# Tickets

This folder is the product and implementation ticket archive for the project.

## Current Working Set

Active tickets live in [`active/`](active/). Start here for day-to-day implementation.

Current phase: `Target Environment Rehearsal / Post-Beta Hardening`

1. [`T102 - Target Beta Environment Rehearsal`](active/T102-target-beta-environment-rehearsal.md)
2. [`T103 - Launch Blocker Fix Pass`](active/T103-launch-blocker-fix-pass.md)
3. [`T104 - Beta Onboarding Polish`](active/T104-beta-onboarding-polish.md)
4. [`T105 - Operational Safety Baseline`](active/T105-operational-safety-baseline.md)

`T095-T101` have been completed and archived.

Dual-role test coverage and expected outcomes are centralized in [DUAL_ROLE_TEST_PLAN.md](/Users/lowhaijer/projects/beta-feedback-platform/DUAL_ROLE_TEST_PLAN.md).

## Completed Archive

Completed tickets live in [`completed/`](completed/). These files are kept as decision history and implementation context, not as the daily working queue.

Latest completed ticket:

- [`T101 - Dual-Role QA, Docs, Seed, and Regression`](completed/T101-dual-role-qa-docs-seed-and-regression.md)

## Numbering Notes

The ticket sequence is mostly chronological, but a few numbers do not currently have standalone ticket files:

- `T075` to `T081`
- `T092`

Those gaps came from planning or implementation work that was captured elsewhere before the ticket folder was reorganized. Avoid reusing those numbers.

## Maintenance Rules

- New planned implementation tickets should be created under [`active/`](active/).
- Once a ticket is completed, move it to [`completed/`](completed/) and update this index.
- Keep the root of `tickets/` limited to this README and category folders.
- Do not delete completed tickets unless there is a separate archive cleanup decision.
