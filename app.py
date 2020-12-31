import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'i_brary'
app.config['MONGO_URI'] = 'mongodb://sw1ckham:1hamcvcw123@myfirstcluster-shard-00-00-iff8d.mongodb.net:27017,myfirstcluster-shard-00-01-iff8d.mongodb.net:27017,myfirstcluster-shard-00-02-iff8d.mongodb.net:27017/i_brary?ssl=true&replicaSet=myFirstCluster-shard-0&authSource=admin&retryWrites=true&w=majority'

mongo = PyMongo(app)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', books=mongo.db.books.find({"book_share": "on"}))  # Only show books on the index.html that has been set to share:on when added.


@app.route('/show_login')  # For the login Button
def show_login():
    return render_template('login.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    users = mongo.db.users
    login_user = users.find_one({'user_username': request.form['user_username']})  #Check if user info is in the system

    if login_user:
        if bcrypt.hashpw(request.form['user_password'].encode('utf-8'), login_user['user_password']) == login_user['user_password']:
            session['user_username'] = request.form['user_username']
            return redirect(url_for('index'))
    else:
        invalid_user = 'Invalid username/password combination'
    return render_template('login.html', message=invalid_user)  # Error message if user info isn't in the system. 


@app.route('/show_register')  # For the register button
def show_register():
    return render_template('register.html')


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        users = mongo.db.users
        existing_user = users.find_one({
            'user_username': request.form['user_username']
            })  # Check if user is in the system
        if existing_user is None:  # If not.. 
            hashpass = bcrypt.hashpw(request.form['user_password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({
                'user_username': request.form['user_username'],   #Insert user info given in the form, into new user object in database
                'user_password': hashpass
                })
            session['user_username'] = request.form['user_username']
            return redirect(url_for('index'))
        else:
            invalid_user = 'This username already exists'
        return render_template('register.html', message=invalid_user)
    


@app.route('/show_books', methods=["POST", "GET"])
def show_books():
    username = session['user_username']
    return render_template('books.html', books=mongo.db.books.find({"added_by": username})) # Only show books that was been uploaded by the username logged in



@app.route('/add_book')
def add_book():
    return render_template('addbook.html')


@app.route('/insert_book', methods=['POST'])
def insert_book():
    books = mongo.db.books
    books.insert_one(request.form.to_dict())
    print(request.form.to_dict())
    return redirect(url_for('show_books'))


@app.route('/edit_book/<book_id>')
def edit_book(book_id):
    the_book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    return render_template('editbook.html', book=the_book)


@app.route('/update_book/<book_id>', methods=['POST'])
def update_book(book_id):
    books = mongo.db.books
    books.update({'_id': ObjectId(book_id)},
    {
        'added_by': request.form.get('added_by'),
        'book_name': request.form.get('book_name'),
        'book_author': request.form.get('book_author'),
        'book_genre': request.form.get('book_genre'),
        'img_url': request.form.get('img_url'),
        'book_rating': request.form.get('book_rating'),
        'book_comments': request.form.get('book_comments')
    })
    return redirect(url_for('show_books'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    mongo.db.books.find_one_and_delete({'_id': ObjectId(book_id)})
    return redirect(url_for('show_books'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=False)


