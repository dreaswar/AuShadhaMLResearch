#########################################################################
# Project : Clubfoot Registry Streamlit
# Author  : Dr. Easwar T.R
# Date    : 26-06-2021
# License : Apache2.0 License
#########################################################################

from datetime import datetime
import pickle
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from clubfoot_models import CLUBFOOT_REG_DF
from registration_pickle_manager import (check_patient_id_conflict,
                                         fetch_next_id,
                                         append_patient_ids)
# from global_vars import CHOSEN_REG_TABLE

# Constants
REGISTRATION_STATUS = False


####################################################################
# Forms
####################################################################


def add_registration(state):
    ''' Adding Registration '''

    def _open(): return state.progress == 'registration'

    reg_form = st.beta_expander(label="Step1: Patient Registration",
                                expanded=_open())
    reg_form.subheader("Clubfoot Registration")

    with reg_form.form(key="clubfoot_form"):
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

                st.success("**Registration Complete**")
                st.write("**You have registered: **",
                         number_input, " on: ", date_of_reg)
                st.info(
                    "Please see the 'Clubfoot Data' table at the top for data stored")

                # if data submitted properly change the state
                REGISTRATION_STATUS = True
                state.progress = 'visit'
                state.REGISTRATION_STATUS = REGISTRATION_STATUS

                # Collect the Form data as per Model Structure
                reg_data = {
                    "ID": int(number_input),
                    "Side": side,
                    "Type": type_of_clubfoot,
                    "Notes": notes
                }

                # Prepare data for pandas frame
                pkl_data = [int(number_input), side, type_of_clubfoot, notes]

                # Initiate an empty list to hold all data to pass to pandas frame
                all_data = []
                print(reg_data)

                # Check if the initial file size is 0 and if so initiate an empty pickle and close
                if os.path.getsize('registration.pickle') == 0:
                    pickle_file = open('registration.pickle', 'wb')
                    init_list = []
                    pickle.dump(init_list, pickle_file)
                    pickle_file.close()
                    print("Pickle Initiated")

                # Start reading from pickle file to aggregaate the data and append new data
                reg_pkl = open("registration.pickle", 'rb')
                with reg_pkl as _f:
                    try:
                        old_data = pickle.load(_f)
                        all_data.append(pkl_data)
                        for _l in old_data:
                            if len(_l) > 0:
                                all_data.append(_l)
                    except Exception as e:
                        print(e)
                        st.exception(e)
                reg_pkl.close()

                # Start a new pickle with write permission for writing all the data back
                reg_pkl = open("registration.pickle", 'wb')
                with reg_pkl as _f:
                    try:
                        pickle.dump(all_data, reg_pkl)
                        print(" Registration Stored ")
                        st.balloons()
                    except Exception as e:
                        print(e)
                        st.exception(e)
                reg_pkl.close()

                # Pass the data to the pandas fram / table for display
                _process_and_update(reg_data, state)

            else:
                state.progress = 'registration'
                state.REGISTRATION_STATUS = False
                REGISTRATION_STATUS = False
                st.error(
                    "Error Submittting the form. Please retry or contact administrator")


def add_visit_form(state):
    ''' Adding a Visit '''

    print("Displaying the Visit Addition Form")
    def _open(): return state.progress == 'visit'
    visit_form = st.beta_expander(
        label="Step:2 OPD Visit Form", expanded=_open())
    visit_form.subheader("Visit Registration")
    with visit_form.form(key="visit-form"):

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
            visit_pd = pd.DataFrame([date_of_visit,
                                     type_of_visit,
                                     pirani_scoring,
                                     notes],
                                    columns=['Date', 'Type', 'Pirani', 'Notes']
                                    )
            st.write(visit_pd)

        else:
            state.progress = 'visit'
            state.REGISTRATION_STATUS = True
            REGISTRATION_STATUS = True


#########Process Layout ################


def process_col1(state):
    ''' Process the First Column of Layout '''
    if (state.progress == 'registration' and state.REGISTRATION_STATUS == False):
        add_registration(state)
    elif(state.progress == 'visit' and state.REGISTRATION_STATUS == True):
        st.text("Add Visit Details  ->")
    else:
        st.error("Something is wrong here !. Please contact Developer")


def process_col2(state):
    ''' Process the Second column of the layout '''
    if(state.progress == 'visit' and state.REGISTRATION_STATUS == True):
        add_visit_form(state)
    elif(state.progress == 'registration' and state.REGISTRATION_STATUS == False):
        st.info("\u2190"+" Add a Patient First")
    else:
        st.error("Something is wrong here !. Please contact Developer")


def process_col3(state):
    ''' Process the Third Column of the Layout '''
    def _status(): return st.success(
        "Registration Status:\nPatient Registered")if state.REGISTRATION_STATUS else st.error("Registration Status:\nPatient awaiting Registration")
    st.header("Instructions & Updates")
    st.info("Registry Choice:\n" +
            state.registry_choice.title())
    st.info("Stage of Data Entry :\n" + state.progress.capitalize())
    _status()


def _process_and_update(reg_data, state):
    ''' Update Data Frame and Table after Data Submission'''

    # global CHOSEN_REG_TABLE
    if (CLUBFOOT_REG_DF.empty and not state.index_to_insert):
        state.index_to_insert = 0
        print("Initialized DataFrame Index...")
    else:
        print("Incrementing DataFrame Index..")
        state.index_to_insert = state.index_to_insert+1

    print("Index: ", state.index_to_insert)

    reg_pkl = open('registration.pickle', 'rb')
    with reg_pkl as _f:
        reg_table_data = pickle.load(_f)
    reg_pkl.close()
    print(reg_table_data)
    clubfoot_update = pd.DataFrame(reg_table_data,
                                   columns=list(reg_data.keys())
                                   )

    CLUBFOOT_REG_DF.append(clubfoot_update, ignore_index=True)
    if (type(state.CHOSEN_REG_TABLE) == bool):
        state.CHOSEN_REG_TABLE = st.table(clubfoot_update)
    else:
        state.CHOSEN_REG_TABLE.add_rows(clubfoot_update)
