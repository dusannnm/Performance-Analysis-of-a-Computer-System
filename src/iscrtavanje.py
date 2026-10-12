"""Iscrtavanje dijagrama na osnovu analitickih rezultata."""

import math

import matplotlib

matplotlib.use("Agg")  # crtanje u fajl, bez potrebe za grafickim okruzenjem
import matplotlib.pyplot as plt

BOJA_PROCESOR = "tab:blue"
BOJA_SISTEMSKI = "tab:orange"
BOJA_KORISNICKI = "tab:green"
BOJA_SISTEM = "tab:red"


def nacrtaj_alfa_max(vrednosti_k, vrednosti_alfa_max, putanja_fajla):
    """Zadatak 2: dijagram zavisnosti granicnog intenziteta ulaznog toka alfa_max(K)."""
    plt.figure(figsize=(7, 5))
    plt.plot(vrednosti_k, vrednosti_alfa_max, marker="o", color="tab:blue")
    plt.xlabel("Broj korisnickih diskova (K)")
    plt.ylabel("alfa_max [posao/s]")
    plt.title("Zavisnost alfa_max od K")
    plt.xticks(vrednosti_k)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(putanja_fajla)
    plt.close()


def _iscrtaj_krivu_sa_beskonacnoscu(ax, vrednosti_k, vrednosti_y, boja, oznaka, labela, y_vrh):
    """Iscrtava liniju kroz konacne tacke; tamo gde je vrednost beskonacna (r=1.00 na
    kritičnom resursu) stavlja strelicu na vrh grafika umesto da pokvari razmeru ose."""
    tacke_k = [K for K, y in zip(vrednosti_k, vrednosti_y) if math.isfinite(y)]
    tacke_y = [y for y in vrednosti_y if math.isfinite(y)]

    if tacke_k:
        ax.plot(tacke_k, tacke_y, marker=oznaka, color=boja, label=labela)
    else:
        ax.plot([], [], marker=oznaka, color=boja, label=labela)  # da se pojavi u legendi

    for K, y in zip(vrednosti_k, vrednosti_y):
        if not math.isfinite(y):
            ax.plot(K, y_vrh * 0.92, marker="^", color=boja, markersize=11, clip_on=False)
            ax.annotate(
                "∞", xy=(K, y_vrh * 0.92), xytext=(K, y_vrh * 1.04),
                ha="center", va="bottom", color=boja, fontsize=17, fontweight="bold", clip_on=False,
            )


def nacrtaj_iskoriscenje_od_k(vrednosti_k, serije, r, putanja_fajla):
    """Tacka a): iskoriscenje procesora / sistemskog diska / korisnickog diska u funkciji od K."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(vrednosti_k, serije["procesor"], marker="o", color=BOJA_PROCESOR, label="procesor")
    ax.plot(vrednosti_k, serije["sistemski_disk_1"], marker="s", color=BOJA_SISTEMSKI, label="sistemski disk 1")
    ax.plot(vrednosti_k, serije["korisnicki_disk_1"], marker="^", color=BOJA_KORISNICKI, label="korisnicki disk")
    ax.set_xlabel("Broj korisnickih diskova (K)")
    ax.set_ylabel("Iskoriscenje")
    ax.set_title(f"Iskoriscenje resursa u funkciji od K (r = {r:.2f})")
    ax.set_xticks(vrednosti_k)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(putanja_fajla)
    plt.close(fig)


def nacrtaj_vreme_odziva_resursa_od_k(vrednosti_k, serije, r, putanja_fajla):
    """Tacka b): vreme odziva procesora / sistemskog diska / korisnickog diska u funkciji od K."""
    fig, ax = plt.subplots(figsize=(7, 5))

    konacne_vrednosti = [v for niz in serije.values() for v in niz if math.isfinite(v)]
    y_vrh = max(konacne_vrednosti) * 1.25 if konacne_vrednosti else 10.0

    _iscrtaj_krivu_sa_beskonacnoscu(ax, vrednosti_k, serije["procesor"], BOJA_PROCESOR, "o", "procesor", y_vrh)
    _iscrtaj_krivu_sa_beskonacnoscu(ax, vrednosti_k, serije["sistemski_disk_1"], BOJA_SISTEMSKI, "s", "sistemski disk 1", y_vrh)
    _iscrtaj_krivu_sa_beskonacnoscu(ax, vrednosti_k, serije["korisnicki_disk_1"], BOJA_KORISNICKI, "^", "korisnicki disk", y_vrh)

    ax.set_xlabel("Broj korisnickih diskova (K)")
    ax.set_ylabel("Vreme odziva [ms]")
    ax.set_title(f"Vreme odziva resursa u funkciji od K (r = {r:.2f})")
    ax.set_xticks(vrednosti_k)
    ax.set_ylim(0, y_vrh * 1.2)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(putanja_fajla)
    plt.close(fig)


def nacrtaj_vreme_odziva_sistema_od_k(vrednosti_k, vreme_odziva_sistema, r, putanja_fajla):
    """Tacka c): vreme odziva sistema u funkciji od K, jedna kriva po r."""
    fig, ax = plt.subplots(figsize=(7, 5))

    konacne_vrednosti = [v for v in vreme_odziva_sistema if math.isfinite(v)]

    if konacne_vrednosti:
        y_vrh = max(konacne_vrednosti) * 1.25
        _iscrtaj_krivu_sa_beskonacnoscu(ax, vrednosti_k, vreme_odziva_sistema, BOJA_SISTEM, "d", "sistem", y_vrh)
        ax.set_ylim(0, y_vrh * 1.2)
        ax.legend()
    else:
        # r = 1.00: alfa = alfa_max je tacno granica stabilnosti za SVAKO K, pa je
        # kriticni resurs uvek zasicen i vreme odziva sistema je beskonacno svuda.
        ax.text(
            0.5, 0.5,
            "Sistem je tacno na granici stabilnosti za svako K (r = 1.00)\nVreme odziva sistema teoretski tezi beskonacnosti za sve K",
            ha="center", va="center", transform=ax.transAxes, fontsize=10.5, color=BOJA_SISTEM, wrap=True,
        )
        ax.set_ylim(0, 1)
        ax.set_yticks([])

    ax.set_xlabel("Broj korisnickih diskova (K)")
    ax.set_ylabel("Vreme odziva sistema [ms]")
    ax.set_title(f"Vreme odziva sistema u funkciji od K (r = {r:.2f})")
    ax.set_xticks(vrednosti_k)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(putanja_fajla)
    plt.close(fig)
