import csv
import requests
from pathlib import Path


# ---------- 1. Hierarchia wyjątków (z ćwiczenia II) ----------

class DownloadError(Exception):
    """Bazowy wyjątek dla operacji pobierania plików."""
    pass


class NotFoundError(DownloadError):
    """Rzucany, gdy serwer zwraca 404 Not Found."""
    pass


class AccessDeniedError(DownloadError):
    """Rzucany, gdy serwer zwraca 403 Forbidden."""
    pass


# ---------- 2. Pobieranie pliku ze strony ----------

URL = "https://oleksandr-fedoruk.com/sggw/podyplomowe/file"


def pobierz_plik(url: str, nazwa_pliku: str = "latest.csv") -> Path:
    """
    Pobiera plik z URL i zapisuje go jako CSV.
    Zwraca ścieżkę do zapisanego pliku.
    Rzuca NotFoundError dla 404 i AccessDeniedError dla 403.
    """
    if not nazwa_pliku.lower().endswith(".csv"):
        nazwa_pliku = f"{nazwa_pliku}.csv"

    try:
        with requests.get(url, stream=True) as response:
            if response.status_code == 404:
                raise NotFoundError(f"Nie znaleziono zasobu (404): {url}")
            if response.status_code == 403:
                raise AccessDeniedError(f"Brak dostępu do zasobu (403): {url}")
            response.raise_for_status()

            sciezka = Path(nazwa_pliku).resolve()
            with open(sciezka, "wb") as plik:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        plik.write(chunk)

        print(f"[OK] Pobrano: {sciezka} ({sciezka.stat().st_size} bajtów)")
        return sciezka

    except NotFoundError as e:
        print(f"[404] {e}")
        raise
    except AccessDeniedError as e:
        print(f"[403] {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"[BŁĄD HTTP] {type(e).__name__}: {e}")
        raise


# ---------- 3. Klasa ETL ----------

class ETLProcessor:
    """Proces ETL: czyta pobrany CSV linia po linii, liczy sumę/średnią/braki, zapisuje wyniki."""

    def __init__(self, wejscie: Path, values_out: str = "values.csv",
                 missing_out: str = "missing_values.csv", delimiter: str = ","):
        self.wejscie = Path(wejscie)
        self.values_out = Path(values_out)
        self.missing_out = Path(missing_out)
        self.delimiter = delimiter

    # --- EKSTRAKCJA: generator czytający linia po linii ---

    def czytaj_linie(self):
        """Generator: zwraca kolejne wiersze jako listy stringów."""
        with open(self.wejscie, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            naglowek = next(reader, None)
            print(f"[INFO] Nagłówek: {naglowek}")
            for wiersz in reader:
                if wiersz and any(cell.strip() for cell in wiersz):
                    yield wiersz

    # --- TRANSFORMACJA: suma, średnia, indeksy braków ---

    def przetworz_wiersz(self, wiersz: list[str]):
        """
        Dla jednego wiersza zwraca:
        - numer porządkowy (kolumna 0),
        - sumę wartości liczbowych,
        - średnią wartości liczbowych,
        - indeksy kolumn z myślnikiem.
        """
        try:
            numer = int(wiersz[0].strip())
        except (ValueError, IndexError):
            return None

        # list comprehension: indeksy braków (myślniki lub puste pola)
        braki = [i for i, v in enumerate(wiersz)
                 if i > 0 and v.strip() in ("-", "")]

        # list comprehension: wartości liczbowe (pomijamy myślniki i kolumnę 0)
        wartosci = []
        for i, v in enumerate(wiersz):
            if i == 0 or v.strip() in ("-", ""):
                continue
            try:
                wartosci.append(float(v))
            except ValueError:
                braki.append(i)

        suma = sum(wartosci) if wartosci else 0.0
        srednia = (suma / len(wartosci)) if wartosci else 0.0

        return numer, suma, srednia, sorted(set(braki))

    def transformuj(self):
        """Generator: dla każdego wiersza zwraca krotkę (numer, suma, średnia, braki)."""
        for wiersz in self.czytaj_linie():
            wynik = self.przetworz_wiersz(wiersz)
            if wynik is not None:
                yield wynik

    # --- ŁADOWANIE: zapis dwóch plików CSV ---

    def zapisz(self):
        with open(self.values_out, "w", newline="", encoding="utf-8") as fv, \
             open(self.missing_out, "w", newline="", encoding="utf-8") as fm:

            writer_v = csv.writer(fv)
            writer_m = csv.writer(fm)

            writer_v.writerow(["numer", "suma", "srednia"])
            writer_m.writerow(["numer", "brakujace_indeksy"])

            licznik = 0
            for numer, suma, srednia, braki in self.transformuj():
                writer_v.writerow([numer, suma, round(srednia, 2)])
                writer_m.writerow([numer, ";".join(map(str, braki))])
                licznik += 1

        print(f"[OK] Zapisano: {self.values_out.resolve()} ({licznik} wierszy)")
        print(f"[OK] Zapisano: {self.missing_out.resolve()} ({licznik} wierszy)")

    def run(self):
        self.zapisz()


# ---------- 4. Uruchomienie całości ----------

if __name__ == "__main__":
    # 1) Pobierz plik ze strony internetowej
    plik = pobierz_plik(URL, "moj_plik_test.csv")

    # 2) Uruchom ETL na pobranym pliku
    etl = ETLProcessor(plik)  # delimiter domyślnie ","
    etl.run()