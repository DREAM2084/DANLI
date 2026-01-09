from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from nav_subsystem.scene_loader import SceneData, SceneObject
from nav_subsystem.semantic_map import SemanticMap


@dataclass
class SearchResult:
    target_type: str
    found: bool
    object_id: Optional[str]
    position: Optional[Tuple[float, float, float]]
    explored: bool
    candidates: List[Tuple[str, Tuple[float, float, float]]]


class NavigationSubsystem:
    """
    Minimal navigation/search subsystem wrapper.

    This keeps DANLI-like responsibilities (search + return target position) but
    uses a simplified semantic map derived from scene JSON. It can be extended
    later to hook into AI2-THOR world-state updates.
    """

    def __init__(self, scene: SceneData):
        self.scene = scene
        self.semantic_map = SemanticMap(scene.objects)
        self.agent_position = scene.agent_position

    def update_agent_position(self, position: Tuple[float, float, float]) -> None:
        self.agent_position = position

    def update_objects(self, objects: List[SceneObject]) -> None:
        self.semantic_map.update(objects)

    def search_target(self, target_type: str) -> SearchResult:
        candidates = self.semantic_map.search(target_type)
        candidate_payload = [(obj.object_id, obj.position) for obj in candidates]

        if not candidates:
            return SearchResult(
                target_type=target_type,
                found=False,
                object_id=None,
                position=None,
                explored=True,
                candidates=[],
            )

        closest = self.semantic_map.closest(target_type, self.agent_position)
        return SearchResult(
            target_type=target_type,
            found=True,
            object_id=closest.object_id if closest else None,
            position=closest.position if closest else None,
            explored=False,
            candidates=candidate_payload,
        )
