import datetime
import streamlit as st
from streamlit_calendar import calendar

ss = st.session_state


def display_solution():
    with st.container():
        st.title("Solution")
        lateness = ss["solution"].lateness
        makespan = ss["solution"].duration
        waiting_time = ss["solution"].waiting_time
        travel_time = ss["solution"].traveling_time

        tab1, tab2, tab3, tab4 = st.tabs(
            ["KPIs", "Calendar", "Map", "Download"]
        )

        with tab1:
            st.header("KPIs")
            lateness_col, traveling_col, makespan_col, waiting_col = st.columns(
                4
            )
            lateness_col.metric(
                "Lateness",
                f"{datetime.timedelta(seconds=lateness)}",
                help="The total time you arrive late at locations",
            )
            traveling_col.metric(
                "Travel Time",
                f"{datetime.timedelta(seconds=travel_time)}",
                help="Total time spent traveling",
            )
            makespan_col.metric(
                "Makespan",
                f"{datetime.timedelta(seconds=makespan)}",
                help="Total operation time from start to finish",
            )
            waiting_col.metric(
                "Waiting Time",
                f"{datetime.timedelta(seconds=waiting_time)}",
                help="Total time spent waiting",
            )
            st.write(f"Total iterations: {ss['solution'].iterations}")
            st.write(
                f"Total time taken to solve: {ss['solution'].time_taken_microseconds / 1_000_000:.2f} seconds"
            )
        with tab2:
            create_calendar()
        with tab3:
            st.header("An owl")
            st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
        with tab4:
            st.write("Download the solution as a CSV file")
            st.write("Download the solution as a JSON file")


def create_calendar():
    calendar_events = []
    for i, event in enumerate(ss["solution"].schedule):
        window = event[0].window
        start = datetime.datetime.fromtimestamp(
            window[0], tz=datetime.timezone.utc
        )
        end = datetime.datetime.fromtimestamp(
            window[1], tz=datetime.timezone.utc
        )
        name = type(event[0]).__name__[2:]
        match name:
            case "Travel":
                calendar_events.append(
                    {
                        "resourceId": name,
                        "title": name,
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                    }
                )
            case "Work":
                location = event[0].location
                calendar_events.append(
                    {
                        "resourceId": name,
                        "title": ss["location_list"][location]["name"],
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                    }
                )
    calendar_options = {
        "initialView": "timeGridWeek",
        "selectable": True,
        "slotMinTime": ss["parameters"]["start_time"].isoformat(),
        "slotMaxTime": ss["parameters"]["end_time"].isoformat(),
        "initialDate": calendar_events[0]["start"],
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": "timeGridWeek,timeGridDay",
        },
    }
    custom_css = {}
    ss["calendar"] = calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css,
    )
    st.write(ss["calendar"])
