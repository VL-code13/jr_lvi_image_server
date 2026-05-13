from flask import Flask, render_template

app = Flask(__name__)


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/upload')
def upload_page():
    return render_template('upload.html')


@app.get('/images/')
def images_page():
    return render_template('images.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
