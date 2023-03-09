def clean(uncleaned_dict) -> dict:
    cleaned_dict = {}
    for key, value in uncleaned_dict.items():
        key = key.strip().replace('"', '').replace(' ', '_').replace('/', '_').replace('#', 'no').lower()
        if type(value) is str:
            value = value.strip()
        cleaned_dict[key] = value
    return cleaned_dict
