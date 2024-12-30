import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_ROOT = PROJECT_ROOT / "resources" / "db_migrations"
INIT_DOWN_COUNT = 1000


def _validate_name(name: str):
    # name must be alphanumeric plus dashes
    if not name.replace("-", "").isalnum():
        raise ValueError("Name must be alphanumeric plus dashes")


def _calc_next_prefix() -> tuple[str, str]:
    up_files = sorted(MIGRATIONS_ROOT.glob("up/*.sql"))
    try:
        head_prefix = up_files[-1].stem.split("-")[0]
    except IndexError:
        head_prefix = "000"
    next_up_count = int(head_prefix) + 1

    next_up_prefix = str(next_up_count).zfill(3)
    next_down_prefix = str(INIT_DOWN_COUNT - next_up_count).zfill(3)
    return next_up_prefix, next_down_prefix


def create_migration(name: str) -> tuple[Path, Path]:
    _validate_name(name)
    up_prefix, down_prefix = _calc_next_prefix()

    up_path = MIGRATIONS_ROOT / f"up/{up_prefix}-{name}.sql"
    up_path.parent.mkdir(parents=True, exist_ok=True)
    up_path.touch(exist_ok=False)

    down_path = MIGRATIONS_ROOT / f"down/{down_prefix}-{name}.sql"
    down_path.parent.mkdir(parents=True, exist_ok=True)
    down_path.touch(exist_ok=False)

    return up_path, down_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()

    up_path, down_path = create_migration(args.name)
    print("Migration created:")
    print(f"- ⬆️ {up_path.resolve()}")
    print(f"- ⬇️ {down_path.resolve()}")


if __name__ == "__main__":
    main()
