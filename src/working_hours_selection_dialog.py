import streamlit as st
import datetime

ss = st.session_state


@st.dialog("Define Working Hours")
def working_hours_selection_dialog():
    co1, co2 = st.columns(2)
    with co1:
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
    with co2:
        ss["parameters"]["travel_speed"] = st.number_input(
            "Set travel speed in km/h", 1, 100, 60
        )
        ss["parameters"]["lunch_break"] = st.checkbox(
            "Take a lunch break", value=True
        )

        ss["parameters"]["lunch_start"] = st.time_input(
            "Set lunch start time",
            datetime.time(12, 0),
            disabled=not ss["parameters"]["lunch_break"],
        )
        ss["parameters"]["lunch_end"] = st.time_input(
            "Set lunch end time",
            datetime.time(13, 0),
            disabled=not ss["parameters"]["lunch_break"],
        )
