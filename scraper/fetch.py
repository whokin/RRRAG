"""fetch: Manifest -> Page Snapshots (data/html/), status: fetched.

Fetch once per episode; re-fetch only with --force (deliberate correction,
ADR-0006). Sequential with a fixed delay between requests."""

from . import manifest, politeness


def run(episodes: list[int] | None = None, limit: int | None = None, force: bool = False) -> None:
    m = manifest.load()
    statuses = None if force else ("discovered",)
    targets = manifest.select(m, episodes=episodes, statuses=statuses)
    if limit is not None:
        targets = targets[:limit]
    if not targets:
        print("fetch: nothing to fetch")
        return

    manifest.HTML_DIR.mkdir(parents=True, exist_ok=True)
    done = 0
    try:
        with politeness.make_client() as client:
            for entry in targets:
                if done:
                    politeness.pace()
                response = politeness.polite_get(client, entry["url"])
                (manifest.HTML_DIR / f"{entry['slug']}.html").write_text(response.text)
                entry["status"] = "fetched"
                entry["fetched_at"] = manifest.now_iso()
                done += 1
                print(f"fetch: [{done}/{len(targets)}] {entry['slug']}")
    except politeness.BlockedError as e:
        print(f"fetch: HALTED — {e}")
        raise SystemExit(2)
    finally:
        manifest.save(m)  # partial progress is real progress; states are per-episode
    print(f"fetch: {done} Page Snapshots saved")
