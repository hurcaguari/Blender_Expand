import bpy
camera_res = bpy.context.object.data.per_camera_resolution

camera_res.resolution_x = 4096
camera_res.resolution_y = 2160
camera_res.resolution_percentage = 100
camera_res.pixel_aspect_x = 1
camera_res.pixel_aspect_y = 1
