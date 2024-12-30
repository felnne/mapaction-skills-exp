from contextlib import contextmanager
from logging import Logger
from pathlib import Path
from typing import Literal, Self, cast

from sqlalchemy import (
    TextClause,
    text,
    Select,
    CursorResult,
    make_url as sa_make_url,
    create_engine as sa_create_engine,
    Engine,
    Connection,
)
from sqlalchemy.exc import DatabaseError as SQLAlchemyDatabaseError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_ROOT = PROJECT_ROOT / "resources" / "db_migrations"


class DatabaseError(Exception):
    """Raised for database errors unless a more specific subclass applies."""

    pass


class DatabaseMigrationError(DatabaseError):
    """Raised when database can't be migrated up or down."""

    pass


class DatabaseClient:
    """Basic database client based on SQLAlchemy."""

    def __init__(self: Self, engine: Engine, logger: Logger) -> None:
        """
        Create client using injected database connection.

        All date times are fetched as UTC.
        """
        self._logger = logger
        self._eng: Engine = engine

    @property
    def engine(self: Self) -> Engine:
        """
        SQLAlchemy database engine.

        If needed for use-cases not covered by this class.
        """
        return self._eng

    def execute(self, sql: str | Select | TextClause, params: dict | None = None) -> CursorResult | None:
        """Simple passthrough to SQLAlchemy connectable"""
        result = None
        args = [] if params is None else [params]

        with self.engine.connect() as conn:
            try:
                conn.begin()
                if isinstance(sql, str):
                    result = conn.exec_driver_sql(sql, *args)
                result = conn.execute(sql, *args)
                conn.commit()
            except SQLAlchemyDatabaseError as e:
                conn.rollback()
                msg = "Error executing statement"
                raise DatabaseError(msg) from e

        return result

    def execute_file(self: Self, path: Path) -> None:
        """Execute SQL statements in a given file."""
        with path.open() as file:
            self._logger.info("Executing SQL from: %s", path.resolve())

            # noinspection PyTypeChecker
            self.execute(text(file.read()))

    def execute_files_in_path(self: Self, path: Path) -> None:
        """Execute statements in all SQL files in a given directory."""
        for file_path in sorted(path.glob("*.sql")):
            self.execute_file(file_path)

    def _migrate(self: Self, direction: Literal["up", "down"]) -> None:
        """
        Migrate DB.

        Migrations are stored as SQL files included within the project.
        """
        try:
            self.execute_files_in_path(MIGRATIONS_ROOT / direction)
        except DatabaseError as e:
            msg = f"Error migrating DB {direction}"
            raise DatabaseMigrationError(msg) from e

    def migrate_upgrade(self: Self) -> None:
        """Upgrade database to head migration."""
        self._logger.info("Upgrading database to head revision...")
        self._migrate("up")

    def migrate_downgrade(self: Self) -> None:
        """Downgrade database to base migration."""
        self._logger.info("Downgrading database to base revision...")
        self._migrate("down")


def make_engine(dsn: str, autocommit: bool = False) -> Engine:
    """
    Create a SQLAlchemy engine from a connection string.

    This method is isolated to make the `DatabaseClient` class easier to mock.
    """
    url = sa_make_url(dsn)
    eng = sa_create_engine(url)

    if autocommit:
        return cast("Engine", eng.execution_options(isolation_level="AUTOCOMMIT"))
    else:
        return cast("Engine", eng)


@contextmanager
def in_transaction(conn: Connection) -> Connection:
    if not conn.in_transaction():
        with conn.begin():
            yield conn
    else:
        yield conn


def encode_insert_params(values: list[dict]) -> tuple[list, dict]:
    placeholders = []
    params = {}

    for i, row in enumerate(values):
        row_placeholders = []
        for col in ["volunteer_id", "skill_id"]:
            var_ = f"{col}_{i}"
            placeholder = f":{var_}"
            row_placeholders.append(placeholder)
            params[var_] = row[col]
        placeholders.append(f"({', '.join(row_placeholders)})")

    return placeholders, params
