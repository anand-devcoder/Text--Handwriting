import os
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
import img2pdf
import pytesseract

# If Tesseract is not in your PATH (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Paper sizes in inches
PAPER_SIZES_IN = {
    'A4': (8.27, 11.69),
    'Letter': (8.5, 11),
    'A5': (5.83, 8.27)
}
DPI = 150

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Default font path
DEFAULT_FONT_PATH = os.path.join('static', 'fonts', 'Kalam-Regular.ttf')


def inches_to_px(size_in_inches, dpi=DPI):
    return int(size_in_inches * dpi)


# ---------------- TEXT TO IMAGE ----------------
def render_text_to_image(text, paper='A4', orientation='portrait',
                         margin_top=15, margin_bottom=15, margin_left=15, margin_right=15,
                         font_path=DEFAULT_FONT_PATH, font_size=120):

    w_in, h_in = PAPER_SIZES_IN.get(paper, PAPER_SIZES_IN['A4'])
    if orientation == 'landscape':
        w_in, h_in = h_in, w_in
    width_px = inches_to_px(w_in)
    height_px = inches_to_px(h_in)

    img = Image.new('RGB', (width_px, height_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Convert mm → px
    margin_top_px = int(margin_top * DPI / 25.4)
    margin_bottom_px = int(margin_bottom * DPI / 25.4)
    margin_left_px = int(margin_left * DPI / 25.4)
    margin_right_px = int(margin_right * DPI / 25.4)

    usable_w = width_px - margin_left_px - margin_right_px
    usable_h = height_px - margin_top_px - margin_bottom_px

    # Font load
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Word-wrap
    lines = []
    words = text.replace('\r', '').split('\n')
    for para in words:
        if para.strip() == '':
            lines.append('')
            continue
        cur = ''
        for word in para.split(' '):
            test = (cur + ' ' + word).strip() if cur else word
            w = draw.textbbox((0, 0), test, font=font)[2]
            if w <= usable_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)

    lh = draw.textbbox((0, 0), 'A', font=font)[3]
    y = margin_top_px

    for line in lines:
        if y + lh > height_px - margin_bottom_px:
            break
        draw.text((margin_left_px, y), line, fill=(0, 0, 0), font=font)
        y += int(lh * 1.25)

    return img


# ---------------- ROUTES ----------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    text_input = request.form.get('text_input', '').strip()
    paper = request.form.get('paper', 'A4')
    orientation = request.form.get('orientation', 'portrait')

    margin_top = float(request.form.get('margin_top', 15))
    margin_bottom = float(request.form.get('margin_bottom', 15))
    margin_left = float(request.form.get('margin_left', 15))
    margin_right = float(request.form.get('margin_right', 15))

    output_type = request.form.get('output_type', 'image')
    font_size = int(request.form.get('font_size', 28))

    # New session folder
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], now)
    os.makedirs(session_folder, exist_ok=True)

    # Uploaded image
    uploaded = request.files.get('upload_image')
    if uploaded and uploaded.filename != '':
        filename = secure_filename(uploaded.filename)
        uploaded_file_path = os.path.join(session_folder, filename)
        uploaded.save(uploaded_file_path)

        # OCR if textbox empty
        if not text_input:
            try:
                ocr_text = pytesseract.image_to_string(Image.open(uploaded_file_path).convert('L')).strip()
                if ocr_text:
                    text_input = ocr_text

                    # ⭐ ADD THIS SINGLE LINE (NO OLD CODE CHANGE)
                    text_input = text_input.replace("\n", " ")


                else:
                    return jsonify({'error': 'OCR did not detect any text.'}), 400
            except Exception as e:
                return jsonify({'error': f'OCR failed: {e}'}), 400

    if not text_input:
        return jsonify({'error': 'No text provided.'}), 400

    # Render image
    img = render_text_to_image(
        text_input,
        paper=paper,
        orientation=orientation,
        margin_top=margin_top,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        margin_right=margin_right,
        font_size=font_size
    )

    # Save image
    img_path = os.path.join(session_folder, "handwritten.png")
    img.save(img_path)

    if output_type == "pdf":
        pdf_path = os.path.join(session_folder, "handwritten.pdf")
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(img_path))
        return jsonify({
            'preview': url_for('download_file', folder=now, filename='handwritten.pdf'),
            'download': url_for('download_file', folder=now, filename='handwritten.pdf')
        })
    else:
        return jsonify({
            'preview': url_for('download_file', folder=now, filename='handwritten.png'),
            'download': url_for('download_file', folder=now, filename='handwritten.png')
        })


@app.route('/uploads/<folder>/<filename>')
def download_file(folder, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)


if __name__ == '__main__':
    app.run(debug=True)
