import streamlit as st
import datetime

from src.geocode import get_duration

ss = st.session_state


@st.dialog("Define Parameters", width="large")
def working_hours_selection_dialog():
    col1, col2 = st.columns(2)
    with col1:
        ss["parameters"]["start_time"] = st.time_input(
            "Set daily start time", datetime.time(6, 0)
        )

        ss["parameters"]["end_time"] = st.time_input(
            "Set daily end time", datetime.time(20, 0)
        )
        st.write("Select the days you work:")
        ss["parameters"]["monday"] = st.checkbox("Monday", value=True)
        ss["parameters"]["tuesday"] = st.checkbox("Tuesday", value=True)
        ss["parameters"]["wednesday"] = st.checkbox("Wednesday", value=True)
        ss["parameters"]["thursday"] = st.checkbox("Thursday", value=True)
        ss["parameters"]["friday"] = st.checkbox("Friday", value=True)
        ss["parameters"]["saturday"] = st.checkbox("Saturday", value=False)
        ss["parameters"]["sunday"] = st.checkbox("Sunday", value=False)
        st.divider()
        ss["parameters"]["breaks"] = st.toggle("Take breaks", value=False)

        ss["parameters"]["travel_time_until_break"] = st.number_input(
            "Travel time until break (in minutes)",
            min_value=60,
            max_value=300,
            value=180,
            disabled=not ss["parameters"]["breaks"],
        )
        ss["parameters"]["break_duration"] = st.number_input(
            "Break length (in minutes)",
            min_value=5,
            max_value=120,
            value=30,
            disabled=not ss["parameters"]["breaks"],
        )
    with col2:
        ss["parameters"]["travel_speed"] = st.slider(
            "Set travel speed in km/h", 20, 120, 80
        )
        ss["parameters"]["fix_time"] = st.slider(
            "Set a fix time added to every travel between locations (in minutes)",
            0,
            120,
            5,
        )
        names = [loc["name"] for loc in ss["location_list"]]
        names_to_geocodes = {
            loc["name"]: loc["geocode"] for loc in ss["location_list"]
        }
        selected_location1 = st.selectbox(
            "Select location 1",
            options=names,
        )
        selected_location2 = st.selectbox(
            "Select location 2",
            options=names,
            index=1,
        )
        st.write(
            f"Travel duration from {selected_location1} to {selected_location2}: {datetime.timedelta(seconds=get_duration(names_to_geocodes[selected_location1], names_to_geocodes[selected_location2], ss['parameters']['travel_speed'], ss['parameters']['fix_time']))}"
        )
        st.divider()
        ss["parameters"]["time_limit"] = st.number_input(
            "Set running time of the solver (in seconds)",
            min_value=1,
            max_value=30,
            value=1,
        )
