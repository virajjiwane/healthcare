"""
This module contains all general purpose utilities.
"""


def clean(uncleaned_dict) -> dict:
    """
    This function cleans a dictionary. Removes any spaces and or special characters from the keys and makes the keys
    lower cased for uniformity.
    :param uncleaned_dict:
    :return: dictionary
    """
    cleaned_dict = {}
    for key, value in uncleaned_dict.items():
        key = key.strip().replace('"', '').replace(' ', '_').replace('/', '_').replace('#', 'no').lower()
        if type(value) is str:
            value = value.strip()
        cleaned_dict[key] = value
    return cleaned_dict
