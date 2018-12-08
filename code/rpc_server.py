import os
import sys
from pathlib import Path
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from config import name_server_url


def path_check(path):
    print(str(root_dir))
    print(str(root_dir / path))



def get_filenames(user_id, cloud_dir_path):
    """
        user_id,
        cloud_dir_path: directory to list

        returns filename array with create and update dates
    """
    # TODO Add timestamps
    names = []
    for x in os.listdir('.' + os.sep + str(user_id) + os.sep + cloud_dir_path):
        names.append(x)
    return names


def delete_file(user_id, cloud_file_path):
    """
        user_id,
        cloud_file_path: path of the file to delete

        returns success/error code
        erases file from this server and its backup server
    """
    pass


def upload_file(user_id, file_bin, cloud_dir_path):
    """
        user_id,
        file_bin: binary file pulled from the network (encrypted)
        cloud_dir_path: directory to upload into

        returns success/error code
        uploads file to this server and its backup server
    """
    pass


def fetch_file(user_id, cloud_file_path):
    """
        user_id,
        cloud_file_path: path of the file to fetch

        returns (success/error flag, file binary (encrypted))
        checks if the file is intact by contacting backup server
        if file broken revert from backup
        if backup broken revert from file
        if both broken return (error, None)
    """
    pass


if __name__ == '__main__':
    root_dir = Path.home()

    if len(sys.argv) != 3:
        print('Wrong number of arguments.')
    else:
        try:
            server_id = int(sys.argv[1])
            server_port = int(sys.argv[2])

            with SimpleXMLRPCServer(('localhost', server_port)) as server:
                server.register_function(get_filenames)
                server.register_function(delete_file)
                server.register_function(upload_file)
                server.register_function(fetch_file)

                server_registered = False
                with ServerProxy(name_server_url, allow_none=True) as proxy:
                    server_registered = proxy.register_file_server(server_id, server.server_address)

                if server_registered:
                    root_dir = root_dir / 'rpc_server_files' / str(server_id)
                    if not root_dir.exists():
                        root_dir.mkdir(parents=True)

                    print('Serving file server on {}.'.format(server.server_address))
                    server.serve_forever()
        except ValueError:
            print('One or more of the arguments are invalid.')
