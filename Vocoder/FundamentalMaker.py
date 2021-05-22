import numpy as np

class PitchMaker:
    def __init__(self, len_block:int, f0:float, fs:float, overlap:float,name:str=None) -> None:
        """
        Unidad generadora de una sola fundamental
        Args:
            len_block (int): [description]
            f0 (float): [description]
            fs (float): [description]
            overlap (float): [description]
            name (str, optional): [description]. Defaults to None.
        """
        self.len_block = len_block
        self.prev_delta = 0
        self.overlap = overlap
        self.f0 = f0
        self.fs = fs
        self.T_samples = int(fs/self.f0)
        self.name = name if name is not None else "nameless Pitch"

    def get_next_block(self):
        block = np.zeros(self.len_block)
        self.current_pos = int(self.len_block*self.overlap) + self.prev_delta 
        if self.current_pos >= self.len_block:
            return block, self.prev_delta-self.len_block
        block[self.current_pos] = 1
        new_delta = 0
        finish = False
        temp_pos = self.current_pos
        while temp_pos >= 0:
            temp_pos = temp_pos - self.T_samples
            if temp_pos >= 0:
                block[temp_pos] = 1
        while not finish:
            dist = self.len_block-self.current_pos
            new_delta = self.T_samples-dist
            if new_delta < 0:
                self.current_pos = self.current_pos+self.T_samples 
                block[self.current_pos] = 1
            else:
                finish = True
        self.prev_delta = new_delta
        return block
    
    def __repr__(self) -> str:
        return f"fundamental frequency of {self.f0}"

    
    def set_fundamental(self, freq:float):
        self.T_samples = int(self.fs/freq)

class ChordMaker():

    def __init__(self, len_block:int, fs:float, overlap:float, name:str=None) -> None:
        """ChordMaker permite combinar diferentes notas

        Args:
            len_block (int): [description]
            fs (float): [description]
            overlap (float): [description]
        """
        self.len_block = len_block
        self.overlap = overlap
        self.fs = fs
        self.name = name if name is not None else "nameless Chord"
        self.notes = {}
        
    def add_note(self, f0):
        new_note = PitchMaker(self.len_block, f0, self.fs, self.overlap)
        if f0 in self.notes.keys():
            print("f0 already in Chord")    
        else:
            self.notes[f0] = new_note

    def remove_note(self, f0):
        try:
            self.notes.pop(f0)
        except KeyError:
            print(f"tried to delte {f0} but no key was found with that name")

    def generate_block(self):
        all_notes = np.zeros(self.len_block)
        for pitch_gen in self.notes.values():
            all_notes = all_notes + pitch_gen.get_next_block()
        return all_notes
    
    def __repr__(self) -> str:
        a = f"Este acorde contiene {len(self.notes)} \n"
        b = "Las notas son"
        c = ""
        for f0 in self.notes.keys():
            c += f"f0: {f0}\n"
        
        return a+b+c
