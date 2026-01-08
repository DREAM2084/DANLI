from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from nav_subsystem.scene_loader import SceneObject


@dataclass
class SemanticObject:
    object_id: str
    object_type: str
    position: Tuple[float, float, float]

    def distance_to(self, agent_position: Tuple[float, float, float]) -> float:
        ax, ay, az = agent_position
        ox, oy, oz = self.position
        return ((ax - ox) ** 2 + (ay - oy) ** 2 + (az - oz) ** 2) ** 0.5


class SemanticMap:
    def __init__(self, objects: Iterable[SceneObject]):
        self._objects: List[SemanticObject] = [
            SemanticObject(obj.object_id, obj.object_type, obj.position) for obj in objects
        ]
        self._index: Dict[str, List[SemanticObject]] = {}
        for obj in self._objects:
            self._index.setdefault(obj.object_type.lower(), []).append(obj)

    def search(self, target_type: str) -> List[SemanticObject]:
        return list(self._index.get(target_type.lower(), []))

    def closest(self, target_type: str, agent_position: Tuple[float, float, float]) -> Optional[SemanticObject]:
        candidates = self.search(target_type)
        if not candidates:
            return None
        return min(candidates, key=lambda obj: obj.distance_to(agent_position))
