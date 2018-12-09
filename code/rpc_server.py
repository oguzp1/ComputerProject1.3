import os
import sys
from pathlib import Path
import hashlib
import argparse
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from config import name_server_url


def get_owner_and_backup_info(rel_path_obj):
    folder = rel_path_obj.parts[0]

    try:
        if folder.endswith('_backup'):
            return int(folder.replace('_backup', '')), 1
        else:
            return int(folder), 0
    except ValueError:
        return -1, 0


def hash_file(file_path_for_hash):
    hash_obj = hashlib.sha256()

    with open(file_path_for_hash, 'rb') as rbFile:
        while True:
            block = rbFile.read(65536)

            if not block:
                break

            hash_obj.update(block)

    return hash_obj.hexdigest()


def path_check(user_id, path):
    base_dir = root_dir / str(user_id)
    path_obj = (base_dir / path).resolve()
    path_exists = path_obj.exists()
    path_str = str(path_obj)
    path_valid = path_str.startswith(str(base_dir))
    rel_path_str = path_str.replace(str(base_dir), '')
    rel_path_str = rel_path_str[1:] if rel_path_str.startswith(os.sep) else rel_path_str
    return path_valid, path_exists, rel_path_str


def get_relative_path(user_id, cloud_path_str):
    return str(Path(cloud_path_str).resolve().relative_to(root_dir / str(user_id)))


def get_filenames(user_id, cloud_dir_path):
    """
        user_id,
        cloud_dir_path: directory to list

        returns array where each elements is a tuple of (is_dir, child_rel_path)
    """
    base_dir = root_dir / str(user_id)
    path_valid, path_exists, rel_path_str = path_check(user_id, cloud_dir_path)

    cd_paths = []

    if path_valid and path_exists:
        for child in (base_dir / rel_path_str).iterdir():
            cd_paths.append((child.is_dir(), str(child.relative_to(root_dir / str(user_id)))))

    return cd_paths


def delete_file(user_id, cloud_file_path):
    """
        user_id,
        cloud_file_path: path of the file to delete

        returns success/error code
        erases file from this server and its backup server
    """

    path_valid, path_exists, rel_path_str = path_check(user_id, cloud_file_path)

    if not path_valid:
        return None

    #with ServerProxy(name_server_url, allow_none=True) as proxy:
        # there will be a name_server function for checking backup

    filename = os.path.basename(cloud_file_path)  # extract the filename from path

    filename_backup = filename + str("_") + str(user_id)

    if os.path.exists(filename):
        os.remove(filename)

    if os.path.exists(filename_backup):
        os.remove(filename_backup)

    return True


def upload_file(user_id, file_bin, cloud_dir_path, filename):
    """
        user_id,
        file_bin: binary file pulled from the network (encrypted)
        cloud_dir_path: directory to upload into

        returns success/error code
        uploads file to this server and its backup server
    """

    path_valid, path_exists, rel_path_str = path_check(user_id, cloud_dir_path)

    if not path_valid:
        return None

    #  decrypt the file bin
    #  ...........................

    with open(os.join(cloud_dir_path, filename), "wb") as handle:
        handle.write(file_bin.data)

    backup_dir = os.join(cloud_dir_path, (filename + "_" + str(user_id)))

    #with ServerProxy(name_server_url, allow_none=True) as proxy:
        # there will be a name_server function for checking backup

    with open(backup_dir, "wb") as handle:
        handle.write(file_bin.data)

    return True


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

    hash_code = hash_file(cloud_file_path)

    #  with ServerProxy(name_server_url, allow_none=True) as proxy:
        #  there will be a function return hash string from name server

    #  if(hash_code != server_hash_code):  # the file is corrupted, go to the back up
        # with ServerProxy(name_server_url, allow_none=True) as proxy:
        # there will be a function return hash string from backup

        #if(hash_code != backup_hash_code):  # the backup is also correupted
        #    print("Sorry, the file is dead")

    #  else:  # take the file from server
        #  decrpyt the file
        #  return the file

    pass


if __name__ == '__main__':
    root_dir = Path.home() / 'rpc_server_files'

    parser = argparse.ArgumentParser()
    parser.add_argument('server_id', help='ID of the file server.', type=int)
    parser.add_argument('port', help='Port of the file server.', type=int)
    args = parser.parse_args()

    with SimpleXMLRPCServer(('localhost', args.port)) as server:
        server.register_function(path_check)
        server.register_function(get_filenames)
        server.register_function(delete_file)
        server.register_function(upload_file)
        server.register_function(fetch_file)

        server_url = 'http://{}:{}'.format(server.server_address[0], server.server_address[1])

        server_registered = False
        with ServerProxy(name_server_url, allow_none=True) as proxy:
            server_registered = proxy.register_file_server(args.server_id, server_url)

        if server_registered:
            root_dir = root_dir / str(args.server_id)
            if not root_dir.exists():
                root_dir.mkdir(parents=True)

            print('Initializing server for files in "{}"...'.format(str(root_dir)))

            file_list = []
            for root, dirs, files in os.walk(str(root_dir)):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    file_last_modified = os.path.getmtime(file_path)
                    file_hash = hash_file(file_path)
                    file_path_rel = Path(file_path).relative_to(root_dir)
                    whose, is_backup = get_owner_and_backup_info(file_path_rel)
                    file_path_str = str(file_path_rel.relative_to(file_path_rel.parts[0]))

                    file_info = (whose, args.server_id, file_path_str, file_name,
                                 is_backup, file_hash, file_last_modified)

                    if whose != -1:
                        print('Added file:', file_info)
                        file_list.append(file_info)

            files_registered = False
            with ServerProxy(name_server_url, allow_none=True) as proxy:
                files_registered = proxy.save_file_info(file_list)

            if files_registered:
                print('Serving file server on {}.'.format(server.server_address))
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    with ServerProxy(name_server_url, allow_none=True) as proxy:
                        proxy.unregister_file_server(args.server_id)
            else:
                print('Failed file registration.')
        else:
            print('Failed server registration.')
