from flask import Flask, render_template, request, redirect
import pymysql
import pymysql.cursors

app = Flask(__name__)

connection = pymysql.connect(
    host="10.100.33.60",
    user="tbobo",
    password="223068750",
    database="tbobo_social",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

@app.route('/feed')
def post_feed():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `posts` JOIN `user` ON `posts`.`user_id` = `user`.`id` ORDER BY `time_stamp` DESC;")

    results = cursor.fetchall()

    return render_template(
        "feed.html.jinja",
        posts=results
    )

if __name__ == '__main__':
    app.run(debug = True)