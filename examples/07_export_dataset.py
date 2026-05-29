"""Export a tiny sample of the hacks dataset to JSONL.

    python examples/07_export_dataset.py
"""
from pyromhacking import dataset, transport


def main() -> None:
    transport.set_delay(2.0)
    n = dataset.export_jsonl("hacks", "hacks_sample.jsonl", limit=5, verbose=True)
    print(f"wrote {n} rows -> hacks_sample.jsonl")


if __name__ == "__main__":
    main()
