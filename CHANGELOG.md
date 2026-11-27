# Changelog

All notable changes to this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Language policy:** the report content is written in Spanish, while commit
messages and this changelog are written in English.

## [Unreleased]

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

[Unreleased]: https://github.com/em-path/quantum-qec-bb84-analysis/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/em-path/quantum-qec-bb84-analysis/releases/tag/v1.0.0
