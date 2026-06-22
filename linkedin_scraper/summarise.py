"""
Reads research_notes.txt, splits on '---', summarises each block with an LLM,
and writes all summaries to output/YYYY-MM-DD-research-summary.md.

    python -m linkedin_scraper.summarise
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from linkedin_scraper.config import LLM_CONFIG, OUTPUT_DIR, RESEARCH_NOTES_FILE
from src.core.llm import MockLLMClient, ProductionLLMClient

PROMPT = """You are summarising a job seeker's raw research notes from a LinkedIn job search session.

Read the notes below and produce a concise, structured summary covering:
- Roles and companies noted
- Key themes or patterns (skills in demand, seniority level, company types)
- Any standout opportunities or red flags
- Action items or follow-ups mentioned by the researcher

Be brief and direct — this is a daily log entry, not a report.

NOTES:
{notes}"""


def get_client():
    if LLM_CONFIG.get("provider") == "mock":
        return MockLLMClient()
    return ProductionLLMClient(LLM_CONFIG)


def load_blocks(path: str) -> list[tuple[str, str]]:
    """Returns list of (heading, notes) parsed from %%% delimited blocks."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    entries = []
    for chunk in raw.split("%%%"):
        chunk = chunk.strip()
        if not chunk:
            continue
        first_line, _, rest = chunk.partition("\n")
        heading = first_line.strip()
        notes = rest.strip()
        if heading and notes:
            entries.append((heading, notes))
    return entries


def main():
    if not os.path.exists(RESEARCH_NOTES_FILE):
        print(f"No file found at {RESEARCH_NOTES_FILE}")
        print("Paste your research notes there. Start each block with %%% <label>, e.g.:")
        print("  %%% solutions engineer, kaliba")
        sys.exit(1)

    blocks = load_blocks(RESEARCH_NOTES_FILE)
    if not blocks:
        print("No note blocks found. Make sure each block starts with %%% <label>")
        sys.exit(1)

    print(f"Found {len(blocks)} note block(s). Summarising...")

    client = get_client()
    model = LLM_CONFIG.get("model", "default")
    summaries = []

    for i, (heading, notes) in enumerate(blocks, 1):
        print(f"  [{i}/{len(blocks)}] {heading}")
        summary = client.query(PROMPT.format(notes=notes), model=model)
        summaries.append((heading, summary.strip()))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{date.today().isoformat()}-research-summary.md")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Job Research Summary — {date.today().isoformat()}\n\n")
        for heading, summary in summaries:
            f.write(f"## {heading}\n\n")
            f.write(summary)
            f.write("\n\n---\n\n")

    print(f"\nDone → {out_path}")


if __name__ == "__main__":
    main()
