"""tbd"""

import os
import threading

from dotenv import load_dotenv
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "hello flask :)"

if __name__ == "__main__":
    app.run(debug=True)
