

# Number Name validator for input parameters
# Throws a ValueError if the provided value is null, not a number, or less than 1
#
# @param number - number to validate
# @param field - the name of the field for validation error message
#
# @return the provided number name if it is valid
def validate(number, field):
    if number is None:
        raise ValueError(f'{field}: a value must be provided')
    elif not is_number(number):
        raise ValueError(f'{field}: "{number}" is not numeric')
    elif int(number) < 1:
        raise ValueError(f'{field}: "{number}" must be greater than 0')
    else:
        return int(number)


def is_number(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
