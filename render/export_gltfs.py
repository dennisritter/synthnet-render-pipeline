import json

class SceneExporter():

    def __init__(self, config_path, helper):
        config_data = None
        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)
        self.config_data = config_data
        self.helper = helper
    
    def get_scene_description(self):
        # parse global scenes
        scene_descriptions = [None]
        render_setups = [[]]
        global_scene = self.config_data["global_scene"]
        if global_scene:
            cameras = []
            lights = []
            envmaps = []
            materials = []
            # iterate over cameras
            for camera in global_scene["cameras"]:
                cameras.append(camera)
            # iterate over lights
            for light in global_scene["lights"]:
                lights.append(light)
            # iterate over envmaps
            for envmap in global_scene["envmaps"]:
                envmaps.append(envmap)
            global_scene_description = dict(cameras=cameras, lights=lights, envmaps=envmaps, materials=materials)
            scene_descriptions[0] = global_scene_description

            # iterate over render setups
            for render_setup in global_scene["render_setups"]:
                render_setups[0].append(render_setup)

        # parse part scenes
        parts = self.config_data["parts"]
        for part in parts:
            scene = part["scenes"]
            if scene:
                cameras = []
                lights = []
                envmaps = []
                materials = []
                # iterate over cameras
                for camera in scene["cameras"]:
                    cameras.append(camera)
                # iterate over lights
                for light in scene["lights"]:
                    lights.append(light)
                # iterate over envmaps
                for envmap in scene["envmaps"]:
                    envmaps.append(envmap)
                local_scene_description = dict(cameras=cameras, lights=lights, envmaps=envmaps, materials=materials)
                # TODO check if scene description exists already and get the index?
                # add scene description
                scene_descriptions.append(local_scene_description)
                # add a new list for render setups using this scene
                render_setups.append([])
                scene_idx = len(scene_descriptions) - 1
            else:
                scene_idx = 0
            # iterate over render setups
            local_render_setups = []
            for render_setup in global_scene["render_setups"]:
                render_setup["obj"] = part
                local_render_setups.append(render_setup)
            render_setups[scene_idx] += local_render_setups
        return scene_descriptions, render_setups

    def validata_scene_description(scene_description):
        # verify valid
        return scene_description


    def load_scene(self, scene_description):
        bpy_scene_description = {}
        for  idx, camera_data in enumerate(scene_description["cameras"]):
            bpy_camera =  self.helper.create_camera("camera_{0}".format(str(idx)), camera_data)
        for idx, light_data in enumerate(scene_description["lights"]):
            bpy_light = self.helper.create_light("light_{0}".format(str(idx)), light_data)
        for material in scene_description["materials"]:
            bpy_material = self.helper.import_materials_from_blend(material)
        for img in scene_description["envmaps"]:
            bpy_image = self.helper.add_image_to_blender(img)

    def create_render_frames(self, bpy_scene_description, render_setup):
        # hide all objects
        for obj in bpy.data.objects:
            obj.hide_viewport = True
        for frame, render in enumerate(scene_description["render_setups"]):
            obj_name = render["obj"]
            camera_index = render["camera"]
            lights_indices = render["lights"]
            env_map = render["envmap"]

            for idx in camera_index


    def run(self):
        scene_description = self.get_scene_description
        #self.validata_scene_description(scene_description)
        #self.load_scene(scene_description)
        #self.create_render_frames(scene_description)



def add_module_to_blender(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module 
    spec.loader.exec_module(module)  

if __name__ == '__main__':
    import importlib
    import sys
    import os
    blender_helper_path = '/home/phillip/repos/iisy/rendering-pipeline'
    sys.path.append(blender_helper_path)
    import render.blender_helper as helper

    test_path = r"./cfg/cfg_test.json"
    scene_exporter = SceneExporter(test_path, helper)

    scene_descriptions, render_setups = scene_exporter.get_scene_description()
    for scene_description in scene_descriptions:
        scene_exporter.load_scene(scene_description=scene_description)


