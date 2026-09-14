# BlueROV2 reference assets

Repository: https://github.com/clydemcqueen/bluerov2_gz
Revision: 661264b719ffd2dcdd0d0990de80547d6029cc16
Author: Clyde McQueen. Upstream package.xml declares MIT; no standalone LICENSE file was present at this revision.
Upstream BlueROV2.md credits Blue Robotics for meshes, sourced from:
- https://grabcad.com/library/bluerov2-1
- https://grabcad.com/library/bluerobotics-t200-thruster-1

The original meshes and adapted model are downloaded locally by prepare_model.py and excluded from Git. Their upstream credits are retained in models/bluerov2/BlueROV2.md. This project's license declaration does not relicense those assets; consult the original sources before redistribution.

Adaptation: remove the ArduPilot plugin; change IMU orientation to FLU and rate to 50 Hz; add 3D ground-truth odometry. Preserve six thrusters and original physics parameters. Upstream explicitly states the model is not tuned.
