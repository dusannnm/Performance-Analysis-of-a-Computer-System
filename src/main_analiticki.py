"""Glavni skript za analiticko resavanje: matricni metod, alfa_max i Dzeksonova teorema."""

import os

import konstante as k
import topologija
import vektor_poseta as vp
import stabilnost
import dzeksonova_teorema as dz
import ulaz_izlaz as io
import iscrtavanje

PUTANJA_KORENA = os.path.join(os.path.dirname(__file__), "..")
PUTANJA_IZLAZ = os.path.join(PUTANJA_KORENA, "output")
PUTANJA_PLOTOVI = os.path.join(PUTANJA_KORENA, "plots")


def izracunaj_topologiju_i_stabilnost_po_k():
    """Za svako K u opsegu [K_MIN, K_MAX] gradi mrezu i racuna vektor poseta i alfa_max."""
    rezultati_po_k = {}
    for K in range(k.K_MIN, k.K_MAX + 1):
        nazivi_cvorova = topologija.napravi_nazive_cvorova(K)
        vreme_opsluzivanja = topologija.napravi_vreme_opsluzivanja(K)
        matrica_prelaza = topologija.napravi_matricu_prelaza(K)

        vektor = vp.izracunaj_vektor_poseta(matrica_prelaza)
        alfa_max, indeks_kritican = stabilnost.izracunaj_alfa_max(vektor, vreme_opsluzivanja)

        rezultati_po_k[K] = {
            "nazivi_cvorova": nazivi_cvorova,
            "vreme_opsluzivanja": vreme_opsluzivanja,
            "vektor_poseta": vektor,
            "alfa_max": alfa_max,
            "kriticni_resurs": nazivi_cvorova[indeks_kritican],
        }
    return rezultati_po_k


def izracunaj_dzeksonove_parametre_po_k_i_r(rezultati_po_k):
    """Za svako K i svako r racuna Dzeksonove parametre mreze pri alfa = r * alfa_max(K)."""
    svi_parametri = {}
    for K, podaci in rezultati_po_k.items():
        svi_parametri[K] = {}
        for r in k.VREDNOSTI_R:
            alfa = r * podaci["alfa_max"]
            svi_parametri[K][r] = dz.izracunaj_parametre_mreze(
                podaci["vektor_poseta"], podaci["vreme_opsluzivanja"], alfa
            )
    return svi_parametri


def pokreni_analiticko_resavanje():
    os.makedirs(PUTANJA_IZLAZ, exist_ok=True)
    os.makedirs(PUTANJA_PLOTOVI, exist_ok=True)

    rezultati_po_k = izracunaj_topologiju_i_stabilnost_po_k()

    io.upisi_protoke_analiticki(
        rezultati_po_k, os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_PROTOCI_ANALITICKI + ".txt")
    )
    io.upisi_alfa_max(rezultati_po_k, os.path.join(PUTANJA_IZLAZ, "alfa_max_i_kriticni_resurs.txt"))

    vrednosti_k = list(range(k.K_MIN, k.K_MAX + 1))
    vrednosti_alfa_max = [rezultati_po_k[K]["alfa_max"] for K in vrednosti_k]
    iscrtavanje.nacrtaj_alfa_max(
        vrednosti_k, vrednosti_alfa_max, os.path.join(PUTANJA_PLOTOVI, "alfa_max_K.png")
    )

    svi_parametri = izracunaj_dzeksonove_parametre_po_k_i_r(rezultati_po_k)
    io.upisi_rezultate_analiticki(
        rezultati_po_k, svi_parametri, os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_REZULTATI_ANALITICKI + ".txt")
    )

    print("Analiticko resavanje zavrseno.")
    print(f"Izlazni fajlovi: {PUTANJA_IZLAZ}")
    print(f"Grafik alfa_max(K): {PUTANJA_PLOTOVI}")


if __name__ == "__main__":
    pokreni_analiticko_resavanje()
