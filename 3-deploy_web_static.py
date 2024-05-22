#!/usr/bin/python3

from fabric.api import env, put, run, local, execute
from datetime import datetime
import os

# Define the IP addresses of your web servers
env.hosts = ['100.25.104.141', '34.207.212.28']
env.user = 'ubuntu'  # Set the remote user to 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'


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

    # Check if the archive was created and return the path or None
    if result.succeeded:
        return archive_name
    else:
        return None


def do_deploy(archive_path):
    """
    Distributes an archive to web servers.

    Args:
        archive_path (str): The path to the archive to distribute.

    Returns:
        bool: True if all operations have been done correctly, otherwise False
    """
    if not os.path.exists(archive_path):
        return False

    # Get the archive filename and its basename (without extension)
    archive_filename = os.path.basename(archive_path)
    archive_basename = archive_filename.split(".")[0]

    # Define the full path on the server
    release_path = "/data/web_static/releases/{}".format(archive_basename)

    try:
        # Upload the archive to the /tmp/ directory of the web server
        put(archive_path, "/tmp/{}".format(archive_filename))

        # Create the release directory on the server
        run("mkdir -p {}".format(release_path))

        # Uncompress the archive to the release directory
        run("tar -xzvf /tmp/{} -C {}".format(archive_filename, release_path))

        # Remove the uploaded archive from the server
        run("rm /tmp/{}".format(archive_filename))

        # Move files from web_static to the release directory
        run("mv {}/web_static/* {}".format(release_path, release_path))

        # Remove the now-empty web_static directory
        run("rm -rf {}/web_static".format(release_path))

        # Delete the existing symbolic link
        run("rm -rf /data/web_static/current")

        # Create a new symbolic link
        run("ln -s {} /data/web_static/current".format(release_path))

        return True
    except Exception:
        return False


def deploy_to_server(archive_path, is_local=False):
    """
    Deploys the archive either locally or to a remote server.

    Args:
        archive_path (str): The path to the archive to distribute.
        is_local (bool): If True, deploys locally; otherwise,\
                deploys to a remote server.

    Returns:
        bool: True if all operations have been done correctly, otherwise False
    """
    if not os.path.exists(archive_path):
        return False

    # Get the archive filename and its basename (without extension)
    archive_filename = os.path.basename(archive_path)
    archive_basename = archive_filename.split(".")[0]

    # Define the full path on the server
    release_path = "/data/web_static/releases/{}".format(archive_basename)

    try:
        if is_local:
            # Local deployment steps
            local("mkdir -p {}".format(release_path))
            local("tar -xzvf {} -C {}".format(archive_path, release_path))
            local("mv {}/web_static/* {}".format(release_path, release_path))
            local("rm -rf {}/web_static".format(release_path))
            local("rm -rf /data/web_static/current")
            local("ln -s {} /data/web_static/current".format(release_path))
        else:
            # Remote deployment steps
            put(archive_path, "/tmp/{}".format(archive_filename))
            run("mkdir -p {}".format(release_path))
            run("tar -xzvf /tmp/{} -C {}".format(
                archive_filename, release_path))
            run("rm /tmp/{}".format(archive_filename))
            run("mv {}/web_static/* {}".format(release_path, release_path))
            run("rm -rf {}/web_static".format(release_path))
            run("rm -rf /data/web_static/current")
            run("ln -s {} /data/web_static/current".format(release_path))

        return True
    except Exception:
        return False


def deploy():
    """
    Creates and distributes an archive to web servers.

    Returns:
        bool: True if the deployment was successful, otherwise False.
    """
    archive_path = do_pack()
    if not archive_path:
        return False

    # Deploy locally first
    if not deploy_to_server(archive_path, is_local=True):
        return False

    # Deploy to remote servers
    return execute(deploy_to_server, archive_path, is_local=False)


if __name__ == "__main__":
    success = deploy()
    if success:
        print("Deployment successful")
    else:
        print("Deployment failed")
