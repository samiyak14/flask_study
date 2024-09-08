from flask import Flask
app=Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello World</h1>'

@app.route('/home/<name>',methods=['GET','POST'],defaults={'name':'Default'})
@app.route('/home/<name>',methods=['GET','POST'])
def home(name) :
    return '<h1>hii {} welcome to this website!</h1>'.format(name)

if __name__=='__main__':
    app.run()