
from flask import Flask, render_template, request, redirect, url_for
from transformers import pipeline, AutoTokenizer, AutoModel
from flask_mysqldb import MySQL 
import os
import string

app = Flask(__name__)
app.config['DEBUG'] = True

# path = ('./model')
# tokenizer = AutoTokenizer.from_pretrained(path)
# # model = AutoModel.from_pretrained(path)
generator = pipeline(
    task='text-generation', 
    model='./model',
    tokenizer= './model')

# prompt = token.encode(add_special_tokens = True)

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
    return render_template('homepage.html')


@app.route("/index")
def index():
  return render_template('index.html')


@app.route('/list_puisi')
def list_puisi():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM list_puisi''')
    rv = cur.fetchall()
    # return str(rv)
    return render_template('list_puisi.html', rv=rv)


@app.route('/about')
def about():
    return render_template('about.html')


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
            return render_template('output.html', name=string)
    elif request.method == 'POST' :
        puisi = request.form['puisi']
        judul = request.form['judul']
        author = request.form['author']
        tanggal = request.form['tanggal']
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO list_puisi (puisi,judul,author,tanggal) VALUES (%s,%s,%s,%s)''', (puisi,judul,author,tanggal))
        mysql.connection.commit()
        return render_template('output.html')

if __name__ == "__main__":
    app.run(debug=True)
