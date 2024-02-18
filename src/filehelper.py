'''
Author: ian vidmar

Description:
    File management helper
'''

# Default modules
import os

def rename_file(path):
    '''Checks if the provided file exists, if it does, add an incremental number to the new file, so the original dont gets replaced.'''
    if not os.path.exists(path):
        # If the file doesn't exist, no need to change the filename
        return path
    else:
        # If the file already exists, find a new filename
        base_name, extension = os.path.splitext(path)
        counter = 1
        while True:
            new_filename = f"{base_name}_{str(counter)}{extension}"
            if not os.path.exists(new_filename):
                # Found a filename that doesn't exist yet
                return new_filename
            else:
                counter += 1