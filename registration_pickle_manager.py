###############################################
#
# Define Pickle Actions to manage Registrations
#
#
###############################################

import os
import pickle
import time


# Pickle ID File
patient_id_pickle = 'patient_ids.pickle'


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


def append_patient_ids(patient_id, step='reg'):
    ''' Append Patient ID to Pickle file '''
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
    ''' Check if there is conflict with existing ID '''
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
    ''' Fetch the next id in the series of pickle - Ascending order '''
    print("Fetching the next ID:")
    if read_patient_ids():
        sorted_ids = read_patient_ids()
        print("Returning the Next ID:")
        print(sorted(sorted_ids)[-1]+1)
        return sorted(sorted_ids)[-1]+1
    else:
        return 1
