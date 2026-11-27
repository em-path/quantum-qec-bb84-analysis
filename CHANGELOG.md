# Changelog

All notable changes to this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Language policy:** the report content is written in Spanish, while commit
messages and this changelog are written in English.

## [Unreleased]

## [1.2.1] - 2026-11-27

### Removed

- `agent-context/` from the public repository. The folder is maintained only in
  the local working environment.

### Changed

- Repository README, report Appendix A.2, `ADVISOR_REVISION_CONTEXT.md`, and
  `control_experiment/README.md` no longer reference a repository-hosted
  `agent-context/`.

## [1.2.0] - 2026-11-27

### Added

- `control_experiment/` folder with English-named scripts and a README.
- `agent-context/` folder with all Markdown context and `LAST_RESULTS.md`.
- IEEE article LaTeX source at `report/articulo_ieee.tex`, so the appendix can
  be rebuilt from the repository.

### Changed

- Renamed `prueba_control.py` to `control_experiment/control_experiment.py` and
  `prueba_control_gemela.py` to
  `control_experiment/twin_control_experiment.py`; both scripts now add the
  repository root to `sys.path` and can be run from any directory.
- Updated `CONTROL_EXPERIMENT.md`, `SESSION_CONTEXT.md`,
  `ADVISOR_REVISION_CONTEXT.md`, `README.md`, and the report/IEEE links to the
  new paths.
- Regenerated `report/reporte-final.pdf` (56 pages) and
  `report/articulo_ieee.pdf` (6 pages).

### Removed

- The old Spanish-named control scripts from the repository root.

## [1.1.0] - 2026-11-27

### Added

- Report subsection 3.3.4, "Experimento de control: redundancia clásica vs.
  corrección cuántica", with the comparative QBER table and the theoretical
  equivalence equation.
- Equivalent control-experiment subsection in the IEEE article, with its own
  table and equation.
- `ADVISOR_REVISION_CONTEXT.md`, documenting the revision context, the empirical
  findings, and the verification record.
- Steane (1996) reference in the IEEE article.

### Changed

- Report Discussion (3.4) now explains that, for the 3-qubit repetition code,
  syndrome correction and majority voting are operationally equivalent, and that
  the contribution is the overhead/key-rate trade-off.
- Report Conclusions (3.5) rewritten to attribute the QBER reduction to
  structural redundancy rather than to the syndrome.
- Report Limitations (3.6) reduced to scoped caveats plus future work.
- IEEE article Conclusion adjusted with the same nuance.
- IEEE article is now six pages (was five); the report appendix description was
  updated accordingly.
- Regenerated `report/reporte-final.pdf` (56 pages) and
  `report/articulo_ieee.pdf` (6 pages).

## [1.0.0] - 2026-11-27

### Added

- Spanish LaTeX source of the final PIA report at `report/reporte-final.tex`.
- Compiled final report at `report/reporte-final.pdf` (52 pages).
- IEEE-format academic article appendix at `report/articulo_ieee.pdf`.
- `report/.gitignore` to keep LaTeX build artifacts out of version control.

### Changed

- The two `\lstinputlisting` paths in the report now point to `../src/`, matching
  the repository layout. The referenced files are byte-identical to the originals
  in `reproduction_package/src/`.

[Unreleased]: https://github.com/em-path/quantum-qec-bb84-analysis/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/em-path/quantum-qec-bb84-analysis/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/em-path/quantum-qec-bb84-analysis/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/em-path/quantum-qec-bb84-analysis/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/em-path/quantum-qec-bb84-analysis/releases/tag/v1.0.0
