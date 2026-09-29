"""
Run once before the demo: pushes each reviewer's past-review history into
their own Hindsight memory bank.

    python seed.py
"""

from dotenv import load_dotenv
load_dotenv()

from memory_bank import ensure_bank, retain_review
from seed_data import REVIEWERS


def main():
    for reviewer in REVIEWERS:
        slug, name, history = reviewer["slug"], reviewer["name"], reviewer["history"]
        print(f"Creating bank for {name} ({slug})...")
        ensure_bank(slug, name)
        for i, memory in enumerate(history, 1):
            retain_review(slug, memory)
            print(f"  [{i}/{len(history)}] retained memory")
    print("\nSeeding complete. Both reviewer banks now have evaluation history.")


if __name__ == "__main__":
    main()
