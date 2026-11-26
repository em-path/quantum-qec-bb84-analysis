"""
prueba_control.py - Experimento de control: QEC vs. redundancia clasica
=======================================================================

Pregunta experimental
---------------------
La reduccion del QBER que se observa en el pipeline con QEC, ¿se debe a la
MEDICION DE SINDROME + CORRECCION cuantica, o basta con la REDUNDANCIA
(repetir el qubit n veces) y la VOTACION POR MAYORIA en la decodificacion?

Diseno
------
Se transmiten los mismos N bits logicos por el mismo canal depolarizante
(probabilidad p por qubit fisico) en dos escenarios que solo difieren en
un paso:

    A) Con QEC ............ codificar -> ruido -> medir_sindrome ->
                            corregir -> decodificar (mayoria)
    B) Solo redundancia ... codificar -> ruido -> decodificar (mayoria)

El escenario B omite deliberadamente medir_sindrome() y corregir(). Si el
QBER de A es significativamente menor que el de B, la correccion por
sindrome aporta algo. Si A ~ B, la reduccion se explica por la redundancia
y la votacion por mayoria.

Como referencia se incluye un tercer escenario sin redundancia (n = 1), que
permite separar el efecto de "repetir el qubit" del de "corregir el qubit".

Uso
---
    python prueba_control.py                    # n=3, p=0.15, 2000 iteraciones
    python prueba_control.py 5000 0.15 3 2026   # iteraciones, p, n, semilla

El script NO escribe ni modifica archivos: solo imprime en pantalla.
"""

from __future__ import annotations

import sys

import numpy as np

# ---------------------------------------------------------------------------
# Imports: compatible with the Spanish working tree (src/qec.py with
# `codificar`, src/simulacion.py, src/canal.py) and with the English
# reproducible package in the remote repository (src/qec.py with `encode`,
# src/simulation.py, src/channel.py). The underlying physics is identical.
# ---------------------------------------------------------------------------
try:
    from src.qec import codificar, medir_sindrome, corregir, decodificar
    from src.simulacion import canal_depolarizante_n
    from src.canal import canal_depolarizante
    from src.bb84 import preparar_qubit, medir_qubit
except ImportError:  # English module/function names (remote package)
    from src.qec import (
        encode as codificar,
        measure_syndrome as medir_sindrome,
        correct as corregir,
        decode as decodificar,
    )
    from src.channel import depolarizing_channel_n as canal_depolarizante_n
    from src.channel import depolarizing_channel as canal_depolarizante
    from src.bb84 import prepare_qubit as preparar_qubit
    from src.bb84 import measure_qubit as medir_qubit


# ===========================================================================
# Parametros por defecto
# ===========================================================================

N_QUBITS = 3        # tamano del codigo de repeticion (n)
P_RUIDO = 0.15      # probabilidad de error por qubit fisico (p)
N_ITER = 2000       # iteraciones (bits logicos) por escenario
SEED = 2026         # semilla base


# ===========================================================================
# Utilidades
# ===========================================================================

def _qber_con_error_estandar(errores: int, total: int) -> tuple[float, float]:
    """Devuelve (QBER, error estandar binomial)."""
    qber = errores / total
    if 0.0 < qber < 1.0:
        se = float(np.sqrt(qber * (1.0 - qber) / total))
    else:
        se = 0.0
    return qber, se


# ===========================================================================
# Escenario A: pipeline con QEC (sindrome + correccion)
# ===========================================================================

def escenario_con_qec(n_iter: int, n: int, p: float, seed: int) -> dict:
    """
    Escenario A: codificar -> canal -> medir_sindrome -> corregir -> decodificar.

    No modifica la logica del proyecto: usa las funciones originales de
    src.qec y src.simulacion tal como estan implementadas.
    """
    np.random.seed(seed)

    errores = 0
    sindromes_no_triviales = 0
    correcciones_efectivas = 0

    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))

        # 1) Codificacion: |b> -> |bbb>
        rho = codificar(bit, n)

        # 2) Canal ruidoso, independiente por qubit fisico
        rho_err = canal_depolarizante_n(rho, p, n)

        # 3) Medicion de sindrome
        sindrome = medir_sindrome(rho_err, n)
        if any(s != 0 for s in sindrome):
            sindromes_no_triviales += 1

        # 4) Correccion
        rho_dec = corregir(rho_err, sindrome, n)
        if not np.allclose(rho_dec.full(), rho_err.full(), atol=1e-12):
            correcciones_efectivas += 1

        # 5) Decodificacion por votacion mayoritaria
        bit_bob = decodificar(rho_dec, n)

        if bit_bob != bit:
            errores += 1

    qber, se = _qber_con_error_estandar(errores, n_iter)
    return {
        "qber": qber,
        "se": se,
        "errores": errores,
        "n_iter": n_iter,
        "sindromes_no_triviales": sindromes_no_triviales,
        "correcciones_efectivas": correcciones_efectivas,
    }


