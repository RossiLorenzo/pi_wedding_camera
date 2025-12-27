import os
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

# Directory where images are stored (relative to this script)
# We use abspath to ensure we are pointing to the correct location regardless of CWD,
# but dependent on script location.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Pictures'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/images')
def get_images():
    """Return a list of images sorted by modification time (newest first)."""
    if not os.path.exists(PICTURES_DIR):
        return jsonify([])

    images = []
    # Extension filter
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    try:
        for filename in os.listdir(PICTURES_DIR):
            if filename.lower().endswith(valid_extensions):
                filepath = os.path.join(PICTURES_DIR, filename)
                # handle potential race condition if file is deleted
                try:
                    mtime = os.path.getmtime(filepath)
                    images.append({
                        'name': filename,
                        'time': mtime
                    })
                except OSError:
                    continue
    except OSError:
        pass # Directory might not exist or be accessible
    
    # Sort by time, newest first
    images.sort(key=lambda x: x['time'], reverse=True)
    return jsonify([img['name'] for img in images])

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(PICTURES_DIR, filename)

if __name__ == '__main__':
    # Ensure Pictures directory exists to avoid errors
    if not os.path.exists(PICTURES_DIR):
        print(f"Warning: Pictures directory not found at {PICTURES_DIR}")
        try:
            os.makedirs(PICTURES_DIR)
            print(f"Created {PICTURES_DIR}")
        except OSError as e:
            print(f"Could not create directory: {e}")

    # Host 0.0.0.0 to be accessible on network
    app.run(host='0.0.0.0', port=8000, debug=False)
