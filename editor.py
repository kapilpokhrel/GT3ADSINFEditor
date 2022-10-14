#Class to parse and edit ads.inf file

class Editor:
    def __read4Bytes(self, file):
        return int.from_bytes(file.read(4), "little")
    
    def __extract(self):
        file = self.file
        file.seek(12)
        self.total_tracks = self.__read4Bytes(file)

        playlists = []
        unkData = {} #Each sone has some block of data; currently unkonwn to us

        tracks_added = 0
        while(tracks_added < self.total_tracks):
            pointer = self.__read4bytes(file)
            trackCount = self.__read4bytes(file)
            playlists.append({'pointer': pointer, 'trackCount': trackCount})
            tracks_added += trackCount
        
        #Offset where pointers list of each track data starts
        tracksInfoptrs_offset = playlists[0]['pointer']
        self.isPAL = True if(file.tell() < tracksInfoptrs_offset) else False
        
        #PAL version have 8 bytes of data with 1st 4 bytes storing pointer to the 1st unk data and later 0s
        if(self.isPAL):
            file.seek(8, 1)
        
        tracksInfo_offset = self.__read4bytes(file)
        for playlist in playlists:
            tracks = []

            current_pointer = playlist['pointer']
            for i in range(len(playlist['trackCount'])):
                file.seek(current_pointer)
                basefilename_ptr = self.__read4bytes(file)
                filename_ptr = self.__read4bytes(file)
                trackname_ptr = self.__read4bytes(file)
                artistname_ptr = self.__read4bytes(file)
                unkData_ptr = self.__read4bytes(file)
                                   
                current_pointer += 20 #20 bytes for each song

                basefilename = self.__readstring(file, basefilename_ptr)
                filename = self.__readstring(file, filename_ptr)
                trackname = self.__readstring(file, trackname_ptr)
                artistname = self.__readstring(file, artistname_ptr)

                unkData_size = 0
                if(playlists.index(playlist) < len(playlists)-1):
                    file.seek(current_pointer+16) #we only want next song's data pointer, so skip 4*4 bytes
                    nextunkData_ptr = self.__read4bytes(file)
                    unkData_size = nextunkData_ptr - unkData_ptr
                else:
                    unkData_size = tracksInfo_offset - unkData_ptr

                file.seek(unkData_ptr)
                unkData[basefilename] = file.read(unkData_size)
                
                tracks.append({
                    'basefilename': basefilename,
                    'filename': filename,
                    'trackname': trackname,
                    'artistname': artistname
                })
            
            playlist.pop('pointer')
            playlist['tracks'] = tracks
        
        self.playlists = playlists
        self.unkData = unkData

    def __init__(self, filepath) -> None:
        self.file = open(filepath, "rb")
        if(self.__read4Bytes(self.file) != 0x5344414d):
            raise Exception("Unsupported File Format")
        self.__extract()

    def assemble_and_save(self, filename):
        pass
        
    def add_track(self, filename, trackname, artist):
        pass
    
    def remove_track(self):
        pass
