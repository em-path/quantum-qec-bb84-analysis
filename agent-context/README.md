# Agent Context

This folder collects the project's Markdown context in one place for agent
handoffs and future sessions. The files here are **snapshots**: the canonical
versions remain at their original paths and should be edited there, then copied
here again if needed.

Snapshot date: **2026-11-27**.

## Contents

| File | Canonical source | Purpose |
|---|---|---|
| `AGENTS.md` | `../AGENTS.md` | Project rules, thesis format, and coding conventions. |
| `LOCAL_PROJECT_README.md` | `../README.md` | Local project overview and folder structure (Spanish). |
| `CHANGELOG.md` | `../CHANGELOG.md` | Release history (English). |
| `CONTROL_EXPERIMENT.md` | `../CONTROL_EXPERIMENT.md` | Full control-experiment report. |
| `CONTROL_EXPERIMENT_README.md` | `../control_experiment/README.md` | Script usage and key result. |
| `SESSION_CONTEXT.md` | `../SESSION_CONTEXT.md` | Historical handoff note. |
| `ADVISOR_REVISION_CONTEXT.md` | `../ADVISOR_REVISION_CONTEXT.md` | Advisor feedback, findings, and edits. |
| `REPRODUCTION_PACKAGE_README.md` | `../reproduction_package/README.md` | Simulation package documentation. |
| `LAST_RESULTS.md` | this folder | Latest results, structure, and publication state. |

## Start here

For the current state of the project, read [`LAST_RESULTS.md`](LAST_RESULTS.md).
It summarizes the control-experiment finding, the advisor revision, the folder
restructure, compilation results, and the latest Git publication.

## Structure update

The control scripts were moved to `control_experiment/` and renamed in English:

| Former path | Current path |
|---|---|
| `prueba_control.py` | `control_experiment/control_experiment.py` |
| `prueba_control_gemela.py` | `control_experiment/twin_control_experiment.py` |

The old Spanish-named files were removed from the repository root.
