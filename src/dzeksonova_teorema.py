"""Racunanje parametara mreze (iskoriscenje, broj poslova, vreme odziva) po Dzeksonovoj teoremi."""

import numpy as np


def izracunaj_parametre_mreze(vektor_poseta, vreme_opsluzivanja_ms, alfa):
    """
    Dzeksonova teorema: u stacionarnom rezimu se svaki cvor otvorene mreze ponasa
    kao nezavisan M/M/1 sistem sa sopstvenim protokom X_i = v_i * alfa (alfa u
    posao/s). Za svaki cvor vazi:

        rho_i = X_i * S_i                    (iskoriscenje, S_i u sekundama)
        L_i   = rho_i / (1 - rho_i)          (prosecan broj poslova, M/M/1)
        R_i   = S_i / (1 - rho_i)            (vreme odziva, Litlova formula R_i = L_i / X_i)

    R_i se racuna direktno sa S_i u ms, pa izlazi u ms (isto vazi i za rezultat R_i
    dobijen deljenjem sa X_i - jedinice se poklapaju sa jedinicama S_i).

    Vreme odziva celog sistema (sa centralnim serverom) se dobija ponovnom
    primenom Litlove formule na sistem kao celinu: R = (suma L_i) / alfa, sto je u
    sekundama pa se mnozi sa 1000 da bude u ms (kao i R_i po cvoru).

    Za r = 1.00 (alfa = alfa_max) kriticni resurs dostize iskoriscenje = 1, sto je
    tacno granica stabilnosti - L_i i R_i tog cvora (a time i celog sistema) tada
    teorijski teze beskonacnosti. Ovo nije numericka greska vec ocekivan rezultat
    koji se komentarise u dokumentaciji.
    """
    vreme_opsluzivanja_s = vreme_opsluzivanja_ms / 1000.0
    protoci = vektor_poseta * alfa
    iskoriscenje = protoci * vreme_opsluzivanja_s

    TOLERANCIJA_ZAOKRUZIVANJA = 1e-9
    if np.any(iskoriscenje > 1.0 + TOLERANCIJA_ZAOKRUZIVANJA):
        raise ValueError("Sistem nije stabilan za dato alfa (iskoriscenje > 1 na nekom cvoru).")
    # Vrednosti u granicama tolerancije oko 1.0 se "lepe" za tacno 1.0, tako da
    # (1 - rho) postane tacno 0 i deljenje da tacno beskonacnost (inf), umesto
    # ogromnog ali konacnog broja koji bi nastao od zaokruzivanja u pokretnom zarezu.
    blizu_granice = np.abs(iskoriscenje - 1.0) <= TOLERANCIJA_ZAOKRUZIVANJA
    iskoriscenje = np.where(blizu_granice, 1.0, iskoriscenje)

    with np.errstate(divide="ignore"):
        prosecan_broj_poslova = iskoriscenje / (1.0 - iskoriscenje)
        vreme_odziva_cvora = vreme_opsluzivanja_ms / (1.0 - iskoriscenje)

    prosecan_broj_poslova_sistem = float(np.sum(prosecan_broj_poslova))
    vreme_odziva_sistema = 1000.0 * prosecan_broj_poslova_sistem / alfa

    return {
        "protoci": protoci,
        "iskoriscenje": iskoriscenje,
        "prosecan_broj_poslova": prosecan_broj_poslova,
        "vreme_odziva_cvora": vreme_odziva_cvora,
        "prosecan_broj_poslova_sistem": prosecan_broj_poslova_sistem,
        "vreme_odziva_sistema": vreme_odziva_sistema,
    }
