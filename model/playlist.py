from typing import List
import random
from model.song import Song

class PlayList:
    def __init__(self):
        self.queue: List[Song] = [] 
        self.history: List[Song] = [] 
        self.loop = False
        
    def add_to_queue(self, item):
        self.queue.append(item) 

    def remove_from_queue(self, item):
        if item in self.queue:
            self.queue.remove(item)
            return True
        return False
    
    def suffle_queue(self):
        random.shuffle(self.queue)
    
    def next_song(self):
        if not self.queue:
            return None
        else:
            song = self.queue.pop(0)
            self.history.append(song)
            return song
        
    def clear_queue(self):
        self.queue = []
            
        