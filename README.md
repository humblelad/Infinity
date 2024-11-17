# Infinity
Easy to manage Linux File permission for System Admins


sudo visudo
Put helper.sh with the owner which is designated as sysadmin:

linuxuserwhoissysadmin ALL=(ALL) NOPASSWD:/filepath/helper.sh

Tested in Python 3.6.9 venv (Pycharm)

source venv/bin/activate

python3 -m flask run 

Flask would start in http://127.0.0.1:5000/
