from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    files = request.files.getlist('file')
    mentor_files = []
    mentee_files = []

    for file in files:
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Check filename for keywords
        if 'mentor' in file.filename.lower():
            mentor_files.append(filepath)
        elif 'mentee' in file.filename.lower():
            mentee_files.append(filepath)
        else:
            return jsonify({'message': 'Invalid file type: must be either mentor or mentee spreadsheet'}), 400
    
    # Process mentor and mentee files accordingly
    process_mentor_files(mentor_files)
    process_mentee_files(mentee_files)
    
    return jsonify({'message': 'Files successfully uploaded and processed'}), 200

def process_mentor_files(files):
    # Process mentor files logic
    for file in files:
        # Implement your processing logic here
        print(f'Processing mentor file: {file}')

def process_mentee_files(files):
    # Process mentee files logic
    for file in files:
        # Implement your processing logic here
        print(f'Processing mentee file: {file}')

if __name__ == '__main__':
    app.run(debug=True)