# ===========================================================================
# Escenario B: solo redundancia (sin medir_sindrome ni corregir)
# ===========================================================================

def escenario_solo_redundancia(n_iter: int, n: int, p: float, seed: int) -> dict:
    """
    Escenario B: codificar -> canal -> decodificar.

    Se omite por completo la QEC: el estado ruidoso se pasa directamente a
    decodificar(), que hace votacion por mayoria. Esto simula "solo
    redundancia clasica".
    """
    np.random.seed(seed)

    errores = 0

    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))

        rho = codificar(bit, n)
        rho_err = canal_depolarizante_n(rho, p, n)

        # Sin sindrome y sin correccion: el estado ruidoso va directo.
        bit_bob = decodificar(rho_err, n)

        if bit_bob != bit:
            errores += 1

    qber, se = _qber_con_error_estandar(errores, n_iter)
    return {
        "qber": qber,
        "se": se,
        "errores": errores,
        "n_iter": n_iter,
    }


# ===========================================================================
# Escenario de referencia: sin redundancia (n = 1)
# ===========================================================================

def escenario_sin_redundancia(n_iter: int, p: float, seed: int) -> dict:
    """
    Referencia: un solo qubit en la base Z, sin repeticion ni mayoria.
    Sirve para medir cuanto QBER hay antes de cualquier redundancia.
    """
    np.random.seed(seed)

    errores = 0

    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))

        rho = preparar_qubit(bit, 0)          # base Z
        rho_err = canal_depolarizante(rho, p)
        bit_bob = medir_qubit(rho_err, 0)     # base Z

        if bit_bob != bit:
            errores += 1

    qber, se = _qber_con_error_estandar(errores, n_iter)
    return {
        "qber": qber,
        "se": se,
        "errores": errores,
        "n_iter": n_iter,
    }


# ===========================================================================
# Presentacion de resultados
# ===========================================================================

