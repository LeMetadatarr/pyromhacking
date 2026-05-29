"""Walk a couple of listing pages and print each parsed hack.

    python examples/04_iter_entries.py
"""
from pyromhacking import iter_entries, transport


def main() -> None:
    transport.set_delay(2.0)   # be polite during the crawl
    for hack in iter_entries("hacks", max_pages=2):
        print(f"{hack.id:>6}  {hack.system:<14}  {hack.title}")


if __name__ == "__main__":
    main()
