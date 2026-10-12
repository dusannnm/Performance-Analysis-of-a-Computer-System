"""Glavni skript za simulaciju: jedna simulacija po (K, r) i usrednjavanje 100 ponavljanja."""

import os
import random

import konstante as k
from main_analiticki import izracunaj_topologiju_i_stabilnost_po_k, PUTANJA_IZLAZ
from simulacija import Simulacija
import ulaz_izlaz as io


def usrednji_rezultate(lista_rezultata):
    """Prosek preko vise ponavljanja simulacije, cvor po cvor."""
    broj_cvorova = len(lista_rezultata[0]["protoci"])
    n = len(lista_rezultata)

    prosek = {
        "protoci": [0.0] * broj_cvorova,
        "iskoriscenje": [0.0] * broj_cvorova,
        "prosecan_broj_poslova": [0.0] * broj_cvorova,
        "vreme_odziva_cvora": [0.0] * broj_cvorova,
        "prosecan_broj_poslova_sistem": 0.0,
        "vreme_odziva_sistema": 0.0,
    }

    for rezultat in lista_rezultata:
        for i in range(broj_cvorova):
            prosek["protoci"][i] += rezultat["protoci"][i] / n
            prosek["iskoriscenje"][i] += rezultat["iskoriscenje"][i] / n
            prosek["prosecan_broj_poslova"][i] += rezultat["prosecan_broj_poslova"][i] / n
            prosek["vreme_odziva_cvora"][i] += rezultat["vreme_odziva_cvora"][i] / n
        prosek["prosecan_broj_poslova_sistem"] += rezultat["prosecan_broj_poslova_sistem"] / n
        prosek["vreme_odziva_sistema"] += rezultat["vreme_odziva_sistema"] / n

    return prosek


def pokreni_simulaciju(trajanje_min=k.PODRAZUMEVANO_TRAJANJE_SIMULACIJE_MIN, broj_ponavljanja=k.BROJ_PONAVLJANJA_SIMULACIJE):
    trajanje_ms = trajanje_min * 60000.0

    rezultati_analiticki = izracunaj_topologiju_i_stabilnost_po_k()
    nazivi_cvorova_po_k = {K: rezultati_analiticki[K]["nazivi_cvorova"] for K in rezultati_analiticki}

    jedna_simulacija_po_k = {}
    usrednjeno_po_k = {}

    for K in range(k.K_MIN, k.K_MAX + 1):
        alfa_max = rezultati_analiticki[K]["alfa_max"]
        jedna_simulacija_po_k[K] = {}
        usrednjeno_po_k[K] = {}

        for r in k.VREDNOSTI_R:
            alfa = r * alfa_max

            ponavljanja = []
            for ponavljanje in range(broj_ponavljanja):
                random.seed(1000 * K + int(r * 100) + ponavljanje)  # reproduktivnost
                simulacija = Simulacija(K, alfa, trajanje_ms)
                ponavljanja.append(simulacija.pokreni())

            jedna_simulacija_po_k[K][r] = ponavljanja[0]
            usrednjeno_po_k[K][r] = usrednji_rezultate(ponavljanja)

            print(f"K={K}, r={r:.2f} -> {broj_ponavljanja} ponavljanja gotovo")

    io.upisi_rezultate_simulacije(
        nazivi_cvorova_po_k,
        jedna_simulacija_po_k,
        os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_REZULTATI_SIMULACIJA + ".txt"),
        "Rezultati jedne simulacije (prvo od 100 ponavljanja)",
    )
    io.upisi_rezultate_simulacije(
        nazivi_cvorova_po_k,
        usrednjeno_po_k,
        os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_REZULTATI_SIMULACIJA_USREDNJENO + ".txt"),
        f"Rezultati usrednjeni preko {broj_ponavljanja} ponavljanja",
    )

    print("Simulacija zavrsena.")


if __name__ == "__main__":
    pokreni_simulaciju()
