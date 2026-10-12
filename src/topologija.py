"""Definise topologiju mreze: cvorove, vremena opsluzivanja i matricu prelaza za dato K."""

import numpy as np

import konstante as k


def napravi_nazive_cvorova(broj_korisnickih_diskova):
    """Redosled naziva odredjuje indekse cvorova u matrici prelaza i vektorima."""
    nazivi = ["procesor", "sistemski_disk_1", "sistemski_disk_2", "sistemski_disk_3"]
    nazivi += [f"korisnicki_disk_{i}" for i in range(1, broj_korisnickih_diskova + 1)]
    return nazivi


def napravi_vreme_opsluzivanja(broj_korisnickih_diskova):
    """Vraca niz srednjih vremena opsluzivanja (ms), u istom redosledu kao cvorovi."""
    vremena = [
        k.VREME_OPSLUZIVANJA_PROCESOR_MS,
        k.VREME_OPSLUZIVANJA_DISK1_MS,
        k.VREME_OPSLUZIVANJA_DISK2_MS,
        k.VREME_OPSLUZIVANJA_DISK3_MS,
    ]
    vremena += [k.VREME_OPSLUZIVANJA_KORISNICKI_DISK_MS] * broj_korisnickih_diskova
    return np.array(vremena)


def napravi_matricu_prelaza(broj_korisnickih_diskova):
    """
    Gradi matricu verovatnoca prelaza P otvorene mreze sa K korisnickih diskova.

    Poredak cvorova: [procesor, sistemski_disk_1..3, korisnicki_disk_1..K].
    P[i][j] = verovatnoca da posao posle opsluzivanja na cvoru i predje na cvor j.
    Verovatnoca izlaska iz sistema sa cvora i je 1 - sum(P[i]) (korisnicki diskovi
    izlaze sa verovatnocom 1, pa su im redovi u P identicki nula).
    """
    K = broj_korisnickih_diskova
    n = 4 + K
    P = np.zeros((n, n))

    verovatnoca_po_disku_iz_procesora = k.VEROVATNOCA_PROCESOR_KORISNICKI_DISKOVI / K
    verovatnoca_po_disku_iz_sistemskog_diska = k.VEROVATNOCA_DISK_KORISNICKI_DISKOVI / K

    # Grananje posle obrade na procesoru (indeks 0)
    P[0, 1] = k.VEROVATNOCA_PROCESOR_DISK1
    P[0, 2] = k.VEROVATNOCA_PROCESOR_DISK2
    P[0, 3] = k.VEROVATNOCA_PROCESOR_DISK3
    P[0, 0] = k.VEROVATNOCA_PROCESOR_POVRATAK
    P[0, 4:] = verovatnoca_po_disku_iz_procesora

    # Grananje posle pristupa svakom sistemskom disku (indeksi 1, 2, 3)
    for indeks_diska in (1, 2, 3):
        P[indeks_diska, 0] = k.VEROVATNOCA_DISK_POVRATAK_PROCESOR
        P[indeks_diska, indeks_diska] = k.VEROVATNOCA_DISK_PONOVI_ISTI
        P[indeks_diska, 4:] = verovatnoca_po_disku_iz_sistemskog_diska

    return P
