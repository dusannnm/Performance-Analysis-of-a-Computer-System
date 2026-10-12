"""Konstante sistema definisane u tekstu zadatka (projekat_2526.pdf)."""

# Vremena opsluzivanja servera (ms), sva eksponencijalno raspodeljena
VREME_OPSLUZIVANJA_PROCESOR_MS = 4.0
VREME_OPSLUZIVANJA_DISK1_MS = 10.0
VREME_OPSLUZIVANJA_DISK2_MS = 15.0
VREME_OPSLUZIVANJA_DISK3_MS = 15.0
VREME_OPSLUZIVANJA_KORISNICKI_DISK_MS = 25.0

# Verovatnoce grananja posle obrade na procesoru (moraju da saberaju 1.0)
VEROVATNOCA_PROCESOR_DISK1 = 0.20
VEROVATNOCA_PROCESOR_DISK2 = 0.15
VEROVATNOCA_PROCESOR_DISK3 = 0.10
VEROVATNOCA_PROCESOR_KORISNICKI_DISKOVI = 0.40
VEROVATNOCA_PROCESOR_POVRATAK = 0.15

# Verovatnoce grananja posle pristupa sistemskom disku (moraju da saberaju 1.0)
VEROVATNOCA_DISK_POVRATAK_PROCESOR = 0.35
VEROVATNOCA_DISK_PONOVI_ISTI = 0.25
VEROVATNOCA_DISK_KORISNICKI_DISKOVI = 0.40

# Opseg broja korisnickih diskova K i vrednosti faktora opterecenja r
K_MIN = 2
K_MAX = 5
VREDNOSTI_R = (0.30, 0.55, 0.80, 1.00)

# Podrazumevano trajanje simulacije (u minutima simuliranog vremena, ne realnog)
PODRAZUMEVANO_TRAJANJE_SIMULACIJE_MIN = 30.0
BROJ_PONAVLJANJA_SIMULACIJE = 100

# Nazivi izlaznih fajlova (bez ekstenzije)
NAZIV_FAJLA_PROTOCI_ANALITICKI = "protoci_analiticki"
NAZIV_FAJLA_REZULTATI_ANALITICKI = "rezultati_analiticki"
NAZIV_FAJLA_REZULTATI_SIMULACIJA = "rezultati_simulacija"
NAZIV_FAJLA_REZULTATI_SIMULACIJA_USREDNJENO = "rezultati_simulacija_usrednjeno"
