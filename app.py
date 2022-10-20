# Server Side Code
# Web Scrapping to MongoDB
# Route Function
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_session import Session
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.dcgxcrg.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)
app.secret_key = 'test'

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return render_template('login.html')
    else:
        return render_template('index.html')

# Mulai Buat API
@app.route('/watchlist', methods=['POST'])
def movielist_post():
    url_receive = request.form['url_give']
    genre_receive = request.form['genre_give']
    schedule_receive = request.form['schedule_give']
    count = db.watchlist.count_documents({})
    num = count + 1
    isDelete = False

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    # Extracting data 
    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    image = og_image['content']
    title = og_title['content']
    description = og_description['content']

    doc = {
        'num' : num,
        'image' : image,
        'title' : title,
        'description' : description,
        'genre' : genre_receive,
        'schedule' : schedule_receive,
        'status' : 0,
        'isDelete' : isDelete
    }

    db.watchlist.insert_one(doc)
    return jsonify({'msg': 'Movie Saved!'})

@app.route("/watchlist", methods=["GET"])
def movie_get():
    movie_list = list(db.watchlist.find({}, {'_id': False}))
    return jsonify({'movies': movie_list}) 

@app.route("/watchlist/delete", methods=["POST"])
def delete_bucket():
    num_receive = request.form['num_give']
    db.watchlist.update_one(
         {'num': int(num_receive)},
         {'$set': {'isDelete': True}}
        )
    return jsonify({'msg': 'Movie Deleted!'})

@app.route("/watchlist/done", methods=["POST"])
def bucket_done():
    num_receive = request.form['num_give']
    db.watchlist.update_one(
        {'num': int(num_receive)},
        {'$set': {'status': 1}}
    )
    return jsonify({'msg': 'update done!'})

@app.route("/watchlist/cancel", methods=["POST"])
def cancel_bucket():
    num_receive = request.form['num_give']
    db.watchlist.update_one(
        {'num': int(num_receive)},
        {'$set': {'status': 0}}
    )
    return jsonify({'msg': 'cancel done!'})

@app.route("/login", methods=["GET","POST"])
def logincheck():
    if request.method == "POST":

        user = db.user.find_one({'id': request.form['user']}, {'pw': request.form['password']})

        if user is not None:
            session['user'] = request.form['user']
            return redirect(url_for('home'))
        else:
            return render_template('login.html')

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        user_receive = request.form['user_give']
        pw_receive = request.form['password_give']
        name_receive = request.form['name_give']

        user = db.user.find_one({'id': user_receive}, {'_id': False})

        if user is None:
            db.user.insert_one({'id': user_receive, 'pw': pw_receive, 'name': name_receive})
            return render_template('login.html')
        else:
            return jsonify({'result': 'fail', 'msg': 'fail'})
    else:
        return render_template('register.html')
    
if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)