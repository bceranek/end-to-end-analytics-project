import pandas as pd
import numpy as np
from random import randint, uniform
from datetime import datetime, timedelta

# baza ścieżek (root repo)
BASE_PATH = Path(__file__).resolve().parent.parent

# input
df_dane_produkt = pd.read_csv(BASE_PATH / "data" / "dane_produkt.csv")
df_dane_ph = pd.read_csv(BASE_PATH / "data" / "dane_ph.csv")
df_slownik_produkt = pd.read_csv(BASE_PATH / "data" / "slownik_produkt.csv")
df_slownik_ph = pd.read_csv(BASE_PATH / "data" / "slownik_ph.csv")
df_slownik_sprzedaz = pd.read_csv(BASE_PATH / "data" / "slownik_sprzedaz.csv")


def build_tabela_produkt(df_dane_produkt):
    
    df_tabela_produkt = df_dane_produkt.copy()

    # kategoria i podkategoria

    df_tabela_produkt["s1"] = df_tabela_produkt["nazwa_produktu"].str.split().str[0]
    unikalne_kategorie = df_tabela_produkt["s1"].unique()
    map_kategoria = {kat: str(i+1).zfill(2) for i, kat in enumerate(unikalne_kategorie)}
    #enumerate nadaje index do kazdego elementu listy, zfill(2) dodaje 0 na poczatku jesli jest potrzeba

    df_tabela_produkt["kategoria"] = df_tabela_produkt["s1"].map(map_kategoria)

    df_tabela_produkt["s2"] = df_tabela_produkt["nazwa_produktu"].str.split().str[0] + "_" + df_tabela_produkt["nazwa_produktu"].str.split().str[1]
    unikalne_podkategorie = df_tabela_produkt["s2"].unique()
    map_podkategoria = {pod: str(i + 1).zfill(2) for i, pod in enumerate(unikalne_podkategorie)}

    df_tabela_produkt["podkategoria"] = df_tabela_produkt["s2"].map(map_podkategoria)
    

    # kod_produktu

    df_tabela_produkt["losowy_numer"] = None
    for (kat, podkat), grupa in df_tabela_produkt.groupby(["kategoria", "podkategoria"]):
        liczba_rekordow = len(grupa)

        numery = np.random.choice(
            range(1, 1001),
            size=liczba_rekordow,
            replace=False
            )
    #grupa zawiera unikalne rekordy dla kazdej kategorii i podkategorii i numery sa losowo wybrane bez powtorzen
        numery = pd.Series(numery).astype(str).str.zfill(4).values
        #zamienia tablicę numpy na Series-stringi, dodaje 0 na początku gdy potrzeba i zwraca z powrotem numpy array.
        df_tabela_produkt.loc[grupa.index, "losowy_numer"] = numery
        #przypisuje unikalne numery do wszystkich wierszy z tej grupy
    df_tabela_produkt["kod_produktu"] = df_tabela_produkt["kategoria"] + df_tabela_produkt["podkategoria"] + df_tabela_produkt["losowy_numer"]

    # koszt_wlasny

    rabat = np.random.uniform(0.3, 0.5001, size=len(df_tabela_produkt))
    df_tabela_produkt["koszt_wlasny"] = (df_tabela_produkt["wartosc_netto"] * (1 - rabat)).round(2)

    # stock

    df_tabela_produkt["stock"] = np.random.randint(200, 1301, size=len(df_tabela_produkt))

    df_tabela_produkt = df_tabela_produkt.drop(columns=["s1", "s2", "losowy_numer"])
    #porzucanie pomocniczych kolumn

    return df_tabela_produkt

