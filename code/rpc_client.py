from xmlrpc.client import ServerProxy
import base64
import bcrypt
import hashlib

name_server_info = ('localhost', 9999)
name_server_url = 'http://{}:{}'.format(name_server_info[0], name_server_info[1])


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

            app = App(user_id)
            app.main_loop()
        else:
            print('Wrong password.')


class App(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def main_loop(self):
        pass


if __name__ == '__main__':
    proxy = ServerProxy(name_server_url, allow_none=True)
    # sign_up('oguzpaksoy', 'abcabcabc')
    login('oguzpaksoy', 'abcabcabc')
