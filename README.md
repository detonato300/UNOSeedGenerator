# UNO Seed Generator

Fork projektu [Rav3nPL/SeedGenerator](https://github.com/Rav3nPL/SeedGenerator): generator mnemonica zgodnego z BIP39, w którym entropia pochodzi z **fizycznie potasowanej talii kart** oraz z czasu, w jakim klikasz kolejne karty. Ten fork przenosi wersję HTML na **talię UNO** i dodaje w pełni offline'owy kreator.

Również nie ufasz generatorom losowości z komputera? O to właśnie chodzi: komputer niczego tu nie losuje.

> **English summary:** fork of Rav3nPL/SeedGenerator. Generates a BIP39 mnemonic from a physically shuffled UNO deck plus click-timing jitter. `uno-seed-studio.html` is a single-file, fully offline wizard (PL/EN). See the disclaimer below: unaudited, no warranty, use only on an offline machine.

## ⚠️ Zastrzeżenia (disclaimer)

- **Brak jakiejkolwiek gwarancji.** Oprogramowanie jest dostarczane „tak jak jest”. Używasz go na własne ryzyko. Autorzy nie odpowiadają za utratę środków.
- **Kod nie przeszedł audytu bezpieczeństwa.** To projekt hobbystyczny/eksperymentalny, nie produkt kryptograficzny.
- Generuj seed **na komputerze odłączonym od sieci** (najlepiej z systemu live, np. Tails), a po wygenerowaniu zamknij przeglądarkę.
- Seed zapisuj **wyłącznie na papierze lub metalu**. Nigdy nie rób zdjęć, zrzutów ekranu, nie wklejaj go do chmury, menedżera haseł online ani komunikatora.
- Zanim wpłacisz większą kwotę: zaimportuj seed do **zaufanego portfela** (najlepiej sprzętowego), zapisz pierwszy adres, usuń portfel i odtwórz go z kartki. Adres musi być identyczny.
- Mnemonic z tej aplikacji jest zgodny z BIP39, ale **nie da się go odtworzyć z samych kart**: czas kliknięć jest częścią entropii. Kartka z 12–24 słowami jest jedyną kopią.
- To jest nieoficjalny fork; oryginalny autor nie jest odpowiedzialny za zmiany wprowadzone tutaj.

## Zawartość repozytorium

| Plik | Co to jest |
|---|---|
| `uno-seed-studio.html` | **Zalecany.** Samodzielny kreator w jednym pliku: edytor talii, instrukcja tasowania, wybieranie kart (z cofaniem i skrótami klawiszowymi), wynik oraz sprawdzenie zapisu. PL/EN, jasny/ciemny motyw, FAQ o BIP39 dla początkujących. |
| `index.html` | Prostszy port HTML+JS oryginalnego programu, dostosowany do talii UNO. |
| `INIT.py` | Konfigurator talii w konsoli (Python 3, bez zależności): pyta, ile masz kart każdego rodzaju, i zapisuje `deck.json`. |
| `deck.json` | Przykładowa konfiguracja: standardowa talia UNO, 108 kart. |
| `SeedGenerator/`, `SeedGenerator.sln` | Oryginalna aplikacja WinForms (.NET) autorstwa Rav3nPL, **bez zmian**, nadal na **52 karty do gry**. |

## Bezpieczeństwo wersji HTML

- **Działa w 100% offline.** `uno-seed-studio.html` ma politykę CSP (`default-src 'none'`), która blokuje przeglądarce każde połączenie sieciowe. Nie ma zewnętrznych czcionek, skryptów ani CDN, a lista słów BIP39 jest wbudowana w plik.
- **Sekrety nie są zapisywane.** Entropia, sól i słowa istnieją tylko w pamięci karty. `localStorage` przechowuje wyłącznie język, motyw, stan samouczka i konfigurację talii. „Nowy seed” oraz zamknięcie karty kasują wszystko.
- Przeglądarkowe `crypto.getRandomValues()` **nie wpływa na seed.** Służy tylko do tasowania kolejności pól w kroku sprawdzania.

## Jak używać (uno-seed-studio.html)

1. Pobierz repozytorium (lub sam plik) i przenieś je na komputer offline.
2. Otwórz `uno-seed-studio.html` w przeglądarce (dwuklik, `file://` działa). Jeśli przeglądarka blokuje `crypto.subtle` dla plików lokalnych, uruchom `python -m http.server` w folderze i wejdź na `http://localhost:8000/uno-seed-studio.html`.
3. **Krok 1, talia:** ustaw, ile kart każdego rodzaju fizycznie masz. Możesz wpisać notację (patrz niżej), wczytać lub wkleić `deck.json`.
4. **Krok 2, długość:** 12, 15, 18, 21 albo 24 słowa. Opcjonalnie wpisz własną sól (tylko drukowalne znaki ASCII).
5. **Krok 3, tasowanie:** potasuj talię metodą [riffle shuffle](https://en.wikipedia.org/wiki/Shuffling#Riffle) co najmniej 7 razy.
6. **Krok 4, karty:** dobieraj karty z wierzchu i klikaj je po kolei (kolor, potem wartość; dzikie karty bez koloru). Dla 24 słów aplikacja poprosi o ponowne potasowanie i drugą rundę.
7. **Krok 5, wynik:** odsłoń słowa, zapisz je na papierze, odhacz listę kontrolną.
8. **Krok 6, sprawdzenie:** słowa są ukryte, a pola pojawiają się w **losowej kolejności**. Wpisz każde słowo z kartki (z autouzupełnianiem z listy BIP39). Błędy są liczone i zaznaczane, więc od razu wiesz, czy zapis jest poprawny.

## Konfiguracja talii (INIT.py)

```
python INIT.py                     # tryb interaktywny, pyta o każdy rodzaj karty
python INIT.py "0 fcc1, 1-9 fcc2, +2,stop,reverse fcc2, wildcolor x4, wild+4 x4"
```

Notacja (ta sama działa w polu tekstowym kreatora):

- `fccN` to N sztuk w każdym kolorze (`fcd` jest akceptowane jako literówka),
- `R2 Y1 G2 B0` to liczby osobno dla kolorów,
- `xN` to liczba dzikich kart bez koloru (`wildcolor`, `wild+4`),
- rodzaje: `0`–`9`, zakresy typu `1-9`, `+2`, `stop`, `reverse`.

Przykład powyżej to standardowa talia UNO (108 kart), identyczna z dołączonym `deck.json`.

## Algorytm

Ten sam co w oryginale:

1. Każde kliknięcie dopisuje kod karty (np. `5R`, `+2Y`, `STOPG`, `REVB`, `WILD`, `WILD4`) do tekstu entropii.
2. Sól jest aktualizowana łańcuchowo: `sól = base64(SHA-512(sól + znacznik_czasu_kliknięcia))`.
3. Seed to `SHA-512(entropia + sól)` obcięte do 128/160/192/224/256 bitów, plus suma kontrolna z SHA-256. Całość jest dzielona na 11-bitowe fragmenty, a każdy fragment wskazuje słowo z angielskiej listy BIP39.

Liczba wymaganych kart jest skalowana do rozmiaru talii (proporcje z oryginalnej tabeli 35/41/47/52/52 z 52 kart). Dla 24 słów jest druga runda. Aktualizacje soli są kolejkowane, więc bardzo szybkie klikanie nie gubi żadnego ogniwa łańcucha.

## Aplikacja WinForms (oryginał)

Binarka oryginału: zakładka ["Releases"](https://github.com/Rav3nPL/SeedGenerator/releases) repozytorium Rav3nPL. Wymaga .NET, czyli Windows albo Linux/macOS z mono/wine. Ta wersja nadal używa dwóch przejść przez talię 52 kart.

## Autorzy

- Oryginalny SeedGenerator: [Rav3nPL](https://github.com/Rav3nPL/SeedGenerator). Tipbox autora oryginału: `1Rav3nkMayCijuhzcYemMiPYsvcaiwHni`
- Port UNO, kreator offline, INIT.py: ten fork.
