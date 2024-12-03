# Infinity

A Tree-node Dashboard designed for System Administrators to efficiently manage and analyze Linux file permissions through a visual interface.

Features like Visual File System Navigation, File Permission Management, Automatic detection and mitigation of overly permissive files. Check wiki for more info.

## Installation
Follow the steps mentioned in [Wiki Installation](https://github.com/humblelad/Infinity/wiki/2.-Installation) to install Infinity automatically.

## Key Features
Refer to the [Wiki Features](https://github.com/humblelad/Infinity/wiki/3.-Features) for a overview of the features offered by Infinity.

## How to Use
Refer to the [Wiki Usage](https://github.com/humblelad/Infinity/wiki/4.-App-Usage) for detailed instructions on how to use Infinity.

### Alternate Manual method
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

## Contributors

<table>
  <tr>
    <td align="center"><a href="https://github.com/humblelad"><img src="https://avatars.githubusercontent.com/u/30574278?v=4" width="100px;" alt=""/><br /><sub><b>humblelad</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/VasanthVanan"><img src="https://avatars.githubusercontent.com/u/30904627?v=4" width="100px;" alt=""/><br /><sub><b>Vasanth Vanan</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/gpmore"><img src="https://avatars.githubusercontent.com/u/107632464?v=4" width="100px;" alt=""/><br /><sub><b>gpmore</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/RincyMariamThomas"><img src="https://avatars.githubusercontent.com/u/51988830?v=4" width="100px;" alt=""/><br /><sub><b>RincyMariamThomas</b></sub></a><br /></td>
</table>
