# -*- coding: utf-8 -*-
"""Generise docs/dokumentacija.docx (Faza 3): objasnjenje metoda, tabele odstupanja,
13 grafika i odgovori na pitanja iz zadatka. Koristi rezultate koje racunaju
glavni_analiticki.py i glavni_poredjenje.py (ne treba ih posebno pokretati - ova
skripta ih poziva direktno) i grafike vec generisane u plots/ (pokrenuti
glavni_poredjenje.py bar jednom pre ovoga da grafici postoje na disku)."""

import math
import os

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import konstante as k
import ulaz_izlaz as io
import poredjenje as por
from glavni_analiticki import (
    izracunaj_topologiju_i_stabilnost_po_k,
    izracunaj_dzeksonove_parametre_po_k_i_r,
    PUTANJA_IZLAZ,
    PUTANJA_PLOTOVI,
)

PUTANJA_KORENA = os.path.join(os.path.dirname(__file__), "..")
PUTANJA_DOCS = os.path.join(PUTANJA_KORENA, "docs")
IZLAZNI_FAJL = os.path.join(PUTANJA_DOCS, "dokumentacija.docx")

RESURS_LABELE = {
    "procesor": "Procesor",
    "sistemski_disk_1": "Sistemski disk 1",
    "korisnicki_disk_1": "Korisnicki disk",
    "sistem": "SISTEM (ukupno)",
}
NAZIV_KRATKO = {"procesor": "Procesor", "korisnicki_disk": "Korisnicki disk", "sistemski_disk": "Sistemski disk"}

BOJA_AKCENT = "1B5B69"
BOJA_ZEBRA = "EAECE6"


def izracunaj_kriticni_grid(analiticki, nazivi_cvorova_po_k, vrednosti_k, vrednosti_r):
    """Za svako (K, r) vraca listu naziva resursa "grupe" (npr. 'procesor', 'korisnicki_disk')
    ciji je iskoriscenje unutar tolerancije od maksimuma (hvata egzaktne remije, npr. K=4)."""
    grid = {}
    for K in vrednosti_k:
        nazivi = nazivi_cvorova_po_k[K]
        grid[K] = {}
        for r in vrednosti_r:
            isk = analiticki[K][r]["iskoriscenje"]
            maxval = max(isk)
            grupe = set()
            for naziv, vrednost in zip(nazivi, isk):
                if vrednost >= maxval - 1e-6:
                    osnova = naziv.rsplit("_", 1)[0] if naziv.startswith("korisnicki") else naziv
                    grupe.add(osnova)
            grid[K][r] = sorted(grupe)
    return grid


class GraditeljDokumenta:
    """Tanak omotac oko python-docx Document-a sa helper metodama za ovaj izvestaj."""

    def __init__(self):
        self.doc = Document()
        normal = self.doc.styles["Normal"]
        normal.font.name = "Calibri"
        normal.font.size = Pt(10.5)

    def _senci_celiju(self, cell, hex_boja):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hex_boja)
        tcPr.append(shd)

    def h1(self, text):
        self.doc.add_heading(text, level=1)

    def h2(self, text):
        self.doc.add_heading(text, level=2)

    def p(self, text="", bold=False, italic=False, size=None, align=None, color=None, space_after=6):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_after = Pt(space_after)
        if align:
            para.alignment = align
        run = para.add_run(text)
        run.bold = bold
        run.italic = italic
        if size:
            run.font.size = Pt(size)
        if color:
            run.font.color.rgb = RGBColor.from_string(color)
        return para

    def caption(self, text):
        self.p(text, italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color="52605A", space_after=14)

    def slika(self, path, width_in=6.0):
        self.doc.add_picture(path, width=Inches(width_in))
        self.doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    def tabela(self, headers, rows, col_widths=None, font_size=8.5):
        table = self.doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        for i, htext in enumerate(headers):
            cell = table.rows[0].cells[i]
            cell.paragraphs[0].text = ""
            run = cell.paragraphs[0].add_run(htext)
            run.bold = True
            run.font.size = Pt(font_size)
            run.font.color.rgb = RGBColor.from_string("FFFFFF")
            self._senci_celiju(cell, BOJA_AKCENT)

        for ridx, row in enumerate(rows):
            cells = table.add_row().cells
            for i, val in enumerate(row):
                cells[i].paragraphs[0].text = ""
                run = cells[i].paragraphs[0].add_run(str(val))
                run.font.size = Pt(font_size)
                if ridx % 2 == 1:
                    self._senci_celiju(cells[i], BOJA_ZEBRA)

        if col_widths:
            for i, w in enumerate(col_widths):
                for row in table.rows:
                    row.cells[i].width = Inches(w)
        return table

    def pejzazna_sekcija(self):
        section = self.doc.add_section()
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = section.page_height, section.page_width
        section.left_margin = section.right_margin = Inches(0.6)
        section.top_margin = section.bottom_margin = Inches(0.6)
        return section

    def portret_sekcija(self):
        section = self.doc.add_section()
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width, section.page_height = Inches(8.27), Inches(11.69)  # A4
        return section

    def sacuvaj(self, putanja):
        self.doc.save(putanja)


