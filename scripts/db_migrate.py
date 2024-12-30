import argparse
import logging
from pathlib import Path
from tomllib import load as toml_load

from db_client import DatabaseClient, make_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_ROOT = PROJECT_ROOT / "resources" / "db_migrations"


def _load_secrets():
    secrets_path = PROJECT_ROOT / ".streamlit" / "secrets.toml"
    with secrets_path.open(mode="rb") as f:
        return toml_load(f)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("direction", choices=["up", "down"])
    args = parser.parse_args()

    secrets = _load_secrets()
    db_dsn = secrets["connections"]["neon"]["url"]
    db = DatabaseClient(engine=make_engine(dsn=db_dsn), logger=logger)

    if args.direction == "up":
        db.migrate_upgrade()
    elif args.direction == "down":
        db.migrate_downgrade()


if __name__ == "__main__":
    main()
