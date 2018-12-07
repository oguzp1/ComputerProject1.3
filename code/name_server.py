import sqlite3

if __name__ == '__main__':
    with sqlite3.connect('info.db') as conn:
        cursor = conn.cursor()
