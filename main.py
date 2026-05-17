import csv  # Načtení modulu pro zápis dat do souboru CSV.
import sys  # Načtení modulu pro práci s argumenty.
from urllib.parse import urljoin  # Import funkce pro skládání URL adres.

import requests  # Import knihovny pro stahování webových stránek.
from bs4 import BeautifulSoup  # Import nástroje pro parsování HTML.

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"  # Povolená základní URL.


def parse_arguments() -> tuple[str, str]:
    """Zkontroluje a vrátí vstupní argumenty zadané v příkazové řádce."""
    if len(sys.argv) != 3:  # Kontrola zadání přesně 2 argumentů.
        print("Chyba: Program vyžaduje přesně dva argumenty!")
        sys.exit(1)  # Ukončení programu s chybovým kódem.

    url = sys.argv[1]  # Uložení 1. argumentu jako URL.
    filename = sys.argv[2]  # Uložení 2. argumentu jako název souboru.

    if not url.startswith(BASE_URL):  # Kontrola, že URL odpovídá volby.cz.
        print("Chyba: První argument není platná URL adresa webu volby.cz!")
        sys.exit(1)  # Ukončení programu při neplatné URL.

    if not filename.endswith(".csv"):  # Kontrola přípony výstupního souboru.
        print("Chyba: Druhý argument musí mít příponu .csv!")
        sys.exit(1)  # Ukončení programu při špatném názvu souboru.

    return url, filename  # Vrácení ověřených argumentů.


def fetch_html(url: str) -> BeautifulSoup:
    """Stáhne HTML obsah ze zadané URL a vrátí objekt BeautifulSoup."""
    # Definice hlavičky: skript se identifikuje jako prohlížeč
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:  # Začátek bloku pro zachycení eventuálních chyb.
        # Odeslání HTTP GET požadavku.
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Vyvolání chyby při neúspěšné odpovědi.
        return BeautifulSoup(response.text, "html.parser")  # Parsování HTML.
    # Záchycení síťové chyby.
    except requests.exceptions.RequestException as err:
        print(f"Chyba při stahování stránky {url}: {err}!")
        sys.exit(1)  # Ukončení programu při chybě stahování.


def extract_municipalities(soup: BeautifulSoup) -> list[dict[str, str]]:
    """Vyhledá na stránce územního celku všechny obce a jejich odkazy."""
    municipalities = []  # Vytvoření prázdného seznamu pro obce.

    # Průchod všemi tabulkami.
    for table in soup.find_all("table", class_="table"):
        for row in table.find_all("tr")[2:]:  # Přeskočení hlaviček tabulky.
            cols = row.find_all("td")  # Získání všech buněk v řádku.
            if len(cols) >= 2:  # Kontrola, že řádek má aspoň dva sloupce.
                # Pokus o nalezení odkazu v 1. buňce.
                link_tag = cols[0].find("a")

                if link_tag:  # Kontrola, že odkaz opravdu existuje.
                    municipalities.append(  # Přidání jedné obce do seznamu.
                        {
                            "code": link_tag.text,  # Kód obce z textu odkazu.
                            "name": cols[1].text,  # Název obce z 2. buňky.
                            # Složení úplné URL detailu obce.
                            "link": urljoin(
                                BASE_URL,
                                str(link_tag.get("href", "")),
                            ),
                        }
                    )

    return municipalities  # Vrácení seznamu nalezených obcí.


