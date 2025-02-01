from datetime import timedelta, datetime
from pathlib import Path
from tomllib import load as toml_load
from typing import Set

import streamlit as st
from pandas import Timestamp, DataFrame
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from streamlit.connections import SQLConnection

from scripts.db_client import encode_insert_params


class VolunteerSkillsClient:
    def __init__(self, conn: SQLConnection):
        self._conn = conn

    @property
    def volunteers(self) -> dict[str, str]:
        df = self._conn.query(
            sql="SELECT id, given_name, family_name FROM v1.volunteer ORDER BY given_name;", ttl=timedelta(minutes=10)
        )
        return {str(row["id"]): f"{row['given_name']} {row['family_name']}" for _, row in df.iterrows()}

    @property
    def possible_skills(self) -> dict[str, str]:
        df = self._conn.query(sql="SELECT id, name FROM v1.skill ORDER BY name;", ttl=timedelta(minutes=10))
        return {str(row["id"]): row["name"] for _, row in df.iterrows()}

    @property
    def available_skills(self) -> list[str]:
        df = self._conn.query(sql="SELECT distinct(name) FROM v1.skill;", ttl=timedelta(minutes=10))
        return sorted(list(df["name"]))

    @property
    def count_volunteers(self) -> int:
        df = self._conn.query(sql="SELECT count(id) FROM v1.volunteer;", ttl=timedelta(minutes=10))
        return df.iloc[0, 0]

    @property
    def count_skills_possible(self) -> int:
        df = self._conn.query(sql="SELECT count(id) FROM v1.skill;", ttl=timedelta(minutes=10))
        return df.iloc[0, 0]

    @property
    def count_skills_available(self) -> int:
        df = self._conn.query(
            sql="SELECT count(distinct(skill_id)) FROM v1.volunteer_skill;", ttl=timedelta(minutes=10)
        )
        return df.iloc[0, 0]

    @property
    def chart_volunteers_skills(self) -> dict[str, int]:
        df = self._conn.query(
            sql="SELECT volunteer, array_length(skills, 1) AS skills_count FROM v1.volunteer_skills;",
            ttl=timedelta(minutes=10),
        )
        return df.set_index("volunteer")["skills_count"].to_dict()

    @property
    def chart_skills(self) -> dict[str, int]:
        df = self._conn.query(
            """
        SELECT skill, COUNT(volunteer) AS volunteer_count
        FROM (
            SELECT volunteer, unnest(skills) AS skill
            FROM v1.volunteer_skills
        ) AS unnest_skills
        GROUP BY skill;
        """,
            ttl=timedelta(minutes=10),
        )
        return df.set_index("skill")["volunteer_count"].to_dict()

    @property
    def export(self) -> DataFrame:
        return self._conn.query(sql="SELECT * FROM v1.volunteer_skills_export;", ttl=timedelta(minutes=10))

    def filter_skills_by_volunteer(self, volunteer_id: str) -> list[str]:
        df = self._conn.query(
            sql="SELECT skill_id FROM v1.volunteer_skill WHERE volunteer_id = :volunteer_id;",
            params={"volunteer_id": volunteer_id},
            ttl=0,
        )
        return [str(row["skill_id"]) for _, row in df.iterrows()]

    def filter_skills_updated_after(self, date: datetime) -> dict[str, str]:
        df = self._conn.query(
            sql="SELECT id, name FROM v1.skill WHERE updated_at > :date ORDER BY name;",
            params={"date": date},
            ttl=timedelta(minutes=10),
        )
        return {str(row["id"]): row["name"] for _, row in df.iterrows()}

    def filter_volunteers_by_skills(self, skills: Set[str]) -> list[str]:
        placeholders = ", ".join([f":skill_{i}" for i in range(len(skills))])
        query = f"SELECT volunteer FROM v1.volunteer_skills WHERE skills @> ARRAY[{placeholders}];"
        params = {f"skill_{i}": skill for i, skill in enumerate(skills)}
        df = self._conn.query(sql=query, params=params, ttl=timedelta(minutes=10))
        return sorted(list(set(df["volunteer"])))

    def set_volunteer_skills(self, volunteer_id: str, skill_ids: list[str]) -> None:
        conn = self._conn.session.connection()

        try:
            conn.execute(
                statement=text("DELETE FROM v1.volunteer_skill WHERE volunteer_id = :volunteer_id;"),
                parameters={"volunteer_id": volunteer_id},
            )

            values = [{"volunteer_id": int(volunteer_id), "skill_id": int(skill_id)} for skill_id in skill_ids]
            placeholders, params = encode_insert_params(values=values)
            statement = f"""
            INSERT INTO v1.volunteer_skill (volunteer_id, skill_id)
            VALUES {', '.join(placeholders)};
            """
            conn.execute(statement=text(statement), parameters=params)

            conn.commit()
        except DatabaseError as e:
            conn.rollback()
            raise RuntimeError("Error updating volunteer skills") from e

    def volunteer_skills_last_updated(self, volunteer_id: str) -> Timestamp:
        df = self._conn.query(
            sql="SELECT last_updated_at FROM v1.volunteer_skill_update WHERE volunteer_id = :volunteer_id LIMIT 1;",
            params={"volunteer_id": volunteer_id},
            ttl=timedelta(minutes=10),
        )
        return df.iloc[0, 0]


def app_version() -> str:
    with Path("pyproject.toml").open(mode="rb") as f:
        # noinspection PyTypeChecker
        data = toml_load(f)
        return data["project"]["version"]


def show_intro() -> None:
    st.title("MapAction Volunteer Skills Experiment")
