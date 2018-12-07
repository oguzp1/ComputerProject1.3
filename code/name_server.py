import sqlite3


def init_user_table(db_cursor):
    db_cursor.execute(
        '''CREATE TABLE IF NOT EXISTS USERS (
            USERID INTEGER PRIMARY KEY, 
            USERNAME TEXT UNIQUE NOT NULL, 
            PASSWORD TEXT NOT NULL, 
            SALT TEXT NOT NULL
          );'''
    )


def init_server_table(db_cursor):
    db_cursor.execute(
        '''CREATE TABLE IF NOT EXISTS SERVERS (
            SERVERID INTEGER PRIMARY KEY, 
            ADDRESS TEXT NOT NULL, 
            ONLINE INTEGER DEFAULT 0 CHECK (ONLINE IN (0, 1))
          );'''
    )


def init_file_table(db_cursor):
    db_cursor.execute(
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


def init_db(db_cursor):
    db_cursor.execute("SELECT name FROM sqlite_master WHERE TYPE = 'table';")
    table_names = db_cursor.fetchall()

    if len(table_names) == 0:
        init_user_table(cursor)
        init_server_table(cursor)
        init_file_table(cursor)


if __name__ == '__main__':
    connection = sqlite3.connect('info.db')
    cursor = connection.cursor()

    init_db(cursor)

    connection.close()