def fmt_num(v, dec=3):
    if isinstance(v, float) and math.isinf(v):
        return "beskonacno"
    return f"{v:.{dec}f}"


def fmt_dev(v):
    return "N/A" if v is None else f"{v:.2f}%"


def fmt_cell(value, deviation, dec=3):
    return f"{fmt_num(value, dec)} ({fmt_dev(deviation)})"


def generisi_dokumentaciju():
    os.makedirs(PUTANJA_DOCS, exist_ok=True)

    rez = izracunaj_topologiju_i_stabilnost_po_k()
    analiticki = izracunaj_dzeksonove_parametre_po_k_i_r(rez)
    nazivi_po_k = {K: rez[K]["nazivi_cvorova"] for K in rez}
    vrednosti_k = list(range(k.K_MIN, k.K_MAX + 1))
    vrednosti_r = list(k.VREDNOSTI_R)

    sim, _ = io.ucitaj_rezultate_simulacije(os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_REZULTATI_SIMULACIJA + ".txt"))
    sim_avg, _ = io.ucitaj_rezultate_simulacije(
        os.path.join(PUTANJA_IZLAZ, k.NAZIV_FAJLA_REZULTATI_SIMULACIJA_USREDNJENO + ".txt")
    )
    odstupanja = por.izracunaj_odstupanja(nazivi_po_k, analiticki, sim, sim_avg, vrednosti_k, vrednosti_r)
    prosek_sim, prosek_avg = por.uporedi_prosecna_odstupanja(odstupanja)

    kriticni_grid = izracunaj_kriticni_grid(analiticki, nazivi_po_k, vrednosti_k, vrednosti_r)
    alfa_max_po_k = {K: rez[K]["alfa_max"] for K in vrednosti_k}

    g = GraditeljDokumenta()

    # ----------------------------------------------------------- naslovna strana
    tp = g.doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.space_before = Pt(140)
    r_ = tp.add_run("Performanse racunarskih sistema")
    r_.bold = True
    r_.font.size = Pt(24)
    r_.font.color.rgb = RGBColor.from_string(BOJA_AKCENT)

    sp = g.doc.add_paragraph()
    sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sp.paragraph_format.space_before = Pt(10)
    sp.add_run("Domaci zadatak — analiza i dokumentovanje resenja").font.size = Pt(15)

    sp2 = g.doc.add_paragraph()
    sp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sp2.paragraph_format.space_before = Pt(4)
    r_ = sp2.add_run("Skolska 2025/2026. godina")
    r_.font.size = Pt(12)
    r_.font.color.rgb = RGBColor.from_string("52605A")

    ip = g.doc.add_paragraph()
    ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ip.paragraph_format.space_before = Pt(90)
    r_ = ip.add_run(
        "Otvorena mreza: procesor + 3 sistemska diska + K korisnickih diskova\n"
        "Analiticko resenje (matricni metod, Dzeksonova teorema) i diskretna simulacija dogadjaja"
    )
    r_.font.size = Pt(10.5)
    r_.italic = True
    r_.font.color.rgb = RGBColor.from_string("52605A")

    g.doc.add_page_break()

    # ------------------------------------------------------------------- uvod
    g.h1("1. Uvod")
    g.p(
        "Predmet ovog dokumenta je performansna analiza jednostavnog multiprogramskog racunarskog "
        "sistema, modelovanog otvorenom mrezom redova cekanja. Sistem se sastoji od procesora, tri "
        "sistemska diska i K korisnickih diskova (K = 2..5). Poasonov tok poslova intenziteta alfa "
        "pristize na procesor; posle obrade posao se, prema zadatim verovatnocama, upucuje na jedan "
        "od sistemskih diskova, vraca u red procesora, ili odlazi na neki od korisnickih diskova, "
        "posle cega napusta sistem. Sva vremena opsluzivanja su eksponencijalno raspodeljena."
    )
    g.tabela(
        ["Server", "Vreme opsluzivanja"],
        [
            ["Procesor", "4 ms"],
            ["Sistemski disk 1", "10 ms"],
            ["Sistemski disk 2 / 3", "15 ms"],
            ["Korisnicki disk (svaki od K)", "25 ms"],
        ],
        col_widths=[3.2, 2.2],
    )
    g.caption("Tabela 1 — Srednja vremena opsluzivanja po serveru.")
    g.p("Zadatak je resen na dva nezavisna nacina koji se zatim medjusobno uporedjuju:")
    g.p("• Analiticko resenje — matricni metod za otvorene mreze i Dzeksonova teorema (odeljak 2).", space_after=2)
    g.p("• Simulacija — dogadjajno vodjena (DES) simulacija istog sistema, ponovljena 100 puta i usrednjena (odeljak 3).", space_after=10)
    g.p(
        "Odeljak 4 upoređuje dobijene vrednosti i njihova relativna odstupanja, odeljak 5 sadrzi "
        "trazene dijagrame, a odeljak 6 odgovara na pitanje koji je resurs kritican za svaku "
        "kombinaciju parametara r i K."
    )

    # --------------------------------------------------------- analiticko resenje
    g.h1("2. Analiticko resenje")

    g.h2("2.1 Matricni metod — vektor poseta")
    g.p(
        "Topologija mreze je predstavljena matricom verovatnoca prelaza P (Pij = verovatnoca da "
        "posao posle opsluzivanja na cvoru i predje na cvor j). Trazeni odnosi protoka i "
        "intenziteta ulaznog toka (v_i = X_i / alfa) dobijaju se resavanjem jednacine ravnoteze "
        "toka za otvorenu mrezu:"
    )
    g.p("v · (I − P) = e", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, bold=True, space_after=10)
    g.p(
        "gde je e jedinicni vektor sa 1 na mestu procesora (jedina tacka ulaska spoljasnjeg toka). "
        "Ova jednacina, za razliku od zatvorenih mreza (gde je sistem homogen i resenje se dobija "
        "trazenjem nula-prostora matrice i proizvoljno normalizuje), ima jedinstveno resenje jer "
        "spoljasnji dolasci daju apsolutnu referencu."
    )

    g.h2("2.2 Granica stabilnosti (alfa_max) i kriticni resurs")
    g.p(
        "Sistem je u stacionarnom rezimu dok je iskoriscenje svakog cvora manje od 1, tj. "
        "alfa · v_i · S_i < 1 za svako i. Odatle sledi:"
    )
    g.p("alfa_max = min_i [ 1 / (v_i · S_i) ]", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, bold=True, space_after=10)
    g.p("Cvor koji ostvaruje ovaj minimum je kriticni resurs (usko grlo) sistema. Dobijene granicne vrednosti:")
    g.tabela(["K", "alfa_max"], [[K, f"{alfa_max_po_k[K]:.2f} posao/s"] for K in vrednosti_k], col_widths=[2.0, 3.0])
    g.caption("Tabela 2 — Granicni intenzitet ulaznog toka u zavisnosti od K.")
    g.slika(os.path.join(PUTANJA_PLOTOVI, "alfa_max_K.png"), width_in=5.2)
    g.caption("Slika 1 — Zavisnost alfa_max od K.")
    g.p(
        "Kriva raste, a zatim se ravna od K = 4: opterecenje procesora po poslu (v · S = 6.25 ms) "
        "ne zavisi od K, dok opterecenje po korisnickom disku (0.4/K · 25 ms) opada sa porastom K. "
        "Za K = 2 i K = 3 korisnicki diskovi su tezi teret pa su usko grlo; na K = 4 su opterecenja "
        "tacno izjednacena (oba 6.25 ms); od K = 5 procesor trajno postaje usko grlo (detaljnije u "
        "odeljku 6)."
    )

    g.h2("2.3 Dzeksonova teorema")
    g.p(
        "Dzeksonova teorema pokazuje da se u stacionarnom rezimu svaki cvor otvorene mreze ponasa "
        "kao nezavisan M/M/1 sistem sa protokom X_i = v_i · alfa:"
    )
    g.p(
        "iskoriscenje: ρ_i = X_i · S_i        prosecan broj poslova: L_i = ρ_i / (1 − ρ_i)        "
        "vreme odziva: R_i = S_i / (1 − ρ_i)",
        align=WD_ALIGN_PARAGRAPH.CENTER, size=10.5, italic=True, space_after=10,
    )
    g.p(
        "Vreme odziva celog sistema dobija se ponovnom primenom Litlove formule na sistem kao "
        "celinu: R = (Σ L_i) / alfa. Ovi parametri su izracunati za svako K (2–5) i svaku vrednost "
        "r ∈ {0.30, 0.55, 0.80, 1.00} (alfa = r · alfa_max), i cine osnovu za dijagrame u odeljku 5 "
        "i poredjenje u odeljku 4."
    )
    g.p(
        "Napomena: za r = 1.00 kriticni resurs po definiciji dostize tacno ρ = 1, pa L_i, R_i i "
        "vreme odziva sistema teorijski teze beskonacnosti. Ovo nije numericka greska vec ocekivan "
        "rezultat tacno na granici stabilnosti, i eksplicitno se vidi u tabelama i dijagramima koji "
        "slede."
    )

    # ------------------------------------------------------------------ simulacija
    g.h1("3. Simulacija")

    g.h2("3.1 Dogadjajno vodjena simulacija")
    g.p(
        "Simulacija ne koristi idealizovane M/M/1 pretpostavke — svaki servisni centar se nezavisno "
        "modeluje generisanjem stvarnih slucajnih vremena. Koriscena je dogadjajno vodjena (DES) "
        "arhitektura: buduci dogadjaji (dolazak posla, zavrsetak usluge) cuvaju se u redu sa "
        "prioritetom (po vremenu), a sat simulacije skace direktno na sledeci dogadjaj — bez greske "
        "diskretizacije. Svaki cvor ima sopstveni FCFS red; posle zavrsetka usluge, sledeci cvor se "
        "bira kumulativnim izvlacenjem direktno nad istom matricom P koriscenom u analitickom delu, "
        "cime je garantovano da oba metoda opisuju identican sistem."
    )

    g.h2("3.2 Prikupljanje statistike")
    g.p("Za svaki cvor se prate tri nezavisne mere, standardnom tehnikom povrsine ispod krive broja poslova:")
    g.p("• Iskoriscenje ρ_i — zbir vremena kad je server zauzet, podeljen ukupnim trajanjem simulacije.", space_after=2)
    g.p("• Prosecan broj poslova L_i — povrsina ispod krive broja poslova na cvoru, podeljena trajanjem.", space_after=2)
    g.p("• Protok X_i — broj zavrsenih usluga podeljen trajanjem.", space_after=2)
    g.p("• Vreme odziva R_i — direktno izmereno (kraj − pocetak) za svaku posetu cvoru, usredeno.", space_after=10)
    g.p(
        "Ove velicine su namerno iste kao u Dzeksonovoj teoremi (odeljak 2.3), sto omogucava "
        "direktno poredjenje broj-na-broj u odeljku 4."
    )

    g.h2("3.3 Ponavljanje i usrednjavanje")
    g.p(
        f"Podrazumevano trajanje simulacije je 0.5h (30 minuta simuliranog vremena rada sistema — "
        f"parametar koji se moze podesiti). Za svaku kombinaciju K i r simulacija je pokrenuta "
        f"{k.BROJ_PONAVLJANJA_SIMULACIJE} puta sa nezavisnim semenima, a rezultati usredneni. Prvo "
        f"ponavljanje svake grupe posluzilo je kao rezultat 'jedne simulacije', dok je prosek svih "
        f"{k.BROJ_PONAVLJANJA_SIMULACIJE} ponavljanja rezultat 'usrednjene simulacije' — oba se "
        f"porede sa analitikom u sledecem odeljku."
    )

    # -------------------------------------------------------- poredjenje (pejzazno)
    g.pejzazna_sekcija()
    g.h1("4. Poredjenje rezultata")
    g.p(
        "Relativno odstupanje se racuna kao odstupanje = |simulacija − analitika| / analitika · "
        "100%. Kada je analiticka vrednost beskonacna (r = 1.00 na kritičnom resursu, videti "
        "odeljak 2.3), odstupanje je oznaceno sa N/A — deljenje sa beskonacnoscu nema smislenu "
        "interpretaciju, ali se simulirana (konacna) vrednost i dalje prikazuje jer sama po sebi "
        "pokazuje kako sistem izgleda na konacnom vremenskom horizontu tacno na granici stabilnosti."
    )
    g.p(
        "Tabele ispod prikazuju cetiri trazena parametra (protok, iskoriscenje, prosecan broj "
        "poslova, vreme odziva) u zavisnosti od K, za reprezentativne resurse (procesor, sistemski "
        "disk 1, korisnicki disk — svi korisnicki diskovi su medjusobno simetricni) i za sistem kao "
        "celinu. Format celije je: analiticka vrednost | simulirana vrednost (odstupanje) | "
        "usrednjena vrednost (odstupanje)."
    )

    resursi_ab = ["procesor", "sistemski_disk_1", "korisnicki_disk_1"]
    resursi_cd = ["procesor", "sistemski_disk_1", "korisnicki_disk_1", "sistem"]
    col_w = [1.35, 0.4, 1.15, 1.65, 1.65, 1.15, 1.65, 1.65]

    def redovi_para(param1, dec1, param2, dec2, resursi, r):
        rows = []
        for resurs in resursi:
            for K in vrednosti_k:
                row = [RESURS_LABELE[resurs], K]
                for param, dec in ((param1, dec1), (param2, dec2)):
                    if resurs not in odstupanja[param]:
                        row += ["—", "—", "—"]
                        continue
                    st = odstupanja[param][resurs][K][r]
                    row.append(fmt_num(st["analitika"], dec))
                    row.append(fmt_cell(st["simulacija"], st["odstupanje_simulacija"], dec))
                    row.append(fmt_cell(st["usrednjeno"], st["odstupanje_usrednjeno"], dec))
                rows.append(row)
        return rows

    tabela_broj = 3
    for r in vrednosti_r:
        g.h2(f"r = {r:.2f}")

        g.p("Protok [posao/s] i iskoriscenje:", bold=True, size=10, space_after=4)
        headers1 = [
            "Resurs", "K", "Protok\nanalitika", "Protok\nsimulacija (odst.)", "Protok\nusrednjeno (odst.)",
            "Iskor.\nanalitika", "Iskor.\nsimulacija (odst.)", "Iskor.\nusrednjeno (odst.)",
        ]
        g.tabela(headers1, redovi_para("protoci", 3, "iskoriscenje", 4, resursi_ab, r), col_widths=col_w)
        g.caption(f"Tabela {tabela_broj} — Protok i iskoriscenje, r = {r:.2f}.")
        tabela_broj += 1

        g.p("Prosecan broj poslova i vreme odziva [ms]:", bold=True, size=10, space_after=4)
        headers2 = [
            "Resurs", "K", "Br.posl.\nanalitika", "Br.posl.\nsimulacija (odst.)", "Br.posl.\nusrednjeno (odst.)",
            "V.odziva\nanalitika", "V.odziva\nsimulacija (odst.)", "V.odziva\nusrednjeno (odst.)",
        ]
        g.tabela(headers2, redovi_para("prosecan_broj_poslova", 3, "vreme_odziva_cvora", 2, resursi_cd, r), col_widths=col_w)
        g.caption(f"Tabela {tabela_broj} — Prosecan broj poslova i vreme odziva, r = {r:.2f}.")
        tabela_broj += 1

    g.h2("Diskusija")
    g.p(
        f"Preko svih parametara, resursa, K i r vrednosti (tamo gde je analiticka vrednost "
        f"konacna), prosecno relativno odstupanje jedne simulacije od analitike iznosi "
        f"{prosek_sim:.3f}%, dok prosecno odstupanje usrednjene simulacije (preko "
        f"{k.BROJ_PONAVLJANJA_SIMULACIJE} ponavljanja) iznosi samo {prosek_avg:.3f}% — priblizno "
        f"{prosek_sim / prosek_avg:.1f} puta manje."
    )
    g.p(
        "Usrednjena simulacija dosledno ima manje odstupanje od analitike nego pojedinacna "
        "simulacija. Razlog je zakon velikih brojeva: svaka pojedinacna simulacija je samo jedna "
        "realizacija stohastickog procesa i nosi sopstveni sum (slucajnu varijaciju) oko prave "
        "(analiticke) vrednosti. Usrednjavanjem N nezavisnih ponavljanja, standardna devijacija "
        "ocene opada srazmerno 1/√N — sa N = 100 ocekuje se priblizno 10 puta manja varijansa "
        "sredine u odnosu na jedno pojedinacno merenje, sto se i vidi u dobijenom faktoru "
        "poboljsanja. Drugim recima, sto je vise ponavljanja simulacije izvrseno, prosecna "
        "vrednost se sve vise priblizava teorijskoj (analitickoj) ocekivanoj vrednosti, dok "
        "pojedinacna simulacija ostaje podlozna slucajnim odstupanjima nezavisno od toga koliko "
        "dugo traje."
    )
    g.p(
        "Vredi napomenuti da odstupanja rastu ka r = 1.00 (sistem blizu granice stabilnosti ima "
        "veci varijabilitet reda cekanja), sto je vidljivo i u dijagramima u odeljku 5 — bas tu je "
        "razlika izmedju pojedinacne i usrednjene simulacije najizrazenija."
    )

    # ------------------------------------------------------------- dijagrami (portret)
    g.portret_sekcija()
    g.h1("5. Dijagrami")
    g.p(
        "Svi dijagrami u ovom odeljku su konstruisani na osnovu rezultata analitickog resenja "
        "(odeljak 2), za tri reprezentativna resursa: procesor, sistemski disk 1 (sistemski diskovi "
        "2 i 3 imaju istu strukturu, razlicito samo vreme opsluzivanja) i korisnicki disk (svi K "
        "korisnickih diskova su medjusobno simetricni)."
    )

    g.h2("5.1 Iskoriscenje resursa u funkciji od K")
    for r in vrednosti_r:
        oznaka = f"{int(round(r * 100)):03d}"
        g.slika(os.path.join(PUTANJA_PLOTOVI, f"iskoriscenje_r{oznaka}.png"), width_in=5.4)
        g.caption(f"r = {r:.2f}")

    g.h2("5.2 Vreme odziva resursa u funkciji od K")
    g.p(
        "Simbol ∞ na vrhu grafika oznacava cvor koji je za dato K tacno kriticni resurs pri "
        "r = 1.00 (iskoriscenje = 1, vreme odziva teorijski beskonacno) — videti odeljak 2.3 i 6."
    )
    for r in vrednosti_r:
        oznaka = f"{int(round(r * 100)):03d}"
        g.slika(os.path.join(PUTANJA_PLOTOVI, f"vreme_odziva_resursa_r{oznaka}.png"), width_in=5.4)
        g.caption(f"r = {r:.2f}")

    g.h2("5.3 Vreme odziva sistema u funkciji od K")
    g.p(
        "Za r = 1.00 je vreme odziva sistema beskonacno za svako K bez izuzetka: sistem je po "
        "definiciji r = alfa/alfa_max tacno na granici stabilnosti, pa kriticni resurs (koji god da "
        "je za dato K) uvek dostize iskoriscenje 1, sto povlaci beskonacan ukupan broj poslova u "
        "sistemu i beskonacno vreme odziva. Dijagram za r = 1.00 zato eksplicitno navodi ovaj "
        "zakljucak umesto krive."
    )
    for r in vrednosti_r:
        oznaka = f"{int(round(r * 100)):03d}"
        g.slika(os.path.join(PUTANJA_PLOTOVI, f"vreme_odziva_sistema_r{oznaka}.png"), width_in=5.4)
        g.caption(f"r = {r:.2f}")

    # ---------------------------------------------------------------- kriticni resurs
    g.h1("6. Kriticni resurs")
    g.p("Kriticni resurs (resurs sa najvecim iskoriscenjem) za svaku kombinaciju K i r:")
    headers_kr = ["K"] + [f"r = {r:.2f}" for r in vrednosti_r]
    rows_kr = []
    for K in vrednosti_k:
        row = [K]
        for r in vrednosti_r:
            imena = kriticni_grid[K][r]
            row.append(" i ".join(NAZIV_KRATKO.get(n, n) for n in imena))
        rows_kr.append(row)
    g.tabela(headers_kr, rows_kr, col_widths=[0.7, 2.3, 2.3, 2.3, 2.3], font_size=9.5)
    g.caption("Tabela 12 — Kriticni resurs po (K, r).")
    g.p(
        "Kljucno zapazanje: identitet kritičnog resursa zavisi iskljucivo od K, ne od r. Razlog je "
        "strukturan — iskoriscenje svakog cvora je ρ_i = r · (v_i·S_i)/(v_krit·S_krit), pa r "
        "skalira iskoriscenje svih resursa proporcionalno i ne menja koji od njih ima najvece "
        "opterecenje po poslu."
    )
    g.p("• K = 2, 3: korisnicki diskovi su usko grlo (opterecenje po poslu 12.5 ms, odnosno 8.33 ms — najvece u sistemu).", space_after=2)
    g.p("• K = 4: procesor i svi korisnicki diskovi imaju tacno isto opterecenje (6.25 ms) — egzaktna izjednacenost, ne numericki artefakt.", space_after=2)
    g.p("• K = 5: procesor postaje trajno usko grlo (6.25 ms opterecenje procesora > 5.0 ms po korisnickom disku).", space_after=10)

    # -------------------------------------------------------------------- zakljucak
    g.h1("7. Zakljucak")
    g.p(
        "Analiticko resenje (matricni metod + Dzeksonova teorema) i dogadjajno vodjena simulacija "
        "istog sistema medjusobno se slazu u granicama statistickog suma: prosecno odstupanje "
        f"pojedinacne simulacije je {prosek_sim:.2f}%, a usrednjene simulacije (100 ponavljanja) "
        f"samo {prosek_avg:.2f}%, sto potvrdjuje ispravnost obe implementacije i medjusobnu "
        "konzistentnost topologije koriscene u oba metoda."
    )
    g.p(
        "Usrednjavanje vise nezavisnih ponavljanja simulacije dosledno smanjuje odstupanje od "
        "teorijske vrednosti, u skladu sa zakonom velikih brojeva (σ opada srazmerno 1/√N). Ovo je "
        "narocito izrazeno pri visim vrednostima r, gde je varijabilnost sistema veca."
    )
    g.p(
        "Granicni slucaj r = 1.00 (sistem tacno na granici stabilnosti) pokazuje vaznu razliku "
        "izmedju dva metoda: analiticko M/M/1 resenje daje beskonacan prosecan broj poslova i "
        "vreme odziva na kritičnom resursu (matematicki tacno, ali samo asimptotski, u granici "
        "beskonacnog vremena), dok simulacija — koja radi na konacnom vremenskom horizontu od 30 "
        "minuta — pokazuje veliki, ali konacan red cekanja. Oba rezultata su tacna u svom domenu i "
        "zajedno daju potpuniju sliku ponasanja sistema blizu zasicenja nego bilo koji metod "
        "pojedinacno."
    )
    g.p(
        "Identitet kritičnog resursa zavisi iskljucivo od broja korisnickih diskova K, a ne od "
        "intenziteta ulaznog toka r: korisnicki diskovi su usko grlo za K ∈ {2, 3}, procesor i "
        "korisnicki diskovi su tacno izjednaceni na K = 4, a procesor je trajno usko grlo za K = 5."
    )

    g.sacuvaj(IZLAZNI_FAJL)
    print("Dokumentacija sacuvana:", IZLAZNI_FAJL)


if __name__ == "__main__":
    generisi_dokumentaciju()
