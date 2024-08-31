# SPDX-FileCopyrightText: 2022-2024 Damien Picard dam.pic AT free.fr
#
# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "Per-Camera Resolution",
    "author": "Damien Picard",
    "version": (2, 2, 2),
    "blender": (3, 0, 0),
    "location": "Properties > Object Data (Camera) > Camera",
    "description": "Allow per-camera resolutions",
    "wiki_url": "",
    "category": "Camera",
}

from . import translations


import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty
from bpy.app.handlers import persistent
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel

from math import floor


def copy_settings(src, dst):
    dst.resolution_x = src.resolution_x
    dst.resolution_y = src.resolution_y
    dst.resolution_percentage = src.resolution_percentage

    dst.pixel_aspect_x = src.pixel_aspect_x
    dst.pixel_aspect_y = src.pixel_aspect_y


def get_use_resolution(self):
    return self.get("use_custom_resolution", False)


def set_use_resolution(self, value):
    """Disable or enable per-camera resolution. Store or restore scene settings"""
    self["use_custom_resolution"] = value

    context = bpy.context

    if self.id_data is not context.scene.camera.data:
        return

    render = context.scene.render
    original_resolution = context.scene.per_camera_resolution.original_resolution

    if value:
        # Store original settings
        copy_settings(render, original_resolution)
    else:
        # Restore on disable
        copy_settings(original_resolution, render)


@persistent
def update_resolution_handler(scene, from_render=False):
    """Update scene resolution on frame change (e.g. playback) and scene update"""
    render = scene.render
    scene_settings = scene.per_camera_resolution
    original_resolution = scene_settings.original_resolution

    # Avoid updating the resolution from the handler during render,
    # as this can cause errors sometimes.
    # Instead, only do it explicitly from the operator.
    if scene_settings.is_rendering and not from_render:
        return

    if scene_settings.previous_camera is not None:
        previous_cam_data = scene_settings.previous_camera.data
    else:
        previous_cam_data = None

    if scene.camera is None:
        if (scene_settings.previous_camera is not None
                and previous_cam_data.per_camera_resolution.use_custom_resolution):
            # Camera was deleted, restore original resolution
            copy_settings(original_resolution, render)
            scene_settings.previous_camera = None
        return

    cam_data = scene.camera.data

    if cam_data.per_camera_resolution.use_custom_resolution:
        # Copy settings from the active camera
        cam_props = cam_data.per_camera_resolution
        if (previous_cam_data is not None
                and not previous_cam_data.per_camera_resolution.use_custom_resolution):
            # Scene resolution was changed and needs to be stored again
            copy_settings(render, original_resolution)
        copy_settings(cam_props, render)
    else:
        # Restore original resolution.
        # This is useful in case multiple cameras are bound to markers
        # and one of them does not use the custom resolution
        if (previous_cam_data is not None
                and previous_cam_data.per_camera_resolution.use_custom_resolution):
            copy_settings(original_resolution, render)

    scene_settings.previous_camera = scene.camera


class RENDER_OT_animated_resolution(Operator):
    """Render an image sequence while taking the custom resolution into account.
Warning: the interface will be frozen during the entire rendering"""
    bl_idname = "render.animated_resolution"
    bl_label = "Render Animated Resolution"

    @classmethod
    def poll(cls, context):
        if context.scene.camera is None:
            cls.poll_message_set("No active camera in the scene.")
            return False

        if context.scene.render.is_movie_format:
            cls.poll_message_set("Video file formats are not supported for custom resolution render.")
            return False

        return True

    def execute(self, context):
        scene = context.scene
        scene_settings = scene.per_camera_resolution
        original_frame = scene.frame_current
        original_filepath = scene.render.filepath

        scene_settings.is_rendering = True
        context.window_manager.progress_begin(scene.frame_start, scene.frame_end)

        for frame in range(scene.frame_start, scene.frame_end + 1, scene.frame_step):
            context.window_manager.progress_update(frame)
            scene.frame_set(frame)
            scene.render.filepath = original_filepath
            scene.render.filepath = scene.render.frame_path(frame=frame)
            update_resolution_handler(scene, from_render=True)
            bpy.ops.render.render(write_still=True)

        scene_settings.is_rendering = False
        context.window_manager.progress_end()
        scene.frame_set(original_frame)
        scene.render.filepath = original_filepath
        self.report({'INFO'}, "Rendering finished")
        return {'FINISHED'}


