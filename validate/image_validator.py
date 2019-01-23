

# Image Name validator for input parameters
# Throws a ValueError if the provided value is null, empty, or not a string
#
# @param image_file_name - file name to validate
#
# @return the provided image file name if it is valid
def validate(image_file_name):
    if image_file_name is None or len(image_file_name) == 0:
        raise ValueError("No image file name provided")
    elif not isinstance(image_file_name, str):
        raise ValueError("Image file name is not a string")
    else:
        return str(image_file_name)
