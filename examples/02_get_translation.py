"""Fetch a fan translation and show its language / target game.

    python examples/02_get_translation.py
"""
from pyromhacking import get_translation


def main() -> None:
    tr = get_translation("1")
    print("title:       ", tr.title)
    print("game:        ", tr.game)
    print("language:    ", tr.language)
    print("system:      ", tr.system)
    print("status:      ", tr.status)
    print("published by:", tr.published_by)
    print("downloads:   ", tr.downloads)


if __name__ == "__main__":
    main()
