# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
def periode_echantillonage(per_signal: float, nombre: int = 255, cycles: float = 3) -> float:
    per_tot: float = per_signal * cycles
    per_ech: float = per_tot / nombre
    return per_ech


def frequence_echantillonage(freq_signal: float, nombre: int = 255, cycles: float = 3) -> float:
    return nombre / cycles * freq_signal