def build_tabela_ph(df_dane_ph):

    df_tabela_ph = df_dane_ph.copy()

    # numer_pracownika

    df_tabela_ph["numer_pracownika"] = np.random.choice(
        range(1, 501),
        size=len(df_tabela_ph),
        replace=False
    )
    
    df_tabela_ph["numer_pracownika"] = (
        df_tabela_ph["numer_pracownika"].astype(str).str.zfill(3)
    )

    # kraj

    kraje = ["PL"] * 12 + ["DE"] * 4 + ["CZ"] * 4
    np.random.shuffle(kraje)
    df_tabela_ph["kraj"] = kraje

    # dywizja

    df_tabela_ph["dywizja"] = None

    ## DE
    current_de = df_tabela_ph["kraj"] == "DE"
    idx_de = df_tabela_ph.index[current_de]

    dywizje_de = ["DE01"] * 2 + ["DE02"] * 2
    np.random.shuffle(dywizje_de)

    df_tabela_ph.loc[idx_de, "dywizja"] = dywizje_de
    #dany index ktory spelnia warunek DE ma przypisane dywizje wczesniej przetasowana

    ## CZ
    current_cz = df_tabela_ph["kraj"] == "CZ"
    idx_cz = df_tabela_ph.index[current_cz]

    dywizje_cz = ["CZ01"] * 2 + ["CZ02"] * 2
    np.random.shuffle(dywizje_cz)

    df_tabela_ph.loc[idx_cz, "dywizja"] = dywizje_cz

    ## PL
    current_pl = df_tabela_ph["kraj"] == "PL"
    idx_pl = df_tabela_ph.index[current_pl]

    dywizje_pl = ["PL01"] * 3 + ["PL02"] * 3 + ["PL03"] * 3 + ["PL04"] * 3
    np.random.shuffle(dywizje_pl)

    df_tabela_ph.loc[idx_pl, "dywizja"] = dywizje_pl

    # czy_polska

    df_tabela_ph["czy_polska"] = np.where(
        df_tabela_ph["kraj"] == "PL",
        "x",
        ""
    )

    # email_sluzbowy

    df_tabela_ph["email_sluzbowy"] = (
        df_tabela_ph["imie"].str[0] +
        df_tabela_ph["nazwisko"]
    ).str.lower() + "@budpol.pl"

    # telefon_sluzbowy

    pierwszy_tel = 603603660
    df_tabela_ph["telefon_sluzbowy"] = [pierwszy_tel + i for i in range(len(df_tabela_ph))]

    return df_tabela_ph

