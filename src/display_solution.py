import datetime
import folium
import streamlit as st
from streamlit_calendar import calendar
from streamlit_folium import st_folium

ss = st.session_state


def display_kpis():
    lateness = ss["solution"].lateness
    makespan = ss["solution"].duration
    waiting_time = ss["solution"].waiting_time
    travel_time = ss["solution"].traveling_time
    lateness_col, traveling_col, makespan_col, waiting_col = st.columns(4)
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
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Total iterations: {ss['solution'].iterations}")
        st.write(
            f"Total time taken to solve: {ss['solution'].time_taken_microseconds / 1_000_000:.2f} seconds"
        )
    with col2:
        st.button("See Solution as Table", on_click=display_solution_df)


@st.dialog("Visiting Order", width="large")
def display_solution_df():
    st.dataframe(
        ss["downloadable_solution"],
        use_container_width=True,
    )


def display_solution():
    with st.container():
        st.title("Solution")
        display_kpis()

    col1, col2 = st.columns(2)
    with col1:
        display_calendar()
    with col2:
        display_solution_map()


def display_calendar():
    calendar_events = []
    next_location = (
        event[0].location
        for event in ss["solution"].schedule
        if type(event[0]).__name__[2:] == "Work"
    )
    for i, event in enumerate(ss["solution"].schedule):
        window = event[0].window
        # very sad but I found no clean solution to show real times in calendar
        start = datetime.datetime.fromtimestamp(
            window[0], tz=datetime.timezone.utc
        ) - datetime.timedelta(hours=1)
        end = datetime.datetime.fromtimestamp(
            window[1], tz=datetime.timezone.utc
        ) - datetime.timedelta(hours=1)
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
                        "resourceId": next(next_location),
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


def display_solution_map():
    st.title("Route (from red to green)")
    m = folium.Map()
    folium.plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(m)
    for i, location in enumerate(ss["location_list"]):
        folium.Marker(
            location["geocode"],
            popup=location["name"],
            icon=folium.Icon(color="blue", icon="home"),
        ).add_to(m)
    for i, location_id in enumerate(ss["solution"].route):
        folium.PolyLine(
            [
                ss["location_list"][location_id]["geocode"],
                ss["location_list"][
                    ss["solution"].route[(i + 1) % len(ss["solution"].route)]
                ]["geocode"],
            ],
            color=get_color(i / len(ss["solution"].route)),
        ).add_to(m)
    st_folium(
        m,
        key="new",
        center=ss["location_list"][ss["solution"].route[0]]["geocode"],
        zoom=6,
        height=400,
        width=700,
    )


def get_color(value):
    # start color red, end color green

    start_color = [255, 0, 0]
    end_color = [0, 255, 0]
    color = [
        int(start_color[i] + (end_color[i] - start_color[i]) * value)
        for i in range(3)
    ]
    # transform to hex
    return "#" + "".join(f"{c:02x}" for c in color)
