import os

def get_extension(filename):
    """ Get the extension of filename """
    return os.path.splitext(filename)[1]