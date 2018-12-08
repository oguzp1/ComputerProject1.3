from xmlrpc.client import ServerProxy, Binary
import base64
import bcrypt
from config import name_server_url
import argparse
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def sign_up(username, password):
    if len(password) > 72:
        print('Password must be less than 72 characters.')
        return

    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(bytes(password, 'utf-8'), salt)
    print(salt, hash_password)

    if proxy.save_user(username, str(base64.b64encode(hash_password), 'utf-8'), str(base64.b64encode(salt), 'utf-8')):
        print('User {} created successfully.'.format(username))
    else:
        print('Could not create user {}.'.format(username))


def login(username, password):
    results = proxy.get_user_credentials(username)

    if results is None:
        print('Username does not exist.')
    else:
        user_id = int(results[0])
        hash_password = bytes(results[1], 'utf-8')

        if bcrypt.checkpw(bytes(password, 'utf-8'), hash_password):
            print('Logged in as {}.'.format(username))
            return App(user_id, username)
        else:
            print('Wrong password.')

    return None


def list_file_names(user_id, cloud_file_path):
    # FIXME
    results = proxy.get_server_addresses(user_id)

    file_list = set()

    for address in results:
        with ServerProxy(address, allow_none=True) as new_proxy:
            file_list.add(new_proxy.get_filenames(user_id, cloud_file_path))

    return file_list

def get_file_binary(local_path):
    with open(local_path, 'rb') as file:
        file_bin = Binary(file.read())
    return file_bin

def decrypt_file(username, file_bin):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=os.urandom(26),
        iterations=100000,
        backend=default_backend()
    )
    _, password =proxy.get_user_credentials(username)
    pass_as_bytes = bytes(password, 'utf-8')
    key = base64.urlsafe_b64encode(kdf.derive(pass_as_bytes))
    f = Fernet(key)
    decrypted = Binary(f.decrypt(file_bin.data))

    return decrypted

def encrypt_file(username, file_bin):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=os.urandom(26),
        iterations=100000,
        backend=default_backend()
    )
    _, password = proxy.get_user_credentials(username)
    pass_as_bytes = bytes(password, 'utf-8')
    key = base64.urlsafe_b64encode(kdf.derive(pass_as_bytes))
    f = Fernet(key)
    encrypted = f.encrypt(file_bin.data)

    return encrypted

class App(object):
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    def main_loop(self):
        list_file_names(self.user_id, '')
        print('OPTIONS\n'
              '- upload <file-path>      <cloud-path-to-upload> <filename>\n'
              '- delete <path-of-file>\n'
              '- fetch  <path-on-cloud>  <local-path-to-save>\n'
              '- exit')

        while True:
            command = str(input('$ ')).split(' ')

            if command[0] == 'upload' and len(command) == 4:
                local_file_path = command[1]
                cloud_file_path = command[2]
                filename = command[3]
                file_bin = encrypt_file(self.username, get_file_binary(local_file_path))
                proxy.upload_file(file_bin, cloud_file_path, filename)

            elif command[0] == 'delete' and len(command) == 2:
                cloud_file_path = command[1]
                proxy.delete_file(self.user_id, cloud_file_path)

            elif command[0] == 'fetch' and len(command) == 3:
                cloud_file_path = command[1]
                local_path_to_save = command[2]
                flag, file_bin = proxy.fetch_file(self.user_id, cloud_file_path)
                path, filename = os.path.split(cloud_file_path)

                if flag:
                    with open(local_path_to_save + filename, "wb") as handle:
                        decrypted = decrypt_file(self.username, file_bin)
                        try:
                            handle.write(decrypted)
                            print('Saved ' + filename + 'to ' + local_path_to_save)
                        except os.error:
                            print('Could not save ' + filename)
            elif command[0] == 'exit':
                break
            else:
               print('INVALID COMMAND')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='Client run mode. Either "signup" or "login".', type=str)
    parser.add_argument('username', help='Username of the user.', type=str)
    parser.add_argument('password', help='Password of the user.', type=str)
    args = parser.parse_args()

    proxy = ServerProxy(name_server_url, allow_none=True)

    if args.mode == 'signup':
        sign_up(args.username, args.password)
    elif args.mode == 'login':
        app = login(args.username, args.password)

        if app is not None:
            app.main_loop()
    else:
        print('Invalid operation.')