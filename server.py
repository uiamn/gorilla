import flask
import sqlite3

DB_PATH = 'db.sqlite3'
app = flask.Flask(__name__, static_folder='images')

@app.route('/results', methods=['GET'])
def get_results() -> str:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        tweets = cur.execute(
            'SELECT tweet, tweet_id, filename, created_at FROM tweets ORDER BY created_at DESC'
        ).fetchall()

    result = [
        {'tweet': t, 'tweet_id': i, 'filename': f, 'created_at': c} for t, i, f, c in tweets
    ]

    return flask.jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
