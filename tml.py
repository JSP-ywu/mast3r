from pygltflib import GLTF2

gltf = GLTF2().load("/data1/pjs/tmpuoq537ox_scene.glb")

# Check number of cameras
print(f"Number of cameras: {len(gltf.cameras)}")

for i, camera in enumerate(gltf.cameras):
    print(f"\nCamera {i}:")
    print(camera)

# Now match cameras to nodes to get their transform
for i, node in enumerate(gltf.nodes):
    if node.camera is not None:
        print(f"\nCamera Node {i}:")
        print(f"Camera index: {node.camera}")
        print(f"Translation (position): {node.translation}")
        print(f"Rotation (quaternion): {node.rotation}")
        print(f"Scale: {node.scale}")