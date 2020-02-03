def check_dict(dictionary, key, default_data):
    """Checks a dictionary for key existance. If it does not exist, it creates default data, otherwise, it uses existing data"""
    if key not in dictionary:
        dictionary[key] = default_data
    
    return dictionary[key]

def format_permission(permission: str, title: bool):
    """Formats a permission string by removing underscores and optionally in title format"""
    newPermission = permission.replace("_", " ")
    if (title): newPermission = newPermission.title()
    return newPermission