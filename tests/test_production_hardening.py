from pathlib import Path


def test_no_machine_specific_paths_in_notebook_helper() -> None:
    content = Path("notebooks/compact_summary.py").read_text()

    assert "/Volumes/" not in content
    assert "/Users/" not in content


def test_production_hardening_files_exist() -> None:
    for path in [
        "Dockerfile",
        ".dockerignore",
        "Makefile",
        "docs/production_hardening.md",
    ]:
        assert Path(path).exists()


def test_env_example_uses_safe_placeholder() -> None:
    content = Path(".env.example").read_text()

    assert "DB_PASSWORD=change_me" in content
