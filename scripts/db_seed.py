import json
import logging
from collections import OrderedDict
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
    skills_path = PROJECT_ROOT / "resources" / "data" / "skills.json"
    with skills_path.open() as f:
        data = json.load(f)["skills"]
    return [skill for skill_group in data.values() for skill in skill_group]


def _process_skills(faker: Faker, skills: list[str], phases_weighted: OrderedDict) -> list[dict]:
    skills_ = []
    for skill in skills:
        phase = faker.random_element(elements=phases_weighted)
        skills_.append(
            {
                "name": skill,
                "description": f"Description for {skill.lower()} ...",
                "created_at": phase,
                "updated_at": phase,
            }
        )

    return skills_


def _pick_skills_for_volunteer(faker: Faker, skills: list[str]) -> list[str]:
    skills = faker.random_elements(elements=skills, unique=True, length=faker.random_int(min=2, max=25))
    return list(skills)


def insert_skills(db: DatabaseClient, faker: Faker, skills: list[str], phases_weighted: OrderedDict) -> None:
    values = _process_skills(faker=faker, skills=skills, phases_weighted=phases_weighted)
    placeholders, params = encode_insert_params(values=values)
    statement = f"""
    INSERT INTO v1.skill (name, description, created_at, updated_at)
    VALUES {', '.join(placeholders)}
    ON CONFLICT (name) DO NOTHING;
    """

    db.execute(sql=text("ALTER TABLE v1.skill DISABLE TRIGGER v1_skill_updated_at;"))
    db.execute(sql=text(statement), params=params)
    db.execute(sql=text("ALTER TABLE v1.skill ENABLE TRIGGER v1_skill_updated_at;"))


def _insert_volunteer(conn: Connection, faker: Faker, skills: list[str]) -> None:
    """
    Insert a volunteer and their skills into the database.
    - generate volunteer data and pick a random set of skills (by ID) from up-to the penultimate phase
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
    volunteer_skill_ids = _pick_skills_for_volunteer(faker=faker, skills=skills)

    try:
        statement = text("""
        INSERT INTO v1.volunteer (given_name, family_name, email)
        VALUES (:given_name, :family_name, :email)
        RETURNING id;
        """)
        result = conn.execute(statement=statement, parameters=volunteer)
        volunteer_id = result.scalar()

        values = [{"volunteer_id": volunteer_id, "skill_id": skill_id} for skill_id in volunteer_skill_ids]
        placeholders, params = encode_insert_params(values=values)
        statement = f"""
        INSERT INTO v1.volunteer_skill (volunteer_id, skill_id)
        VALUES {', '.join(placeholders)}
        ON CONFLICT DO NOTHING;
        """
        conn.execute(statement=text(statement), parameters=params)

        conn.commit()
    except SQLAlchemyDatabaseError as e:
        conn.rollback()
        msg = "Error inserting volunteer and/or volunteer skills"
        raise RuntimeError(msg) from e


def insert_volunteers(db: DatabaseClient, faker: Faker, logger: logging.Logger, phases_weighted: OrderedDict) -> None:
    volunteer_target = 42
    volunteer_count = db.execute(sql=text("SELECT COUNT(*) FROM v1.volunteer;")).scalar()

    # get skills upto the penultimate phase
    results = db.execute(
        sql=text("""
        SELECT id
        FROM v1.skill
        WHERE created_at < (
            SELECT distinct(created_at) FROM v1.skill ORDER BY created_at DESC OFFSET 1 LIMIT 1
        );""")
    )
    skills_subset = [str(skill_id) for skill_id in results.scalars().all()]

    if volunteer_count >= volunteer_target:
        logger.info(f"Target count of {volunteer_target} volunteers reached.")
        return

    with db.engine.connect() as conn:
        for i in range(volunteer_target - volunteer_count):
            logger.info(f"Inserting volunteer {volunteer_count + i + 1} of {volunteer_target}")
            _insert_volunteer(conn=conn, faker=faker, skills=skills_subset)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    secrets = _load_secrets()
    db_dsn = secrets["connections"]["neon"]["url"]
    db = DatabaseClient(engine=make_engine(dsn=db_dsn), logger=logger)

    faker = Faker("en_GB")
    # generate 4 random date times in the past at which skills were added, weighted such that 1st at 50%, 2nd at 30%, 3rd at 5%, 4th at 15%
    phases = [faker.date_time_between(start_date="-1y", end_date="now") for _ in range(4)]
    phases_weighted = OrderedDict([(phases[0], 50), (phases[1], 30), (phases[2], 5), (phases[3], 15)])
    skills = _load_skills_flat()

    insert_skills(db=db, faker=faker, skills=skills, phases_weighted=phases_weighted)
    insert_volunteers(db=db, faker=faker, logger=logger, phases_weighted=phases_weighted)


if __name__ == "__main__":
    main()
