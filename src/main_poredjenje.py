"""Glavni skript za Fazu 3: tabele odstupanja + 12 trazenih dijagrama (a, b, c) x 4 vrednosti r."""

import os

import konstante as k
import ulaz_izlaz as io
import poredjenje as por
import iscrtavanje as isc
from main_analiticki import izracunaj_topologiju_i_stabilnost_po_k, izracunaj_dzeksonove_parametre_po_k_i_r, PUTANJA_IZLAZ, PUTANJA_PLOTOVI

RESURSI = ["procesor", "sistemski_disk_1", "korisnicki_disk_1"]


def izvuci_serije(analiticki, nazivi_cvorova_po_k, vrednosti_k, r, parametar):
    """Vraca {resurs: [vrednost za svako K]} za dati parametar i vrednost r."""
    serije = {resurs: [] for resurs in RESURSI}
    for K in vrednosti_k:
        nazivi = nazivi_cvorova_po_k[K]
        parametri = analiticki[K][r]
        for resurs in RESURSI:
            indeks = nazivi.index(resurs)
            serije[resurs].append(parametri[parametar][indeks])
    return serije


def izvuci_vreme_odziva_sistema(analiticki, vrednosti_k, r):
    return [analiticki[K][r]["vreme_odziva_sistema"] for K in vrednosti_k]


def nacrtaj_svih_12_dijagrama(analiticki, nazivi_cvorova_po_k, vrednosti_k):
    for r in k.VREDNOSTI_R:
        oznaka_r = f"{int(round(r * 100)):03d}"

        serije_iskoriscenja = izvuci_serije(analiticki, nazivi_cvorova_po_k, vrednosti_k, r, "iskoriscenje")
        isc.nacrtaj_iskoriscenje_od_k(
            vrednosti_k, serije_iskoriscenja, r, os.path.join(PUTANJA_PLOTOVI, f"iskoriscenje_r{oznaka_r}.png")
        )

        serije_vremena = izvuci_serije(analiticki, nazivi_cvorova_po_k, vrednosti_k, r, "vreme_odziva_cvora")
        isc.nacrtaj_vreme_odziva_resursa_od_k(
            vrednosti_k, serije_vremena, r, os.path.join(PUTANJA_PLOTOVI, f"vreme_odziva_resursa_r{oznaka_r}.png")
        )

        vreme_sistem = izvuci_vreme_odziva_sistema(analiticki, vrednosti_k, r)
        isc.nacrtaj_vreme_odziva_sistema_od_k(
            vrednosti_k, vreme_sistem, r, os.path.join(PUTANJA_PLOTOVI, f"vreme_odziva_sistema_r{oznaka_r}.png")
        )

        print(f"r = {r:.2f}: 3 dijagrama nacrtana")


def pokreni_poredjenje():
    rezultati_po_k = izracunaj_topologiju_i_stabilnost_po_k()
    analiticki = izracunaj_dzeksonove_parametre_po_k_i_r(rezultati_po_k)
    nazivi_cvorova_po_k = {K: rezultati_po_k[K]["nazivi_cvorova"] for K in rezultati_po_k}
    vrednosti_k = list(range(k.K_MIN, k.K_MAX + 1))

    sim, _ = io.ucitaj_rezultate_simulacije(os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_REZULTATI_SIMULACIJA + ".txt"))
    sim_usrednjeno, _ = io.ucitaj_rezultate_simulacije(
        os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_REZULTATI_SIMULACIJA_USREDNJENO + ".txt")
    )

    odstupanja = por.izracunaj_odstupanja(nazivi_cvorova_po_k, analiticki, sim, sim_usrednjeno, vrednosti_k, k.VREDNOSTI_R)
    io.upisi_izvestaj_odstupanja(odstupanja, vrednosti_k, k.VREDNOSTI_R, os.path.join(PUTANJA_IZLAZ, "izvestaj_odstupanja.txt"))

    prosek_sim, prosek_avg = por.uporedi_prosecna_odstupanja(odstupanja)
    print(f"Prosecno odstupanje jedne simulacije: {prosek_sim:.4f}%")
    print(f"Prosecno odstupanje usrednjene simulacije ({k.BROJ_PONAVLJANJA_SIMULACIJE}x): {prosek_avg:.4f}%")

    nacrtaj_svih_12_dijagrama(analiticki, nazivi_cvorova_po_k, vrednosti_k)

    print("Faza 3 (tabele + dijagrami) zavrsena.")
    return odstupanja, prosek_sim, prosek_avg


if __name__ == "__main__":
    pokreni_poredjenje()
