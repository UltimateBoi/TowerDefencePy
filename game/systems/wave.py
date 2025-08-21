"""
Wave system for managing bloon spawning
"""
from typing import List, Optional, Tuple, TYPE_CHECKING
from ..entities.bloon_types import BloonType

if TYPE_CHECKING:
    from ..entities.bloon import Bloon


class Wave:
    def __init__(self, bloon_types: List[BloonType], counts: List[int], spawn_delay: float = 1000):
        self.bloon_types = bloon_types
        self.counts = counts
        self.spawn_delay = spawn_delay # milliseconds between spawns
        self.spawned = 0
        self.total_bloons = sum(counts)
        self.last_spawn_time = 0
        self.current_type_index = 0
        self.current_type_count = 0
        
    def spawn_next_bloon(self, current_time: float, path: List[Tuple[int, int]]) -> Optional['Bloon']:
        if self.spawned >= self.total_bloons:
            return None
            
        if current_time - self.last_spawn_time < self.spawn_delay:
            return None
        
        # Spawn bloon of current type
        if self.current_type_index < len(self.bloon_types):
            bloon_type = self.bloon_types[self.current_type_index]
            from ..entities.bloon import Bloon
            bloon = Bloon(bloon_type, path)
            
            self.spawned += 1
            self.current_type_count += 1
            self.last_spawn_time = current_time
            
            # Move to next type if current type is exhausted
            if self.current_type_count >= self.counts[self.current_type_index]:
                self.current_type_index += 1
                self.current_type_count = 0
            
            return bloon
        
        return None
    
    def is_complete(self) -> bool:
        return self.spawned >= self.total_bloons
