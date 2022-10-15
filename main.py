import PySimpleGUI as sg
from editor import Editor

table = sg.Table(
    values=[],
    headings=['Track', 'Filename', 'Artist'],
    justification='left',
    auto_size_columns=False,
    col_widths=[40, 12, 20],
    expand_x=True,
    expand_y=True,
    enable_events=True,
    key='-TABLE-',
    display_row_numbers=True,
    vertical_scroll_only=False,
    select_mode=sg.TABLE_SELECT_MODE_BROWSE
)

layout = [
    [sg.Button("Open")],
    [table]
]

def playlist_to_TableValues(playlist):
    return [*[[lst['trackname'], lst['filename'], lst['artistname']] for lst in playlist['tracks'] ]]

selected_track = 0
if __name__ == '__main__':
    window = sg.Window("GT3ADSINFEditor", layout=layout, size=(720,480));

    editor = None
    while True:
        event, values = window.read();
        if event in (sg.WIN_CLOSED, 'Exit'):
            break;
        
        elif event == 'Open':
            filepath = sg.popup_get_file("Choose the .inf file to edit.")
            if filepath not in [None, ""]:
                try:
                    editor = Editor(filepath)
                    window['-TABLE-'].update(
                        values=playlist_to_TableValues(editor.playlists[2]), # We are only intrested in 3rd playlist
                        select_rows=[selected_track]
                    )
                except Exception as e:
                    sg.popup(e)
    
    window.close()
