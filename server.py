import flask
from flask import request
import sqlite3
from flask.json import jsonify
import requests  # urllibに置き換えたい
import re

DB_PATH = 'db.sqlite3'
app = flask.Flask(__name__, static_folder='images')

@app.route('/results', methods=['GET'])
def get_results() -> str:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        tweets = cur.execute(
            'SELECT tweet, tweet_id_str, filename, created_at FROM tweets ORDER BY created_at DESC'
        ).fetchall()

    result = [
        {'tweet': t, 'tweet_id': i, 'filename': f, 'created_at': c} for t, i, f, c in tweets
    ]

    return flask.jsonify(result)


@app.route('/')
def top_page() -> str:
    return flask.render_template('index.html')


@app.route('/register', methods=['POST'])
def register() -> str:
    data = request.json
    print(data)

    # 一応 Discord ID の形式を確認しておく
    print(re.match(r'.+#[0-9]{4}', data['discord_id']))
    if not re.match(r'.+#[0-9]{4}', data['discord_id']):
        return jsonify({
            'is_successful': False,
            'message': 'Discord ID が不正です'
        })

    portal_id = data['portal_id']
    portal_pass = data['portal_pass']
    discord_id = data['discord_id']

    # portal の API を叩いて本人確認
    a = requests.post(
        'https://beatech.mydns.jp:8080/beatech/login/',
        json={'user_id': portal_id, 'password': portal_pass},
        headers={'Content-Type': 'application/json'}
    )

    if a.status_code == 403:
        return jsonify({
            'is_successful': False,
            'message': 'portal の user id か password が不正です'
        })

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id, )).fetchone()
        if user is None:
            cur.execute('INSERT INTO users(discord_id, is_enable) VALUES (?, ?)', (discord_id, data['is_start']))
            message = '登録が完了しました'
        else:
            cur.execute('UPDATE users SET is_enable = ? WHERE discord_id = ?', (data['is_start'], discord_id))
            message = '変更が完了しました'

    return jsonify({
        'is_successful': True,
        'message': message
    })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=34567)
