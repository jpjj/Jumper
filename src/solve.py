import datetime
import streamlit as st
import traveling_rustling

from src.geocode import fetch_distance_matrix

ss = st.session_state


def solve():
    data = ss["data"]

    location_list = []
    i = -1
    for name, row in data.iterrows():
        i += 1
        location_list.append(
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
        for idx in data.columns[7:]:
            if row[idx]:
                location_list[i]["time_windows"].append(idx)

    time_windows = [[] for _ in range(len(location_list))]
    for i, location in enumerate(location_list):
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
        int(location["working_time"] * 60) for location in location_list
    ]

    distance_matrix = fetch_distance_matrix(
        [location["geocode"] for location in location_list]
    )
    operation_times = (8 * 3600, 20 * 3600)

    solution = traveling_rustling.solve(
        distance_matrix,
        distance_matrix,
        working_times,
        time_windows,
        operation_times,
        1,
    )
    lateness = solution.lateness
    makespan = solution.duration
    waiting_time = solution.waiting_time
    travel_time = solution.traveling_time

    st.write("Optimized Route:")
    for i, event in enumerate(solution.schedule):
        window = event[0].window
        start = datetime.datetime.fromtimestamp(
            window[0], tz=datetime.timezone.utc
        )
        end = datetime.datetime.fromtimestamp(
            window[1], tz=datetime.timezone.utc
        )
        name = type(event[0]).__name__
        if hasattr(event[0], "location"):
            location = event[0].location
            st.write(
                f"{location_list[location]['name']} {datetime.datetime.strftime(start, '%d.%m.%Y %H:%M:%S')} to {datetime.datetime.strftime(end, '%d.%m.%Y %H:%M:%S')}"
            )
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
    st.write(f"Total iterations: {solution.iterations}")
    st.write(
        f"Total time taken to solve: {solution.time_taken_microseconds / 1_000_000:.2f} seconds"
    )
