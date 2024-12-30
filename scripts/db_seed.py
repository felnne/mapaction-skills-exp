import json
import logging
from pathlib import Path
from tomllib import load as toml_load

from faker import Faker
from sqlalchemy import text, Connection
from sqlalchemy.exc import DatabaseError as SQLAlchemyDatabaseError

from db_client import DatabaseClient, make_engine, encode_insert_params

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_secrets():
    secrets_path = PROJECT_ROOT / ".streamlit" / "secrets.toml"
    with secrets_path.open(mode="rb") as f:
        return toml_load(f)


def _load_skills_flat() -> list[str]:
    with PROJECT_ROOT / "resources" / "data" / "skills.json" as f:
        data = json.load(f)["skills"]
    return [skill for skill_group in data.values() for skill in skill_group]


def _pick_skills_for_volunteer(faker: Faker, skills: list[str]) -> list[str]:
    skills = faker.random_elements(elements=skills, unique=True, length=faker.random_int(min=2, max=25))
    return list(skills)


def insert_skills(db: DatabaseClient, skills: list[str]) -> None:
    skills_dicts = [{"name": skill} for skill in skills]
    placeholders, params = encode_insert_params(values=skills_dicts)
    statement = f"INSERT INTO v1.skill (name) VALUES {', '.join(placeholders)} ON CONFLICT DO NOTHING;"
    db.execute(sql=text(statement), params=params)


def _insert_volunteer(conn: Connection, faker: Faker, skills: list[str]) -> None:
    """
    Insert a volunteer and their skills into the database.
    - generate volunteer data na pick a random set of skills (by name)
    - within a single DB transaction to ensure consistency:
        - fetch row IDs for selected skills (to ensure all are known)
        - insert volunteer returning row ID
        - insert join table rows (volunteer_id, skill_id)

    Note: This could be done in a single statement with a CTE, with skills selected from the DB instead.
    """
    _given_name = faker.first_name()
    _family_name = faker.last_name()
    _email = f"{_given_name.lower()[:1]}{_family_name.lower()}@mapaction.org.com"

    volunteer = {"given_name": _given_name, "family_name": _family_name, "email": _email}
    volunteer_skills = _pick_skills_for_volunteer(faker=faker, skills=skills)

    try:
        result = conn.execute(
            statement=text("SELECT id FROM v1.skill WHERE name IN :names"),
            parameters={"names": tuple(volunteer_skills)},
        )
        skill_ids = result.scalars().all()

        statement = text("""
        INSERT INTO v1.volunteer (given_name, family_name, email)
        VALUES (:given_name, :family_name, :email)
        RETURNING id;
        """)
        result = conn.execute(statement=statement, parameters=volunteer)
        volunteer_id = result.scalar()

        values = [{"volunteer_id": volunteer_id, "skill_id": skill_id} for skill_id in skill_ids]
        placeholders, params = encode_insert_params(values=values)
        statement = f"""
        INSERT INTO v1.volunteer_skill (volunteer_id, skill_id)
        VALUES {', '.join(placeholders)} ON CONFLICT DO NOTHING;
        """
        conn.execute(statement=text(statement), parameters=params)

        conn.commit()
    except SQLAlchemyDatabaseError as e:
        conn.rollback()
        msg = "Error inserting volunteer and/or volunteer skills"
        raise RuntimeError(msg) from e


def insert_volunteers(db: DatabaseClient, faker: Faker, logger: logging.Logger, skills: list[str]) -> None:
    volunteer_target = 42
    volunteer_count = db.execute(sql=text("SELECT COUNT(*) FROM v1.volunteer;")).scalar()

    if volunteer_count >= volunteer_target:
        logger.info(f"Target count of {volunteer_target} volunteers reached.")
        return

    with db.engine.connect() as conn:
        for i in range(volunteer_target - volunteer_count):
            logger.info(f"Inserting volunteer {volunteer_count + i + 1} of {volunteer_target}")
            _insert_volunteer(conn=conn, faker=faker, skills=skills)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    secrets = _load_secrets()
    db_dsn = secrets["connections"]["neon"]["url"]
    db = DatabaseClient(engine=make_engine(dsn=db_dsn), logger=logger)

    faker = Faker("en_GB")
    skills = _load_skills_flat()

    insert_skills(db=db, skills=skills)
    insert_volunteers(db=db, faker=faker, logger=logger, skills=skills)


if __name__ == "__main__":
    main()
