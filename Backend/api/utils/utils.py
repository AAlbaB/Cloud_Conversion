import re

def validate_password(password):
    if 8 <= len(password) <= 24:
        if re.search('[a-z]', password) and re.search('[A-Z]', password):
            if re.search('[0-9]', password):
                return True
    
    return False