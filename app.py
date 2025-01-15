# add to requirements.txt
# traveling_rustling==0.1.1

import folium
import streamlit as st
import traveling_rustling as tr
from streamlit_folium import st_folium
import pandas as pd
from src.solve import solve
from src.geocode import geocode_address
from src import setup
# from src.components import sidebar

# sidebar.show_sidebar()
ss = st.session_state
st.set_page_config(layout="wide", page_icon="assets/horse.svg")


setup.setup_LOL()

# Customize the sidebar
logo = "assets/horse.svg"
st.sidebar.image(logo)

# Customize page title
st.title("Jumper App")

st.markdown(
    """
    This is the Jumper App. It solves the Traveling Salesperson Problem (TSP) using the Rust library [traveling_rustling](https://pypi.org/project/traveling-rustling/).
    """
)

st.header("Instructions")

markdown = """
1. Upload a csv file with addresses of the places you want to visit, its opening times and availabilities. Geocodes are optional.
2. The addresses not geocoded will be geocoded using the [OpenStreetMap Nominatim API](https://nominatim.org/release-docs/develop/api/Search/).
3. Check the data again and click on the "Generate schedule" button.
4. Explore the results.
"""

st.markdown(markdown)
radio_choice = st.radio(
    "Choose Mode",
    ["Use Example Data", "Upload Data"],
    on_change=setup.reset,
)


if radio_choice == "Use Example Data":
    ss["data"] = pd.read_csv("./data/example.csv", index_col=0)


else:
    uploaded_file = st.file_uploader(
        "Upload a CSV file with addresses and time windows",
        type=["csv"],
        on_change=setup.reset,
    )

    if uploaded_file:
        ss["data"] = pd.read_csv(uploaded_file, index_col=0)

if ss["data"] is not None:
    if not ss["geocodes_checked"]:
        # check if all geocodes existent
        for i, row in ss["data"].iterrows():
            if pd.isna(row["Lat"]) or pd.isna(row["Lat"]):
                st.write(
                    f"Finding missing geocode for address {row['Address']}..."
                )
                geocode = geocode_address(row["Address"])
                ss["data"].at[i, "Lat"] = geocode[0][0]
                ss["data"].at[i, "Lon"] = geocode[0][1]
        st.write("All addresses geocoded.")
        ss["geocodes_checked"] = True
    with st.expander("Check Data"):
        st.data_editor(
            ss["data"],
            column_config={
                column_date: st.column_config.CheckboxColumn()
                for column_date in ss["data"].columns[7:]
            },
            hide_index=False,
        )
    with st.expander("See Geocodes on Map"):
        geocodes = ss["data"][["Lat", "Lon"]].values.tolist()
        m = folium.Map(location=geocodes[0], zoom_start=6)
        for i, geo in enumerate(geocodes):
            folium.Marker(geo, popup=ss["data"].iloc[i]["Address"]).add_to(m)

        # call to render Folium map in Streamlit
        st_data = st_folium(m, width=725)
    clicked = st.button("Generate schedule")
    if clicked:
        solve()
