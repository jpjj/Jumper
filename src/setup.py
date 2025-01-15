import streamlit as st

ss = st.session_state


def reset():
    ss["data"] = None
    ss["geocodes_checked"] = False


def setup_LOL():
    if "data" not in ss:
        ss["data"] = None
    if "geocodes_checked" not in ss:
        ss["geocodes_checked"] = False
