#########################################################################
# Project : Clubfoot Registry Streamlit
# Author  : Dr. Easwar T.R
# Date    : 26-06-2021
# License : Apache2.0 License
#########################################################################

from datetime import datetime
import pandas as pd
import streamlit as st


from clubfoot_models import CLUBFOOT_REG_DF
from registration_pickle_manager import (check_patient_id_conflict,
                                         fetch_next_id,
                                         append_patient_ids)


# Constants
REGISTRATION_STATUS = False


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
                st.subheader("Registration Complete")
                st.write("You have registered: ",
                         number_input, " on: ", date_of_reg)
                st.write("Side: ", side)
                st.write("Type: ", type_of_clubfoot)
                st.write("Additional Notes: ", notes)

                REGISTRATION_STATUS = True
                state.progress = 'visit'
                state.REGISTRATION_STATUS = REGISTRATION_STATUS

                reg_data = {"ID": [str(number_input)],
                            "Side": [side],
                            "Type": [type_of_clubfoot],
                            "Notes": [notes]
                            }

                if (CLUBFOOT_REG_DF['ID'].empty):
                    index_to_insert = 0
                    print("Initialized DataFrame Index...")
                else:
                    print("Incrementing DataFrame Index..")
                    index_to_insert = int(CLUBFOOT_REG_DF['ID'].iloc[-1])+1
                    print(index_to_insert)

                clubfoot_update = pd.DataFrame(
                    [[number_input, side, type_of_clubfoot, notes]],
                    columns=list(reg_data.keys()),
                    index=[index_to_insert]
                )
                CLUBFOOT_REG_DF.append(clubfoot_update)
                state.CHOSEN_REG_TABLE.add_rows(clubfoot_update)

            else:
                state.progress = 'registration'
                state.REGISTRATION_STATUS = False
                REGISTRATION_STATUS = False


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
        "Registration Status:\nPatient Registered")if state.REGISTRATION_STATUS else st.error("Registration Status:\nPatient Not Registered")
    st.header("Instructions & Updates")
    st.info("Registry Choice:\n" +
            state.registry_choice.title())
    st.info("State of Data Entry :\n" + state.progress.capitalize())
    _status()

