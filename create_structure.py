import os
from pathlib import Path

# Define the structure
structure = {
    'app.py': '',
    '.env': '',
    'requirements.txt': '',
    'static/css': {},
    'static/js': {},
    'static/images': {},
    'templates': {
        'base.html': '',
        'index.html': '',
        'partials': {
            'header.html': '',
            'footer.html': '',
            'side-icons.html': ''
        }
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = Path(base_path) / name
        if isinstance(content, dict):  # It's a directory
            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)
        else:  # It's a file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()  # Create empty file
            # Optionally write content to file
            if content:
                path.write_text(content)

# Run it
create_structure('.', structure)
print("Structure created successfully!")