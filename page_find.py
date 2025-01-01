import streamlit as st
from streamlit.connections import SQLConnection

from shared import show_intro, VolunteerSkillsClient


def show_skills_query(data: VolunteerSkillsClient) -> None:
    st.header("Find a volunteer by their skills", divider=True)
    selected_skills = st.multiselect("Choose skills", data.available_skills)
    if len(selected_skills) > 0:
        filtered_volunteers = data.filter_volunteers_by_skills(set(selected_skills))
        if len(filtered_volunteers) > 0:
            st.markdown("\n".join(f"- {volunteer}" for volunteer in filtered_volunteers))
        else:
            st.warning("No volunteers found with all the selected skills.")


conn: SQLConnection = st.connection("neon", type="sql")
engine = VolunteerSkillsClient(conn=conn)

show_intro()
show_skills_query(data=engine)
