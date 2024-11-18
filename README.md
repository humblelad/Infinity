# Infinity
Easy to manage Linux File permission for System Admins

## Installation

1. Clone the repository
```s
git clone https://github.com/humblelad/Infinity.git
```
2. Install Virtual Environment
```s
apt install python3-venv
```
3. Create a virtual environment
```sh
# Tested in Python 3.6.9 venv (Pycharm)
python3 -m venv virtual-env-name
source virtual-env-name/bin/activate
```
4. Install the requirements
```s
pip install -r requirements.txt
```
5. Go to colors.txt in /templates to configure the color specification for a particular user. 

 6. Set necessary permissions
```sh
sudo visudo
# type i to edit the file
# add the following line at the end of the file
# Put helper.sh with the owner which is designated as sysadmin:
linuxuserwhoissysadmin ALL=(ALL) NOPASSWD:/file_path/Infinity/sysadmin/helper.sh
# type esc to exit the editor
# type :wq to save and exit
```
7. Run the App
```sh
python3 -m flask run 
# Flask would start in http://127.0.0.1:5000/
```

## Usage

- Query the Folder in the Input box and click the `Submit` button
- The results will be displayed in the table
- If file needs to be displayed along with folders, check `Include Files` box and `Submit` again
- click the Folder names to display the current permissions
- select a node and press `spacebar` to bring the modal box.
- enter the new permissions and click `Update`

