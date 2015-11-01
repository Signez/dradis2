import os
from flask import send_from_directory, render_template
from dradis.main import app


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/front/<path:filename>')
def send_foo(filename):
    return send_from_directory(os.path.join('/home/signez/git/dradis/', 'front/dist'), filename)


@app.route('/public/<path:filename>')
def send_bar(filename):
    return send_from_directory(os.path.join('/home/signez/git/dradis/', 'front/public'), filename)


@app.route('/', defaults={'path': '/'})
@app.route('/<path:path>')
def main_interface(path=None):
    return render_template('interface.html', dradis_api_key=app.config["DRADIS_API_KEY"].decode('utf8'))