class RENDER_OT_bake_render_border(Operator):
    """Bake the render border to a new camera"""
    bl_idname = "render.bake_render_border"
    bl_label = "Bake Render Border"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object is None:
            cls.poll_message_set("No active object.")
            return False

        if context.object.type != 'CAMERA':
            cls.poll_message_set("The active object is not a camera.")
            return False

        if not context.scene.render.use_border:
            cls.poll_message_set("No render border is defined.")
            return False

        if context.object.type == 'PANO':
            cls.poll_message_set("Not supported for panoramic cameras.")
            return False

        return True

    def execute(self, context):
        scene = context.scene
        render = scene.render
        camera = context.object

        new_cam_data = camera.data.copy()
        new_cam = camera.copy()
        new_cam.data = new_cam_data
        new_pc_res = new_cam_data.per_camera_resolution

        for coll in camera.users_collection:
            coll.objects.link(new_cam)
        for obj in context.selected_objects:
            obj.select_set(False)
        context.view_layer.objects.active = new_cam
        new_cam.select_set(True)

        if camera.data.sensor_fit == 'AUTO':
            # Let's not complicate things more than needed
            if render.resolution_x > render.resolution_y:
                new_cam_data.sensor_fit = 'HORIZONTAL'
            else:
                new_cam_data.sensor_fit = 'VERTICAL'
                new_cam_data.sensor_height = new_cam_data.sensor_width

        # Enable custom resolution
        new_pc_res.use_custom_resolution = True
        if not camera.data.per_camera_resolution.use_custom_resolution:
            copy_settings(render, context.scene.per_camera_resolution.original_resolution)

        # Calculate border bounds in pixels
        # It is floored in Blender so let's do that here too
        border_min_x = floor(render.border_min_x * render.resolution_x)
        border_max_x = floor(render.border_max_x * render.resolution_x)
        border_min_y = floor(render.border_min_y * render.resolution_y)
        border_max_y = floor(render.border_max_y * render.resolution_y)

        # Calculate back the relative border positions, after flooring to pixel
        border_min_relative_x = border_min_x / render.resolution_x
        border_max_relative_x = border_max_x / render.resolution_x
        border_min_relative_y = border_min_y / render.resolution_y
        border_max_relative_y = border_max_y / render.resolution_y

        # Calculate new resolution
        new_resolution_x = border_max_x - border_min_x
        new_resolution_y = border_max_y - border_min_y
        new_pc_res.resolution_x = new_resolution_x
        new_pc_res.resolution_y = new_resolution_y

        # Calculate shift
        x_scale = new_resolution_x / render.resolution_x
        y_scale = new_resolution_y / render.resolution_y
        original_center_x = (border_max_relative_x + border_min_relative_x) / 2.0 + new_cam_data.shift_x
        original_center_y = (border_max_relative_y + border_min_relative_y) / 2.0 + new_cam_data.shift_y
        new_cam_data.shift_x = (original_center_x - 0.5) / x_scale
        new_cam_data.shift_y = (original_center_y - 0.5) / y_scale

        # Compensate shift for non-fit side, and calculate new scale / focal length
        if new_cam_data.sensor_fit == 'HORIZONTAL':
            new_cam_data.shift_y *= new_resolution_y / new_resolution_x
            new_cam_data.ortho_scale *= (border_max_relative_x - border_min_relative_x)
            new_cam_data.lens /= (border_max_relative_x - border_min_relative_x)
        else:
            new_cam_data.shift_x *= new_resolution_x / new_resolution_y
            new_cam_data.ortho_scale *= (border_max_relative_y - border_min_relative_y)
            new_cam_data.lens /= (border_max_relative_y - border_min_relative_y)

        return {'FINISHED'}


class AddPresetCameraResolution(AddPresetBase, Operator):
    """Add or remove a Camera Resolution Preset"""
    bl_idname = "camera.resolution_preset_add"
    bl_label = "Add Camera Resolution Preset"
    preset_menu = "CAMERA_PT_format_presets"

    preset_defines = [
        "camera_res = bpy.context.object.data.per_camera_resolution"
    ]

    preset_values = [
        "camera_res.resolution_x",
        "camera_res.resolution_y",
        "camera_res.resolution_percentage",
        "camera_res.pixel_aspect_x",
        "camera_res.pixel_aspect_y",
    ]

    preset_subdir = "per_camera_resolution"


class CAMERA_PT_format_presets(PresetPanel, Panel):
    bl_label = "Camera Resolution Presets"
    preset_subdir = "per_camera_resolution"
    preset_operator = "script.execute_preset"
    preset_add_operator = "camera.resolution_preset_add"

    @staticmethod
    def post_cb(context, _filepath):
        """XXX Force updating the UI when loading the preset"""
        context.region.tag_redraw()

    def draw(self, context):
        """Copied from bpy.types.Menu.draw_preset()

        This allows shipping presets with the add-on.
        """
        layout = self.layout
        layout.emboss = 'PULLDOWN_MENU'
        layout.operator_context = 'EXEC_DEFAULT'

        import os

        ext_valid = {".py"}
        props_default = getattr(self, "preset_operator_defaults", None)
        add_operator = getattr(self, "preset_add_operator", None)
        add_operator_props = getattr(self, "preset_add_operator_properties", None)
        preset_paths = bpy.utils.preset_paths(self.preset_subdir)
        preset_paths.append(os.path.join(os.path.dirname(__file__),
                                         "presets", *self.preset_subdir.split("/")))
        self.path_menu(
            preset_paths,
            self.preset_operator,
            props_default=props_default,
            filter_ext=lambda ext: ext.lower() in ext_valid,
            add_operator=add_operator,
            add_operator_props=add_operator_props,
            display_name=lambda name: bpy.path.display_name(name, title_case=False)
        )


