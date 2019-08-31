import pickle
import os.path
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from django.contrib.staticfiles import finders
import data_display.utils.constants as constants
from data_display.utils.string_display import get_strings_from_cache
from fuzzywuzzy import fuzz

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

# CREDENTIALS LOCATION
CREDENTIALS_PATH = finders.find('credentials.json')


def choose_import_type(import_type):
    """
    Given an import type <string>, return the corresponding function to be executed later.

    :param import_type:
    :return: import function
    """
    return {
        constants.INDEPENDENT: independent_import,
        constants.INTERSECTION: intersection_import,
        constants.UNION: union_import,
        constants.MAP: map_import
    }[import_type]


def independent_import():
    pass


def intersection_import(new_data, existing_model, app_context):
    """
    Performs an intersection import as defined in the README, but does not save the data.

    :param new_data: the data that is coming in from Google Sheets
    :param existing_model: the existing table in our database
    :param app_context:
    :return: returns the new data, appended to the old data in the existing table.
    """
    # Get the last n entries from our old table (to be first half of diff view)
    last_n = existing_model.objects.all().order_by('-id').values_list()[:50]

    # Get the headers of both sets of data
    existing_model_headers = get_strings_from_cache(existing_model._meta.get_fields(), app_context)

    list_len = len(new_data[0])
    indices_to_include = set()
    headers_to_include = []
    headers_already_included = set()

    for i in range(list_len):
        # list isn't sorted, best we can do is O(n^2)
        for old_header in existing_model_headers:
            # append '-' to the header to designate deletion on the UI if headers don't match fuzzy ratio
            # for more information on fuzzywuzzy see:
            # https://stackoverflow.com/questions/10383044/fuzzy-string-comparison

            # TODO: mess around with this weighted average for better performance
            # For reference: ratio is an exact match (length considered), while partial_ratio matches substrings.
            match_weighted_avg = (fuzz.ratio(new_data[0][i], old_header)
                                  + fuzz.partial_ratio(new_data[0][i], old_header))/2

            if match_weighted_avg > 60 and old_header not in headers_already_included:
                indices_to_include.add(i)
                headers_to_include.append(old_header)
                headers_already_included.add(old_header)

    # Fix the new data so we only get columns close to the existing table
    new_data = copy_without_columns(new_data, indices_to_include)

    # Return the new data (show the end of the old data and the part of the new inserted data)
    return new_data[1:], headers_to_include, last_n, existing_model_headers


def copy_without_columns(arr, indices_set):
    """
    Copies the given data without the columns in the set of provided indices

    :param arr: the data
    :param indices_set: the indices to ignore
    :return: the filtered data
    """
    new_table = []

    for i in range(1, len(arr)):
        new_row = []
        for j in range(len(arr[i])):
            if j in indices_set:
                new_row.append(arr[i][j])
        new_table.append(new_row)

    return new_table


def union_import():
    pass


def map_import():
    pass


def get_data_from(url):
    """
    Gives unstructured data from Google Sheets

    :param url: the url of the Sheet
    :return: unstructured data
    """

    gsheet_id = validate_url(_get_id_from_url(url))
    creds = validate_login()

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    sheet_metadata = service.spreadsheets().get(spreadsheetId=gsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    title = sheets[0].get("properties", {}).get("title", "Sheet1")

    # Note that 'title' only returns the non-indexed version of the form. Google forms will often
    # append indices to sheet names because it's automated, so adding the 1 works here.
    # TODO: WARNING: THIS COULD BE A BUG IN THE FUTURE IF WE EXTEND FUNCTIONALITY TO ALLOW CUSTOM SHEETS
    result = sheet.values().get(spreadsheetId=gsheet_id,
                                range=title).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        return values


def validate_url(id_match):
    """
    Checks the given url against a templated ID

    :param id_match:
    :return: id
    """
    if not id_match:
        raise KeyError('Not a google sheet url!')
    else:
        return id_match.group(0)


# some copy pasta from google sheets API
def validate_login():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def _get_id_from_url(url):
    return re.search('[-\w]{25,}', url)


def append_records_to_existing_table(table, data, headers, app_context):
    column_headers = get_strings_from_cache(headers, app_context)
    for row_data in data:
        data_as_dict = dict(zip(column_headers, row_data))

        # build a new object for the model
        t = table(**data_as_dict)
        t.save()


# Test script copied from quick start
def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))


if __name__ == '__main__':
    main()