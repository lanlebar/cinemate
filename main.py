import re
import subprocess

try:
    from flask import Flask, render_template, request, redirect, session, flash
except ImportError:
    subprocess.check_call(['pip', 'install', 'flask'])
    from flask import Flask, render_template, request, redirect, session, flash

try:
    from tinydb import TinyDB, Query, where
except ImportError:
    subprocess.check_call(['pip', 'install', 'tinydb'])
    from tinydb import TinyDB, Query, where

try:
    from datetime import timedelta
except ImportError:
    subprocess.check_call(['pip', 'install', 'datetime'])
    from datetime import timedelta

try:
    import requests
except ImportError:
    subprocess.check_call(['pip', 'install', 'requests'])
    import requests

try:
    import random
except ImportError:
    subprocess.check_call(['pip', 'install', 'random'])
    import random

try:
    import hashlib
except ImportError:
    subprocess.check_call(['pip', 'install', 'hashlib'])
    import hashlib

try:
    import Levenshtein
except ImportError:
    subprocess.check_call(['pip', 'install', 'Levenshtein'])
    import Levenshtein


# Initialize and configure Flask app
app = Flask('CineMate')
app.secret_key = 'kys'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize TinyDB and tables 
db = TinyDB('db.json')
users = db.table('users')

# side functions
def check_password(password):
    # regex tempalte to check password requirements
    regex = "^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,}$"
    if re.search(regex, password):
        return True
    else:
        return False


# webpage routes
@app.route('/')
def login():
    if 'user_id' in session:
        return render_template("search.html")
    else:
        return render_template("login.html")

@app.route('/register')
def register():
    if 'user_id' in session:
        return render_template("search.html")
    else:
        return render_template("register.html")

@app.route('/search')
def search():
    if 'user_id' in session:
        return render_template("search.html")
    else:
        flash('Session has expired. Please log in again')
        return redirect('/')

@app.route('/liked')
def liked():
    if 'user_id' in session:
        return render_template("liked.html")
    else:
        flash('Session has expired. Please log in again')
        return redirect('/')

@app.route('/profile')
def profile():
    if 'user_id' in session:
        return render_template("profile.html", username=session['user_id'], name=session['name'])
    else:
        flash('Session has expired. Please log in again')
        return redirect('/')

# error handling routes
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html')


# working routes
@app.route('/register_set', methods=["POST"])
def register_set():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    # check for mistakes
    errors = []
    if len(name) < 3:
        errors.append("Name must be at least 3 characters long.")
    if len(username) < 6:
        errors.append("username must be at least 6 characters long.")
    # check password strength
    if not check_password(password):
        errors.append("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit..")
        
    if errors:
        for error in errors:
            flash(error)
        return redirect('/register')

    # check if username exists
    for user in users.all():
        if username == user["username"]:
            flash("Username is already taken!")
            return redirect('/register')

    try:
        # add user to users table
        user = {
            "name": name,
            "username": username,
            "password": password
        }
        users.insert(user)

        # create users own table - for storing movies
        user_table =  db.table(f'{username}')
        # make a dummy insert to save table to database
        user_table.insert({})

        # login user that just created an account and display success message
        flash("Account successfully created")
        return login_set(username, password)
    except:
        return render_template("errors/500.html")

@app.route('/login_set', methods=["POST"])
def login_set(*credentials):
    if credentials:
        username = credentials[0]
        password = credentials[1]
    else:
        username = request.form['username']
        password = request.form['password']

    # check if username/password is empty
    errors = []
    if username.isspace() or not username:
        errors.append("Enter username")
    if password.isspace() or not password:
        errors.append("Enter password")
    
    if errors:
        if len(errors) == 2:
            flash("Enter username and password")
            return redirect('/')
        else:
            for error in errors:
                flash(error)
            return redirect('/')
    
    # check if user exists
    for user in users.all():
        if username == user['username'] and password == user['password']:
            session['user_id'] = user['username']
            session['name'] = user['name']
            return redirect('/search')
    
    # user doesn't exist
    flash('Invalid username or password')
    return redirect('/')

@app.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect('/')

