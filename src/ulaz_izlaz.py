"""Upis analitickih rezultata u citljive tekstualne fajlove."""

import re


def upisi_protoke_analiticki(rezultati_po_k, putanja_fajla):
    """Zadatak 1: odnosi protoka i intenziteta ulaznog toka (v_i = X_i/alfa) po K."""
    with open(putanja_fajla, "w", encoding="utf-8") as fajl:
        fajl.write("Protoci analiticki (X_i / alfa) po cvorovima mreze\n")
        fajl.write("Dobijeno matricnim metodom za otvorene mreze: v * (I - P) = e\n\n")
        for K, podaci in rezultati_po_k.items():
            fajl.write(f"K = {K}\n")
            fajl.write(f"{'cvor':<20}{'v_i (X_i/alfa)':>18}\n")
            for naziv, v_i in zip(podaci["nazivi_cvorova"], podaci["vektor_poseta"]):
                fajl.write(f"{naziv:<20}{v_i:>18.6f}\n")
            fajl.write("\n")


def upisi_alfa_max(rezultati_po_k, putanja_fajla):
    """Zadatak 2: granicne vrednosti alfa_max i kriticni resurs po K."""
    with open(putanja_fajla, "w", encoding="utf-8") as fajl:
        fajl.write("Granicne vrednosti intenziteta ulaznog toka (alfa_max) i kriticni resurs po K\n\n")
        fajl.write(f"{'K':<6}{'alfa_max [posao/s]':>22}   kriticni resurs\n")
        for K, podaci in rezultati_po_k.items():
            fajl.write(f"{K:<6}{podaci['alfa_max']:>22.6f}   {podaci['kriticni_resurs']}\n")


def upisi_rezultate_analiticki(rezultati_po_k, svi_parametri, putanja_fajla):
    """Zadatak 3: Dzeksonovi parametri (protok, iskoriscenje, br. poslova, vreme odziva) po K i r."""
    with open(putanja_fajla, "w", encoding="utf-8") as fajl:
        fajl.write("Rezultati analitickog resavanja (Dzeksonova teorema)\n\n")
        for K, po_r in svi_parametri.items():
            nazivi_cvorova = rezultati_po_k[K]["nazivi_cvorova"]
            for r, parametri in po_r.items():
                alfa = r * rezultati_po_k[K]["alfa_max"]
                fajl.write(f"K = {K}, r = {r:.2f} (alfa = {alfa:.6f} posla/s)\n")
                fajl.write(
                    f"{'cvor':<20}{'protok[posao/s]':>16}{'iskoriscenje':>14}"
                    f"{'br.poslova':>12}{'vreme_odziva[ms]':>18}\n"
                )
                for i, naziv in enumerate(nazivi_cvorova):
                    fajl.write(
                        f"{naziv:<20}"
                        f"{parametri['protoci'][i]:>16.6f}"
                        f"{parametri['iskoriscenje'][i]:>14.6f}"
                        f"{parametri['prosecan_broj_poslova'][i]:>12.6f}"
                        f"{parametri['vreme_odziva_cvora'][i]:>18.6f}\n"
                    )
                indeks_kriticni = int(parametri["iskoriscenje"].argmax())
                fajl.write(f"Prosecan broj poslova u sistemu: {parametri['prosecan_broj_poslova_sistem']:.6f}\n")
                fajl.write(f"Vreme odziva sistema: {parametri['vreme_odziva_sistema']:.6f} ms\n")
                fajl.write(f"Kriticni resurs (najvece iskoriscenje): {nazivi_cvorova[indeks_kriticni]}\n\n")


def upisi_rezultate_simulacije(nazivi_cvorova_po_k, svi_parametri, putanja_fajla, naslov):
    """Isti format kao rezultati_analiticki, koristi se i za jednu simulaciju i za usrednjeno."""
    with open(putanja_fajla, "w", encoding="utf-8") as fajl:
        fajl.write(f"{naslov}\n\n")
        for K, po_r in svi_parametri.items():
            nazivi_cvorova = nazivi_cvorova_po_k[K]
            for r, parametri in po_r.items():
                fajl.write(f"K = {K}, r = {r:.2f}\n")
                fajl.write(
                    f"{'cvor':<20}{'protok[posao/s]':>16}{'iskoriscenje':>14}"
                    f"{'br.poslova':>12}{'vreme_odziva[ms]':>18}\n"
                )
                for i, naziv in enumerate(nazivi_cvorova):
                    fajl.write(
                        f"{naziv:<20}"
                        f"{parametri['protoci'][i]:>16.6f}"
                        f"{parametri['iskoriscenje'][i]:>14.6f}"
                        f"{parametri['prosecan_broj_poslova'][i]:>12.6f}"
                        f"{parametri['vreme_odziva_cvora'][i]:>18.6f}\n"
                    )
                indeks_kriticni = parametri["iskoriscenje"].index(max(parametri["iskoriscenje"]))
                fajl.write(f"Prosecan broj poslova u sistemu: {parametri['prosecan_broj_poslova_sistem']:.6f}\n")
                fajl.write(f"Vreme odziva sistema: {parametri['vreme_odziva_sistema']:.6f} ms\n")
                fajl.write(f"Kriticni resurs (najvece iskoriscenje): {nazivi_cvorova[indeks_kriticni]}\n\n")


