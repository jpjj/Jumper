import datetime
import streamlit as st
import traveling_rustling
from streamlit_calendar import calendar
from src.geocode import fetch_distance_matrix

ss = st.session_state


def solve():
    data = ss["data"]

    ss["location_list"] = []
    i = -1
    for name, row in data.iterrows():
        i += 1
        ss["location_list"].append(
            {
                "name": name,
                "address": row["Address"],
                "geocode": (row["Lat"], row["Lon"]),
                "working_time": row["Duration (Minutes)"],
                "open_time": datetime.time.fromisoformat(
                    row["Open (HH:MM:SS)"] + "Z"
                ),
                "close_time": datetime.time.fromisoformat(
                    row["Close (HH:MM:SS)"] + "Z"
                ),
                "time_windows": [],
            }
        )
        # here erstmal nur die Reihe aller Daten. raw.
        for idx in data.columns[6:]:
            if row[idx]:
                ss["location_list"][i]["time_windows"].append(idx)

    time_windows = [[] for _ in range(len(ss["location_list"]))]
    for i, location in enumerate(ss["location_list"]):
        for date_str in location["time_windows"]:
            date = datetime.datetime.strptime(date_str, "%d.%m.%Y").date()
            open_time = location["open_time"]
            date_utc = datetime.datetime(
                date.year,
                date.month,
                date.day,
                open_time.hour,
                open_time.minute,
                tzinfo=datetime.timezone.utc,
            )
            start = date_utc.timestamp()
            close_time = location["close_time"]
            end = (
                date_utc.replace(hour=close_time.hour, minute=close_time.minute)
            ).timestamp()
            if len(time_windows[i]) == 0:
                time_windows[i].append([int(start), int(end)])
            elif time_windows[i][-1][1] == start:
                time_windows[i][-1][1] = int(end)
            else:
                time_windows[i].append([int(start), int(end)])
    for i in range(len(time_windows)):
        for j in range(len(time_windows[i])):
            time_windows[i][j] = tuple(time_windows[i][j])

    working_times = [
        int(location["working_time"] * 60) for location in ss["location_list"]
    ]

    distance_matrix = fetch_distance_matrix(
        [location["geocode"] for location in ss["location_list"]]
    )
    start = (ss["start_time"].hour * 60 + ss["start_time"].minute) * 60 + ss[
        "start_time"
    ].second
    end = (ss["end_time"].hour * 60 + ss["end_time"].minute) * 60 + ss[
        "end_time"
    ].second
    operation_times = (start, end)

    ss["solution"] = traveling_rustling.solve(
        distance_matrix,
        distance_matrix,
        working_times,
        time_windows,
        operation_times,
        1,
    )


def display_solution():
    lateness = ss["solution"].lateness
    makespan = ss["solution"].duration
    waiting_time = ss["solution"].waiting_time
    travel_time = ss["solution"].traveling_time

    # st.write("Optimized Route:")
    # for i, event in enumerate(ss["solution"].schedule):
    #     window = event[0].window
    #     start = datetime.datetime.fromtimestamp(
    #         window[0], tz=datetime.timezone.utc
    #     )
    #     end = datetime.datetime.fromtimestamp(
    #         window[1], tz=datetime.timezone.utc
    #     )
    #     name = type(event[0]).__name__
    #     if hasattr(event[0], "location"):
    #         location = event[0].location
    #         st.write(
    #             f"{ss['location_list'][location]['name']} {datetime.datetime.strftime(start, '%d.%m.%Y %H:%M:%S')} to {datetime.datetime.strftime(end, '%d.%m.%Y %H:%M:%S')}"
    #         )
    # else:
    #     st.write(
    #         f"{name} {datetime.strftime(start, '%d.%m.%Y %H:%M:%S')} to {datetime.strftime(end, '%d.%m.%Y %H:%M:%S')}"
    #     )
    st.write(f"Lateness: {datetime.timedelta(seconds=lateness)}")
    st.write(f"Waiting Time: {datetime.timedelta(seconds=waiting_time)}")
    st.write(
        f"Makespan (Total Operation Time): {datetime.timedelta(seconds=makespan)}"
    )
    st.write(f"Total Travel Time: {datetime.timedelta(seconds=travel_time)}")
    st.write(f"Total iterations: {ss['solution'].iterations}")
    st.write(
        f"Total time taken to solve: {ss['solution'].time_taken_microseconds / 1_000_000:.2f} seconds"
    )


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
        "timeFormat": "H(:mm)",
        "selectable": True,
        "slotMinTime": ss["start_time"].isoformat(),
        "slotMaxTime": ss["end_time"].isoformat(),
        "initialDate": calendar_events[0]["start"],
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": "timeGridWeek,timeGridDay",
        },
    }
    custom_css = {}
    calendar1 = calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css,
    )
    st.write(calendar1)
