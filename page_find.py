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


def show_data_export(data: VolunteerSkillsClient) -> None:
    st.header("Export data", divider=True)
    st.download_button("Download data as CSV for analysis.", data.export.to_csv(), "volunteer_skills.csv", "text/csv")
    expand = st.expander("Data schema", icon=":material/info:")
    expand.markdown("""
    ### V1 schema

    #### Columns
    1. (index, no header row text)
    1. `volunteer_id`
    1. `volunteer_name` (given + family)
    1. `volunteer_updated_at` (ISO 8601)
    1. `skill_id`
    1. `skill_name`
    1. `skill_description`
    1. `skill_updated_at` (ISO 8601)
    1. `volunteer_skills_last_updated_at` (ISO 8601)
    1. `query_ts` (ISO 8601, point of query, same value for all rows, to indicate caching)

    #### Notes
    - `volunteer_id`, `skill_id` values are unique to this application
    - ordered by `volunteer_id`, `skill_id`
    """)


conn: SQLConnection = st.connection("neon", type="sql")
engine = VolunteerSkillsClient(conn=conn)

show_intro()
show_skills_query(data=engine)
show_data_export(data=engine)
