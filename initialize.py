import sqlite3

def create_tables(db_path: str) -> None:
    """必要なテーブル群を作成する関数

    Args:
        db_path (str): データベースファイルへのパス
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE tweets( \
            id INTEGER PRIMARY KEY AUTOINCREMENT, \
            tweet TEXT, \
            filename TEXT UNIQUE, \
            created_at TEXT \
        )'
    )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    with open('LATEST_TWEET_ID.txt', 'w') as f:
        f.write('0')
    create_tables('db.sqlite3')
