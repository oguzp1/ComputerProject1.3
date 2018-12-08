import sqlite3
from xmlrpc.server import SimpleXMLRPCServer
import base64
from config import name_server_info


def init_user_table():
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS USERS (
            USERID INTEGER PRIMARY KEY, 
            USERNAME TEXT UNIQUE NOT NULL, 
            PASSWORD TEXT NOT NULL, 
            SALT TEXT NOT NULL
          );'''
    )


def init_server_table():
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS SERVERS (
            SERVERID INTEGER PRIMARY KEY, 
            ADDRESS TEXT NOT NULL, 
            ONLINE INTEGER DEFAULT 0 CHECK (ONLINE IN (0, 1))
          );'''
    )


def init_file_table():
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS FILES (
            FILEID INTEGER PRIMARY KEY,
            USERID INTEGER NOT NULL,
            SERVERID INTEGER NOT NULL,
            PATH TEXT NOT NULL,
            FILENAME TEXT NOT NULL,
            FILEHASH TEXT NOT NULL,
            CREATEDATE TEXT,
            UPDATEDATE TEXT,
            FOREIGN KEY (USERID) REFERENCES USERS(USERID),
            FOREIGN KEY (SERVERID) REFERENCES SERVERS(SERVERID)
          );'''
    )


def init_db():
    cursor.execute("SELECT name FROM sqlite_master WHERE TYPE = 'table';")
    table_names = cursor.fetchall()

    if len(table_names) == 0:
        init_user_table()
        init_server_table()
        init_file_table()


def save_user(username, hash_password, salt):
    try:
        before = cursor.lastrowid
        cursor.execute('INSERT INTO USERS (USERNAME, PASSWORD, SALT) VALUES (?, ?, ?);',
                       (username, str(base64.b64decode(hash_password), 'utf-8'), str(base64.b64decode(salt), 'utf-8')))
        connection.commit()
        after = cursor.lastrowid

        return before + 1 == after
    except sqlite3.Error:
        return False


def get_user_credentials(username):
    try:
        cursor.execute('SELECT USERID, PASSWORD FROM USERS WHERE USERNAME = ?;', (username, ))
        results = cursor.fetchone()

        return results
    except sqlite3.Error:
        return None


def get_server_addresses(user_id):
    try:
        cursor.execute('SELECT DISTINCT ADDRESS FROM FILES JOIN SERVERS USING (SERVERID) WHERE USERID = ?;',
                       (user_id, ))
        results = cursor.fetchall()

        return results
    except sqlite3.Error:
        return []


def register_file_server(server_id, address):
    pass


if __name__ == '__main__':
    connection = sqlite3.connect('info.db')
    cursor = connection.cursor()

    init_db()

    with SimpleXMLRPCServer(name_server_info, allow_none=True) as server:
        server.register_function(save_user)
        server.register_function(get_user_credentials)
        server.register_function(get_server_addresses)
        server.register_function(register_file_server)
        server.serve_forever()

    connection.close()
