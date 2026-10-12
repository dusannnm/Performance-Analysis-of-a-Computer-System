"""Dogadjajno vodjena (event-driven) simulacija otvorene mreze za dato K i alfa."""

import heapq
import random

import topologija


class Simulacija:
    """Jedno izvrsavanje simulacije mreze u trajanju od trajanje_ms simuliranog vremena.

    alfa se prosledjuje u posao/s (isto kao u analitickom delu), a interno se
    simulacija vodi u ms (isto kao vremena opsluzivanja), pa se alfa konvertuje
    u posao/ms za generisanje medjudolaznih vremena.
    """

    def __init__(self, K, alfa, trajanje_ms):
        self.alfa = alfa
        self.alfa_po_ms = alfa / 1000.0
        self.trajanje_ms = trajanje_ms

        self.nazivi_cvorova = topologija.napravi_nazive_cvorova(K)
        self.vreme_opsluzivanja = topologija.napravi_vreme_opsluzivanja(K)
        self.matrica_prelaza = topologija.napravi_matricu_prelaza(K)
        self.broj_cvorova = len(self.nazivi_cvorova)

        # buduci dogadjaji (FES) - heap od (vreme, redni_broj, tip, cvor, posao_id)
        # redni_broj sluzi samo da razbije remi kad su dva dogadjaja u isto vreme
        self.dogadjaji = []
        self.brojac_dogadjaja = 0

        # red_na_cvoru[i] je lista id-jeva poslova na cvoru i, prvi u listi je taj koji se trenutno opsluzuje
        self.red_na_cvoru = [[] for _ in range(self.broj_cvorova)]

        self.vreme_poslednje_izmene = [0.0] * self.broj_cvorova
        self.povrsina_broja_poslova = [0.0] * self.broj_cvorova  # za prosecan broj poslova (Litl)
        self.vreme_pocetka_usluge = [0.0] * self.broj_cvorova
        self.vreme_zauzetosti = [0.0] * self.broj_cvorova  # za iskoriscenje
        self.zbir_vremena_u_cvoru = [0.0] * self.broj_cvorova  # za vreme odziva cvora
        self.broj_zavrsenih_na_cvoru = [0] * self.broj_cvorova  # za protok

        self.vreme_ulaska_u_cvor = {}
        self.vreme_ulaska_u_sistem = {}
        self.vremena_odziva_sistema = []

        self.sledeci_id_posla = 0

    def zakazi(self, vreme, tip, cvor=None, posao_id=None):
        self.brojac_dogadjaja += 1
        heapq.heappush(self.dogadjaji, (vreme, self.brojac_dogadjaja, tip, cvor, posao_id))

    def azuriraj_statistiku_cvora(self, cvor, novo_vreme):
        # dodaje povrsinu ispod krive broja poslova na cvoru od poslednje izmene do sada
        proteklo = novo_vreme - self.vreme_poslednje_izmene[cvor]
        self.povrsina_broja_poslova[cvor] += len(self.red_na_cvoru[cvor]) * proteklo
        self.vreme_poslednje_izmene[cvor] = novo_vreme

    def pokreni(self):
        self.zakazi(random.expovariate(self.alfa_po_ms), "DOLAZAK")

        while self.dogadjaji:
            vreme, _, tip, cvor, posao_id = heapq.heappop(self.dogadjaji)
            if vreme > self.trajanje_ms:
                break

            if tip == "DOLAZAK":
                self.obradi_spoljasnji_dolazak(vreme)
            else:
                self.obradi_zavrsetak_usluge(cvor, posao_id, vreme)

        # na kraju simuliranog vremena treba "zatvoriti" statistiku do trajanje_ms
        for cvor in range(self.broj_cvorova):
            self.azuriraj_statistiku_cvora(cvor, self.trajanje_ms)
            if self.red_na_cvoru[cvor]:  # server je jos uvek zauzet kad je simulacija stala
                self.vreme_zauzetosti[cvor] += self.trajanje_ms - self.vreme_pocetka_usluge[cvor]

        return self.sakupi_rezultate()

    def obradi_spoljasnji_dolazak(self, vreme):
        posao_id = self.sledeci_id_posla
        self.sledeci_id_posla += 1
        self.vreme_ulaska_u_sistem[posao_id] = vreme

        self.posao_stize_na_cvor(0, posao_id, vreme)  # 0 = procesor

        self.zakazi(vreme + random.expovariate(self.alfa_po_ms), "DOLAZAK")

    def posao_stize_na_cvor(self, cvor, posao_id, vreme):
        self.azuriraj_statistiku_cvora(cvor, vreme)

        self.vreme_ulaska_u_cvor[posao_id] = vreme
        red = self.red_na_cvoru[cvor]
        red.append(posao_id)

        if len(red) == 1:  # server je bio slobodan, usluga pocinje odmah
            self.vreme_pocetka_usluge[cvor] = vreme
            trajanje_usluge = random.expovariate(1.0 / self.vreme_opsluzivanja[cvor])
            self.zakazi(vreme + trajanje_usluge, "ZAVRSETAK", cvor, posao_id)

    def obradi_zavrsetak_usluge(self, cvor, posao_id, vreme):
        self.azuriraj_statistiku_cvora(cvor, vreme)

        self.vreme_zauzetosti[cvor] += vreme - self.vreme_pocetka_usluge[cvor]
        self.zbir_vremena_u_cvoru[cvor] += vreme - self.vreme_ulaska_u_cvor[posao_id]
        self.broj_zavrsenih_na_cvoru[cvor] += 1

        red = self.red_na_cvoru[cvor]
        red.pop(0)

        if red:  # ima jos poslova u redu, sledeci pocinje uslugu odmah
            self.vreme_pocetka_usluge[cvor] = vreme
            trajanje_usluge = random.expovariate(1.0 / self.vreme_opsluzivanja[cvor])
            self.zakazi(vreme + trajanje_usluge, "ZAVRSETAK", cvor, red[0])

        sledeci_cvor = self.izaberi_sledeci_cvor(cvor)
        if sledeci_cvor is None:
            self.vremena_odziva_sistema.append(vreme - self.vreme_ulaska_u_sistem.pop(posao_id))
        else:
            self.posao_stize_na_cvor(sledeci_cvor, posao_id, vreme)

    def izaberi_sledeci_cvor(self, cvor):
        # bira sledeci cvor po redovima matrice prelaza, ostatak verovatnoce = izlazak iz sistema
        slucajan_broj = random.random()
        kumulativno = 0.0
        for sledeci in range(self.broj_cvorova):
            kumulativno += self.matrica_prelaza[cvor, sledeci]
            if slucajan_broj < kumulativno:
                return sledeci
        return None

    def sakupi_rezultate(self):
        # broj_zavrsenih/trajanje_ms je protok u posao/ms, *1000 da bude posao/s
        protoci = [1000.0 * self.broj_zavrsenih_na_cvoru[i] / self.trajanje_ms for i in range(self.broj_cvorova)]
        iskoriscenje = [self.vreme_zauzetosti[i] / self.trajanje_ms for i in range(self.broj_cvorova)]
        prosecan_broj_poslova = [self.povrsina_broja_poslova[i] / self.trajanje_ms for i in range(self.broj_cvorova)]

        vreme_odziva_cvora = []
        for i in range(self.broj_cvorova):
            if self.broj_zavrsenih_na_cvoru[i] > 0:
                vreme_odziva_cvora.append(self.zbir_vremena_u_cvoru[i] / self.broj_zavrsenih_na_cvoru[i])
            else:
                vreme_odziva_cvora.append(0.0)

        vreme_odziva_sistema = 0.0
        if self.vremena_odziva_sistema:
            vreme_odziva_sistema = sum(self.vremena_odziva_sistema) / len(self.vremena_odziva_sistema)

        return {
            "protoci": protoci,
            "iskoriscenje": iskoriscenje,
            "prosecan_broj_poslova": prosecan_broj_poslova,
            "vreme_odziva_cvora": vreme_odziva_cvora,
            "prosecan_broj_poslova_sistem": sum(prosecan_broj_poslova),
            "vreme_odziva_sistema": vreme_odziva_sistema,
        }
