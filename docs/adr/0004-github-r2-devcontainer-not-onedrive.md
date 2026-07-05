# Multi-machine work via GitHub + R2 + devcontainer, not OneDrive

The repo originally lived in a OneDrive-synced folder so the project could be
picked up from another computer. OneDrive is the wrong tool for all three
things it was standing in for: `.git` directories corrupt under file-sync
daemons, embedded Lance index files churn and risk mid-write corruption, and
Docker bind-mounts of macOS CloudStorage paths are slow and flaky. Each pillar
gets a purpose-built sync channel instead: **code → GitHub** (end every session
with a push; WIP branches welcome), **data → private R2 bucket**
(`make sync-data`), **environment → devcontainer** (identical on any machine;
Codespaces as the escape hatch). The repo moved to `~/Projects/RRRAG`, outside
OneDrive; a pointer note remains at the old location.
