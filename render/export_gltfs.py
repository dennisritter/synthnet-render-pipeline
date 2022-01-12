import json
import os

class SceneExporter():

    def __init__(self, config_path, helper):
        config_data = None
        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)
        self.config_data = config_data
        self.helper = helper
        self.data_path = r"./data/"
        self.material_path = os.path.join(self.data_path, "materials")
    
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

        # parse part scenes
        parts = self.config_data["parts"]
        for part in parts:
            scene = part["scenes"]
            # add the materials to be imported to the scene description
            materials = [os.path.join(self.material_path, single_part["material"])  if not single_part["material"] == "default" else "default" for single_part in part["single_parts"]]
            if len(scene) > 0:
                cameras = []
                lights = []
                envmaps = []
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

                # get render setups
                local_render_setups = []
                for render_setup in part["render_setups"]:
                    local_render_setup = render_setup.copy()
                    local_render_setup["part"] = part
                    local_render_setups.append(local_render_setup)
                render_setups[scene_idx] += local_render_setups
            else:
                scene_idx = 0
                # iterate over render setups
                local_render_setups = []
                for render_setup in global_scene["render_setups"]:
                    local_render_setup = render_setup.copy()
                    local_render_setup["part"] = part
                    local_render_setups.append(local_render_setup)
                render_setups[scene_idx] += local_render_setups
            # add materials to scene description
            scene_descriptions[scene_idx]["materials"] = materials

        return scene_descriptions, render_setups

    def validata_scene_description(scene_description):
        # verify valid
        return scene_description


    def load_scene(self, scene_description):
        bpy_scene_description = {"cameras": [], "lights": [], "materials":[], "envmaps": [], "scene": None}
        bpy_scene_description["scene"] = self.helper.create_scene("scene_descr")
        for  idx, camera_data in enumerate(scene_description["cameras"]):
            bpy_camera =  self.helper.create_camera("camera_{0}".format(str(idx)), camera_data)
            bpy_scene_description["cameras"].append(bpy_camera)
            #self.helper.add_object_to_scene(bpy_scene_description["scene"], bpy_camera)
        for idx, light_data in enumerate(scene_description["lights"]):
            bpy_light = self.helper.create_light("light_{0}".format(str(idx)), light_data)
            bpy_scene_description["lights"].append(bpy_light)
            #self.helper.add_object_to_scene(bpy_scene_description["scene"], bpy_light)
        for material in scene_description["materials"]:
            if material == "default":
                continue
            bpy_material = self.helper.import_materials_from_blend(material)
            bpy_scene_description["materials"].append(bpy_material)
            #self.helper.add_object_to_scene(bpy_scene_description["scene"], bpy_material)
        for img in scene_description["envmaps"]:
            bpy_image = self.helper.add_image_to_blender(img)
            bpy_scene_description["envmaps"].append(bpy_image)
            #self.helper.add_object_to_scene(bpy_scene_description["scene"], bpy_image)
        return bpy_scene_description

    def get_render_parts(self, part_ids: list, root_collection) -> list[tuple]:
        """ returns a list of tuples.

            Args:
                part_ids (list<str>): A list of part IDs .
                root_collection (bpy_types.Collection): A blender collection that should contain machine parts subcollections.
        """
        print(f'- ' * 20)
        print(f'Matching (part_id, bpy_object) pairs')

        matches = []
        # validate whether part_ids match with first part of collection names
        for part_id in part_ids:
            # Get collections
            for coll in self.helper.get_scene_collections(root_collection):
                coll.name = coll.name.replace(" ", "_")
                if coll.name.startswith(part_id) and part_id not in [m[0] for m in matches]:
                    matches.append((part_id, coll))

                for obj in coll.objects:
                    obj.name = obj.name.replace(" ", "_")
                    if obj.name.startswith(part_id) and part_id not in [m[0] for m in matches]:
                        matches.append((part_id, obj))

        # Assert
        # get matched part ids
        matched_part_ids = [part_id[0] for part_id in matches]
        unmatched_part_ids = [part_id for part_id in part_ids if part_id not in matched_part_ids]
        # assert no duplicates
        assert len(matched_part_ids) == len(set(matched_part_ids))

        # # Debug
        # for match in matches:
        #     print(f'{match[0], match[1].name}')
        # for nomatch in unmatched_part_ids:
        #     print(nomatch)

        print('---')
        print(f'root collection: {root_collection.name}')
        print(f'part_ids: {len(part_ids)}')
        print(f'matched: {len(matches)}')
        print(f'unmatched: {len(unmatched_part_ids)}')
        print(f'- ' * 20)
        return matches

    def create_render_frames(self, bpy_scene_description, render_setups):
        # hide all objects
        for frame, render in enumerate(render_setups):
            # hide all
            self.helper.hide_all()
            # get relevant objects
            bpy_ob = self.helper.get_object_by_name(render["obj"]["id"])
            camera_index = render["camera_i"]
            lights_indices = render["lights_i"]
            env_map = render["envmap_fname"]
            cameras = bpy_scene_description["cameras"]
            lights = bpy_scene_description["lights"]
            # make object visible or active
            self.helper.show(bpy_ob)
            # make camera active or visible
            self.helper.show(cameras[camera_index])
            # make lights visible
            for idx in lights_indices:
                self.helper.show(lights[idx])
            #TODO add envmap to material later
            # set keys
            self.helper.set_keyframe(bpy_ob, "hide_render", frame)
            for camera in cameras:
                #self.helper.set_keyframe(camera, "hide_viewport", frame)
                self.helper.set_keyframe(camera, "hide_render", frame)
            for light in lights:
                #self.helper.set_keyframe(light, "hide_viewport", frame)
                self.helper.set_keyframe(light, "hide_render", frame)

    
    
    def export_gltfs(self, output_directory, parts_scene_path):
        scene_descriptions, render_setups = scene_exporter.get_scene_description()
        helper.open_scene(parts_scene_path)
        for scene_description, render_setup in zip(scene_descriptions, render_setups):
            # create empty scene
            helper.open_scene(parts_scene_path)
            # test per scene TODO optimize
            part_ids = [render["part"]["id"] for render_setup in render_setups for render in render_setup]
            root_col = self.helper.get_collections_by_suffix(".hierarchy")[0]
            parts_scene_dict = {part_id: ob for part_id, ob in self.get_render_parts(part_ids, root_col)}
            # import the parts file
            bpy_scene_description = scene_exporter.load_scene(scene_description=scene_description)
            # get relevant objects from scene description
            cameras = bpy_scene_description["cameras"]
            lights = bpy_scene_description["lights"]
            # iterate over all renders in render setup
            for render_idx, render in enumerate(render_setup):
                if not render["part"]["id"] in parts_scene_dict.keys():
                    continue
                objects_to_export = []
                # assign material
                bpy_single_parts = []
                for single_part in render["part"]["single_parts"]:
                    # get object
                    if not single_part["id"] in parts_scene_dict.keys():
                        continue
                    bpy_ob = parts_scene_dict[single_part["id"]]
                    bpy_single_parts.append(bpy_ob)
                    if single_part["material"] == "default":
                        continue
                    continue
                    self.helper.apply_material(bpy_ob, single_part["material"])
                # get the bounding sphere center
                bsphere_center, bsphere_radius = self.helper.get_bounding_sphere(bpy_single_parts)
                self.helper.translate_all_objects_in_scene(root_col, -1 * bsphere_center)
                # get object
                render_ob = parts_scene_dict[render["part"]["id"]]
                # get cameras
                render_camera = cameras[render["camera_i"]]
                render_lights = [lights[idx] for idx in render["lights_i"]]
                #env_map = render["envmap_fname"]
                # select objects and export to gltf
                objects_to_export.append(render_camera)
                objects_to_export += render_lights
                objects_to_export.append(render_ob)
                self.helper.select(objects_to_export)
                # export gltf
                self.helper.export_gltf(os.path.join(output_directory, render["part"]["id"] + "_" + str(render_idx) + ".glb"))
                self.helper.translate_all_objects_in_scene(root_col, bsphere_center)


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
    part_scenes_path = r"C:\Users\Phillip\Documents\beuth\rendering-pipeline\data\drucker-example\drucker.blend"

    test_path = r"./cfg/rcfg_v2_test.json"
    scene_exporter = SceneExporter(test_path, helper)

    scene_exporter.export_gltfs(tempdir, part_scenes_path)



