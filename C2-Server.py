from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_DIR", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

TEMPLATE = """
<!doctype html>
<title>Upload</title>
<h1>Upload a file</h1>
<form method=post enctype=multipart/form-data action="{{ url_for('upload') }}">
  <input type=file name=file required>
  <button type=submit>Upload</button>
</form>
<h2>Files</h2>
<ul>
  {% for f in files %}<li><a href="{{ url_for('files', filename=f) }}">{{ f }}</a></li>{% else %}
  <li><em>No files yet</em></li>{% endfor %}
</ul>
"""

@app.get("/")
def index():
    return render_template_string(TEMPLATE, files=sorted(os.listdir(app.config["UPLOAD_FOLDER"])))

@app.post("/upload")
def upload():
    f = request.files.get("file")
    if not f or f.filename == "":
        return "No file provided", 400
    name = secure_filename(f.filename)
    f.save(os.path.join(app.config["UPLOAD_FOLDER"], name))
    return redirect(url_for("index"))

@app.get("/files/<path:filename>")
def files(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
