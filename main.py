# ============================================================
# ============================================================

#Zadanie 1

# ============================================================
# ============================================================


# ============================================================
# 1. Logger
# ============================================================

class Logger:
    """Context manager logujący wejście i wyjście z sekcji."""

    def __enter__(self):
        print("Start sekcji logowania")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Koniec sekcji logowania")
        return False


# ============================================================
# 2 + 3. FileWriter (wersja z zadania 3 – loguje wyjątek, ale go nie tłumi)
# ============================================================

class FileWriter:
    """Context manager otwierający plik do zapisu i zamykający go w __exit__.
    Przy wyjątku wypisuje komunikat, ale go NIE tłumi."""

    def __init__(self, sciezka: str):
        self.sciezka = sciezka
        self.plik = None

    def __enter__(self):
        self.plik = open(self.sciezka, "w", encoding="utf-8")
        return self.plik          # zwracamy uchwyt pliku

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.plik is not None:
            self.plik.close()     # zamyka plik niezależnie od wyjątku

        if exc_type is not None:
            print(f"Błąd podczas zapisu: {exc_val}")
            return False          # wyjątek NIE jest tłumiony

        return False


# ============================================================
# 4. SafeDivision
# ============================================================

class SafeDivision:
    """Context manager tłumiący ZeroDivisionError w metodzie divide()."""

    def __enter__(self):
        return self

    def divide(self, a, b):
        return a / b

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ZeroDivisionError:
            print("Nie można dzielić przez zero")
            return True           # True -> wyjątek stłumiony
        return False              # inne wyjątki propagują się


# ============================================================
# Testy
# ============================================================

if __name__ == "__main__":
    # --- Test 1: Logger ---
    print("=== Test 1: Logger ===")
    with Logger():
        print("Coś w środku sekcji logowania")

    # --- Test 2: FileWriter – zwykły zapis ---
    print("\n=== Test 2: FileWriter – zwykły zapis ===")
    with FileWriter("test_ok.txt") as f:
        f.write("Linia 1\n")
        f.write("Linia 2\n")
    print("Plik test_ok.txt zapisany poprawnie.")

    # --- Test 3: FileWriter – wyjątek w bloku with ---
    print("\n=== Test 3: FileWriter – wyjątek w bloku with ===")
    try:
        with FileWriter("test_blad.txt") as f:
            f.write("Przed wyjątkiem\n")
            raise ValueError("Celowy błąd w środku bloku with")
    except ValueError as e:
        print(f"Wyjątek nadal propaguje się do wywołującego: {e}")
    print(f"Czy plik został zamknięty mimo wyjątku? {f.closed}")

    # --- Test 4a: SafeDivision – bez błędu ---
    print("\n=== Test 4a: SafeDivision – dzielenie bez błędu ===")
    with SafeDivision() as sd:
        print(f"10 / 2 = {sd.divide(10, 2)}")

    # --- Test 4b: SafeDivision – dzielenie przez zero (tłumione) ---
    print("\n=== Test 4b: SafeDivision – dzielenie przez zero ===")
    with SafeDivision() as sd:
        sd.divide(10, 0)
    print("Program idzie dalej – wyjątek został stłumiony.")

    # --- Test 4c: SafeDivision – inny wyjątek NIE jest tłumiony ---
    print("\n=== Test 4c: SafeDivision – inny wyjątek NIE jest tłumiony ===")
    try:
        with SafeDivision() as sd:
            sd.divide("abc", 2)
    except TypeError as e:
        print(f"TypeError propaguje się poprawnie: {e}")