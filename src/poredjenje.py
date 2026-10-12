"""Poredjenje analitickih i simulacionih rezultata - relativna odstupanja."""

import math

RESURSI_ZA_POREDJENJE = ["procesor", "sistemski_disk_1", "korisnicki_disk_1"]
PARAMETRI_PO_CVORU = ["protoci", "iskoriscenje", "prosecan_broj_poslova", "vreme_odziva_cvora"]


def _vrednost_resursa(parametri, nazivi_cvorova, resurs, parametar):
    indeks = nazivi_cvorova.index(resurs)
    return parametri[parametar][indeks]


def relativno_odstupanje(vrednost, referenca):
    """Relativno odstupanje u procentima. None ako analiticka (referentna) vrednost nije konacna."""
    if not math.isfinite(referenca) or referenca == 0:
        return None
    return abs(vrednost - referenca) / referenca * 100.0


def izracunaj_odstupanja(nazivi_cvorova_po_k, rezultati_analiticki, rezultati_sim, rezultati_sim_usrednjeno, vrednosti_k, vrednosti_r):
    """
    odstupanja[parametar][resurs][K][r] = {
        "analitika", "simulacija", "odstupanje_simulacija" (ili None),
        "usrednjeno", "odstupanje_usrednjeno" (ili None),
    }

    "sistem" je poseban "resurs" koji koristi prosecan_broj_poslova_sistem / vreme_odziva_sistema
    (postoji samo za ta dva parametra, protok i iskoriscenje su po definiciji po-resursu).
    """
    odstupanja = {}

    for parametar in PARAMETRI_PO_CVORU:
        ima_sistem = parametar in ("prosecan_broj_poslova", "vreme_odziva_cvora")
        resursi = RESURSI_ZA_POREDJENJE + (["sistem"] if ima_sistem else [])
        odstupanja[parametar] = {}

        for resurs in resursi:
            odstupanja[parametar][resurs] = {}
            for K in vrednosti_k:
                odstupanja[parametar][resurs][K] = {}
                nazivi = nazivi_cvorova_po_k[K]
                for r in vrednosti_r:
                    p_an = rezultati_analiticki[K][r]
                    p_sim = rezultati_sim[K][r]
                    p_avg = rezultati_sim_usrednjeno[K][r]

                    if resurs == "sistem":
                        kljuc = "prosecan_broj_poslova_sistem" if parametar == "prosecan_broj_poslova" else "vreme_odziva_sistema"
                        analitika, simulacija, usrednjeno = p_an[kljuc], p_sim[kljuc], p_avg[kljuc]
                    else:
                        analitika = _vrednost_resursa(p_an, nazivi, resurs, parametar)
                        simulacija = _vrednost_resursa(p_sim, nazivi, resurs, parametar)
                        usrednjeno = _vrednost_resursa(p_avg, nazivi, resurs, parametar)

                    odstupanja[parametar][resurs][K][r] = {
                        "analitika": analitika,
                        "simulacija": simulacija,
                        "odstupanje_simulacija": relativno_odstupanje(simulacija, analitika),
                        "usrednjeno": usrednjeno,
                        "odstupanje_usrednjeno": relativno_odstupanje(usrednjeno, analitika),
                    }

    return odstupanja


def uporedi_prosecna_odstupanja(odstupanja):
    """Prosecno odstupanje jedne simulacije naspram usrednjenih 100, preko svih parametara/resursa/K/r
    (racuna se samo tamo gde je analiticka vrednost konacna)."""
    zbir_sim, broj_sim = 0.0, 0
    zbir_avg, broj_avg = 0.0, 0

    for parametar in odstupanja.values():
        for resurs in parametar.values():
            for K in resurs.values():
                for stavka in K.values():
                    if stavka["odstupanje_simulacija"] is not None:
                        zbir_sim += stavka["odstupanje_simulacija"]
                        broj_sim += 1
                    if stavka["odstupanje_usrednjeno"] is not None:
                        zbir_avg += stavka["odstupanje_usrednjeno"]
                        broj_avg += 1

    prosek_sim = zbir_sim / broj_sim if broj_sim else None
    prosek_avg = zbir_avg / broj_avg if broj_avg else None
    return prosek_sim, prosek_avg
