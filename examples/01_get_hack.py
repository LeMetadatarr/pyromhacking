"""Fetch a single ROM hack and print its core fields.

    export PYROMHACKING_FLARESOLVERR_URL=http://192.168.1.116:8191
    python examples/01_get_hack.py
"""
from pyromhacking import get_hack


def main() -> None:
    hack = get_hack("1")
    print(hack)                       # "<title> (<system>)"
    print("game:       ", hack.game)
    print("category:   ", hack.category)
    print("genre:      ", hack.genre)
    print("version:    ", hack.version)
    print("authors:    ", ", ".join(hack.authors))
    print("released:   ", hack.release_date)
    print("downloads:  ", hack.downloads)
    print()
    print(hack.description[:300])


if __name__ == "__main__":
    main()