def main() -> None:
    # Forzar UTF-8 en la consola de Windows si es posible.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    n_iter = int(sys.argv[1]) if len(sys.argv) > 1 else N_ITER
    p = float(sys.argv[2]) if len(sys.argv) > 2 else P_RUIDO
    n = int(sys.argv[3]) if len(sys.argv) > 3 else N_QUBITS
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else SEED

    if n < 3 or n % 2 == 0:
        raise SystemExit("ERROR: n debe ser impar y >= 3.")
    if not (0.0 <= p <= 1.0):
        raise SystemExit("ERROR: p debe estar en [0, 1].")
    if n_iter < 1:
        raise SystemExit("ERROR: el numero de iteraciones debe ser >= 1.")

    print("=" * 80)
    print(" EXPERIMENTO DE CONTROL - ¿QEC o solo redundancia clasica?")
    print("=" * 80)
    print(f" Tamano de codigo (n) ............ {n} qubits")
    print(f" Ruido por qubit (p) ............. {p:.4f}")
    print(f" Iteraciones por escenario ....... {n_iter}")
    print(f" Canal .......................... depolarizante independiente por qubit")
    print(f" Semillas (A, B, R) .............. {seed}, {seed + 1}, {seed + 2}")
    print("-" * 80)
    print(" A) Con QEC ........ codificar -> ruido -> sindrome -> corregir -> decodificar")
    print(" B) Solo redundancia  codificar -> ruido -> (sin corregir)      -> decodificar")
    print(" R) Referencia ...... 1 qubit, sin redundancia ni mayoria")
    print("=" * 80)

    res_a = escenario_con_qec(n_iter, n, p, seed)
    res_b = escenario_solo_redundancia(n_iter, n, p, seed + 1)
    res_r = escenario_sin_redundancia(n_iter, p, seed + 2)

    dif = res_a["qber"] - res_b["qber"]
    se_dif = float(np.hypot(res_a["se"], res_b["se"]))
    z = dif / se_dif if se_dif > 0 else 0.0

    # ------------------------------------------------------------------
    # Tabla 1: comparacion solicitada
    # ------------------------------------------------------------------
    print()
    print("[1] TABLA COMPARATIVA DE QBER")
    print("-" * 80)
    print(f" {'Escenario':<44} {'QBER':>8} {'EE':>8} {'Errores':>10}")
    print("-" * 80)
    print(f" {'A) Con QEC (sindrome + correccion)':<44} "
          f"{res_a['qber']:>8.4f} {res_a['se']:>8.4f} "
          f"{res_a['errores']:>5}/{res_a['n_iter']:<4}")
    print(f" {'B) Solo redundancia (sin corregir)':<44} "
          f"{res_b['qber']:>8.4f} {res_b['se']:>8.4f} "
          f"{res_b['errores']:>5}/{res_b['n_iter']:<4}")
    print("-" * 80)
    print(f" {'Diferencia (A - B)':<44} {dif:>+8.4f} {se_dif:>8.4f}")
    print(f" {'Estadistico z = (A-B)/EE':<44} {z:>+8.2f}")
    print("-" * 80)

    # ------------------------------------------------------------------
    # Tabla 2: diagnostico del mecanismo
    # ------------------------------------------------------------------
    print()
    print("[2] DIAGNOSTICO DEL MECANISMO (Escenario A)")
    print("-" * 80)
    frac_sind = res_a["sindromes_no_triviales"] / n_iter
    frac_corr = res_a["correcciones_efectivas"] / n_iter
    print(f" Sindrome no trivial (se detecto error) ... "
          f"{res_a['sindromes_no_triviales']:>5}/{n_iter}  ({frac_sind:6.2%})")
    print(f" Correcciones efectivas aplicadas ......... "
          f"{res_a['correcciones_efectivas']:>5}/{n_iter}  ({frac_corr:6.2%})")
    print(" (Si ambos son 0, 'corregir' no modifico ningun estado: A y B")
    print("  son el mismo canal a efectos del bit decodificado.)")

    # ------------------------------------------------------------------
    # Tabla 3: referencia teorica y sin redundancia
    # ------------------------------------------------------------------
    q = 2.0 * p / 3.0
    qber_sin_red_teo = q
    qber_mayoria_3 = 3.0 * q**2 * (1.0 - q) + q**3

    print()
    print("[3] REFERENCIA: SIN REDUNDANCIA Y VALORES TEORICOS")
    print("-" * 80)
    print(f" q = 2p/3 (prob. efectiva de bit-flip por qubit) ... {q:.4f}")
    print(f" {'Escenario':<44} {'QBER':>8} {'EE':>8} {'Errores':>10}")
    print("-" * 80)
    print(f" {'R) Sin redundancia (n=1)':<44} "
          f"{res_r['qber']:>8.4f} {res_r['se']:>8.4f} "
          f"{res_r['errores']:>5}/{res_r['n_iter']:<4}")
    print("-" * 80)
    print(f" QBER teorico sin redundancia (1 qubit) ........... {qber_sin_red_teo:.4f}")
    print(f" QBER teorico mayoria de {n} (sin QEC) .............. "
          f"{qber_mayoria_3:.4f}")
    print(" (El segundo valor es 3q^2(1-q) + q^3: falla la mayoria solo si")
    print("  se invierten 2 o 3 de los 3 qubits.)")

    # ------------------------------------------------------------------
    # Lectura automatica del resultado
    # ------------------------------------------------------------------
    print()
    print("[4] LECTURA DEL RESULTADO")
    print("-" * 80)
    if abs(z) < 2.0:
        print(f" * La diferencia A - B ({dif:+.4f}) NO es significativa "
              f"(|z| = {abs(z):.2f} < 2).")
    else:
        print(f" * La diferencia A - B ({dif:+.4f}) es significativa "
              f"(|z| = {abs(z):.2f} >= 2).")

    if res_a["correcciones_efectivas"] == 0:
        print(" * corregir() no actuo en ninguna iteracion: el sindrome medido")
        print("   fue trivial y el estado llego intacto a la decodificacion.")
        print(" * Entonces, en este experimento la reduccion del QBER NO proviene")
        print("   de la correccion cuantica, sino de la redundancia (n qubits) y")
        print("   de la votacion por mayoria en decodificar().")
    else:
        print(f" * corregir() actuo en {res_a['correcciones_efectivas']} iteraciones;")
        print("   parte de la diferencia (si existe) puede atribuirse a la QEC.")

    print(" * Nota teorica: para el codigo de repeticion de bit-flip, corregir")
    print("   un error unico a partir del sindrome es operacionalmente")
    print("   equivalente a la votacion por mayoria. La ventaja de la QEC")
    print("   aparece con codigos que corrigen X y Z a la vez (p. ej. Shor o")
    print("   superficie), no con el codigo de repeticion en la base Z.")
    print("=" * 80)


if __name__ == "__main__":
    main()
