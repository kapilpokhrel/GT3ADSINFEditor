# GT3ADSINFEDITOR
GUI Tool for editing Gran Turismo 3 asd.inf files. It allows addition, removal, and to change the order of music tracks inside the .inf file.

## Running the Script
To run the python script or the build the executable for youself then first you have to have python installed and you have to build the dependency with
```
pip install -r requirements.txt
```

To run the script, use
```
python main.py
```

To build the stand alone executable file for yourself, run the following command and you'll have the executable inside the dist folder.
```
pyinstaller -F -n "GT3PMBBINEditor" main.py
```

## Credits
- Misuka ミ ス カ - File format reverse engineering
- [kapilpokhrel](https://github.com/kapilpokhrel/) - Programming

## Other Resources for Gran Turismo 3 modification
- [GT3PMBBINEditor](https://github.com/kapilpokhrel/GT3PMBBINEditor)