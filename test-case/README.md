# Test case documentation — Bloxorz Solver

## Purpose

This folder contains the reviewable test plan for CSC14003 Project 1. `TEST_SPECIFICATION.md` is authoritative; `test-cases.md` is the readable case catalog, and `levels-test-cases.json` is its structured companion for future automation. These files do not implement the game or run solvers.

## Organization

- `TEST_SPECIFICATION.md`: scope, traceability, fixtures, protocols, open decisions, and acceptance criteria.
- `test-cases.md`: detailed cases with objective, preconditions, input/fixture, steps, expected result, type, status, and sources.
- `levels-test-cases.json`: structured cases plus a structural inventory of all 33 dataset levels.

## IDs and groups

IDs use the established `GROUP-NN` convention and are preserved: ORI (orientation), MOV (movement), GOAL, FRG (fragile), SWT (switches), BRG (bridges), SPL (split/control), MRG (merge), LV (level validation), SOL (solver correctness), INT (integration), GUI (GUI/deliverable acceptance), and BEN (benchmark). `LV-DATA-01` is the full-dataset structural audit.

## Types and statuses

`unit`, `integration`, `acceptance`, and `benchmark` identify test type. `READY` means the expected behavior is specified well enough to implement without resolving an open rule; it does not mean implemented or passed. `PENDING` requires a developer decision before pass/fail assertions. Evidence labels distinguish PDF requirements (`ĐỀ BÀI`), observed dataset structure (`JSON`), proposed validation policy (`ĐỀ XUẤT`), and unresolved behavior (`CẦN XÁC MINH`).

Current catalog: 78 unique cases; 53 READY and 25 PENDING. Group counts: ORI 12, MOV 4, GOAL 2, FRG 3, SWT 8, BRG 5, SPL 4, MRG 3, LV 13, SOL 4, INT 8, GUI 5, BEN 7.

## How to use

1. Review the authoritative specification and resolve pending decisions with the developers.
2. Implement unit cases with small semantic fixtures where possible; do not infer glyph meanings from appearance.
3. Implement integration cases when the required loader, engine, and solver interfaces exist.
4. Run benchmark cases only after agreeing on a common manifest, rules, costs, resource policy, and metrics.
5. Keep the Markdown and JSON catalogs synchronized; record benchmark outcomes only after measurement.

The 33-level audit checks structure only; INT-07 separately specifies loader coverage for all entries and remains pending until schema/mapping are finalized. Neither case asserts solvability. Benchmark levels are candidates, not a difficulty ranking or claim of solution status.
