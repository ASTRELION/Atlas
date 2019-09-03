def check_dict(dictionary, key, default_data):
    """Checks a dictionary for key existance. If it does not exist, it creates default data, otherwise, it uses existing data"""
    if key not in dictionary:
        dictionary[key] = default_data
    
    return dictionary[key]