#########################################################################
# Project : Streamlit App for Orthopaedic Research Registry Prototyping
# Author  : Dr. Easwar T.R
# Date    : 26-06-2021
# License : Apache License
# File    : Main Switchboard file to orchestrate the component
#########################################################################


import streamlit as st

# Internal Imports
from session_state import _get_state
from registry_models import REGISTRY_DF
from clubfoot_models import CLUBFOOT_REG_DF
from clubfoot import (process_col1,
                      process_col2,
                      process_col3)


# Constant to check Registration of patient
REGISTRATION_STATUS = False


# Subtitle and Description of Project
st.title("Paediatric Orthopaedic Research Registry")


# Set State
state = _get_state()

# Sidebar Choice
state.registry_choice = st.sidebar.selectbox(
    "Which Registry do you want to test ?",
    REGISTRY_DF['Registry Name'])

st.sidebar.write(REGISTRY_DF)

if state.registry_choice in ['Cerebral Palsy - Hip Surveillance', 'DDH']:
    st.write("You Selected", state.registry_choice)
    st.write("This is yet to be implemented")

else:
    st.write("You Selected : ", state.registry_choice)

    state.progress = 'registration'
    state.REGISTRATION_STATUS = REGISTRATION_STATUS

    state.CHOSEN_REG_TABLE = st.table(CLUBFOOT_REG_DF)
    st.write()

    # Layout Columns
    col1, col2, col3 = st.beta_columns(3)

    with col1:
        process_col1(state)
    with col2:
        process_col2(state)
    with col3:
        process_col3(state)
