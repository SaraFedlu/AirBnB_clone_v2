#!/usr/bin/python3

from fabric.api import local
from datetime import datetime
import os


def do_pack():
    """
    Generates a .tgz archive from the contents of the web_static folder.

    The archive will be stored in a folder named 'versions', which will be
    created if it does not exist. The name of the archive will include the
    current timestamp in the format web_static_<year><month><day><hour>\
    <minute><second>.tgz.

    Returns:
        str: The path to the created archive if successful, otherwise None.
    """
    # Create the versions directory if it doesn't exist
    if not os.path.exists("versions"):
        os.makedirs("versions")

    # Generate the archive name with the current date and time
    now = datetime.now()
    archive_name = "versions/web_static_{}.tgz".format(now.strftime(
        "%Y%m%d%H%M%S"))

    # Create the archive from the web_static folder
    result = local("tar -czvf {} web_static".format(archive_name))

    # Check if the archive was created successfully and return the path or None
    if result.succeeded:
        return archive_name
    else:
        return None
