from xmlrpc.client import ServerProxy
import base64
import bcrypt
import hashlib

name_server_info = ('localhost', 9999)
name_server_url = 'http://{}:{}'.format(name_server_info[0], name_server_info[1])


def sign_up(username, password):
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(base64.b64encode(hashlib.sha256(bytes(password, 'utf-8')).digest()), salt)
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
        hash_password = results

        if bcrypt.checkpw(str(base64.b64encode(bytes(password, 'utf-8')), 'utf-8'), hash_password):
            print('Logged in as {}.'.format(username))
        else:
            print('Wrong password.')


if __name__ == '__main__':
    proxy = ServerProxy(name_server_url)
    # sign_up('oguzpaksoy', 'abcabcabc')
    login('oguzpaksoy', 'abcabcabc')
