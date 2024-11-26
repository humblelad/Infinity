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

def check_sensitive_files(path):
    security_sections = {
        "Configuration Files": {
            "patterns": [
                ("web.config", "High", "644", "Microsoft IIS Web configuration: Ensure only web server user can read."),
                ("config.ini", "High", "644", "Application configuration file: Restrict to application user access only."),
                ("config", "High", "644", "Generic configuration file: Limit access to application owner."),
                ("config.json", "High", "644", "JSON configuration file: Restrict to application user."),
                (".docker/config.json", "High", "600", "Docker credentials file: Must be readable only by Docker daemon user."),
                ("appsettings.json", "High", "644", ".NET Application settings may contain connection strings. Limit to app user."),
                (".htaccess", "Medium", "644", "Apache configuration file: Should be readable only by web server."),
                (".env", "Critical", "600", "Environment variables file may contain secrets. Must be readable only by owner."),
                ("credentials.json", "Critical", "600", "Credentials storage file: Strictly limit to owner access only."),
                (".git-credentials", "Critical", "600", "Git credentials file: Must be accessible only by Git user."),
                (".aws/credentials", "Critical", "600", "AWS credentials file: Restrict to AWS CLI user only.")
            ]
        },
        "Keys and Private Files": {
            "patterns": [
                (".key", "Critical", "600", "Private key file: Must be readable only by service owner."),
                (".pem", "Critical", "600", "SSL/SSH private key: Strictly limit to service user access."),
                ("server.crt", "Critical", "600", "SSL certificate: Restrict access to web server user only."),
                ("id_rsa", "Critical", "600", "SSH private key: Must be accessible only by key owner."),
                ("shadow", "Critical", "600", "Linux password file: Restrict to root access only."),
                ("passwd", "Critical", "644", "User account file: Should be world-readable but write-protected.")
            ]
        },
        "Log Files": {
            "patterns": [
                ("error.log", "Medium", "644", "Avoid log poisoning by restricting access to log files."),
                ("access.log", "Medium", "644", "Avoid log poisoning by restricting access to log files.")
            ]
        },
        "Backup and Data Files": {
            "patterns": [
                (".bak", "High", "600", "Backup files may contain sensitive data: Limit to backup service user."),
                (".backup", "High", "600", "Backup archives may contain sensitive content: Restrict to backup user."),
                (".sql", "Medium", "600", "Database dumps may contain sensitive data: Limit to database admin access."),
                (".sqlite", "High", "600", "SQLite database files: Restrict to application user only.")
            ]
        }
    }
    
    security_issues = []
    
    # Define paths to exclude
    excluded_paths = ['.venv', 'site-packages', 'lib']
    
    for root, dirs, files in os.walk(path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_paths]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_perms = oct(os.stat(file_path).st_mode)[-3:]
                
                for section, content in security_sections.items():
                    for pattern, severity, recommended_chmod, recommendation in content["patterns"]:
                        if pattern.lower() in file.lower():
                            if int(file_perms, 8) > int(recommended_chmod, 8):
                                security_issues.append({
                                    'file': file_path,
                                    'permission': file_perms,
                                    'risk_level': severity,
                                    'section': section,
                                    'recommendation': f'{recommendation} (change to: {recommended_chmod})'
                                })
                
            except Exception as e:
                continue
                
    return security_issues

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
    root_path = request.args.get('path', '/Users')
    include_files = request.args.get('include_files', 'false').lower() == 'true'
    
    if not os.path.isabs(root_path):
        root_path = os.path.abspath(root_path)

    if not os.path.exists(root_path):
        abort(404, description="Root path not found")

    security_issues = check_sensitive_files(root_path)
    file_structure = get_file_structure(root_path, include_files)
    
    return jsonify({
        'structure': file_structure,
        'security_analysis': security_issues
    })




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
