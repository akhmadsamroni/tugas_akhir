
from flask import Flask, flash, render_template, request, redirect, url_for, session
from transformers import pipeline, AutoTokenizer, AutoModel
from flask_mysqldb import MySQL 
from werkzeug.security import check_password_hash, generate_password_hash
import os
import string

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'kunci rahasia'

# path = ('./model')
# tokenizer = AutoTokenizer.from_pretrained(path)
# # model = AutoModel.from_pretrained(path)
generator = pipeline(
    task='text-generation', 
    model='./model',
    tokenizer= './model')


# def process(text_generator, text: str, max_length: int = 100, do_sample: bool = True, top_k: int = 50, top_p: float = 0.95,
#             temperature: float = 1.0, max_time: float = 120.0, seed=42, repetition_penalty=1.0):
#     # st.write("Cache miss: process")
#     set_seed(seed)
#     if repetition_penalty == 0.0:
#         min_penalty = 1.05
#         max_penalty = 1.5
#         repetition_penalty = max(min_penalty + (1.0-temperature) * (max_penalty-min_penalty), 0.8)
#     result = text_generator(text, max_length=max_length, do_sample=do_sample,
#                             top_k=top_k, top_p=top_p, temperature=temperature,
#                             max_time=max_time, repetition_penalty=repetition_penalty)
#     return result

# koneksi database
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "puisi"
# Extra configs, optional:
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"
# app.config["MYSQL_CUSTOM_OPTIONS"] = {"ssl": {"ca": "/path/to/ca-file"}}  # https://mysqlclient.readthedocs.io/user_guide.html#functions-and-attributes

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('landing/homepage.html')

# @app.route('/landing/homepage')
# def homepage():
#     return render_template('landing/homepage.html')

@app.route("/index")
def index():
    if 'loggedin' in session:
        return render_template('pages/index.html')
    flash('Harap Login dulu','danger')
    return redirect(url_for('landing/login'))

#registrasi
@app.route('/register', methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        #cek username atau email
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username=%s OR email=%s',(username, email, ))
        akun = cursor.fetchone()
        if akun is None:
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (username, email, generate_password_hash(password), level))
            mysql.connection.commit()
            flash('Registrasi Berhasil','success')
        else :
            flash('Username atau email sudah ada','danger')
    return render_template('landing/register.html')

#login
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        #cek data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s',(email, ))
        akun = cursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek Username Anda','danger')
        elif not check_password_hash(akun[3], password):
            flash('Login gagal, Cek Password Anda', 'danger')
        else:
            session['loggedin'] = True
            session['username'] = akun[1]
            session['level'] = akun[4]
            return redirect(url_for('index'))
    return render_template('landing/login.html')

#logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('level', None)
    return redirect(url_for('landing/login'))


@app.route('/list_puisi')
def list_puisi():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM list_puisi''')
    l_puisi = cur.fetchall()
    return render_template('pages/list_puisi.html', l_puisi=l_puisi)


@app.route('/about')
def about():
    return render_template('pages/about.html')


@app.route('/output', methods=['POST'])
def output():
    if request.method == 'POST' and "name" in request.form:
        isi = request.form['name']
        output = generator(
            isi,
            max_length=50, # max token to generate
            num_return_sequences=1, #jumlah balok skor tertinggi yang harus dikembalikan ? jumlah sample yang ingin dikeluarkan sesuai yang didefinisikan
            repetition_penalty=1.0, # mencegah kata pengulangan
            temperature=2.0, # untuk mengatur probability next word 
            top_k=50, # ambil top kata dengan probability tertinggi / kata yang paling mungkin
            top_p=0.95, # ambil kata dan jumlah kan probalitiy nya sesuai yang di definisikan
            no_repeat_ngram_size=2 # agar tidak ada 2 gram/kata yang muncul dua kali:
            )

        # Converting list to string and removing newline chars
        string = ""
        for i in output:
            string += str(i)
            n = len(string)
            string = string[20:n-2]
            string = string.replace('\\n', '')
            return render_template('generate/output.html', name=string)
    elif request.method == 'POST' :
        puisi = request.form['puisi']
        judul = request.form['judul']
        author = request.form['author']
        tanggal = request.form['tanggal']
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO list_puisi (puisi,judul,author,tanggal) VALUES (%s,%s,%s,%s)''', (puisi,judul,author,tanggal))
        mysql.connection.commit()
        return render_template('generate/output.html')

@app.route('/list_users')
def list_users():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM users''')
    l_users = cur.fetchall()
    return render_template('pages/admin/list_users.html', l_users=l_users)

@app.route('/account')
def account():
    return render_template('pages/account.html')

@app.route('/edit_user/<username>', methods=['GET','POST'])
def edit_user(username):
    if request.method == 'GET':
        
        cur = mysql.connection.cursor()
        cur.execute('''
        SELECT * 
        FROM users  
        WHERE username = %s''', (username, ))
        user = cur.fetchone()
        cur.close()

        return render_template('/pages/admin/edit_user.html', user=user)
    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        
        cur.execute(''' 
        UPDATE users 
        SET 

            email = %s,
            password = %s
        WHERE
            username = %s;
        ''',(email, generate_password_hash(password), username))
        
        mysql.connection.commit()
        cur.close()
        flash('Edit berhasil','success')
        return redirect(url_for('list_users'))


if __name__ == "__main__":
    app.run(debug=True)
