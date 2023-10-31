from flask import Flask, send_from_directory
app = Flask(__name__)
import werkzeug


@app.route("/<path:path>")
def index(path):
    return send_from_directory('uploads',path)

app.run('0.0.0.0',5555)

