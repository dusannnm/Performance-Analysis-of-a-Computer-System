"""Matricni metod za racunanje vektora poseta (relativnih protoka) otvorene mreze."""

import numpy as np


def izracunaj_vektor_poseta(matrica_prelaza, indeks_ulaznog_cvora=0):
    """
    Resava v * (I - P) = e po vektoru poseta v.

    e je jedinicni vektor sa 1 na mestu cvora u koji ulazi spoljasnji Poasonov tok
    (procesor). v[i] je ocekivan broj poseta cvoru i po jednom poslu koji udje u
    sistem, tj. odnos protoka kroz cvor i i intenziteta ulaznog toka alfa (X_i/alfa).
    """
    n = matrica_prelaza.shape[0]
    e = np.zeros(n)
    e[indeks_ulaznog_cvora] = 1.0

    # v (I - P) = e  <=>  (I - P)^T v^T = e^T, pa se resava transponovani sistem
    matrica_sistema = (np.eye(n) - matrica_prelaza).T
    vektor_poseta = np.linalg.solve(matrica_sistema, e)
    return vektor_poseta


def izracunaj_protoke(vektor_poseta, alfa):
    """Protok kroz svaki cvor: X_i = v_i * alfa."""
    return vektor_poseta * alfa
