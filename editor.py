#Class to parse and edit ads.inf file

class Editor:
    def __read4Bytes(self, file):
        return int.from_bytes(file.read(4), "little")
    
    def __readString(self, file, ptr):
        file.seek(ptr)
        str = b''
        ch = file.read(1)
        while(ch not in [b'\x00', b'']):
            str += ch
            ch = file.read(1)
        return str.decode('ASCII')
    
    def __extract(self):
        file = self.file
        file.seek(12)
        self.total_tracks = self.__read4Bytes(file)

        playlists = []
        unkData = {} #Each sone has some block of data; currently unkonwn to us

        tracks_added = 0
        while(tracks_added < self.total_tracks):
            pointer = self.__read4Bytes(file)
            trackCount = self.__read4Bytes(file)
            playlists.append({'pointer': pointer, 'trackCount': trackCount})
            tracks_added += trackCount
        
        #Offset where pointers list of each track data starts
        tracksInfoptrs_offset = playlists[0]['pointer']
        self.isPAL = True if(file.tell() < tracksInfoptrs_offset) else False
        
        #PAL version have 8 bytes of data with 1st 4 bytes storing pointer to the 1st unk data and later 0s
        if(self.isPAL):
            file.seek(8, 1)
        
        tracksInfo_offset = self.__read4Bytes(file)
        for playlist in playlists:
            tracks = []

            current_pointer = playlist['pointer']
            for i in range(playlist['trackCount']):
                file.seek(current_pointer)
                basefilename_ptr = self.__read4Bytes(file)
                filename_ptr = self.__read4Bytes(file)
                trackname_ptr = self.__read4Bytes(file)
                artistname_ptr = self.__read4Bytes(file)
                unkData_ptr = self.__read4Bytes(file)
                                   
                current_pointer += 20 #20 bytes for each song

                basefilename = self.__readString(file, basefilename_ptr)
                filename = self.__readString(file, filename_ptr)
                trackname = self.__readString(file, trackname_ptr)
                artistname = self.__readString(file, artistname_ptr)

                unkData_size = 0
                if(playlists.index(playlist) < len(playlists)-1):
                    file.seek(current_pointer+16) #we only want next song's data pointer, so skip 4*4 bytes
                    nextunkData_ptr = self.__read4Bytes(file)
                    unkData_size = nextunkData_ptr - unkData_ptr
                else:
                    unkData_size = tracksInfo_offset - unkData_ptr

                file.seek(unkData_ptr)
                unkData[basefilename] = file.read(unkData_size)
                
                tracks.append({
                    'basename': basefilename,
                    'filename': filename,
                    'trackname': trackname,
                    'artist': artistname
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
        with open(filename, "wb") as file:
            file.write(bytearray([0x4d, 0x41, 0x44, 0x53]))
            file.write(bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
            file.write(self.total_tracks.to_bytes(4, byteorder="little"))

            playlists = self.playlists

            #Offset where list of all pointers to data of all tracks begins
            tracksInfoptrs_offset = 16 + 8*len(playlists)
            if(self.isPAL):
                tracksInfoptrs_offset += 8
            
            current_ptr = tracksInfoptrs_offset
            for playlist in playlists:
                trackCount = playlist['trackCount']
                file.write( current_ptr.to_bytes(4, byteorder="little"))
                file.write( trackCount.to_bytes(4, byteorder="little"))
                current_ptr += 20*trackCount
            
            tracksInfoptrs_blocksize = self.total_tracks*20
            unkData_blocksize = 0
            for key, value in self.unkData.items():
                unkData_blocksize += len(value)
            tracksInfo_offset = tracksInfoptrs_offset + tracksInfoptrs_blocksize + unkData_blocksize
            unkData_offset = tracksInfoptrs_offset + tracksInfoptrs_blocksize
            
            #PAL exclusive
            if(self.isPAL):
                file.write((file.tell() + tracksInfoptrs_blocksize + 8).to_bytes(4, byteorder="little"))
                file.write(bytearray([0x00, 0x00, 0x00, 0x00]))
            
            '''
            Writing trackdata pointers block.
            In orginal file, if multiple track have same artists, artists name are not stored seperately
            rather, other track points to the address where artist name is already localted.
            So to emulate this, we maintain a dict of artists, to store whether their name have been already written or not,
            if yes, we point to previous location of name, else we write the name in file and update the dict.
            This goes for track's name too.

            We write the info of tracks (name, artistname etc) at at the end of the file but
            we need the pointers of those data while writing the tracksInfoptrs block,
            so we first write everyting in a bytearray and
            get the real location by adding the tracksInfo offset to the current length of the bytearray.
            '''

            artists = {}
            tracks = {}
            tracksInfo = b''

            unkData_ptr = unkData_offset
            for playlist in playlists:
                for track in playlist['tracks']:
                    file.write((tracksInfo_offset + len(tracksInfo)).to_bytes(4, byteorder="little"))
                    tracksInfo += bytes(track['basename'], 'ascii') + b'\x00'

                    file.write((tracksInfo_offset + len(tracksInfo)).to_bytes(4, byteorder="little"))
                    tracksInfo += bytes(track['filename'], 'ascii') + b'\x00'

                    trackname = track['trackname']
                    if trackname not in tracks:
                        tracks[trackname] = tracksInfo_offset + len(tracksInfo)
                        tracksInfo += bytes(trackname, 'ascii') + b'\x00'
                    file.write(tracks[trackname].to_bytes(4, byteorder="little"))

                    artist = track['artist']
                    if artist not in artists:
                        artists[artist] = tracksInfo_offset + len(tracksInfo)
                        tracksInfo += bytes(artist, 'ascii') + b'\x00'
                    file.write(artists[artist].to_bytes(4, byteorder="little"))
                    
                    '''
                    If track doesn't have any unkData assined to it, i.e. newly added track,
                    assign pointer to the unk data of 1st track in playlist[2] (main playlist)
                    '''

                    file.write(unkData_ptr.to_bytes(4, byteorder="little"))

                    '''
                    If a track doesn't have unk data assigned to it i.e. newly added track,
                    assign it with a unk Data of 1st track in playlists[2] (main playlist)
                    '''
                    if track['basename'] in self.unkData:
                        unkData_ptr += len(self.unkData[track['basename']])
                    else:
                        unkData_ptr += len(self.unkData[playlists[0]['tracks'][0]['basename']])
                        unkData_ptr += len(self.unkData[playlists[1]['tracks'][0]['basename']])

            for playlist in playlists:
                for track in playlist['tracks']:
                    basename = track['basename']
                    if basename in self.unkData:
                        file.write(self.unkData[basename])
                    else:
                        file.write(self.unkData[playlists[2]['tracks'][0]['basename']])

            file.write(tracksInfo)        

        
            

        
    def add_track(self, basename, filename, trackname, artist):
        self.playlists[2]['tracks'].append({
            'basename': basename,
            'filename': filename,
            'trackname': trackname,
            'artist': artist
        })
        self.playlists[2]['trackCount'] += 1
        self.total_tracks += 1
    
    def remove_track(self, index):
        basename = self.playlists[2]['tracks'][index]['basename']
        del self.playlists[2]['tracks'][index]

        if basename in self.unkData:
            del self.unkData[basename]
        
        self.total_tracks -= 1
        self.playlists[2]['trackCount'] -= 1
