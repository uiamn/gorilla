import sqlite3

def create_tables(db_path: str) -> None:
    """必要なテーブル群を作成する関数

    Args:
        db_path (str): データベースファイルへのパス
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE users( \
            id INTEGER PRIMARY KEY AUTOINCREMENT, \
            portal_id TEXT UNIQUE, \
            discord_id TEXT UNIQUE, \
            is_enable INT \
        )'
    )

    cur.execute(
        'CREATE TABLE results( \
            id INTEGER PRIMARY KEY AUTOINCREMENT, \
            user INTEGER, \
            comment TEXT, \
            filename TEXT UNIQUE, \
            created_at TEXT, \
            FOREIGN KEY (user) REFERENCES users(portal_id) \
        )'
    )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables('db.sqlite3')
