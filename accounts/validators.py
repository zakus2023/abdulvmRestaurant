from django.core.exceptions import ValidationError
import os


# # this will handle file selection validation
# def allow_only_images_validator(value):
#     #get the extension of the file
#     ext = os.path.splitext(value.name)[1]
#     print(ext)

#     #this are the allowed extensions
#     valid_extensions = ['.png', '.jpg', '.jpeg']

#     #change the PNG or JPEG or JPG to lowercase if not in lowercase and check if not in allowed exts
#     if not ext.lower() in valid_extensions:
#         # raise the error below
#         raise ValidationError('Unsupported field extensions. Upload only: ' +str(valid_extensions))



def allow_only_images_validator(value):
    # Get the extension of the uploaded file
    ext = os.path.splitext(value.name)[1]  # Returns a tuple, [1] gives the extension part
    print(ext)  # For debugging purposes

    # List of allowed extensions
    valid_extensions = ['.png', '.jpg', '.jpeg']

    # Convert extension to lowercase and check if it's in the list of valid extensions
    if ext.lower() not in valid_extensions:
        # Raise a ValidationError with a custom error message
        raise ValidationError(f'Unsupported file extension. Upload only: {valid_extensions}')

    