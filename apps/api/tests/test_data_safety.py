from pathlib import Path

FORBIDDEN_MARKERS = [
    "customer_id",
    "internal.company",
    "vpn",
    "prod-secret",
    "authorization:",
]


def test_seed_data_has_no_private_markers() -> None:
    root = Path(__file__).resolve().parents[3]
    this_file = Path(__file__).resolve()
    searchable = []
    for path in root.rglob("*"):
        if path.resolve() == this_file:
            continue
        if path.is_file() and ".git" not in path.parts and ".learning" not in path.parts:
            if path.suffix.lower() in {".py", ".md", ".json", ".yml", ".yaml", ".txt", ".example"}:
                searchable.append(path.read_text(encoding="utf-8", errors="ignore").lower())
    combined = "\n".join(searchable)
    for marker in FORBIDDEN_MARKERS:
        assert marker not in combined
