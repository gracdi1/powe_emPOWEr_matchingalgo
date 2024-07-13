# utils/__init__.py

# You can import modules here to make them available when utils is imported
from .file_processor import process_file

# Optionally define __all__ to specify what gets imported with `from utils import *`
__all__ = ['process_file']

# You can also put initialization code here if needed
print("Initializing utils package...")
