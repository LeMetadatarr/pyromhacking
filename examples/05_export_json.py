"""Serialise an entry to a JSON file via ``.as_dict``.

    python examples/05_export_json.py
"""
import json

from pyromhacking import get_hack


def main() -> None:
    hack = get_hack("1")
    path = "hack_1.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(hack.as_dict, fh, ensure_ascii=False, indent=2)
    print("wrote", path)


if __name__ == "__main__":
    main()
