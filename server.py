import flask
from flask import request
import sqlite3
import requests  # urllibに置き換えたい
import re
from flask_cors import CORS

DB_PATH = 'db.sqlite3'
app = flask.Flask(__name__, static_folder='images')
CORS(app)

@app.after_request
def after_request(response):
  # response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/results', methods=['GET'])
def get_results() -> str:
    user_id = request.args.get('user')
    if user_id is None:
        return flask.jsonify([])

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        query_res = cur.execute(
            'SELECT filename, created_at FROM results WHERE user = ?', (user_id, )
        ).fetchall()

    result = [
        {'filename': f, 'created_at': c} for f, c in query_res
    ]

    return flask.jsonify(result)


@app.route('/')
def top_page() -> str:
    return flask.render_template('index.html')


@app.route('/register', methods=['POST'])
def register() -> str:
    data = request.json

    # 一応 Discord ID の形式を確認しておく
    if not re.match(r'.+#[0-9]{4}', data['discord_id']):
        return flask.jsonify({
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
        return flask.jsonify({
            'is_successful': False,
            'message': 'portal の user id か password が不正です'
        })

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM users WHERE portal_id = ?', (portal_id, )).fetchone()
        if user is None:
            cur.execute('INSERT INTO users(discord_id, portal_id, is_enable) VALUES (?, ?, ?)', (discord_id, portal_id, data['is_start']))
            message = '登録が完了しました'
        else:
            cur.execute('UPDATE users SET is_enable = ?, discord_id = ? WHERE portal_id = ?', (data['is_start'], discord_id, portal_id))
            message = '変更が完了しました'

    return flask.jsonify({
        'is_successful': True,
        'message': message
    })


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=34568)
