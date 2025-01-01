import streamlit as st

from shared import app_version

find_page = st.Page("page_find.py", title="Find volunteers with skills", icon=":material/manage_search:")
stats_page = st.Page("page_stats.py", title="Volunteer skills statistics", icon=":material/insights:")
update_page = st.Page("page_update.py", title="Update volunteer skills", icon=":material/edit:")
app = st.navigation([find_page, stats_page, update_page])

st.set_page_config(page_title="MapAction Skills", page_icon=":material/point_scan:")
with st.sidebar:
    st.markdown(
        f"""
        #### Experiment info
        - App version: {app_version()}
        - repo: [felnne/mapaction-skills-exp](https://github.com/felnne/mapaction-skills-exp)
        - data queries are cached for 10 minutes
        """
    )
app.run()
