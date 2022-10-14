import PySimpleGUI as sg
from editor import Editor


layout = [
    [sg.Button("Open")]
]

if __name__ == '__main__':
    window = sg.Window("GT3ADSINFEditor", layout=layout);

    while True:
        event, values = window.read();
        if event in (sg.WIN_CLOSED, 'Exit'):
            break;
    
    window.close()
