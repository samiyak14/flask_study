from flask import Flask
app = Flask(__name__)

@app.route('/<name>')
def index(name): 
    return '<h1>Hello {}!</h1>'.format(name)

@app.route('/home')
def home():
    return '<h1>You are on the home page</h1>'

if __name__=='__main__' :
    app.run()

    