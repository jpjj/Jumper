import datetime
import pandas as pd
import streamlit as st
import traveling_rustling
from streamlit_calendar import calendar
from src.geocode import fetch_distance_matrix

ss = st.session_state


def solve(data: pd.DataFrame, parameters: dict):  # -> (list, PyOutput)
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
        for idx in data.columns[6:]:
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
    start = (
        parameters["start_time"].hour * 60 + parameters["start_time"].minute
    ) * 60 + parameters["start_time"].second
    end = (
        parameters["end_time"].hour * 60 + parameters["end_time"].minute
    ) * 60 + parameters["end_time"].second
    operation_times = (start, end)

    solution = traveling_rustling.solve(
        distance_matrix,
        distance_matrix,
        working_times,
        time_windows,
        operation_times,
        1,
    )
    return solution, location_list
