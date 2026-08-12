# Static GitHub Pages mirror for evolutionnews.net

- Expected GitHub user: `EvolutionNews`
- Expected GitHub email: `github@evolutionnews.net`
- Expected user Pages repo: `EvolutionNews.github.io`
- Custom domain: `evolutionnews.net`
- Local source: `/home/netuser/dev/sites/evolutionnews.net/public_html`

## Provisioning Notes

This directory is intended to be pushed as the GitHub Pages repository for the domain.
It was generated from the local static `public_html` snapshot and includes `CNAME` and `.nojekyll`.

Server-side scripts, CGI directories, logs, and private web-server files are excluded from the publish copy.
Review `PAGES_STATIC_RISK_REPORT.md` before DNS cutover.

## Evidence-docket bibliography enrichment

Every public docket’s `citations.bib` must pass through the CiteGeist enrichment
workflow before publication. From the repository root, run:

```bash
/home/netuser/bin/CiteGeist/.venv/bin/python tools/enrich_docket_bibliographies.py
```

The pass normalizes and annotates every record with CiteGeist provenance, adds
Crossref abstracts when a DOI record supplies one, and records explicit
`not_available` status when no abstract is available. It never invents an
abstract; older sources such as Muller (1918) may therefore remain without
one. Run it for new or revised dockets before committing their HTML, JSON, and
BibTeX artifacts.
