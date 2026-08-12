#!/usr/bin/env python3
"""Normalize and enrich public evidence-docket BibTeX files.

Every docket bibliography is round-tripped through CiteGeist with review
annotations. DOI records are then supplemented with Crossref abstracts when
Crossref supplies one. Missing abstracts are left missing and are not
invented; the BibTeX record records the enrichment status.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from pybtex.database import parse_file


ROOT = Path(__file__).resolve().parents[1]
CITEGEIST = Path("/home/netuser/bin/CiteGeist/.venv/bin/citegeist")
CITEGEIST_DB = Path("/home/netuser/bin/CiteGeist/talkorigins.sqlite3")


def crossref_abstract(doi: str) -> str:
    if not doi:
        return ""
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "EvolutionNews docket bibliography enrichment mailto:welsberr@cns.fyi"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            item = json.load(response).get("message", {})
    except Exception:
        return ""
    abstract = str(item.get("abstract") or "")
    abstract = re.sub(r"<[^>]+>", " ", abstract)
    abstract = re.sub(r"\s+", " ", abstract).strip()
    return abstract


def citegeist_round_trip(source: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="evolutionnews-citegeist-") as temp:
        output = Path(temp) / "enriched.bib"
        command = [
            str(CITEGEIST), "--db", str(CITEGEIST_DB), "sync-jabref", str(source),
            "--output", str(output), "--no-resolve", "--annotate-review",
            "--source-label", "EvolutionNews public docket bibliography enrichment",
        ]
        env = {**os.environ, "PYTHONPATH": "/home/netuser/bin/CiteGeist/src"}
        result = subprocess.run(command, text=True, capture_output=True, env=env, timeout=180)
        if result.returncode or not output.exists():
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "CiteGeist export failed")
        return output.read_text(encoding="utf-8")


def enrich_bibtex(path: Path) -> tuple[int, int]:
    with tempfile.NamedTemporaryFile("w", suffix=".bib", encoding="utf-8", delete=False) as handle:
        handle.write(path.read_text(encoding="utf-8"))
        source = Path(handle.name)
    try:
        normalized = citegeist_round_trip(source)
    finally:
        source.unlink(missing_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".bib", encoding="utf-8", delete=False) as handle:
        handle.write(normalized)
        normalized_path = Path(handle.name)
    try:
        bibliography = parse_file(str(normalized_path))
    finally:
        normalized_path.unlink(missing_ok=True)

    abstracts = 0
    entries = len(bibliography.entries)
    for entry in bibliography.entries.values():
        doi = str(entry.fields.get("doi") or "").strip()
        if not entry.fields.get("abstract") and doi:
            abstract = crossref_abstract(doi)
            if abstract:
                entry.fields["abstract"] = abstract
                entry.fields["x_abstract_source"] = "Crossref DOI metadata"
                abstracts += 1
        entry.fields.setdefault("x_citegeist_abstract_status", "present" if entry.fields.get("abstract") else "not_available")

    rendered = bibliography.to_string("bibtex")
    header = (
        "% CiteGeist-normalized public docket bibliography.\n"
        "% CiteGeist review annotations identify the normalization/provenance pass.\n"
        "% DOI abstracts are included only when supplied by Crossref; missing abstracts are not inferred.\n\n"
    )
    path.write_text(header + rendered, encoding="utf-8")
    return entries, abstracts


def update_summary(path: Path, entries: int, abstracts: int) -> None:
    summary = json.loads(path.read_text(encoding="utf-8"))
    summary["citation_enrichment"] = {
        "pipeline": "CiteGeist sync-jabref normalization with Crossref DOI abstract supplement",
        "status": "completed",
        "bibliography_records": entries,
        "abstracts_in_bibtex": abstracts,
        "missing_abstracts_are_not_invented": True,
        "research_timestamp": "2026-08-12",
    }
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def seed_missing_bibliography(docket: Path) -> None:
    """Create a DOI seed BibTeX file for older dockets without a download."""
    bib = docket / "citations.bib"
    summary_path = docket / "docket-summary.json"
    if bib.exists() or not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    blocks = []
    for index, citation in enumerate(summary.get("verified_citations") or [], 1):
        doi = str(citation.get("doi") or "").strip()
        if not doi:
            continue
        key = re.sub(r"[^a-z0-9]+", "", doi.lower())[:45] or f"docket{index}"
        oa = citation.get("open_access") or {}
        oa_url = oa.get("url") if isinstance(oa, dict) else ""
        fields = [
            f"@article{{{key},",
            f"  title = {{{citation.get('title', '')}}},",
            f"  journal = {{{citation.get('journal', '')}}},",
            f"  year = {{{citation.get('year', '')}}},",
            f"  doi = {{{doi}}},",
            f"  url = {{{citation.get('url', '')}}},",
        ]
        if oa_url:
            fields.append(f"  openaccessurl = {{{oa_url}}},")
        fields.append("}")
        blocks.append("\n".join(fields))
    if blocks:
        bib.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docket", action="append", help="Docket slug; repeat to limit scope")
    args = parser.parse_args()
    wanted = set(args.docket or [])
    results = []
    for docket in sorted((ROOT / "dockets").glob("*/")):
        if not wanted or docket.name in wanted:
            seed_missing_bibliography(docket)
    for bib in sorted((ROOT / "dockets").glob("*/citations.bib")):
        slug = bib.parent.name
        if wanted and slug not in wanted:
            continue
        entries, abstracts = enrich_bibtex(bib)
        summary = bib.parent / "docket-summary.json"
        if summary.exists():
            update_summary(summary, entries, abstracts)
        results.append((slug, entries, abstracts))
    for slug, entries, abstracts in results:
        print(f"{slug}: {entries} records, {abstracts} Crossref abstracts")


if __name__ == "__main__":
    main()
