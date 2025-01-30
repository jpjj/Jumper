# add to requirements.txt
# traveling_rustling==0.1.1

import streamlit as st
import pandas as pd
from src.display_input import display_input
from src.display_solution import display_solution
from src.solve import get_location_list, solve
from src.geocode import add_geocodes
from src import setup
from src.working_hours_selection_dialog import working_hours_selection_dialog
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
    if ss["data"] is None:
        ss["data"] = pd.read_csv("./data/example.csv", index_col=0)


else:
    uploaded_file = st.file_uploader(
        "Upload a CSV file with addresses and time windows",
        type=["csv"],
        on_change=setup.reset,
    )

    if uploaded_file and ss["data"] is None:
        ss["data"] = pd.read_csv(uploaded_file, index_col=0)

if ss["data"] is not None:
    if not ss["geocodes_checked"]:
        # check if all geocodes existent
        add_geocodes(ss["data"])
        st.write("All addresses geocoded.")
        ss["location_list"] = get_location_list(ss["data"])
        ss["geocodes_checked"] = True
    display_input()

    st.button("Set Parameters", on_click=working_hours_selection_dialog)

    clicked = st.button("Generate schedule", disabled=not ss["parameters_set"])
    if clicked:
        ss["location_list"] = get_location_list(ss["data_edited"])
        ss["solution"], ss["downloadable_solution"] = solve(
            ss["location_list"], parameters=ss["parameters"]
        )

        ss["solve"] = True
if ss["solve"]:
    display_solution()
