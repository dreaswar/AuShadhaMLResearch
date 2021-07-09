#########################################################################
# Project : Clubfoot Registry Streamlit
# Author  : Dr. Easwar T.R
# Date    : 26-06-2021
# License : MIT License
#########################################################################

import os
import pickle
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime


# Importing to create a Session State
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from streamlit.hashing import _CodeHasher


patient_id_pickle = 'patient_ids.pickle'
REGISTRATION_STATUS = False


# Check if the pickle file is empty
if os.path.getsize(patient_id_pickle) == 0:
    pickle_file = open(patient_id_pickle, 'wb')
    init_list = [0]
    pickle.dump(init_list, pickle_file)
    pickle_file.close()
    print("Pickle Initiated")


##################### Session Object ################################

class _SessionState:
    ''' From :https://gist.github.com/okld/0aba4869ba6fdc8d49132e6974e2e662'''

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(
            self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


######################### Define Pickle Actions ##########################
def read_patient_ids():
    ''' Reading existing Patient IDS from pickle file '''

    try:
        print("Reading from Pickle...")
        patient_id_file = open(patient_id_pickle, 'rb')
        patient_list = pickle.load(patient_id_file)
        patient_id_file.close()
        print(patient_list)
        if len(patient_list) > 0:
            print("Printing Patient list")
            return patient_list
        print("There are no registered patients")
        return [0]
    except EOFError as err:
        print(err)


def append_patient_ids(patient_id, step='reg'):
    try:
        if check_patient_id_conflict(patient_id):
            patient_id_file = open(patient_id_pickle, 'rb')
            patient_list = pickle.load(patient_id_file)
            patient_list.append(patient_id)
            patient_id_file.close()

            patient_id_file = open(patient_id_pickle, 'wb')
            print("ID list is: ")
            print(patient_list)
            pickle.dump(patient_list, patient_id_file)
            patient_id_file.close()

            return True
        else:
            return False
    except Exception as ex:
        print(ex)


def check_patient_id_conflict(id_to_check):
    try:
        print("Checking for", id_to_check)
        stored_ids = sorted(read_patient_ids())
        print(stored_ids)
        if id_to_check in stored_ids:
            print("ID Duplication")
            return False
        print("ID is not duplicated")
        return True
    except Exception:
        return False


def fetch_next_id():
    ''' Fetch the next id'''
    print("Fetching the next ID:")
    if read_patient_ids():
        sorted_ids = read_patient_ids()
        print("Returning the Next ID:")
        print(sorted(sorted_ids)[-1]+1)
        return sorted(sorted_ids)[-1]+1
    else:
        return 1

####################################################################
# Forms
####################################################################


def add_registration(state):
    ''' Adding Registration '''

    with st.form(key="clubfoot_form"):
        st.subheader("Clubfoot Registration")
        number_input = st.number_input(
            label="Deidentified Patient No.",
            step=1,
            value=fetch_next_id(),
            min_value=fetch_next_id(),
            max_value=fetch_next_id())
        date_of_reg = st.date_input("Date of Registration",
                                    value=datetime.today(),
                                    max_value=datetime.today(),
                                    min_value=datetime.today(),
                                    help="Registration Date")
        side = st.selectbox("Unilateral / Bilateral",
                            ["R", "L", "Bilateral"])
        type_of_clubfoot = st.selectbox("Type of Clubfoot",
                                        ['Idiopathic',
                                         'Syndromic',
                                         'Neurologic/Spinal Cord Anomaly Related'])
        notes = st.text_area(label="Other Notes", value="NIL",
                             max_chars=1000, help="If additional Notes")

        submit_button = st.form_submit_button(
            label="Start Registering Patient")

        if submit_button:
            if check_patient_id_conflict(number_input):
                append_patient_ids(number_input, 'reg')
                # st.write(read_patient_ids())
                # number_input.value += 1
                st.subheader("Registration Complete")
                st.write("You have registered: ",
                         number_input, " on: ", date_of_reg)
                st.write("Side: ", side)
                st.write("Type: ", type_of_clubfoot)
                st.write("Additional Notes: ", notes)
                REGISTRATION_STATUS = True
                state.progress = 'visit'
                state.REGISTRATION_STATUS = REGISTRATION_STATUS
                # state.sync()
            else:
                state.progres = 'registration'
                state.REGISTRATION_STATUS = False
                REGISTRATION_STATUS = False
                # state.sync()


def add_visit_form(state):
    ''' Adding a Visit '''

    print("Displaying the Visit Addition Form")
    with st.form(key="visit-form"):
        st.subheader("Visit Registration")
        date_of_visit = st.date_input("Date of OutPatient Visit",
                                      value=datetime.today(),
                                      max_value=datetime.today(),
                                      min_value=datetime.today(),
                                      help="OPD Visit Date")
        type_of_visit = st.selectbox("Type of Out Patient Visit",
                                     ['Serial Casting',
                                      'Tenotomy',
                                      'Post-Tenotomy Follow Up',
                                      'Other'])
        pirani_scoring = st.number_input("Pirani Scoring",
                                         value=0,
                                         max_value=6,
                                         min_value=0,
                                         step=1,
                                         help="Input the Pirani Score for the day")

        notes = st.text_area(label="Other Notes", value="NIL",
                             max_chars=1000, help="If additional Notes")

        add_visit_btn = st.form_submit_button(
            label="Add Visit")

        if add_visit_btn:
            st.subheader("Registration Complete")
            REGISTRATION_STATUS = True
            state.progress = 'complete'
            state.REGISTRATION_STATUS = REGISTRATION_STATUS
            # state.sync()
        else:
            state.progress = 'visit'
            state.REGISTRATION_STATUS = True
            REGISTRATION_STATUS = True
            # state.sync()


def process_col1(state):
    if (state.progress == 'registration' and state.REGISTRATION_STATUS == False):
        add_registration(state)
    elif(state.progress == 'visit' and state.REGISTRATION_STATUS == True):
        add_visit_form(state)
    else:
        st.error("Something is wrong here !. Please contact Developer")


################################# App ###################################


# Subtitle and Description of Project
st.title("AuShadhaML Research")
st.write("Our Projects")

# Project listing under AuShadhaML
projects_df = pd.DataFrame({
    'Project Name': ['Orthopaedic Research Registry',
                     'Osteoporosis ML',
                     'Orthopaedic Fractures'],
    'Status': ['Early Planning',
               'Active Development',
               'Early Planning'
               ]
})

registry_df = pd.DataFrame({
    'Registry Name': ['Clubfoot',
                      'Cerebral Palsy - Hip Surveillance',
                      'DDH'],
    'Status': ['Active Development',
               'Early Planning',
               'Early Planning'
               ]
})

st.write()

# Set State
state = _get_state()

# Sidebar Choice
state.project_options = st.sidebar.selectbox(
    "Which Project do you want to test ?",
    projects_df['Project Name'])

if state.project_options in ['Osteoporosis ML', 'Orthopaedic Fractures']:
    st.write("You Selected", state.project_options)
    st.write("This is yet to be implemented")
else:
    st.write("You Selected : ", state.project_options)
    st.write(registry_df)
    state.progress = 'registration'
    state.REGISTRATION_STATUS = REGISTRATION_STATUS

    # Forms
    col1, col2, col3 = st.beta_columns(3)

    with col1:
        if (state.progress == 'registration' and state.REGISTRATION_STATUS == False):
            add_registration(state)
        elif(state.progress == 'visit' and state.REGISTRATION_STATUS == True):
            st.text("Add Visit Details  ->")
        else:
            st.error("Something is wrong here !. Please contact Developer")
    with col2:
        if(state.progress == 'visit' and state.REGISTRATION_STATUS == True):
            add_visit_form(state)
        elif(state.progress == 'registration' and state.REGISTRATION_STATUS == False):
            st.text("<- Add a Patient First")
        else:
            st.error("Something is wrong here !. Please contact Developer")

    with col3:
        st.header("Instructions & Updates")
        st.write(state.project_options)
        st.write(state.progress)
        st.write(state.REGISTRATION_STATUS)

    # state.sync()