@app.route('/get_movie_info')
def get_movie_info(*args):
    # etr to get custom image
    if args:
        title = args[0]
    else:
        title = request.args['title']
    
    # if title doesn't exist, return not found - at least the title must always exist when displaying a movie
    if title == "N/A":
        return "not found"
    
    if title.isspace() or len(title) == 0:
        return "empty"
    
    # format keyword so it can be used in a link
    apiKeyword = ""
    for k in title:
        if k == " ": apiKeyword += "+"
        else: apiKeyword += k
    
    omdb_key = "a8086a92"
    url = f"http://www.omdbapi.com/?apikey={omdb_key}&t={apiKeyword}"
    try:
        response = requests.get(url).json()
        return {
            "id": hashlib.sha256(title.encode()).hexdigest(),
            "title": response['Title'],
            "image": response['Poster'] if response['Poster'] != "N/A" else "static/images/no_image.png",
            "year": response['Year'] if response['Year'] != "N/A" else "No year info :(",
            "imdb": response['imdbRating'] if response['imdbRating'] != "N/A" else "No IMDB rating info :(",
            "runtime": response['Runtime'] if response['Runtime'] != "N/A" else "No runtime info :(",
            "director": response['Director'] if response['Director'] != "N/A" else "No director info :(",
            "genre": response['Genre'] if response['Genre'] != "N/A" else "No genre info :(",
            "actors": response['Actors'] if response['Actors'] != "N/A" else "No actors info :(",
            "overview": response['Plot'] if response['Plot'] != "N/A" else "No overview info :("
        }
    except:
        return "not found"

@app.route('/get_random_movie')
def get_random_movie():
    tmdb_key = "d7d5efc2b0a01c3159863df99e1e1d12"
    # dummy call - to get number of results
    dummy_call = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_key}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=100&with_watch_monetization_types=flatrate").json()

    # search for movie that will have all the needed info
    while True:
        # only display the top 1 % of discocer results
        random_page_number = random.randint(1, int(dummy_call["total_pages"]/100))
        random_movie_on_page = random.randint(1, 20) # 20 results per page

        # actual call
        response = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_key}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page={random_page_number}&with_watch_monetization_types=flatrate").json()
        try:
            random_movie = response['results'][random_movie_on_page]
        except:
            continue
        
        try:
            # call get_movie_info_data() to get needed data about movie
            get_movie_info_data = get_movie_info(random_movie['title'])
            if get_movie_info_data == "not found" or get_movie_info_data == "empty":
                continue
            else:
                print(get_movie_info_data)
                return get_movie_info_data

        except:
            # try calling get_movie_info_data() again with the original title
            try:
                get_movie_info_data = get_movie_info(random_movie['original_title'])
                if get_movie_info_data == "not found" or get_movie_info_data == "empty":
                    continue
                else:
                    print(get_movie_info_data)
                    return get_movie_info_data
            except:
                continue

@app.route('/like_movie')
def like_movie():
    # get username - needed for database insertion
    username = session['user_id']
    if request.args:
        # get movie details
        title = request.args['title']
        id = request.args['movie_id']
        image = request.args['image']
        year = request.args['year']
        imdb = request.args['imdb']
        runtime = request.args['runtime']
        director = request.args['director']
        genre = request.args['genre']
        actors = request.args['actors']
        overview = request.args['overview']
        
        # get actual table object using username, which is the name of the table - each user has its own tabled named by his username
        user_table = db.table(username)
        
        # check if movie already exists in liked list
        if user_table.search(where("id") == id):
            return "already"
        else:
            user_table.insert({
                'list': 'like', # this is liked list - future improvement room where users can create their own watching lists
                'id': hashlib.sha256(title.encode()).hexdigest(),
                'title': title,
                'image': image,
                'year': year,
                'imdb': imdb,
                'runtime': runtime,
                'director': director,
                'genre': genre,
                'actors': actors,
                'overview': overview
            })
            return "ok"
    else:
        return "error"

@app.route('/get_liked_movies')
def get_liked_movies():
    username = session['user_id']
    # get all movies from users table
    user_table = db.table(username)
    all_movies = user_table.all()
    all_movies.pop(0) # first insert is a dummy insert made on register
    if all_movies:
        return all_movies
    else:
        return "no liked"

