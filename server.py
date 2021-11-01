import flask
import sqlite3
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
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        tweets = cur.execute(
            'SELECT tweet, tweet_id_str, filename, created_at FROM tweets ORDER BY created_at DESC'
        ).fetchall()

    result = [
        {'tweet': t, 'tweet_id': i, 'filename': f, 'created_at': c} for t, i, f, c in tweets
    ]

    return flask.jsonify(result)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=34568)
