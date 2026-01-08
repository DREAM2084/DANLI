import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

if __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from nav_subsystem.alfred_scene_loader import AlfredSceneConfig, load_alfred_scene_config


@dataclass
class SemanticObject:
    object_id: str
    object_type: str
    position: Tuple[float, float, float]


class SemanticMap:
    def __init__(self) -> None:
        self._objects: Dict[str, Dict[str, SemanticObject]] = {}

    def update(self, objects: Iterable[SemanticObject]) -> None:
        for obj in objects:
            self._objects.setdefault(obj.object_type.lower(), {})[obj.object_id] = obj

    def find(self, target_type: str) -> List[SemanticObject]:
        return list(self._objects.get(target_type.lower(), {}).values())


class AlfredNavigator:
    def __init__(self, controller) -> None:
        self.controller = controller
        self.semantic_map = SemanticMap()

    def _extract_objects(self, event) -> List[SemanticObject]:
        objects = []
        for obj in event.metadata.get("objects", []):
            position = obj.get("position")
            if position is None:
                continue
            objects.append(
                SemanticObject(
                    object_id=obj.get("objectId", obj.get("name", "")),
                    object_type=obj.get("objectType", obj.get("name", "")),
                    position=(float(position["x"]), float(position["y"]), float(position["z"])),
                )
            )
        return objects

    def _closest(self, candidates: List[SemanticObject], agent_pos: Dict[str, float]) -> Optional[SemanticObject]:
        if not candidates:
            return None
        ax, ay, az = agent_pos["x"], agent_pos["y"], agent_pos["z"]

        def _distance(obj: SemanticObject) -> float:
            ox, oy, oz = obj.position
            return ((ax - ox) ** 2 + (ay - oy) ** 2 + (az - oz) ** 2) ** 0.5

        return min(candidates, key=_distance)

    def step_and_update(self, action: Dict) -> None:
        event = self.controller.step(action)
        self.semantic_map.update(self._extract_objects(event))

    def search_for_object(self, target_type: str, max_steps: int) -> Optional[SemanticObject]:
        action_cycle = [
            {"action": "RotateLeft", "forceAction": True},
            {"action": "MoveAhead", "forceAction": True},
            {"action": "RotateRight", "forceAction": True},
            {"action": "MoveAhead", "forceAction": True},
            {"action": "LookUp", "forceAction": True},
            {"action": "LookDown", "forceAction": True},
        ]

        for step in range(max_steps):
            current = self.semantic_map.find(target_type)
            if current:
                agent_pos = self.controller.last_event.metadata["agent"]["position"]
                return self._closest(current, agent_pos)

            self.step_and_update(action_cycle[step % len(action_cycle)])

        return None


def _safe_step(controller, action: Dict) -> None:
    try:
        controller.step(action)
    except ValueError as exc:
        action_name = action.get("action")
        print(f"Skipping unsupported action '{action_name}': {exc}")


def _initialize_scene(controller, scene: AlfredSceneConfig) -> None:
    scene_name = f"FloorPlan{scene.scene_number}"
    controller.reset(scene_name)
    _safe_step(
        dict(
            action="Initialize",
            gridSize=0.25,
            cameraY=0.675,
            renderImage=True,
            renderDepthImage=False,
            renderClassImage=False,
            renderObjectImage=False,
            visibility_distance=1.5,
            makeAgentsVisible=False,
        )
    )

    if scene.object_toggles:
        _safe_step(controller, dict(action="SetObjectToggles", objectToggles=scene.object_toggles))
    if scene.dirty_and_empty:
        _safe_step(controller, dict(action="SetStateOfAllObjects", StateChange="CanBeDirty", forceAction=True))
        _safe_step(controller, dict(action="SetStateOfAllObjects", StateChange="CanBeFilled", forceAction=False))
    if scene.object_poses:
        _safe_step(controller, dict(action="SetObjectPoses", objectPoses=scene.object_poses))
    if scene.init_action:
        _safe_step(controller, dict(scene.init_action))


def main() -> None:
    parser = argparse.ArgumentParser(description="ALFRED scene navigation demo.")
    parser.add_argument("--scene", required=True, help="Path to ALFRED traj_data.json")
    parser.add_argument("--target", required=True, help="Target object type, e.g., Mug")
    parser.add_argument("--max-steps", type=int, default=40, help="Max exploration steps")
    args = parser.parse_args()

    try:
        from ai2thor.controller import Controller
    except ImportError as exc:
        raise SystemExit("ai2thor is required for this demo. Install ai2thor and retry.") from exc

    controller = Controller()
    scene = load_alfred_scene_config(args.scene)
    _initialize_scene(controller, scene)

    navigator = AlfredNavigator(controller)
    navigator.step_and_update({"action": "Pass"})

    result = navigator.search_for_object(args.target, args.max_steps)
    if result is None:
        print(f"Target '{args.target}' not found after {args.max_steps} steps.")
    else:
        print(f"Found {result.object_type} (id={result.object_id}) at {result.position}")

    controller.stop()


if __name__ == "__main__":
    main()
