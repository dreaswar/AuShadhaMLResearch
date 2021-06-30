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

patient_id_pickle = 'patient_ids.pickle'

REGISTRATION_STATUS = False

# Check if the pickle file is empty
if os.path.getsize(patient_id_pickle) == 0:
    pickle_file = open(patient_id_pickle, 'wb')
    init_list = [0]
    pickle.dump(init_list, pickle_file)
    pickle_file.close()
    print("Pickle Initiated")


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


def append_patient_ids(patient_id):
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

# Forms


def add_visit_form():
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
        notes = st.text_area(label="Other Notes", value="NIL",
                             max_chars=1000, help="If additional Notes")

        add_visit_btn = st.form_submit_button(
            label="Add Visit")


# Title of the App
st.title("AuShadhaML Research")

# Subtitle and Description of Project
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


# Sidebar Choice
# np.random.seed(10)


project_options = st.sidebar.selectbox(
    "Which Project do you want to test ?",
    projects_df['Project Name'])


if project_options in ['Osteoporosis ML', 'Orthopaedic Fractures']:
    st.write("You Selected", project_options)
    st.write("This is yet to be implemented")
else:
    st.write("You Selected : ", project_options)
    st.write(registry_df)

    # Forms

    # registration_ph = st.empty()
    # reg_form = st.form(key="clubfoot_form")
    # registration_ph.subheader("Clubfoot Registration")
    # reg_form.number_input(
    #         label="Deidentified Patient No.",
    #         step=1,
    #         value=fetch_next_id(),
    #         min_value=fetch_next_id(),
    #         max_value=fetch_next_id())
    # reg_form.form_submit_button(
    #          label="Start Registering Patient")

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
                append_patient_ids(number_input)
                # st.write(read_patient_ids())
                #number_input.value += 1
                st.subheader("Registration Complete")
                st.write("You have registered: ",
                         number_input, " on: ", date_of_reg)
                st.write("Side: ", side)
                st.write("Type: ", type_of_clubfoot)
                st.write("Additional Notes: ", notes)
                REGISTRATION_STATUS = True
            else:
                REGISTRATION_STATUS = False
                st.error("Patient ID exisits !!")

visit_placeholder = st.empty()
if REGISTRATION_STATUS:
    add_visit_btn = st.button("Add Visit Infomation")

    if add_visit_btn:
        visit_form = st.form(key="visit-form")
        visit_placeholder.text("Visit Registration")
        visit_form.date_input("Date of OutPatient Visit",
                              value=datetime.today(),
                              max_value=datetime.today(),
                              min_value=datetime.today(),
                              help="OPD Visit Date")
        visit_form.selectbox("Type of Out Patient Visit",
                             ['Serial Casting',
                              'Tenotomy',
                              'Post-Tenotomy Follow Up',
                              'Other'])
        visit_form.text_area(label="Other Notes", value="NIL",
                             max_chars=1000, help="If additional Notes")
        visit_form.form_submit_button(
            label="Add Visit")
        visit_placeholder.form(visit_form)
