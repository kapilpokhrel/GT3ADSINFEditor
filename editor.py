#Class to parse and edit ads.inf file

class Editor:
    def __read4Bytes(self, file):
        return int.from_bytes(file.read(4), "little")
    
    def __extract(self):
        pass
        
    def __init__(self, filepath) -> None:
        self.file = open(filepath, "rb")
        if(self.__read4Bytes(self.file) != 0x5344414d):
            raise Exception("Unsupported File Format")
        self.__extract()

    def assemble_and_save(self, filename):
        pass
        
    def add_track(self, filename, ingame_name, artist):
        pass
    
    def remove_track(self):
        pass
