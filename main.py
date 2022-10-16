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
    [sg.Button("Open"), sg.Button("Save"), sg.VerticalSeparator(), sg.Button("Add"), sg.Button("Remove")],
    [table]
]

def playlist_to_TableValues(playlist):
    return [*[[lst['trackname'], lst['filename'], lst['artist']] for lst in playlist['tracks'] ]]

def add_window():
    trackinfo = None
    layout = [
        [sg.Text("Enter the details of the track:")],
        [sg.Text("Filename: ", s=13, justification='r'), sg.In(size=(25, 1), enable_events=True, key="-FILENAME-")],
        [sg.Text("In-game name: ", s=13, justification='r'), sg.In(size=(25, 1), enable_events=True, key="-TRACKNAME-")],
        [sg.Text("Artist: ", s=13, justification='r'), sg.In(size=(25, 1), enable_events=True, key="-ARTIST-")],
        [sg.Push(), sg.Button("Add"), sg.Button("Cancel"), sg.Push()]
    ]
    add_window = sg.Window("Track Adder", layout, modal=True)
    while True:
        event, values = add_window.read()
        if event in (sg.WIN_CLOSED, 'Exit') or event == 'Cancel':
            break
            
        elif event == 'Add':
            filename = values['-FILENAME-']
            trackname = values['-TRACKNAME-']
            artist = values['-ARTIST-']
            if filename == "":
                sg.popup("Filename can't be empty")
            elif trackname == "":
                sg.popup("In-game trackname can't be empty")
            else:
                filename = filename.split('.')
                if(len(filename) == 2):
                    if(filename[1] == "ads"):
                        artist = "NONE" if artist == "" else artist
                        trackinfo = [filename[0], values['-FILENAME-'], trackname, artist]
                        break
                    else:
                        sg.popup("filename doesn't have .ads extension")
                else:
                    sg.popup("Filename doesn't look like a actual filename")
        
    add_window.close()
    return trackinfo

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
        
        elif event == 'Add':
            if editor == None:
                sg.popup("Open the ads file first to add track.")
            else:
                info = add_window()
                if info is not None:
                    editor.add_track(info[0], info[1], info[2], info[3])
                    window['-TABLE-'].update(
                        values=playlist_to_TableValues(editor.playlists[2]), # We are only intrested in 3rd playlist
                        select_rows=[selected_track]
                    )
        
        elif event == 'Remove':
            if editor == None:
                sg.popup("Open the ads file first to add track.")
            elif editor.playlists[2]['trackCount'] == 0:
                pass
            else:
                editor.remove_track(selected_track)
                selected_track = min(selected_track, editor.playlists[2]['trackCount']-1)
                window['-TABLE-'].update(
                    values=playlist_to_TableValues(editor.playlists[2]), # We are only intrested in 3rd playlist
                    select_rows=[] if editor.playlists[2]['trackCount'] == 0 else [selected_track]
                )
        
        elif event == '-TABLE-':
            if(len(values['-TABLE-']) >= 1):
                selected_track = values['-TABLE-'][0]
            else:
                selected_track = 0
        
        elif event == 'Save':
            editor.assemble_and_save("out.inf")
            sg.popup("Saved as "+"out.inf")
    
    window.close()
