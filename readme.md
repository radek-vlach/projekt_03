# 🗳️ Election Scraper 2017

Tento Python skript slouží k scrapování (automatizovanému sběru) výsledků parlamentních voleb konaných v roce 2017 ze serveru [volby.cz](https://www.volby.cz).

Skript vyextrahuje data pro zvolený územní celek (okres) a výsledky všech obcí přehledně uloží do souboru formátu **CSV**.

---

## 🛠️ Požadavky na provoz

Pro správný chod skriptu je vyžadováno:
* 🐍 **Python** verze **3.10** nebo vyšší. (Projekt je postaven a testován v prostředí Python verze **3.14.4**.)
* 📦 **Virtuální prostředí** (venv) pro izolaci závislostí.

---

## 🚀 Instalace a nastavení

1. **Příprava:** Naklonujte repozitář nebo stáhněte soubory do lokální složky.
2. **Virtuální prostředí:** Pro čistou instalaci použijte následující příkazy:

### 🐧 OS Linux/MacOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 🪟 OS Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🖥️ Spuštění skriptu

Skript se spouští z terminálu (příkazového řádku) a vyžaduje **dva povinné argumenty**:

1.  **URL:** Odkaz na územní celek z webu [volby.cz](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ) (výběr obce/okresu).
2.  **Výstup:** Název výsledného souboru (například `vysledky.csv`).

**Struktura příkazu:**
```bash
python main.py "URL_ADRESA" "NAZEV_SOUBORU.csv"
```

---

## 📊 Praktická ukázka

Pokud chcete získat data pro okres **Děčín**, použijte tento konkrétní příkaz:

```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=6&xnumnuts=4201" "vysledky_decin.csv"
```

## Průběh a výsledek:
* Během stahování skript informuje o zpracování jednotlivých obcí.
* Po dokončení se nachází v adresáři soubor s příponou `.csv`.
* **Struktura dat:**
    * *code*: Kód obce.
    * *location*: Název obce.
    * *registered*: Počet registrovaných voličů.
    * *envelopes*: Počet vydaných obálek.
    * *valid*: Počet platných hlasů.
    * *Jednotlivé politické strany*: Dynamické sloupce s počty hlasů.

---

## Ukázka částečného výstupu z CSV souboru:

```csv
kód obce,název obce,voliči v seznamu,vydané obálky,platné hlasy,...
562343,Arnoltice,333,233,232,92,1,0,1,0,14,2,0,33,0,3,0,0,1,10,1,2,1,15,6,30,20,0,0
562351,Benešov nad Ploučnicí,2993,1625,1618,577,15,3,5,13,173,17,3,121,5,17,1,5,9,99,...
544647,Bynovec,256,163,162,47,1,0,0,2,16,1,0,13,0,1,0,0,0,3,1,5,3,28,10,21,10,0,0
```

* **Oddělovač (Delimiter):** Čárka (`,`).
* **Kódování (Encoding):** Unicode UTF-8.

---
