import logging
from flask import Flask, jsonify, send_from_directory, render_template, request, abort
import os
import stat
import pwd
import grp
import subprocess
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_permissions(path):
    st = os.stat(path)
    return stat.filemode(st.st_mode)



def get_file_structure(path, include_files=False):
    structure = []
    if os.path.isdir(path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                structure.append({
                    "name": entry,
                    "path": full_path,
                    "type": "directory",
                    "permissions": get_permissions(full_path),
                    "owner": pwd.getpwuid(os.stat(full_path).st_uid).pw_name,
                    "group": grp.getgrgid(os.stat(full_path).st_gid).gr_name,
                    "children": get_file_structure(full_path, include_files)
                })
            elif include_files and os.path.isfile(full_path):
                structure.append({
                    "name": entry,
                    "path": full_path,
                    "type": "file",
                    "permissions": get_permissions(full_path),
                    "owner": pwd.getpwuid(os.stat(full_path).st_uid).pw_name,
                    "group": grp.getgrgid(os.stat(full_path).st_gid).gr_name
                })
    return structure

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates/colors.txt')
def serve_colors():
    return send_from_directory('templates', 'colors.txt')


@app.route('/files', methods=['GET'])
def list_files():
    root_path = request.args.get('path', '/Users')  # Default to /Users if no path is provided
    include_files = request.args.get('include_files', 'false').lower() == 'true'
    app.logger.info(f"Requested path: {root_path}, include_files: {include_files}")

    # Ensure the path is absolute
    if not os.path.isabs(root_path):
        root_path = os.path.abspath(root_path)

    if not os.path.exists(root_path):
        app.logger.error(f"Path not found: {root_path}")
        abort(404, description="Root path not found")

    file_structure = get_file_structure(root_path, include_files)
    return jsonify(file_structure)



@app.route('/update_permissions', methods=['POST'])
def update_permissions():
    data = request.get_json()
    path = data.get('path')
    new_permissions = data.get('permissions')

    if not path or not new_permissions:
        return jsonify({'success': False, 'error': 'Invalid input'})

    # Validate the path
    if not os.path.exists(path):
        return jsonify({'success': False, 'error': 'Path does not exist'})

    # Validate the permissions
    if not new_permissions.isdigit() or len(new_permissions) != 3 or not all(c in '01234567' for c in new_permissions):
        return jsonify({'success': False, 'error': 'Invalid permissions format'})
    try:
        result = subprocess.run(['sudo', './helper.sh', path, new_permissions], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            updated_permissions = stat.filemode(os.stat(path).st_mode)
            app.logger.info(f"Permissions for {path} updated to {updated_permissions}")
            return jsonify({'success': True, 'permissions': updated_permissions})
        else:
            app.logger.error(f"Failed to update permissions: {result.stderr}")
            return jsonify({'success': False, 'error': result.stderr})
    except Exception as e:
        app.logger.error(f"Failed to update permissions: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('/', filename)

if __name__ == '__main__':
    app.run(debug=True)
