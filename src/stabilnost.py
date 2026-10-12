"""Odredjivanje granicnog intenziteta ulaznog toka (alfa_max) i kritičnog resursa."""

import numpy as np


def izracunaj_alfa_max(vektor_poseta, vreme_opsluzivanja_ms):
    """
    Sistem je u stacionarnom rezimu dok je iskoriscenje svakog cvora ispod 1,
    tj. alfa * v_i * S_i < 1 za svako i (S_i u sekundama). Odatle je:

        alfa_max = min_i [ 1 / (v_i * S_i) ]      [posao/s]

    Cvor koji ostvaruje ovaj minimum prvi dostize zasicenje i predstavlja
    kriticni resurs (usko grlo) sistema.
    """
    vreme_opsluzivanja_s = vreme_opsluzivanja_ms / 1000.0
    opterecenje_po_poslu = vektor_poseta * vreme_opsluzivanja_s  # v_i * S_i, u sekundama
    granicne_vrednosti_alfa = 1.0 / opterecenje_po_poslu
    indeks_kritican = int(np.argmin(granicne_vrednosti_alfa))
    alfa_max = granicne_vrednosti_alfa[indeks_kritican]
    return alfa_max, indeks_kritican