def ucitaj_rezultate_simulacije(putanja_fajla):
    """Cita nazad fajl koji je napisala upisi_rezultate_simulacije (izbegava ponovno,
    skupo pokretanje 100 ponavljanja simulacije samo da bi se uporedilo sa analitikom).

    Vraca (svi_parametri, nazivi_cvorova_po_k) - isti oblik kakav koristi glavni_analiticki.
    """
    zaglavlje_bloka = re.compile(r"^K = (\d+), r = ([\d.]+)")

    svi_parametri = {}
    nazivi_cvorova_po_k = {}
    K = None
    r = None
    trenutni = None
    nazivi_trenutno = []

    with open(putanja_fajla, "r", encoding="utf-8") as fajl:
        for linija in fajl:
            linija = linija.rstrip("\n")

            poklapanje = zaglavlje_bloka.match(linija)
            if poklapanje:
                K = int(poklapanje.group(1))
                r = round(float(poklapanje.group(2)), 2)
                trenutni = {"protoci": [], "iskoriscenje": [], "prosecan_broj_poslova": [], "vreme_odziva_cvora": []}
                nazivi_trenutno = []
                svi_parametri.setdefault(K, {})[r] = trenutni
                continue

            if trenutni is None or not linija.strip() or linija.startswith("cvor"):
                continue

            if linija.startswith("Prosecan broj poslova u sistemu:"):
                trenutni["prosecan_broj_poslova_sistem"] = float(linija.split(":")[1])
                continue
            if linija.startswith("Vreme odziva sistema:"):
                trenutni["vreme_odziva_sistema"] = float(linija.split(":")[1].strip().split()[0])
                continue
            if linija.startswith("Kriticni resurs"):
                nazivi_cvorova_po_k[K] = nazivi_trenutno
                continue

            delovi = linija.split()
            if len(delovi) == 5:
                naziv, protok, iskoriscenje, brp, vreme_odziva = delovi
                nazivi_trenutno.append(naziv)
                trenutni["protoci"].append(float(protok))
                trenutni["iskoriscenje"].append(float(iskoriscenje))
                trenutni["prosecan_broj_poslova"].append(float(brp))
                trenutni["vreme_odziva_cvora"].append(float(vreme_odziva))

    return svi_parametri, nazivi_cvorova_po_k


def upisi_izvestaj_odstupanja(odstupanja, vrednosti_k, vrednosti_r, putanja_fajla):
    """Zadatak iz 'Analiza i dokumentovanje': tabelarni izvestaj odstupanja simulacije od analitike."""
    nazivi_parametara = {
        "protoci": "Protok [posao/s]",
        "iskoriscenje": "Iskoriscenje",
        "prosecan_broj_poslova": "Prosecan broj poslova",
        "vreme_odziva_cvora": "Vreme odziva [ms]",
    }

    with open(putanja_fajla, "w", encoding="utf-8") as fajl:
        fajl.write("Relativna odstupanja simulacije od analitickog resenja\n")
        fajl.write("odstupanje = |simulacija - analitika| / analitika * 100%   (N/A = analiticka vrednost je beskonacna)\n\n")

        for r in vrednosti_r:
            fajl.write(f"===== r = {r:.2f} =====\n\n")
            for parametar, naslov in nazivi_parametara.items():
                if parametar not in odstupanja:
                    continue
                fajl.write(f"-- {naslov} --\n")
                fajl.write(
                    f"{'resurs':<20}{'K':>4}{'analitika':>14}{'simulacija':>14}"
                    f"{'odst.sim[%]':>13}{'usrednjeno':>14}{'odst.usr[%]':>13}\n"
                )
                for resurs, po_k in odstupanja[parametar].items():
                    for K in vrednosti_k:
                        st = po_k[K][r]
                        odst_sim = f"{st['odstupanje_simulacija']:.3f}" if st["odstupanje_simulacija"] is not None else "N/A"
                        odst_avg = f"{st['odstupanje_usrednjeno']:.3f}" if st["odstupanje_usrednjeno"] is not None else "N/A"
                        fajl.write(
                            f"{resurs:<20}{K:>4}"
                            f"{st['analitika']:>14.4f}{st['simulacija']:>14.4f}{odst_sim:>13}"
                            f"{st['usrednjeno']:>14.4f}{odst_avg:>13}\n"
                        )
                fajl.write("\n")
