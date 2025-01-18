import streamlit as st

ss = st.session_state


def reset():
    ss["data"] = None
    ss["geocodes_checked"] = False
    ss["solve"] = False
    ss["parameters"] = {}
    ss["parameters_set"] = False


def setup_LOL():
    if "data" not in ss:
        ss["data"] = None
    if "geocodes_checked" not in ss:
        ss["geocodes_checked"] = False
    if "solve" not in ss:
        ss["solve"] = False
    if "parameters" not in ss:
        ss["parameters"] = {}
    if "parameters_set" not in ss:
        ss["parameters_set"] = False
