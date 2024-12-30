from datetime import timedelta
from pathlib import Path
from tomllib import load as toml_load
from typing import Set

import streamlit as st
from streamlit.connections import SQLConnection


class VolunteerSkillsClient:
    def __init__(self, conn: SQLConnection):
        self._conn = conn

    @property
    def available_skills(self) -> list[str]:
        df = self._conn.query(sql="SELECT distinct(skill) FROM v1.volunteer_skills;", ttl=timedelta(minutes=10))
        return sorted(list(df["skill"]))

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
        df = self._conn.query(sql="SELECT count(distinct(skill)) FROM v1.volunteer_skills;", ttl=timedelta(minutes=10))
        return df.iloc[0, 0]

    @property
    def chart_volunteers_skills(self) -> dict[str, int]:
        df = self._conn.query(
            sql="SELECT volunteer, count(skill) FROM v1.volunteer_skills GROUP BY volunteer;", ttl=timedelta(minutes=10)
        )
        return df.set_index("volunteer")["count"].to_dict()

    @property
    def chart_skills(self) -> dict[str, int]:
        df = self._conn.query(
            sql="SELECT skill, count(volunteer) FROM v1.volunteer_skills GROUP BY skill;", ttl=timedelta(minutes=10)
        )
        return df.set_index("skill")["count"].to_dict()

    def filter_volunteers_by_skills(self, skills: Set[str]) -> list[str]:
        df = self._conn.query(
            sql="SELECT volunteer, skill FROM v1.volunteer_skills WHERE skill IN :skills;",
            params={"skills": tuple(skills)},
            ttl=timedelta(minutes=10),
        )
        return sorted(list(set(df["volunteer"])))


def app_version() -> str:
    with Path("pyproject.toml").open(mode="rb") as f:
        # noinspection PyTypeChecker
        data = toml_load(f)
        return data["project"]["version"]


def show_intro() -> None:
    st.title("MapAction Volunteer Skills Experiment")


def show_skills_query(data: VolunteerSkillsClient) -> None:
    st.header("Find a volunteer by their skills", divider=True)
    selected_skills = st.multiselect("Select skills", data.available_skills)
    if len(selected_skills) > 0:
        volunteers = data.filter_volunteers_by_skills(set(selected_skills))
        st.markdown("\n".join(f"- {volunteer}" for volunteer in volunteers))


def show_skills_stats(data: VolunteerSkillsClient) -> None:
    st.header("Volunteer skills statistics", divider=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Volunteers", data.count_volunteers)
    col2.metric("Skills (Possible)", data.count_skills_possible)
    col3.metric("Skills (Available)", data.count_skills_available)

    tab1, tab2 = st.tabs(["Volunteer skills", "Skill count"])
    tab1.bar_chart(data.chart_volunteers_skills, horizontal=True)
    tab2.bar_chart(data.chart_skills, horizontal=True)


def show_experiment_info() -> None:
    st.markdown("---")
    expand = st.expander("Experiment information")
    with expand:
        st.markdown(
            f"""
            ### App info
            - version: {app_version()}
            - repo: [github.com/felnne/mapaction-skills-exp](https://github.com/felnne/mapaction-skills-exp)
            - the chart and metrics are for me to learn more about streamlit
            - data queries are cached for 10 minutes
            """
        )


def main() -> None:
    conn: SQLConnection = st.connection("neon", type="sql")
    engine = VolunteerSkillsClient(conn=conn)

    show_intro()
    show_skills_query(data=engine)
    show_skills_stats(data=engine)
    show_experiment_info()


if __name__ == "__main__":
    main()
