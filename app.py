from flask import Flask, render_template, jsonify, request, send_from_directory, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge
import os
import logging
import uuid
from io import BytesIO
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

IMAGES_DIR = Path(os.getenv('IMAGES_DIR', BASE_DIR / 'images'))

LOGS_DIR = Path(os.getenv('LOGS_DIR', BASE_DIR / 'logs'))

MAX_FILE_SIZE = 5 * 1024 * 1024

REQUEST_LIMIT = MAX_FILE_SIZE + 1024 * 1024

ALLOWED_IMAGE_FORMATS = {
    'JPEG': 'jpg',
    'PNG': 'png',
    'GIF': 'gif'
}

app.config['MAX_CONTENT_LENGTH'] = REQUEST_LIMIT

IMAGES_DIR.mkdir(exist_ok=True)

LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / 'app.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def detect_image_extension(file_data: bytes):
    try:
        with Image.open(BytesIO(file_data)) as image:
            image.verify()

            return ALLOWED_IMAGE_FORMATS.get(image.format)
    except (UnidentifiedImageError, OSError):
        return None


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/upload')
def upload_page():
    return render_template('upload.html')


@app.get('/images/')
def images_page():
    images = []

    for image_path in sorted(IMAGES_DIR.iterdir(), key=lambda path:path.stat().st_mtime, reverse=True):
        if not image_path.is_file():
            continue

        relative_url:str = url_for('get_image', filename=image_path.name)
        full_url = request.host_url.rstrip('/') + relative_url

        images.append(
            {
                'name': image_path.name,
                'url': relative_url,
                'full_url': full_url
            }
        )
    return render_template('images.html', images=images)


@app.post('/upload')
def upload_image():
    uploaded_file = request.files.get('image')

    if uploaded_file is None:
        logging.warning('No image uploaded. Файл image не найден в запросе.')
        return jsonify({
            'error': 'No image uploaded. Файл не найден. Поле формы должно называться image'
        })

    original_filename = uploaded_file.filename or 'Unknown'

    file_data = uploaded_file.read()    # стал bytes

    if not file_data:
        logging.warning(f'Ошибка: файл пустой {original_filename}')
        return jsonify({
            'error': 'Файл пустой'
        }), 400

    if len(file_data) > MAX_FILE_SIZE:
        logging.warning(f'Ошибка: Файл {original_filename} не должен быть больше 5 Мб.')
        return jsonify({
            'error': 'Файл не должен быть больше 5 Мб.'
        })

    image_extension = detect_image_extension(file_data)

    if image_extension is None:
        logging.warning(f'Ошибка: Файл {original_filename} имеет не верный формат.')
        return jsonify({
            'error': 'Файл не верного формата. Поддерживаются только jpg, png, gif.'
        })

    unique_filename = f'{uuid.uuid4().hex}.{image_extension}'   # генерируем уникальное имя

    target_path = IMAGES_DIR / unique_filename

    target_path.write_bytes(file_data)

    relative_url = url_for('get_image', filename=unique_filename)
    full_url = request.host_url.rstrip('/') + relative_url

    logging.info(f'Успех. Изображение загружено как {original_filename}')
    return jsonify(
        {
            'message': "Изображение успешно загружено",
            'id': unique_filename,
            'url': relative_url,
            'full_url': full_url
        }
    ), 201


@app.get('/images/<path:filename>')
def get_image(filename: str):
    return send_from_directory(IMAGES_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
