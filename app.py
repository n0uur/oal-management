"""tbd"""

from logging import log
from dotenv import load_dotenv
from werkzeug.utils import redirect
load_dotenv()

import os
from dotenv import load_dotenv
from flask import Flask, request, session, render_template
from flask_session import Session

from models import Setting

app = Flask(
    __name__,
    static_folder='./public',
    static_url_path='/',
    template_folder='templates'
)

app.config["SESSION_PERMANENT"] = False

app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_COOKIE_NAME"] = "g5_oal_session"
app.config["SESSION_COOKIE_PATH"] = "APPLICATION_ROOT"
app.config["SESSION_FILE_DIR"] = "sessions"

app.secret_key = os.environ.get("WEB_SECRET_KEY", "ABCD")

_session = Session()
_session.init_app(app)

@app.route("/")
def home():
    if not session.get('is_permit', False):
        return redirect('/login')
    return "Logged in" if session.get('is_permit', False) else "No Permission"

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == "POST":
        password = os.environ.get('WEB_LOGIN_SECRET', False)
        if not password:
            return redirect('/login')

        if request.form.get('app_password') == password:
            session["is_permit"] = True
            return redirect('/')
        
        error = "รหัสผ่านไม่ถูกต้อง"

    return render_template('login.html', error=error)

@app.route('/logout', methods=['POST'])
def logout():
    session["is_permit"] = False

if __name__ == "__main__":
    app.run(debug=True)
