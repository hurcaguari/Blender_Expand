import bpy
camera_res = bpy.context.object.data.per_camera_resolution

camera_res.resolution_x = 1440
camera_res.resolution_y = 1080
camera_res.resolution_percentage = 100
camera_res.pixel_aspect_x = 4
camera_res.pixel_aspect_y = 3
