from xmlrpc.client import ServerProxy
import base64
import bcrypt
from config import name_server_url
import argparse


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
            return App(user_id)
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


class App(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def main_loop(self):
        list_file_names(self.user_id, '')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='Client run mode. Either "signup" or "login".', type=str)
    parser.add_argument('username', help='Username of the user.', type=str)
    parser.add_argument('password', help='Password of the user.', type=str)
    args = parser.parse_args()

    proxy = ServerProxy(name_server_url, allow_none=True)

    if args.mode == 'signup':
        sign_up(args.username, args.password)
        proxy.close()
    elif args.mode == 'login':
        app = login(args.username, args.password)

        if app is not None:
            app.main_loop()

        proxy.close()
    else:
        print('Invalid operation.')
        proxy.close()
