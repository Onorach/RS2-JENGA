#!/usr/bin/env python3
"""Spawn Jenga blocks with per-layer delays so each layer settles before the next."""

import os
import subprocess
import sys
import time

from ament_index_python.packages import get_package_share_directory


# (entity_name, block_sdf_key, x, y, z, yaw) — "odd" or "even" for block type
# z values: 20mm above settle position so each layer drops gently onto the one below
TOWER_LAYOUT = [
    # Layer 1 (odd: long axis Y)
    ("jenga_L1_B1", "odd", 0.325, 0.0, 1.1195, 0.0),
    ("jenga_L1_B2", "odd", 0.350, 0.0, 1.1195, 0.0),
    ("jenga_L1_B3", "odd", 0.375, 0.0, 1.1195, 0.0),
    # Layer 2 (even)
    ("jenga_L2_B1", "even", 0.35, -0.025, 1.1345, 0.0),
    ("jenga_L2_B2", "even", 0.35, 0.0, 1.1345, 0.0),
    ("jenga_L2_B3", "even", 0.35, 0.025, 1.1345, 0.0),
    # Layer 3 (odd)
    ("jenga_L3_B1", "odd", 0.325, 0.0, 1.1495, 0.0),
    ("jenga_L3_B2", "odd", 0.350, 0.0, 1.1495, 0.0),
    ("jenga_L3_B3", "odd", 0.375, 0.0, 1.1495, 0.0),
    # Layer 4 (even)
    ("jenga_L4_B1", "even", 0.35, -0.025, 1.1645, 0.0),
    ("jenga_L4_B2", "even", 0.35, 0.0, 1.1645, 0.0),
    ("jenga_L4_B3", "even", 0.35, 0.025, 1.1645, 0.0),
    # Layer 5 (odd)
    ("jenga_L5_B1", "odd", 0.325, 0.0, 1.1795, 0.0),
    ("jenga_L5_B2", "odd", 0.350, 0.0, 1.1795, 0.0),
    ("jenga_L5_B3", "odd", 0.375, 0.0, 1.1795, 0.0),
    # Layer 6 (even)
    ("jenga_L6_B1", "even", 0.35, -0.025, 1.1945, 0.0),
    ("jenga_L6_B2", "even", 0.35, 0.0, 1.1945, 0.0),
    ("jenga_L6_B3", "even", 0.35, 0.025, 1.1945, 0.0),
    # Layer 7 (odd)
    ("jenga_L7_B1", "odd", 0.325, 0.0, 1.2095, 0.0),
    ("jenga_L7_B2", "odd", 0.350, 0.0, 1.2095, 0.0),
    ("jenga_L7_B3", "odd", 0.375, 0.0, 1.2095, 0.0),
    # Layer 8 (even)
    ("jenga_L8_B1", "even", 0.35, -0.025, 1.2245, 0.0),
    ("jenga_L8_B2", "even", 0.35, 0.0, 1.2245, 0.0),
    ("jenga_L8_B3", "even", 0.35, 0.025, 1.2245, 0.0),
]


def main():
    pkg_share = get_package_share_directory("ur3e_controller")
    block_files = {
        "odd": os.path.join(pkg_share, "config", "jenga_block_odd.sdf"),
        "even": os.path.join(pkg_share, "config", "jenga_block_even.sdf"),
    }
    for p in block_files.values():
        if not os.path.isfile(p):
            print(f"Block SDF not found: {p}", file=sys.stderr)
            sys.exit(1)

    # Wait for Gazebo and world to settle
    print("Waiting 6 s for Gazebo to be ready...")
    time.sleep(6.0)

    for i, (entity, block_key, x, y, z, yaw) in enumerate(TOWER_LAYOUT):
        block_sdf = block_files[block_key]
        cmd = [
            "ros2", "run", "gazebo_ros", "spawn_entity.py",
            "-entity", entity,
            "-file", block_sdf,
            "-x", str(x), "-y", str(y), "-z", str(z),
        ]
        if yaw != 0.0:
            cmd.extend(["-Y", str(yaw)])
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            print(f"Spawn failed for {entity}", file=sys.stderr)
            sys.exit(ret.returncode)
        # Pause between blocks in same layer; longer pause between layers
        if (i + 1) % 3 == 0:
            time.sleep(2.0)
        else:
            time.sleep(0.3)

    print("Jenga tower spawn complete.")


if __name__ == "__main__":
    main()
