# PIA_QEC_BB84

Proyecto de investigación aplicada de la Maestría en Ciberseguridad (UTM):
corrección de errores cuánticos y tasa de clave segura en el protocolo BB84 bajo
canales ruidosos.

## Estructura del proyecto

- `src/`: módulos del canal, BB84 y QEC del árbol de trabajo en español.
- `reproduction_package/`: paquete de reproducción autocontenido en inglés.
- `control_experiment/`: scripts del experimento de control (redundancia clásica
  frente a corrección cuántica), con nombres y documentación en inglés.
- `documento-final/`: fuente LaTeX, PDF del informe final y artículo IEEE.
- `data/`, `figs/`, `scripts/`: resultados, figuras y scripts auxiliares.
- `agent-context/`: contexto y hallazgos para agentes; incluye
  `LAST_RESULTS.md` con el estado más reciente.
- `CONTROL_EXPERIMENT.md`: informe completo del experimento de control.
- `CHANGELOG.md`: historial de cambios, en inglés.
- `README.md`: este archivo.

## Reproducción

Desde la raíz del proyecto, con Python 3.14 y QuTiP 5.x:

```bash
python control_experiment/control_experiment.py 2000 0.15 3 2026
python control_experiment/twin_control_experiment.py 2000 0.15 3 2026
```

El paquete de simulación completo se documenta en
`reproduction_package/README.md`.
