import argparse
import sys
from pathlib import Path

if __package__ is None:  # allow direct execution
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from nav_subsystem.scene_loader import load_scene_from_json
from nav_subsystem.search_subsystem import NavigationSubsystem


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal navigation search demo.")
    parser.add_argument("--scene", required=True, help="Path to scene json file")
    parser.add_argument("--target", required=True, help="Target object type (e.g., Mug)")
    args = parser.parse_args()

    scene_path = Path(args.scene)
    scene = load_scene_from_json(str(scene_path))
    subsystem = NavigationSubsystem(scene)

    result = subsystem.search_target(args.target)

    print(f"Scene: {scene.scene_id}")
    print(f"Target: {result.target_type}")
    print(f"Found: {result.found}")
    if result.found:
        print(f"Object ID: {result.object_id}")
        print(f"Position: {result.position}")
    else:
        print("No matching objects found; explore/update state and retry.")


if __name__ == "__main__":
    main()
