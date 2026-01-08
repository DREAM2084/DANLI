import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class SceneObject:
    object_id: str
    object_type: str
    position: Tuple[float, float, float]


@dataclass(frozen=True)
class SceneData:
    scene_id: str
    agent_position: Tuple[float, float, float]
    objects: List[SceneObject]


_POSITION_KEYS = ("position", "center", "centroid", "location")


def _parse_position(raw_obj: Dict) -> Optional[Tuple[float, float, float]]:
    for key in _POSITION_KEYS:
        value = raw_obj.get(key)
        if isinstance(value, dict):
            try:
                return (float(value["x"]), float(value["y"]), float(value["z"]))
            except (KeyError, TypeError, ValueError):
                continue
        if isinstance(value, (list, tuple)) and len(value) == 3:
            try:
                return (float(value[0]), float(value[1]), float(value[2]))
            except (TypeError, ValueError):
                continue
    return None


def _parse_object_type(raw_obj: Dict) -> Optional[str]:
    for key in ("objectType", "type", "name", "category"):
        value = raw_obj.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _parse_object_id(raw_obj: Dict, fallback_index: int) -> str:
    for key in ("objectId", "id", "instanceId", "instance_id"):
        value = raw_obj.get(key)
        if isinstance(value, str) and value:
            return value
    return f"object_{fallback_index}"


def _extract_objects(raw_objects: Iterable[Dict]) -> List[SceneObject]:
    objects: List[SceneObject] = []
    for idx, raw in enumerate(raw_objects):
        if not isinstance(raw, dict):
            continue
        object_type = _parse_object_type(raw)
        position = _parse_position(raw)
        if object_type is None or position is None:
            continue
        object_id = _parse_object_id(raw, idx)
        objects.append(SceneObject(object_id=object_id, object_type=object_type, position=position))
    return objects


def load_scene_from_json(path: str) -> SceneData:
    scene_path = Path(path)
    if not scene_path.exists():
        raise FileNotFoundError(f"Scene json not found: {scene_path}")

    with scene_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    scene_id = payload.get("scene_id") or payload.get("sceneId") or scene_path.stem

    agent_position = (0.0, 0.0, 0.0)
    agent_block = payload.get("agent") or payload.get("agent_position") or {}
    if isinstance(agent_block, dict):
        position = _parse_position({"position": agent_block.get("position", agent_block)})
        if position is not None:
            agent_position = position

    raw_objects = payload.get("objects") or payload.get("scene") or []
    objects = _extract_objects(raw_objects)

    return SceneData(scene_id=scene_id, agent_position=agent_position, objects=objects)
