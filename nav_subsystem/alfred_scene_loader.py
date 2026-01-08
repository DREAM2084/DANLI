import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class AlfredSceneConfig:
    scene_number: int
    object_poses: List[Dict[str, Any]]
    object_toggles: List[Dict[str, Any]]
    dirty_and_empty: bool
    init_action: Dict[str, Any]


def load_alfred_scene_config(path: str) -> AlfredSceneConfig:
    scene_path = Path(path)
    if not scene_path.exists():
        raise FileNotFoundError(f"ALFRED scene json not found: {scene_path}")

    with scene_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if "scene" not in payload:
        raise KeyError("Missing 'scene' key in ALFRED json")

    scene = payload["scene"]
    return AlfredSceneConfig(
        scene_number=int(scene["scene_num"]),
        object_poses=list(scene.get("object_poses", [])),
        object_toggles=list(scene.get("object_toggles", [])),
        dirty_and_empty=bool(scene.get("dirty_and_empty", False)),
        init_action=dict(scene.get("init_action", {})),
    )
