#!/usr/bin/env python3
"""Konfigurator decka UNO dla index.html: zapisuje deck.json z liczbą każdej karty.

Notacja:
  fccN  - karta występuje w każdym z 4 kolorów N razy (full color card)
  xN    - karta bez koloru (wild) występuje N razy
  R2 Y1 G2 B0 - osobna liczba dla każdego koloru

Tryb jednolinijkowy:
  python INIT.py "0 fcc1, 1-9 fcc2, +2,stop,reverse fcc2, wildcolor x4, wild+4 x4"
Bez argumentu: tryb interaktywny.
"""

import json
import re
import sys
from pathlib import Path

COLORS = [("R", "Czerwony"), ("Y", "Żółty"), ("G", "Zielony"), ("B", "Niebieski")]
TYPES = [str(n) for n in range(10)] + ["+2", "STOP", "REV"]
TYPE_LABELS = {"STOP": "Stop", "REV": "Reverse"}
WILDS = [("WILD", "Wild (zmiana koloru)"), ("WILD4", "Wild +4")]

STANDARD_SPEC = "0 fcc1, 1-9 fcc2, +2,stop,reverse fcc2, wildcolor x4, wild+4 x4"

TYPE_ALIASES = {"+2": "+2", "stop": "STOP", "skip": "STOP", "reverse": "REV", "rev": "REV"}
WILD_ALIASES = {"wildcolor": "WILD", "wild": "WILD", "wild+4": "WILD4", "wild+4color": "WILD4", "wild4": "WILD4"}


def empty_deck() -> dict:
    deck = {c: {t: 0 for t in TYPES} for c, _ in COLORS}
    deck["WILD"] = {w: 0 for w, _ in WILDS}
    return deck


def parse_colored_count(text: str) -> dict:
    """'fcc2' / '2' -> same count for every color; 'R2 Y1 G2 B0' -> per color."""
    text = text.strip().lower()
    m = re.fullmatch(r"(?:fcc|fcd)?\s*(\d+)", text)
    if m:
        return {c: int(m.group(1)) for c, _ in COLORS}
    counts = {c: 0 for c, _ in COLORS}
    parts = re.findall(r"([rygb])\s*(\d+)", text)
    if not parts or re.sub(r"[rygb]\s*\d+|\s", "", text):
        raise ValueError(f"nie rozumiem '{text}' (użyj fccN albo R2 Y1 G2 B0)")
    for color, n in parts:
        counts[color.upper()] = int(n)
    return counts


def parse_wild_count(text: str) -> int:
    m = re.fullmatch(r"x?\s*(\d+)", text.strip().lower())
    if not m:
        raise ValueError(f"nie rozumiem '{text}' (użyj xN)")
    return int(m.group(1))


def expand_types(token: str) -> list:
    token = token.strip().lower()
    m = re.fullmatch(r"(\d)-(\d)", token)
    if m:
        return [str(n) for n in range(int(m.group(1)), int(m.group(2)) + 1)]
    if re.fullmatch(r"\d", token):
        return [token]
    if token in TYPE_ALIASES:
        return [TYPE_ALIASES[token]]
    raise ValueError(f"nieznana karta '{token}'")


def parse_spec(spec: str) -> dict:
    """Parse e.g. '0 fcc1, 1-9 fcc2, +2,stop,reverse fcc2, wildcolor x4, wild+4 x4'."""
    deck = empty_deck()
    pending = []
    for chunk in (c.strip() for c in spec.split(",")):
        if not chunk:
            continue
        m = re.fullmatch(r"(\S+)\s+(.+)", chunk)
        name = (m.group(1) if m else chunk).lower()
        count = m.group(2) if m else None
        if name in WILD_ALIASES:
            if count is None:
                raise ValueError(f"brak liczby dla '{name}' (np. {name} x4)")
            deck["WILD"][WILD_ALIASES[name]] = parse_wild_count(count)
            continue
        pending += expand_types(name)
        if count is None:
            continue  # "+2,stop,reverse fcc2" - count comes with the last item
        counts = parse_colored_count(count)
        for t in pending:
            for c in counts:
                deck[c][t] = counts[c]
        pending = []
    if pending:
        raise ValueError(f"brak liczby dla: {', '.join(pending)}")
    return deck


def ask(prompt: str, default: str, parser):
    while True:
        raw = input(f"{prompt} [{default}]: ").strip() or default
        try:
            return parser(raw)
        except ValueError as e:
            print(f"   {e}")


def interactive() -> dict:
    print("Dla każdej karty wpisz: fccN (N sztuk w każdym kolorze), R2 Y1 G2 B0 (osobno), Enter = domyślnie.")
    standard = parse_spec(STANDARD_SPEC)
    deck = empty_deck()
    for t in TYPES:
        default = f"fcc{standard['R'][t]}"
        counts = ask(f"  {TYPE_LABELS.get(t, t)}", default, parse_colored_count)
        for c in counts:
            deck[c][t] = counts[c]
    for w, label in WILDS:
        deck["WILD"][w] = ask(f"  {label}", f"x{standard['WILD'][w]}", parse_wild_count)
    return deck


def print_summary(deck: dict) -> int:
    labels = [TYPE_LABELS.get(t, t) for t in TYPES]
    header = "Kolor".ljust(11) + "".join(l.rjust(8) for l in labels) + "   Razem"
    print("\n" + header)
    print("-" * len(header))
    total = 0
    for code, name in COLORS:
        row = deck[code]
        subtotal = sum(row.values())
        total += subtotal
        print(name.ljust(11) + "".join(str(row[t]).rjust(8) for t in TYPES) + str(subtotal).rjust(8))
    for code, label in WILDS:
        total += deck["WILD"][code]
        print(f"{label}: x{deck['WILD'][code]}")
    print(f"\nRazem kart w decku: {total}")
    return total


def main() -> None:
    print("=== INIT.py: konfigurator decka UNO ===")
    print(f"Standardowy deck: {STANDARD_SPEC}\n")

    if len(sys.argv) > 1:
        try:
            deck = parse_spec(" ".join(sys.argv[1:]))
        except ValueError as e:
            print(f"Błąd: {e}")
            sys.exit(1)
    else:
        deck = interactive()

    if print_summary(deck) == 0:
        print("Deck jest pusty, nic nie zapisano.")
        sys.exit(1)

    out = Path(input("\nZapisz jako [deck.json]: ").strip() or "deck.json")
    out.write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Zapisano {out.resolve()}")
    print("W index.html kliknij 'Wczytaj własny deck (deck.json)' przed wyborem długości mnemonica.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrzerwano.")
        sys.exit(1)