class DATA_PT_per_camera_resolution(Panel):
    bl_label = "Custom Resolution"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = "DATA_PT_camera"

    def draw_header(self, context):
        cam = context.camera
        props = cam.per_camera_resolution
        self.layout.prop(props, "use_custom_resolution", text="")

    def draw_header_preset(self, _context):
        CAMERA_PT_format_presets.draw_panel_header(self.layout)

    def draw(self, context):
        """Draw camera resolution in the Camera panel"""
        cam = context.camera
        props = cam.per_camera_resolution

        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        col.active = props.use_custom_resolution

        sub = col.column(align=True)
        sub.prop(props, "resolution_x", text="Resolution X")
        sub.prop(props, "resolution_y", text="Y")
        sub.prop(props, "resolution_percentage", text="%")

        sub = col.column(align=True)
        sub.prop(props, "pixel_aspect_x", text="Aspect X")
        sub.prop(props, "pixel_aspect_y", text="Y")

        layout.separator()

        col = layout.column(align=True)
        col.operator("render.animated_resolution", icon='RENDER_ANIMATION')
        col.operator("render.bake_render_border")


def format_panel_warning(self, context):
    layout = self.layout

    if (context.scene.camera is not None
            and context.scene.camera.data.per_camera_resolution.use_custom_resolution):
        # Maybe a box is obnoxious, but left-aligned text looks weird otherwise
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Scene camera uses a custom resolution.", icon='ERROR')
        col.label(text="Set it in the camera data properties.", icon='BLANK1')


class PerCameraResolutionProps(PropertyGroup):
    use_custom_resolution: BoolProperty(
        name="Use Custom Resolution", description="Whether to use the default scene resolution, or the camera one",
        default=False,
        get=get_use_resolution,
        set=set_use_resolution,
    )

    resolution_x: IntProperty(
        name="Resolution X",
        description="Number of horizontal pixels in the rendered image",
        default=1920, min=1,
        options={'ANIMATABLE', 'PROPORTIONAL'},
        subtype="PIXEL",
    )
    resolution_y: IntProperty(
        name="Resolution Y",
        description="Number of vertical pixels in the rendered image",
        default=1080, min=1,
        options={'ANIMATABLE', 'PROPORTIONAL'},
        subtype="PIXEL",
    )
    resolution_percentage: IntProperty(
        name="Resolution Scale",
        description="Percentage scale for render resolution",
        default=100, min=1, soft_max=100,
        subtype="PERCENTAGE",
    )

    pixel_aspect_x: FloatProperty(
        name="Pixel Aspect X",
        description="Horizontal aspect ratio - for anamorphic or non-square pixel output",
        default=1.0, min=1.0, max=200.0,
        precision=3,
        options={'ANIMATABLE', 'PROPORTIONAL'},
    )
    pixel_aspect_y: FloatProperty(
        name="Pixel Aspect Y",
        description="Vertical aspect ratio - for anamorphic or non-square pixel output",
        default=1.0, min=1.0, max=200.0,
        precision=3,
        options={'ANIMATABLE', 'PROPORTIONAL'},
    )


class PerCameraResolutionSceneProps(PropertyGroup):
    original_resolution: PointerProperty(type=PerCameraResolutionProps)
    previous_camera: PointerProperty(type=bpy.types.Object)
    is_rendering: BoolProperty(default=False)


classes = (
    PerCameraResolutionProps,
    PerCameraResolutionSceneProps,
    DATA_PT_per_camera_resolution,
    CAMERA_PT_format_presets,
    RENDER_OT_animated_resolution,
    RENDER_OT_bake_render_border,
    AddPresetCameraResolution,
)
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()

    bpy.types.Camera.per_camera_resolution = PointerProperty(type=PerCameraResolutionProps)
    bpy.types.Scene.per_camera_resolution = PointerProperty(type=PerCameraResolutionSceneProps)

    bpy.app.handlers.depsgraph_update_pre.append(update_resolution_handler)
    bpy.app.handlers.frame_change_pre.append(update_resolution_handler)

    bpy.types.RENDER_PT_format.prepend(format_panel_warning)

    bpy.app.translations.register(__name__, translations.translations_dict)


def unregister():
    bpy.app.translations.unregister(__name__)

    bpy.types.RENDER_PT_format.remove(format_panel_warning)

    bpy.app.handlers.depsgraph_update_pre.remove(update_resolution_handler)
    bpy.app.handlers.frame_change_pre.remove(update_resolution_handler)

    del bpy.types.Scene.per_camera_resolution
    del bpy.types.Camera.per_camera_resolution

    class_unregister()


if __name__ == "__main__":
    register()
