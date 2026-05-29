"""List entry ids on the first page of each section.

    python examples/03_list_section.py
"""
from pyromhacking import SECTIONS, list_ids


def main() -> None:
    for section in SECTIONS:
        ids = list_ids(section)
        print(f"{section:13s} {len(ids):3d} ids: {', '.join(ids[:8])} ...")


if __name__ == "__main__":
    main()
