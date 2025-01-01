import streamlit as st
from streamlit.connections import SQLConnection

from shared import show_intro, VolunteerSkillsClient


def show_skills_stats(data: VolunteerSkillsClient) -> None:
    st.header("Volunteer skills statistics", divider=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Volunteers", data.count_volunteers)
    col2.metric("Skills (Possible)", data.count_skills_possible)
    col3.metric("Skills (Available)", data.count_skills_available)

    st.info("These metrics and charts were me messing around with streamlit, I don't think they're very useful.")

    tab1, tab2 = st.tabs(["Volunteer skills", "Skill count"])
    tab1.bar_chart(data.chart_volunteers_skills, horizontal=True)
    tab2.bar_chart(data.chart_skills, horizontal=True)


conn: SQLConnection = st.connection("neon", type="sql")
engine = VolunteerSkillsClient(conn=conn)

show_intro()
show_skills_stats(data=engine)
