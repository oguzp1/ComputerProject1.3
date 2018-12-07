import os
from xmlrpc.server import SimpleXMLRPCServer
import socketserver

name_server_info = ('localhost', 9999)

def get_filenames(userid, cloud_dir_path):
    '''
        userid,
        cloud_dir_path: direcory to list

        returns filename array with create and update dates
    '''
    # TODO Add timestamps
    names = []
    for x in os.listdir('.' + os.sep + str(userid) + os.sep + cloud_dir_path):
        names.append(x)
    return names

def delete_file(userid, cloud_file_path):
    '''
        userid,
        cloud_file_path: path of the file to delete

        returns success/error code
        erases file from this server and its backup server
    '''
    pass

def upload_file(userid, file_bin, cloud_dir_path):
    '''
        userid,
        file_bin: binary file pulled from the network (encrypted)
        cloud_dir_path: directory to upload into

        returns success/error code
        uploads file to this server and its backup server 
    '''
    pass

def fetch_file(userid, cloud_file_path):
    '''
        userid,
        cloud_file_path: path of the file to fetch

        returns (success/error flag, file binary (encrypted))
        checks if the file is intact by contacting backup server
        if file broken revert from backup
        if backup broken revert from file
        if both broken return (error, None)
    '''
    pass

if __name__ == '__main__':
    with SimpleXMLRPCServer(('localhost', 8080)) as server:
        server.register_function(get_filenames)
        server.register_function(delete_file)
        server.register_function(upload_file)
        server.register_function(fetch_file)
        server.serve_forever()




