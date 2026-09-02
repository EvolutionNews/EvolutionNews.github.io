# Private monitor backlog manifest

`ops/evidence-pipeline/backlog_manifest.py` implements the first executable
slice of the monitor-backlog publication roadmap (P0). It inventories explicitly
selected historical run JSON files into a deterministic, checksummed manifest:

```sh
python ops/evidence-pipeline/backlog_manifest.py build \
  private/backlog-manifest.json private/runs/*.json --lane florida
```

Failed or malformed runs remain in the manifest with diagnostics and hashes,
but are excluded from replay. Replay is read-only and resumable through a
private completion-state file:

```sh
python ops/evidence-pipeline/backlog_manifest.py replay \
  private/backlog-manifest.json --state private/replay-state.json --limit 20
python ops/evidence-pipeline/backlog_manifest.py mark-complete \
  private/replay-state.json run-2026-08-01
```

The utility does not recover sources, generate drafts, modify the workbench, or
write public site artifacts. Paths and run contents remain private; only the
operator-selected manifest and replay state are written. A repaired failed run
must be re-inventoried into a new manifest before it can become replayable.
