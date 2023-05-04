from flask import Flask, render_template, request, redirect, g
import pymysql
import pymysql.cursors
from flask_login import LoginManager, current_user

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

class User:
    def __init__(self, id, username, banned):
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = not banned

        self.username = username
        self.id = id
    
    def get_id(self):
        return str(self.id)

def connect_db():
    return pymysql.connect(
        host="10.100.33.60",
        user="tbobo",
        password="223086750",
        database="tbobo_social",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def get_db():
    '''Opens a new database connection per request.'''        
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db    

@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close() 


@login_manager.user_loader
def user_loader(user_id):
    cursor = get_db().cursor()

    cursor.execute("SELECT * FROM `users` WHERE `id` = " + user_id)

    result = cursor.fetchone()

    if result is None:
        return None
    
    return User(result['id'], result['username'], result['banned'])

@app.route('/feed')
def post_feed():

    cursor = get_db().cursor()


    cursor.execute("SELECT * FROM `posts` JOIN `user` ON `posts`.`user_id` = `user`.`id` ORDER BY `time_stamp` DESC;")

    results = cursor.fetchall()

    return render_template(
        "feed.html.jinja",
        posts=results
    )


@app.errorhandler(404)
def page_not_found(err):
    return render_template('404.html.jinja'), 404


@app.route('/signup', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        cursor = get_db().cursor()


        photo = request.files['photo']

        file_name = photo.filename

        file_extension = file_name.split('.')[-1]

        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            photo.save('media/users/' + file_name)
        else:
            raise Exception('Invalid file type')

        cursor.execute("""
            INSERT INTO `user` (`display_name`,`email`,`password`,`photo`,`username`, `birthday`, `bio`)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (request.form['display_name'], request.form['email'], request.form['password'], file_name, request.form['username'], request.form['birthday'], request.form['bio']))


        return redirect('/feed')
    elif request.method == 'GET':
        return render_template("signup.html.jinja")
    

@app.route('/profile/<username>')
def user_profile(username):
    cursor = cursor = get_db().cursor()


    cursor.execute("SELECT * FROM `user` WHERE `username`= %s", (username))

    result = cursor.fetchone()

    return render_template("userprofile.html.jinja", user=result)

@app.route('/post')
def create_post():
    cursor = get_db().cursor()

    photo = request.files['file']

    file_name = photo.filename

    file_extension = file_name.split('.')[-1]

    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
        photo.save('media/users/' + file_name)
    else:
        raise Exception('Invalid file type')

    cursor.execute("INSERT INTO `posts` (`user_id`,`post_text`,`post_image`) VALUES (%s, %s, %s)",
                   (current_user.id, request.form['post'], file_name))
    
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect('/feed')
    
    return render_template("home.html.jinja")






if __name__ == '__main__':
    app.run(debug = True)
