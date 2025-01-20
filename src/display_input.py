import streamlit as st
import folium
from streamlit_folium import st_folium

ss = st.session_state

START_DATES_COLUMN = 6


def display_input():
    st.title("Check the input data")
    tab1, tab2 = st.tabs(["Table View", "Map View"])
    with tab1:
        display_input_dataframe()
    with tab2:
        display_input_map()


def display_input_dataframe():
    ss["data"] = st.data_editor(
        ss["data"],
        column_config={
            column_date: st.column_config.CheckboxColumn()
            for column_date in ss["data"].columns[START_DATES_COLUMN:]
        },
        hide_index=False,
    )


def display_input_map():
    geocodes = ss["data"][["Lat", "Lon"]].values.tolist()
    m = folium.Map(location=geocodes[0], zoom_start=6)
    for i, geo in enumerate(geocodes):
        folium.Marker(geo, popup=ss["data"].iloc[i]["Address"]).add_to(m)

    # call to render Folium map in Streamlit
    st_folium(m, width=725)
