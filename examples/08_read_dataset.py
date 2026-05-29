"""Read back a JSONL dataset and summarise it offline.

Run ``07_export_dataset.py`` first to produce ``hacks_sample.jsonl``.

    python examples/08_read_dataset.py
"""
import collections
import json
import sys


def main(path: str = "hacks_sample.jsonl") -> None:
    systems: collections.Counter = collections.Counter()
    rows = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            rows += 1
            systems[row.get("system") or "?"] += 1
    print(f"{rows} rows")
    for system, count in systems.most_common():
        print(f"  {system:<16} {count}")


if __name__ == "__main__":
    main(*sys.argv[1:])
