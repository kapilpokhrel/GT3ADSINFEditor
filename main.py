import PySimpleGUI as sg
from editor import Editor
import json


layout = [
    [sg.Button("Open")]
]

if __name__ == '__main__':
    window = sg.Window("GT3ADSINFEditor", layout=layout);

    editor = None
    while True:
        event, values = window.read();
        if event in (sg.WIN_CLOSED, 'Exit'):
            break;
        
        elif event == 'Open':
            try:
                filepath = sg.popup_get_file("Choose the .inf file to edit.")
                editor = Editor(filepath)
                with open("playlists.json") as jsonfile:
                    json.dump(editor.playlists, jsonfile)
            except Exception as e:
                sg.popup(e)
    
    window.close()