@app.route('/dislike_movie')
def dislike_movie():
    username = session['user_id']
    user_table = db.table(username)
    # these 2 identifiers are enough to find the exact movie
    id = request.args['movie_id']
    try:
        user_table.remove(Query().id == id)
        return "ok"
    except:
        return "error"

@app.route('/search_movie')
def search_movie():
    username = session['user_id']
    user_table = db.table(username)

    # get the searched title - lowercase, remove spaces
    input_title = request.args['title']

    searched_title = ((input_title).strip()).lower()

    search_results = []
    for movie in user_table.all():
        if 'title' in movie:
            movie_title = (movie['title']).lower()
            # get search results using Levenshtein search algorithm - 0.6 is the score match needed to count as a valid result
            if Levenshtein.ratio(movie_title, searched_title) >= 0.6:
                search_results.append(movie)
    
    if search_results:
        return search_results
    else:
        return "none"




@app.route('/change_name', methods=["POST"])
def change_name():
    # get users actual credentials
    username = session['user_id']
    for user in db.table("users"):
        if user['username'] == username:
            user_data = user

    # get inputed data
    input_old_name = request.form['name_old_name']
    input_new_name = request.form['name_new_name']
    input_password = request.form['name_password_confirm']

    # check if old name name is correct 
    if input_old_name != user_data['name']:
        flash("Inputed old name is inncorrect!")
        return redirect('/profile')
    
    # check if password is correct
    if input_password != user_data['password']:
        flash("Inputed password is inncorrect!")
        return redirect('/profile')
    else:
        # check if name is in correct format
        if len(input_new_name) < 3:
            flash("Name must be at least 3 characters long.")
            return redirect('/profile')
        
        query = Query().username == username
        db.table("users").update({'name': input_new_name}, query)
        session['name'] = input_new_name
        flash("Name changed successfully!")
        return redirect('/profile')

@app.route('/change_username', methods=["POST"])
def change_username():
    # get users actual credentials
    username = session['user_id']
    for user in db.table("users"):
        if user['username'] == username:
            user_data = user

    # get inputed data
    input_old_username = request.form['username_old_username']
    input_new_username = request.form['username_new_username']
    input_password = request.form['username_password_confirm']

    # check if old username is correct 
    if input_old_username != user_data['username']:
        flash("Inputed old username is inncorrect!")
        return redirect('/profile')
    
    # check if password is correct
    if input_password != user_data['password']:
        flash("Inputed password is inncorrect!")
        return redirect('/profile')
    else:
        # check if username is in correct format
        if len(input_new_username) < 6:
            flash("Username must be at least 6 characters long.")
            return redirect('/profile')

        # check if username already existis
        for user in db.table("users"):
            if user['username'] == input_new_username:
                flash("The username you have entered is already taken. Please choose a different username.")
                return redirect("/profile")
        
        query = Query().username == username
        db.table("users").update({'username': input_new_username}, query)
        session.clear()
        flash("Username changed successfully! Please login again with the new username.")
        return redirect('/')


@app.route('/change_password', methods=["POST"])
def change_password():
    # get users actual credentials
    username = session['user_id']
    for user in db.table("users"):
        if user['username'] == username:
            user_data = user

    # get inputed data
    input_old_password = request.form['password_old_password']
    input_new_password = request.form['password_new_password_confirm']

    # check if old password is correct 
    if input_old_password != user_data['password']:
        flash("Inputed old password is inncorrect!")
        return redirect('/profile')
    else:
        # check if password is in correct format
        if not check_password(input_new_password):
            flash("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit..")
            return redirect('/profile')
        
        query = Query().username == username
        db.table("users").update({'password': input_new_password}, query)
        session.clear()
        flash("Password changed successfully! Please login again with the new password.")
        return redirect('/')

@app.route('/delete_user', methods=["POST"])
def delete_user():
    username = session['user_id']
    for user in db.table("users"):
        if user['username'] == username:
            user_data = user

    # get inputed data
    input_password = request.form['delete_password_confirm']

    # check if password is correct
    if input_password != user_data['password']:
        flash("Inputed password is inncorrect!")
        return redirect('/profile')
    else:
        # delete user
        db.table("users").remove(Query().username == username)
        # delete users data - liked movies
        db.drop_table(username)
        session.clear()
        flash("User successfully deleted!")
        return redirect('/')

app.run(host='0.0.0.0', port=8080, debug=True)