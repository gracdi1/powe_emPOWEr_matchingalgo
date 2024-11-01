from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import pandas as pd
from collections import defaultdict

app = Flask(__name__, static_folder='static')
CORS(app, origins=["http://localhost:3000"])  # Limit CORS to the front-end origin

UPLOAD_FOLDER = './uploads'
GENERATED_FOLDER = './generated_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(GENERATED_FOLDER):
    os.makedirs(GENERATED_FOLDER)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload request received")  # Log when the upload starts
    if 'file' not in request.files:
        print("No file part in request")  # Log missing file part
        return jsonify({'message': 'No file part'}), 400

    files = request.files.getlist('file')
    if not files:
        print("No files uploaded")  # Log if no files were uploaded
        return jsonify({'message': 'No files uploaded'}), 400

    mentor_files = []
    mentee_files = []

    for file in files:
        if file.filename == '':
            print("No selected file")  # Log if a file has no name
            return jsonify({'message': 'No selected file'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        print(f"File saved: {filepath}")  # Log the saved file path

        # Check filename for keywords
        if 'mentor' in file.filename.lower():
            mentor_files.append(filepath)
            print("mentor file saved")
            print(mentor_files)
        elif 'mentee' in file.filename.lower():
            mentee_files.append(filepath)
            print("mentee file saved")
            print(mentee_files)
        else:
            print("Invalid file type")  # Log if the file type is invalid
            return jsonify({'message': 'Invalid file type: must be either mentor or mentee spreadsheet'}), 400

    # Process and match files
    matches_file = match_mentors_and_mentees(mentor_files, mentee_files)
    return send_file( os.path.join(GENERATED_FOLDER, "matches.xlsx"), as_attachment=True)

@app.route('/download', methods=['GET'])
def download():
    csv_filename = request.args.get('filename')
    csv_filepath = os.path.join(GENERATED_FOLDER, csv_filename)
    print("downloading to user")
    return send_file(csv_filepath, as_attachment=True)
    #return send_from_directory(directory='.', path=matches_file, as_attachment=True)

def match_mentors_and_mentees(mentor_files, mentee_files):
    mentor_replacement_mapping = {
        "First": "mentor_name",
        "Major": "engineering",
        "language": "mentor_language",
        "student": "max_mentee"
    }

    mentee_replacement_mapping = {
        "Last": "mentee_name",
        "Major": "interest",
        "language": "language",
        "Email Address": "email",
        "expect": "expectations"
    }

    def safe_read_excel(file):
        try:
            return pd.read_excel(file, engine='openpyxl')
        except Exception as e:
            print(f"Error reading {file}: {e}")
            return pd.DataFrame()

    mentors = pd.concat([safe_read_excel(file) for file in mentor_files], ignore_index=True)
    for column_name in mentors.columns:
        for word_to_find, new_word in mentor_replacement_mapping.items():
            if word_to_find in column_name:
                mentors.rename(columns={column_name: column_name.replace(column_name, new_word)}, inplace=True)

    mentees = pd.concat([safe_read_excel(file) for file in mentee_files], ignore_index=True)
    for column_name in mentees.columns:
        for word_to_find, new_word in mentee_replacement_mapping.items():
            if word_to_find in column_name:
                mentees.rename(columns={column_name: column_name.replace(column_name, new_word)}, inplace=True)

    mentees['interest'] = mentees['interest'].str.split(',')

    mentor_mentee_mapping = defaultdict(list)
    unmatched_mentees = []

    for mentee_row in mentees.itertuples():
        mentee = mentee_row._asdict()
        best_mentor = None
        min_mentee_count = float('inf')

        for mentor_row in mentors.itertuples():
            mentor = mentor_row._asdict()
            if mentor["mentor_language"] == mentee["language"] or mentee["language"] == "Bilingual" or mentor["mentor_language"] == "Bilingual":
                common_fields = set(mentee["interest"]).intersection([mentor["engineering"]])
                if common_fields:
                    if len(mentor_mentee_mapping[mentor["mentor_name"]]) < mentor["max_mentee"]:
                        if len(mentor_mentee_mapping[mentor["mentor_name"]]) < min_mentee_count:
                            min_mentee_count = len(mentor_mentee_mapping[mentor["mentor_name"]])
                            best_mentor = mentor["mentor_name"]

        if best_mentor is not None:
            mentor_mentee_mapping[best_mentor].append(mentee["mentee_name"])
            print(best_mentor + " + " + mentee["mentee_name"])
        else:
            unmatched_mentees.append(mentee["mentee_name"])

    result_list = []
    for mentor, mentees in mentor_mentee_mapping.items():
        result_list.append({"Mentor": mentor, "Mentees": mentees})

    matches_file = save_matches_to_excel(result_list, unmatched_mentees)

    # Save results to a file (CSV for example)
    # matches_file = os.path.join(GENERATED_FOLDER, 'matches.xlsx')
    # with open(matches_file, 'w') as f:
    #     for match in result_list:
    #         f.write(f"{match['Mentor']}, {', '.join(match['Mentees'])}\n")

    return matches_file

def save_matches_to_excel(result_list, unmatched_mentees):
    # Create a DataFrame for matched mentors and mentees
    matched_data = {
        'Mentor': [],
        'Mentees': []
    }
    
    for match in result_list:
        matched_data['Mentor'].append(match['Mentor'])
        matched_data['Mentees'].append(', '.join(match['Mentees']))

    matched_df = pd.DataFrame(matched_data)

    # Create a DataFrame for unmatched mentees
    unmatched_df = pd.DataFrame(unmatched_mentees, columns=['Unmatched Mentees'])

    # Create a Pandas Excel writer using openpyxl as the engine
    excel_file_path = 'generated_files/matches.xlsx'
    with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
        matched_df.to_excel(writer, sheet_name='Matched', index=False)
        unmatched_df.to_excel(writer, sheet_name='Unmatched', index=False)

    return excel_file_path

if __name__ == '__main__':
    app.run(debug=True)
