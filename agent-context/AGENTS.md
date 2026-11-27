# Contexto del Proyecto: PIA UTM - QEC en BB84

## 1. Descripción General
Este repositorio contiene el código y los documentos para el Proyecto de Investigación Aplicada (PIA) de la Maestría en Ciberseguridad de la UTM.
El tema es: "Corrección de errores cuánticos y tasa de clave segura en el protocolo BB84 bajo canales ruidosos".
El objetivo es identificar el tamaño óptimo de código QEC (n=3,5,7) que maximiza la tasa de clave efectiva (R_efectiva) bajo distintos niveles de ruido (p).

## 2. Estructura del Repositorio
- `documento-final/`
  - `reporte-final.tex`: Documento principal del PIA (Formato UTM).
- `src/`: Código fuente Python (QuTiP).
  - `canal.py`: Modelo del canal depolarizante.
  - `bb84.py`: Protocolo BB84 sin QEC.
  - `qec.py`: Código de repetición (codificar, síndromes, corregir).
  - `simulacion.py`: Pipeline integrado y barrido de parámetros.
- `scripts/`: Scripts auxiliares (generación de figuras, tablas).
- `data/`: Archivos CSV con resultados (ej. `resultados_finales.csv`).
- `figs/`: Gráficas finales (PNG) para el documento.
- `PIA_UTM_Final.tex`: Documento principal del PIA (Formato UTM).

## 3. Reglas de Formato del Documento (Guía UTM)
- **Fuente:** Arial 12 (usar paquete `helvet` en LaTeX).
- **Márgenes:** Izquierdo 3.5cm, Superior/Inferior/Derecho 2.5cm.
- **Interlineado:** 1.15.
- **Títulos:** Capítulos en mayúsculas y negrita, numerados con arábigos.
- **Referencias:** APA 7 (solo fuentes citadas).
- **Estructura:** Carátula, Resumen (250-350 palabras), Cap I (Problema), Cap II (Método), Cap III (Resultados), Anexos, Referencias.

## 4. Reglas de Código y Datos
- Usar Python 3.14 y QuTiP 5.0.
- Los resultados numéricos deben guardarse en `data/resultados_finales.csv`.
- Las gráficas deben tener estilo académico (Matplotlib, DPI 300).
- No modificar la lógica física de `canal.py`, `bb84.py` o `qec.py` sin consultar.

## 5. Reglas de Redacción de Capítulos (obligatorias)

El jurado es interdisciplinario: no todos sus integrantes son físicos o matemáticos. Todo capítulo nuevo debe redactarse con **rigor científico, pero en lenguaje accesible**.

- **Tono:** académico, en tercera persona e impersonal ("se analiza", "se determinó"). Sin primera persona del plural.
- **Ecuaciones y citas:** conservar siempre las ecuaciones formales, las notaciones y las citas APA 7. La accesibilidad no justifica eliminar precisión.
- **Ecuaciones numeradas y referenciables:** toda fórmula que se use fuera del lugar donde se define debe ir en `\begin{equation}` con `\label{eq:...}` y citarse en el texto con `Ecuación~\eqref{eq:...}` (por ejemplo, «sustituyendo la Ecuación~(1.5) en la Ecuación~(1.3)»). No usar `\[ ... \]` para fórmulas que se referencian después. Las figuras y tablas se citan con `Figura~\ref{...}` y `Tabla~\ref{...}`, y deben llevar unidad, fuente de datos y condiciones en el pie.
- **Concepto técnico nuevo → glosa breve entre paréntesis** en su primera aparición. Ejemplos ya aplicados en el Cap. 1: *logaritmo discreto*, *tiempo polinómico*, *tolerante a fallos*, *base no ortogonal*, *no-clonación*, *decoherencia*, *cuentas oscuras*, *amplitud de probabilidad*, *matriz de densidad*, *autoespacio*, *síndrome*, *entropía de Shannon*, *fidelidad de canal*, *entrelazamiento*, *distancia de código*.
- **Analogías obligatorias ya establecidas** (mantener y reutilizar, no reinventar):
  - **Qubit / superposición (Sección 1.2.1):** la *moneda girando en el aire*. Un bit es un interruptor; un qubit es una moneda que gira y solo al atraparla (medirla) se define cara o cruz. Precisar que la moneda no guarda dos respuestas a la vez.
  - **Compromiso (trade-off) corrección \textit{vs.} overhead (Sección 1.2.4):** los *guardias de seguridad*. Barrio tranquilo → pocos guardias; amenaza alta → más guardias. En QEC los guardias son los qubits físicos adicionales: el corchete de `R_efectiva` es la protección y el factor `1/n` es el costo.
- **Reglas de estilo de las analogías:** máximo una analogía principal por sección; integrarla en la argumentación (no como adorno), aclarar siempre su límite físico y no repetirla más de una vez por capítulo (salvo retorno breve para cerrar el razonamiento).
- **Estructura:** cada concepto introducido debe usarse después en el modelo o en los resultados; no acumular definiciones.
- **Prohibido:** afirmaciones alarmistas sin cita, resultados no sustentados en `data/`, y referencias inventadas o no verificadas (validar con `python -m refproof documento-final/reporte-final.tex`).