def extract_election_data(url: str) -> dict[str, str | int]:
    """Ze stránky konkrétní obce vyscrapuje počty voličů a hlasy stran."""
    soup = fetch_html(url)  # Stažení a zpracování HTML detailní stránky.
    data = {}  # Vytvoření slovníku pro data jedné obce.

    voters = soup.find("td", headers="sa2")  # Nalezení počtu voličů v seznamu.
    # Nalezení počtu vydaných obálek.
    envelopes = soup.find("td", headers="sa3")
    # Vyhledání počtu platných hlasů.
    valid_votes = soup.find("td", headers="sa6")

    # Uložení voličů, obálek a hlasů.
    data["voliči v seznamu"] = "".join(voters.text.split()) if voters else "0"
    data["vydané obálky"] = (
    "".join(envelopes.text.split()) if envelopes else "0"
    )
    data["platné hlasy"] = (
    "".join(valid_votes.text.split()) if valid_votes else "0"
    )

    # Průchod tabulkami stran.
    for table in soup.find_all("table", class_="table")[1:]:
        for row in table.find_all("tr")[2:]:  # Přeskočení hlavičkových řádků.
            cols = row.find_all("td")  # Získání buněk aktuálního řádku.
            if len(cols) >= 3:  # Kontrola, zda má řádek potřebný počet buněk.
                # Načtení názvu politické strany.
                party_name = cols[1].text.strip()
                # Přeskočení neplatných či prázdných řádků.
                if party_name != "-":
                    # Hlasy pro stranu.
                    data[party_name] = "".join(cols[2].text.split())

    return data  # Vrácení kompletních dat pro jednu obec.


def save_to_csv(
    filename: str,  # Název výstupního souboru.
    header: list[str],  # Seznam názvů sloupců.
    data: list[dict[str, str | int]],  # Seznam řádků k zápisu.
) -> None:
    """Uloží nashromážděná data do CSV souboru."""
    try:  # Začátek bloku pro ošetření chyby zápisu.
        with open(  # Otevření souboru pro zápis.
            filename,
            mode="w",  # Otevření v režimu zápisu.
            newline="",  # Zabraňuje vkládání prázdných řádků.
            encoding="utf-8-sig",  # Přidání BOM značky na začátek souboru.
        ) as file:  # Pojmenování otevřeného souboru jako file.
            # Vytvoření zapisovače.
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()  # Zápis hlavičky CSV souboru.
            writer.writerows(data)  # Zápis všech řádků dat.
    except IOError as err:  # Zachycení chyby při práci se souborem.
        print(f"Chyba při zápisu do souboru {filename}: {err}")
        sys.exit(1)  # Ukončení programu při chybě zápisu.


def main() -> None:
    """Hlavní řídící funkce: volá funkce ve správném pořadí."""
    url, filename = parse_arguments()  # Načtení a ověření argumentů.
    print(f"Zahájení stahování dat z: {url}")

    soup = fetch_html(url)  # Stažení hlavní stránky se seznamem obcí.
    municipalities = extract_municipalities(soup)  # Získání seznamu obcí.

    if not municipalities:  # Kontrola, zda byly nalezeny obce.
        print("Na dané adrese nebyly nalezeny žádné obce k vyscrapování!")
        sys.exit(1)  # Ukončení programu, pokud není co ke zpracování.

    all_data = []  # Seznam pro všechna nasbíraná data.
    parties_header = set()  # Množina pro názvy všech nalezených stran.

    for mun in municipalities:  # Postupné zpracování každé obce.
        print(f"Zpracování obce: {mun['name']}")
        # Vytvoření základního slovníku pro jednu obec.
        mun_data: dict[str, str | int] = {
            "kód obce": mun["code"],  # Uložení kódu obce.
            "název obce": mun["name"],  # Uložení názvu obce.
        }

        stats_and_parties = extract_election_data(mun["link"])  # Detail obce.
        # Spojení základních a detailních dat.
        mun_data.update(stats_and_parties)

        # Průchod všech klíčů detailních dat.
        for key in stats_and_parties.keys():
            if key not in (  # Kontrola, že klíč není obecná statistika.
                "voliči v seznamu",
                "vydané obálky",
                "platné hlasy",
            ):
                parties_header.add(key)  # Přidání názvu strany do hlavičky.

        all_data.append(mun_data)  # Přidání hotových dat obce do seznamu.

    header = [  # Sestavení hlavičky CSV souboru.
        "kód obce",
        "název obce",
        "voliči v seznamu",
        "vydané obálky",
        "platné hlasy",
    ] + sorted(list(parties_header))  # Připojení seřazených názvů stran.

    save_to_csv(filename, header, all_data)  # Uložení všech dat do CSV.
    print(f"Hotovo! Data byla uložena do souboru: {filename}")
    print("Skript ukončen!")


if __name__ == "__main__":  # Podmínka přímého spuštění skriptu.
    main()  # Zavolání hlavní funkce skriptu.
