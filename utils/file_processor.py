import pandas as pd
from collections import defaultdict
import os

# def process_file(filepath):
#     try:
#         # Check keywords in filename or content
#         filename = os.path.basename(filepath)
#         if 'mentor' in filename.lower():
#             process_mentor_spreadsheet(filepath)
#         if 'mentee' in filename.lower():
#             process_mentee_spreadsheet(filepath)
#         else:
#             print(f'Unrecognized spreadsheet: {filename}')

#     except Exception as e:
#         print(f'Error processing file {filepath}: {e}')

def process_mentor_files(filepath):
    try:
        # Implement processing logic for mentor spreadsheet
        print(f'Processing mentor spreadsheet: {filepath}')
        df = pd.read_excel(filepath)
        print(f'Headers of {filepath}: {df.columns.tolist()}')
        # Add specific processing steps for mentor spreadsheet
    except Exception as e:
        print(f'Error processing file {filepath}: {e}')

def process_mentee_files(filepath):
    try:
        # Implement processing logic for mentee spreadsheet
        print(f'Processing mentee spreadsheet: {filepath}')
        df = pd.read_excel(filepath)
        print(f'Headers of {filepath}: {df.columns.tolist()}')
        # Add specific processing steps for mentee spreadsheet
    except Exception as e:
        print(f'Error processing file {filepath}: {e}')

