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
        bpy_scene_description = {"cameras": [], "lights": [], "materials":[], "envmaps": []}
        for  idx, camera_data in enumerate(scene_description["cameras"]):
            bpy_camera =  self.helper.create_camera("camera_{0}".format(str(idx)), camera_data)
            bpy_scene_description["cameras"].append(bpy_camera)
        for idx, light_data in enumerate(scene_description["lights"]):
            bpy_light = self.helper.create_light("light_{0}".format(str(idx)), light_data)
            bpy_scene_description["lights"].append(bpy_light)
        for material in scene_description["materials"]:
            bpy_material = self.helper.import_materials_from_blend(material)
            bpy_scene_description["materials"].append(bpy_material)
        for img in scene_description["envmaps"]:
            bpy_image = self.helper.add_image_to_blender(img)
            bpy_scene_description["envmaps"].append(bpy_image)
        return bpy_scene_description

    def create_render_frames(self, bpy_scene_description, render_setups):
        # hide all objects
        for frame, render in enumerate(render_setups):
            # hide all
            self.helper.hide_all()
            # get relevant objects
            obj_name = render["obj"]
            camera_index = render["camera_i"]
            lights_indices = render["lights_i"]
            env_map = render["envmap_fname"]
            cameras = bpy_scene_description["cameras"]
            lights = bpy_scene_description["lights"]
            # make camera active or visible
            self.helper.show(cameras[camera_index])
            # make lights visible
            for idx in lights_indices:
                self.helper.show(lights[idx])
            #TODO add envmap later
            
            # set keys
            for camera in cameras:
                #self.helper.set_keyframe(camera, "hide_viewport", frame)
                self.helper.set_keyframe(camera, "hide_render", frame)
            for light in lights:
                #self.helper.set_keyframe(light, "hide_viewport", frame)
                self.helper.set_keyframe(light, "hide_render", frame)


            


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
    blender_helper_path = r'C:\Users\Phillip\Documents\beuth\rendering-pipeline'
    sys.path.append(blender_helper_path)
    import render.blender_helper as helper

    tempdir = r'C:\Users\Phillip\Documents\beuth\tempdir'

    test_path = r"./cfg/cfg_test.json"
    scene_exporter = SceneExporter(test_path, helper)

    scene_descriptions, render_setups = scene_exporter.get_scene_description()
    i = 0
    for scene_description, render_setup in zip(scene_descriptions, render_setups):
        # create empty scene
        helper.new_scene()
        bpy_scene_description = scene_exporter.load_scene(scene_description=scene_description)
        scene_exporter.create_render_frames(bpy_scene_description, render_setup)

        output_path = os.path.join(tempdir, "test_{0}.blend".format(str(i)))
        helper.save_scene(output_path)
        i+=1