def build_tabela_sprzedaz(df_tabela_produkt, df_tabela_ph):

    n_fv = 5000 
    #faktur w 2024 roku
    liczba_pozycji = np.random.randint(1, 6, size=n_fv)
    #liczba pozycji
    numery_fv = pd.Series(
        np.random.choice(np.arange(1, 10000), size=n_fv, replace=False)
    ).astype(str).str.zfill(4)
    # sales_id na poziomie faktury (np. S030157), np.arange(1, 10000) tworzy tablicę liczb 1–9999

    # sales_id

    sales_id_fv = "S" + pd.Series(liczba_pozycji).astype(str).str.zfill(2) + numery_fv
    sales_id_column = np.repeat(sales_id_fv.values, liczba_pozycji)
    #to tworzy układ: każdy wiersz= jedna pozycja sprzedaży, sales_id_fv nmoże wystąpuje tyle raz co liczba_pozycji
    df_tabela_sprzedaz = pd.DataFrame({"sales_id": sales_id_column})

    # daty

    df_fv = pd.DataFrame({"sales_id": sales_id_fv})
    # pomocnicza tabela faktur (unikalne sales_id)

    ## data_sprzedazy

    # losowy dzień sprzedaży w całym 2024 roku (01.01–31.12)
    date_range = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    df_fv["data_sprzedazy"] = np.random.choice(date_range, size=n_fv) 

    ## data_ksiegowania

    df_fv["data_ksiegowania"] = df_fv["data_sprzedazy"] + pd.Timedelta(days=1)
    weekday = df_fv["data_ksiegowania"].dt.weekday
    #jaki dzień tygodnia
    przesuniecie = (weekday == 5) * 2 + (weekday == 6) * 1
    #warunek true false (1,0), jeśli sobota +2 jeśli niedziela + 1
    df_fv["data_ksiegowania"] += pd.to_timedelta(przesuniecie, unit="D")
    #przesunięcie z soboty/niedzieli na poniedziałek
    
    # termin_platnosci i data_platnosci

    mozliwe_terminy = [1, 7, 14, 30, 45]
    df_fv["termin_platnosci"] = pd.to_timedelta(np.random.choice(mozliwe_terminy, size=n_fv), unit="D")
    df_fv["data_platnosci"] = df_fv["data_ksiegowania"] + df_fv["termin_platnosci"]

    # ph_id, klient_id, kanal_sprzedazy

    df_fv["ph_id"] = np.random.choice(df_tabela_ph["ph_id"], size=n_fv)
    df_fv["klient_id"] = pd.Series(np.random.randint(1, 101, size=n_fv)).astype(str).str.zfill(3)
    df_fv["kanal_sprzedazy"] = np.random.choice(["www", "b2b", "market"], size=n_fv)

    # merge wszystkich kolumn z df_fv do df_tabela_sprzedaz

    df_tabela_sprzedaz = df_tabela_sprzedaz.merge(
        df_fv[["sales_id", "data_sprzedazy", "data_ksiegowania", "termin_platnosci", "data_platnosci", "ph_id", "klient_id", "kanal_sprzedazy"]],
        on="sales_id",
        how="left"
    )

    # product_id

    df_tabela_sprzedaz["product_id"] = np.random.choice(df_tabela_produkt["product_id"],size=len(df_tabela_sprzedaz))

    # merge danych produktu (wartości jednostkowe)

    df_produkt_jednostkowe = df_tabela_produkt[
        ["product_id", "jm", "waga_jednostkowa_kg", 
         "wartosc_netto", "wartosc_brutto", "koszt_wlasny"]
    ].rename(columns={
        "wartosc_netto": "wartosc_netto_jednostkowa",
        "wartosc_brutto": "wartosc_brutto_jednostkowa",
        "koszt_wlasny": "koszt_wlasny_jednostkowa"
    })

    df_tabela_sprzedaz = df_tabela_sprzedaz.merge(
        df_produkt_jednostkowe,
        on="product_id",
        how="left"
    )

    # ilosc

    df_tabela_sprzedaz["ilosc"] = df_tabela_sprzedaz["jm"].apply(
        lambda x: np.random.randint(1, 100) if x == "szt" else
            round(np.random.uniform(10.5, 200.0), 2)
    )

    # wartości i koszty: wartosc_netto, wartosc_brutto, koszt_wlasny, waga_kg
    
    df_tabela_sprzedaz["waga_kg"] = df_tabela_sprzedaz["ilosc"] * df_tabela_sprzedaz["waga_jednostkowa_kg"]
    df_tabela_sprzedaz["wartosc_netto"] = (df_tabela_sprzedaz["ilosc"] * df_tabela_sprzedaz["wartosc_netto_jednostkowa"]).round(2)
    df_tabela_sprzedaz["wartosc_brutto"] = (df_tabela_sprzedaz["ilosc"] * df_tabela_sprzedaz["wartosc_brutto_jednostkowa"]).round(2)
    df_tabela_sprzedaz["koszt_wlasny"] = (df_tabela_sprzedaz["ilosc"] * df_tabela_sprzedaz["koszt_wlasny_jednostkowa"]).round(2)
    
    # usunięcie pomocniczych kolumn jednostkowych merge
    df_tabela_sprzedaz = df_tabela_sprzedaz.drop(columns=
        ["wartosc_netto_jednostkowa", "wartosc_brutto_jednostkowa", "koszt_wlasny_jednostkowa"])
    return df_tabela_sprzedaz


df_tabela_produkt = build_tabela_produkt(df_dane_produkt)
df_tabela_ph = build_tabela_ph(df_dane_ph)
df_tabela_sprzedaz = build_tabela_sprzedaz(df_tabela_produkt, df_tabela_ph)

# output
(df_tabela_produkt.to_csv(BASE_PATH / "db" / "tabela_produkt.csv", index=False))
(df_tabela_ph.to_csv(BASE_PATH / "db" / "tabela_ph.csv", index=False))
(df_tabela_sprzedaz.to_csv(BASE_PATH / "db" / "tabela_sprzedaz.csv", index=False))
