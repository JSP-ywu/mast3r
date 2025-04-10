#!/usr/bin/env python3
import json
import numpy as np
import os
from pathlib import Path
import argparse

def quaternion_from_matrix(matrix):
    """Convert rotation matrix to quaternion in COLMAP order (qw, qx, qy, qz)."""
    from scipy.spatial.transform import Rotation
    rot = Rotation.from_matrix(matrix)
    q = rot.as_quat()  # x, y, z, w
    return [q[3], q[0], q[1], q[2]]  # convert to COLMAP order

def main(args):
    with open(args.transforms, 'r') as f:
        data = json.load(f)

    camera_model = data.get("camera_model", "OPENCV")

    original_w, original_h = data["w"], data["h"]
    target_w, target_h = 960, 540

    scale_x = target_w / original_w
    scale_y = target_h / original_h

    fl_x, fl_y = data["fl_x"] * scale_x, data["fl_y"] * scale_y
    cx, cy = data["cx"] * scale_x, data["cy"] * scale_y
    k1, k2, p1, p2 = data["k1"], data["k2"], data["p1"], data["p2"]
    distortion = [k1, k2, p1, p2]
    frames = data["frames"]

    output_path = Path(args.output_model)
    output_path.mkdir(parents=True, exist_ok=True)

    # Write cameras.txt
    with open(output_path / "cameras.txt", "w") as f:
        f.write("# Camera list with one line of data per camera:\n")
        f.write("#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
        f.write("# Number of cameras: 1\n")
        f.write(f"1 {camera_model} {target_w} {target_h} {fl_x} {fl_y} {cx} {cy} {' '.join(map(str, distortion))}\n")

    # Write images.txt
    with open(output_path / "images.txt", "w") as f:
        f.write("# Image list with two lines per image:\n")
        f.write("#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, IMAGE_NAME\n")
        f.write("#   POINTS2D[] as (X, Y, POINT3D_ID)\n")
        f.write(f"# Number of images: {len(frames)}, mean observations: 0\n")
        for frame in frames:
            im_id = frame["colmap_im_id"]
            name = Path(frame["file_path"]).name
            T = np.array(frame["transform_matrix"])  # c2w
            R = T[:3, :3]
            t = T[:3, 3]

            # Convert from c2w to w2c (camera pose)
            R_w2c = R.T
            t_w2c = -R.T @ t
            qvec = quaternion_from_matrix(R_w2c)

            f.write(f"{im_id} {' '.join(map(str, qvec))} {' '.join(map(str, t_w2c))} 1 {name}\n")
            f.write("\n")  # No 2D-3D matches yet

    # Write empty points3D.txt
    with open(output_path / "points3D.txt", "w") as f:
        f.write("# 3D point list with one line of data per point:\n")
        f.write("#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n")
        f.write("# Number of points: 0, mean track length: 0\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transforms", type=str, required=True, help="Path to transforms.json")
    parser.add_argument("--output_model", type=str, required=True, help="Output COLMAP model directory")
    parser.add_argument("--database", type=str, required=True, help="(Unused, for compatibility)")
    args = parser.parse_args()
    main(args)
