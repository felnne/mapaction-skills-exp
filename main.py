from pathlib import Path
from tomllib import load as toml_load
from typing import Set

import streamlit as st
from faker import Faker

from skills import skills_flat as all_skills_flat


class VolunteerSkillsClient:
    def __init__(self):
        self._volunteer_skills = self._generate()

    @staticmethod
    def _generate() -> dict[str, list[str]]:
        volunteers_skills = {}

        faker = Faker("en_GB")
        common_skill = faker.random_element(all_skills_flat)
        max_len = len(all_skills_flat)

        for _ in range(42):
            volunteer_skills = faker.random_elements(
                elements=all_skills_flat,
                unique=True,
                length=faker.random_int(min=2, max=max_len),
            )
            volunteers_skills[faker.unique.name()] = list(volunteer_skills) + [common_skill]

        return volunteers_skills

    @property
    def available_skills(self) -> list[str]:
        return sorted(list(set(skill for skills in self._volunteer_skills.values() for skill in skills)))

    @property
    def count_volunteers(self) -> int:
        return len(self._volunteer_skills)

    @property
    def count_skills_possible(self) -> int:
        return len(all_skills_flat)

    @property
    def count_skills_available(self) -> int:
        return len(self.available_skills)

    @property
    def chart_volunteers_skills(self) -> dict[str, int]:
        return {volunteer: len(skills) for volunteer, skills in self._volunteer_skills.items()}

    def filter_volunteers_by_skills(self, skills: Set[str]) -> list[str]:
        return [
            volunteer
            for volunteer, volunteer_skills in self._volunteer_skills.items()
            if skills.issubset(volunteer_skills)
        ]


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
    st.bar_chart(data.chart_volunteers_skills, horizontal=True)


def show_experiment_info() -> None:
    st.markdown("---")
    expand = st.expander("Experiment information")
    with expand:
        st.markdown(
            f"""
            ### App info
            - version: {app_version()}
            - repo: [github.com/felnne/mapaction-skills-exp](https://github.com/felnne/mapaction-skills-exp)
            """
        )


def main() -> None:
    engine = VolunteerSkillsClient()

    show_intro()
    show_skills_query(data=engine)
    show_skills_stats(data=engine)
    show_experiment_info()


if __name__ == "__main__":
    main()
