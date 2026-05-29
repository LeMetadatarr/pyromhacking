"""Convert an entry to a metadatarr ``ExternalIds.extra`` dict.

    python examples/06_external_ids.py
"""
from pyromhacking import entry_to_extra, get_hack


def main() -> None:
    hack = get_hack("1")
    extra = entry_to_extra(hack)
    for key in sorted(extra):
        print(f"{key:28s} {extra[key]}")
    print()
    print("anchor:", extra["romhacking_section"], extra["romhacking_id"])


if __name__ == "__main__":
    main()
