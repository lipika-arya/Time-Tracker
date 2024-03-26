from flask import Flask, render_template
app = Flask(__name__) 

@app.route("/")
def home():
    return render_template('login.html')

@app.route("/mainpage")
def mainpage():
    return render_template('mainpage.html')
