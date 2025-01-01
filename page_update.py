from itertools import islice

import streamlit as st
from pandas import Timestamp
from streamlit.connections import SQLConnection

from shared import show_intro, VolunteerSkillsClient


def _format_datetime(ts: Timestamp) -> str:
    return ts.strftime("%d %b %Y %H:%M")


def show_volunteer_select(data: VolunteerSkillsClient) -> None:
    st.subheader("What is your name?")
    options = {0: "I am...", **data.volunteers}
    volunteer_name = st.selectbox("volunteer", options.values(), label_visibility="hidden")

    st.session_state.volunteer_id = None
    try:
        st.session_state.volunteer_id = next(k for k, v in data.volunteers.items() if v == volunteer_name)
    except StopIteration:
        pass


def show_skills(data: VolunteerSkillsClient) -> None:
    volunteer_id = st.session_state.volunteer_id
    skills_total_quarter = data.count_skills_possible // 3
    possible_skills = data.possible_skills
    prev_selected_skills = data.filter_skills_by_volunteer(volunteer_id=volunteer_id)
    volunteer_version = data.volunteer_skills_last_updated(volunteer_id=volunteer_id)
    new_updated_skills = data.filter_skills_updated_after(date=volunteer_version)

    st.subheader("What skills do you have?")
    st.info(
        f"**{len(new_updated_skills)} skills** (indicated by ✨) have been added or updated since you last "
        f"updated your skills."
    )

    col1, col2, col3 = st.columns(3)
    cols = [
        (col1, dict(islice(possible_skills.items(), skills_total_quarter))),
        (col2, dict(islice(possible_skills.items(), skills_total_quarter, 2 * skills_total_quarter))),
        (col3, dict(islice(possible_skills.items(), 2 * skills_total_quarter, None))),
    ]
    for col, skills in cols:
        with col:
            for skill_id, skill_name in skills.items():
                label = f"**{skill_name} ✨**" if skill_id in new_updated_skills else skill_name
                st.checkbox(
                    label=label, key=f"skill_{skill_id}_v_{volunteer_id}", value=skill_id in prev_selected_skills
                )

    save_changes = st.button("Save changes")
    if save_changes:
        new_selected_skill_ids = [
            key.replace("skill_", "").replace(f"_v_{volunteer_id}", "")
            for key in st.session_state
            if key.startswith("skill_") and f"v_{volunteer_id}" in key and st.session_state[key]
        ]
        data.set_volunteer_skills(volunteer_id=volunteer_id, skill_ids=new_selected_skill_ids)
        st.success("Skills updated")


conn: SQLConnection = st.connection("neon", type="sql")
engine = VolunteerSkillsClient(conn=conn)

show_intro()
st.header("Update your skills", divider=True)
show_volunteer_select(data=engine)
if st.session_state.volunteer_id:
    show_skills(data=engine)
