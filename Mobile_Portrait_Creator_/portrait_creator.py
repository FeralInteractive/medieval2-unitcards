#---------------
# IMPORT MODULES
#---------------

# Python
import os
import re
import time

# Blender Python
import bpy
import bmesh


########################################################################################################################

#------
# SETUP
#------

# Files & Directories
master_directory = os.path.dirname(bpy.data.filepath) + '/'

# Log
log_file = (master_directory + 'log_file' + '.txt')  # txt file

# Input text file info
input_text_file_path = (master_directory + 'inputfile' + '.txt')  # txt file

# Unit data
input_character_models_path =  (master_directory + 'source_assets/models/human' + '/')
input_character_textures_path =  (master_directory + 'source_assets/textures/human' + '/')

# Additional object data
input_additional_object_textures_path = (master_directory + 'source_assets/textures/additional_objects' + '/')

# Output image renders
output_renders_path =  (master_directory + 'output_directory' + '/')

# Materials
material_main_name = 'characterlod0__main'  # string - must match the material name on imported characters
material_attachments_name = 'characterlod0__attach'  # string - must match the material name on imported characters


########################################################################################################################

#--------
# CLASSES
#--------

class Portrait:
    '''
    Used to process information for each portrait using the input text file
    '''
    def __init__(self,
                portrait_id,
                portrait_file_output,
                game,
                faction,
                pose_id,
                additional_object_name,
                additional_object_texture,
                character_model_file,
                character_texture_main_albedo_file,
                character_texture_main_pbr_file,
                character_texture_extras_albedo_file,
                character_texture_extras_pbr_file,
                output_directory,
                visible_models,
                ):

        self.portrait_id = portrait_id
        self.portrait_file_output = portrait_file_output
        self.game = game
        self.faction = faction
        self.pose_id = pose_id
        self.additional_object_name = additional_object_name
        self.additional_object_texture = additional_object_texture
        self.character_model_file = character_model_file
        self.character_texture_main_albedo_file = character_texture_main_albedo_file
        self.character_texture_main_pbr_file = character_texture_main_pbr_file
        self.character_texture_extras_albedo_file = character_texture_extras_albedo_file
        self.character_texture_extras_pbr_file = character_texture_extras_pbr_file
        self.output_directory = output_directory
        self.visible_models = visible_models


    def portrait_details(self):
        print('\n'.join([str(key) + ': ' + str(value) for key, value in vars(self).items()]))


########################################################################################################################

#----------
# FUNCTIONS
#----------
#   01 MODEL
#   02 MATERIALS & TEXTURES
#   03 GENERIAL ACTIONS
#   04 OUTPUT
#   05 CLEANUP
#   06 PROCESS
#   07 RUN



# FUNCTIONS - 01 MODEL
def model_character_import(portrait, full_model_path, model_file_format, target_collection='Characters'):
    '''
    IMPORTS CHARACTER MODEL
    '''
    # Set collection (must be under 'Scene Collection')
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[target_collection]

    print('\nImporting character\n')

    full_model_path = (full_model_path + '.' + model_file_format)
    
    # Import model
    if model_file_format == 'fbx':
        bpy.ops.import_scene.fbx(filepath=full_model_path)
    elif model_file_format == 'dae':
        bpy.ops.wm.collada_import(filepath=full_model_path)
    else:
        print(f'The following file format is not valid! "{model_file_format}" check variable "model_file_format"')


def component_assign_human_default(armature_name='Armature', which_primary_to_hide='primaryactive1'):
    '''
    ONLY RENDERS THE FIRST ITEM WITH A UNIQUE PREFIX
    '''
    children = bpy.data.objects[armature_name].children

    prefix = ' '
    all_secondary_weapon_prefix = 'secondaryactive'

    for i in children:
        if i.type == 'MESH':
            if i.name.startswith(prefix) or i.name.startswith(which_primary_to_hide) or i.name.startswith(all_secondary_weapon_prefix):
                bpy.data.objects[i.name].hide_render = True
            else:
                prefix = i.name.split('__')[0]  # Components prefix are broken up by '__'


def models_to_hide_from_render(armature_name='Armature'):
    '''
    HIDES ALL MODELS WHICH WE NEVER WANT TO SHOW
    '''
    character_skeleton = bpy.data.objects[armature_name]

    for i in character_skeleton.children:
        if i.name.startswith('ramrod0'):
            bpy.data.objects[i.name].hide_render = True


def visibility_toggle_render_human_meshes(visible_objects, armature_name='Armature'):
    '''
    TOGGLES RENDER VISIBILITY FOR MESH OBJECTS PARENTED UNDER THE IMPORTED CHARACTER SKELETON
    THIS REFERS TO THE LAST ARGUMENT IN THE REGULAR EXPRESSION
    IF THE ITEM IS not IN THE LIST, IT WILL not BE RENDERED
    '''
    character_skeleton = bpy.data.objects[armature_name]

    for i in character_skeleton.children:
        if not (i.name in visible_objects):
            bpy.data.objects[i.name].hide_render = True


def visibility_render_toggle_single_target(object_name, hide_from_render, object_type='collections'):
    '''
    TOGGLES RENDER VISIBILITY FOR A SINGLE OBJECT
    '''
    if object_type == 'objects':
        bpy.data.objects[object_name].hide_render = hide_from_render  # Hide from Render display (True=Hidden, False=Visible)
    elif object_type == 'collections':
        bpy.data.collections[object_name].hide_render = hide_from_render  # Hide from Render display (True=Hidden, False=Visible)
    else:
        print(f'\n \'object_type\' not valid ({object_type})')


def hide_all_animal_meshes(animal_collection_name):
    collection = bpy.data.collections[animal_collection_name]
    all_objects = collection.all_objects
    child_collections = collection.children

    objects_names = [obj.name for obj in all_objects]

    # Hide all objects in sub collections
    for obj_name in objects_names:
        visibility_render_toggle_single_target(obj_name, True, 'objects')


def visibility_toggle_render_animal_meshes(hide_value, animal_collection_name, visible_objects):
    '''
    TOGGLES RENDER VISIBILITY FOR ANIMAL MESH VARIATION
    '''
    collection = bpy.data.collections[animal_collection_name]
    all_objects = collection.all_objects
    child_collections = collection.children

    use_default = True

    for vis_ob in visible_objects:
        if vis_ob in all_objects:
            bpy.data.objects[vis_ob].hide_render = hide_value
            use_default = False

    if use_default == True:
        # Gets objects in default collection
        for col in child_collections:
            if 'DEFAULT' in col.name:
                default_collection_objects = bpy.data.collections[col.name].all_objects

        default_collection_objects_names = [obj.name for obj in default_collection_objects]
        # Hides objects in default collection
        for obj_name in default_collection_objects_names:
            bpy.data.objects[obj_name].hide_render = hide_value



# FUNCTIONS - 02 MATERIALS & TEXTURES
def material_character_set_channel_default(material, channel, value):
    '''
    SET DEFAULT MATERIAL
    '''
    bsdf = material.node_tree.nodes['Principled BSDF']
    bsdf.inputs[channel].default_value = value


def material_character_set_node_structure(material, color=(1, 1, 1, 1)):
    '''
    INITIAL MATERIAL STRUCTURE SETUP
    '''
    material.use_nodes = True

    # bsdf_node = material.node_tree.nodes['Principled BSDF']
    # RGB_color_node = material.node_tree.nodes.new('ShaderNodeRGB')
    # RGB_color_node.outputs['Color'].default_value = color


def material_character_setup(character, include_albedo, include_metal, include_normal,
    include_rough, texture_file_format):
        '''
        SETUP MATERIALS
        '''
        for material in bpy.data.materials:
            # Main character material (Medieval 2 setup)
            if material.name == material_main_name:
                if character.character_texture_main_albedo_file != '/' and character.character_texture_main_albedo_file != '?':
                    material_character_set_node_structure(material=material)
                    texture_character_import_and_assign(texture_path=(input_character_textures_path),
                                            game=character.game,
                                            albedo_texture_name=(character.character_texture_main_albedo_file + '.' + texture_file_format),
                                            pbr_texture_name=(character.character_texture_main_pbr_file + '.' + texture_file_format),
                                            alpha_mode='STRAIGHT',
                                            include_albedo=include_albedo, include_metal=include_metal,
                                            include_normal=include_normal, include_rough=include_rough,
                                            material=material)
                    # Set alpha blend method
                    bpy.data.materials[material.name].blend_method = 'CLIP'
                else:
                    continue

            # Attachment character material (Medieval 2 setup)
            elif material.name == material_attachments_name:
                if character.character_texture_extras_albedo_file != '/' and character.character_texture_extras_albedo_file != '?':
                    material_character_set_node_structure(material=material)
                    texture_character_import_and_assign(texture_path=(input_character_textures_path),
                                            albedo_texture_name=(character.character_texture_extras_albedo_file + '.' + texture_file_format),
                                            game=character.game,
                                            pbr_texture_name=(character.character_texture_extras_pbr_file + '.' + texture_file_format),
                                            alpha_mode='STRAIGHT',
                                            include_albedo=include_albedo, include_metal=include_metal,
                                            include_normal=include_normal, include_rough=include_rough,
                                            material=material)
                    # Set alpha blend method
                    bpy.data.materials[material.name].blend_method = 'CLIP'
                else:
                    continue

            else:
                pass


def texture_character_import_and_assign(texture_path, game, albedo_texture_name, pbr_texture_name, alpha_mode,
    include_albedo, include_metal, include_normal, include_rough,
    material):
        '''
        IMPORT EACH TEXTURE image
        '''
        # Set Specular to dieletrics for everything - may not be correct for metals but handling this would be painful. Portraits are also so small that this will hardly make a difference.
        material_character_set_channel_default(material=material, channel='Specular', value=0.03)

        if include_albedo:
            albedo_texture = bpy.data.images.load(os.path.join(texture_path, game, albedo_texture_name))  # Loading albedo texture

            texture_character_setup(texture=albedo_texture, material=material,
                                     alpha_mode=alpha_mode, alpha_connect=True,
                                     color_space='sRGB', usage='Base Color',
                                     receiving_node='Principled BSDF')

        if include_metal:
            metal_texture = bpy.data.images.load(os.path.join(texture_path, game, pbr_texture_name))

            texture_character_setup(texture=metal_texture, material=material,
                                     alpha_mode=alpha_mode, alpha_connect=False,
                                     color_space='Linear', usage='Metallic')
        else:
            material_character_set_channel_default(material=material, channel='Metallic', value=0)

        if include_normal:
            normal_texture = bpy.data.images.load(os.path.join(texture_path, game, pbr_texture_name))

            texture_character_setup(texture=normal_texture, material=material,
                                     alpha_mode=alpha_mode, alpha_connect=False,
                                     color_space='Non-Color', usage='Color',
                                     receiving_node='Normal')

        if include_rough:
            rough_texture = bpy.data.images.load(os.path.join(texture_path, game, pbr_texture_name))

            texture_character_setup(texture=rough_texture, material=material,
                                     alpha_mode=alpha_mode, alpha_connect=False,
                                     color_space='Linear', usage='Roughness')
        else:
            material_character_set_channel_default(material=material, channel='Roughness', value=0.9)


def texture_character_setup(texture, material, alpha_mode, alpha_connect, color_space, usage, receiving_node='Principled BSDF'):
    '''
    CONNECT TEXTURE IN MATERIAL
    '''
    material.use_nodes = True
    bsdf_node = material.node_tree.nodes[receiving_node]

    texture.alpha_mode = alpha_mode
    texture.colorspace_settings.name = color_space

    destination = material.node_tree.nodes[receiving_node]

    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')  # creating a node for the texture
    texture_node.image = texture
    material.node_tree.links.new(destination.inputs[usage], texture_node.outputs['Color'])
    
    # Alpha
    if alpha_connect:
        material.node_tree.links.new(bsdf_node.inputs['Alpha'], texture_node.outputs['Alpha'])


def texture_additional_object_import_and_assign(material_name, texture_name, texture_path, texture_file_format='dds'):
    texture_name = (texture_name + '.' + texture_file_format)
    albedo_texture = bpy.data.images.load(os.path.join(texture_path, texture_name))  # Loading albedo texture

    bpy.data.materials[material_name].node_tree.nodes['albedo_image_texture'].image = albedo_texture



# FUNCTIONS - 03 GENERIAL ACTIONS
def link_skeletons(armature_name='Armature', armature_action='human_pose_id_actions'):
    '''
    APPLIES THE POSE BY USING THE REFERENCE SKELETON AND THE ACTIONS
    '''
    # Link skeleton to pose_id
    reference_action = bpy.data.actions[armature_action]
    imported_character_armature = bpy.data.objects[armature_name]
    imported_character_armature.animation_data_create()
    imported_character_armature.animation_data.action = reference_action


def set_frame_to_id(pose_id_number):
    '''
    SET CURRENT FRAME TO MATCH THE INPUT POSE_ID - THE POSE_ID NUMBER SHOULD MATCH THE FRAME NUMBER!
    '''
    bpy.context.scene.frame_set(pose_id_number)


def reassign_game_and_faction(game, faction, animal):
    '''
    If the faction/game assignments are a bit messy this will redefine them
    '''
    new_game = game
    new_faction = faction

    # Examples
    # Faction only
    if faction == 'old_faction_name':
        new_faction = 'new_faction_name'
    # Game only
    if game == 'old_game_name':
        new_game = 'new_game_name'
    # Faction & Game
    if game == 'old_game_name2' and faction == 'old_faction_name2':
        new_faction = 'new_faction_name2'

    return (new_game, new_faction)


def fix_object_parent_bone_assignment(armature_name='Armature'):
    '''
    SOME UNITS HAVE WEAPONS/ITEMS WHICH ARE NOT PARENTED TO THE CORRECT BONE.
    USUALLY REFERENCING THE LEFT WEAPON (BOW) TO 'bone_weapon_group01' instead of 'bone_weapon_group03'
    Bone hierarchy is as follows:
        bone_Rhand
            bone_weapon_group01
                bone_weapon_group02
                bone_weapon_group04
        bone_Lhand
            bone_weapon_group03
    '''
    children = bpy.data.objects[armature_name].children

    right_hand_weapon_bones = ['bone_weapon_group01', 'bone_weapon_group02', 'bone_weapon_group04']
    left_hand_weapon_bone = 'bone_weapon_group03'

    for item in children:
        if item.type == 'MESH' and 'primary' in item.name or 'secondary' in item.name: 
            if '_bow' in item.name or 'longbow' in item.name :
                bpy.data.objects[item.name].vertex_groups[0].name = left_hand_weapon_bone


def update_3d_text(portrait_id_number, txt=(bpy.data.objects['portrait_id_3d_text'])):
    '''
    Updates 3d text number to first argument from the input text file
    '''
    txt.data.body = str(portrait_id_number)



# FUNCTIONS - 04 OUTPUT
def render(portrait, camera,):
    '''
    RENDERS OUT PORTRAIT IMAGE
    '''
    scene = bpy.data.scenes[0]
    scene.camera = camera

    rendered = ''

    # Close up camera render output
    if camera.name.endswith('closeup'):
        bpy.data.collections["render_camera_full_environment"].hide_render = True
        bpy.data.collections["render_camera_closeup_environment"].hide_render = False
        rendered = portrait.game + '/units/' + portrait.output_directory + '/' + portrait.portrait_file_output
    
    # Full camera render output
    if camera.name.endswith('full'):
        bpy.data.collections["render_camera_closeup_environment"].hide_render = True
        bpy.data.collections["render_camera_full_environment"].hide_render = False
        rendered = portrait.game + '/unit_info/' + portrait.output_directory + '/' + portrait.portrait_file_output + '_info'

    scene.render.filepath = os.path.join(output_renders_path, rendered)
    bpy.ops.render.render(write_still=1)


def render_character(portrait):
    '''
    FINDS CAMERAS USED FOR RENDERING
    '''
    cameras = [obj for obj in bpy.data.objects if obj.name.startswith('render_camera') and bpy.data.objects[obj.name].type == 'CAMERA']

    for camera in cameras:
        # if camera.name.endswith('closeup'):  # Rendering only portraits and not full character
        render(portrait, camera)



# FUNCTIONS - 05 CLEANUP
def delete_character(armature_name='Armature'):
    '''
    DETELES CHARACTER
    ONCE COMPLETED RENDER
    '''
    armature = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE', extend=False)
    objects = [ob for ob in bpy.data.objects if ob.select_get()]

    bpy.data.objects.remove(armature)
    for obj in objects:
        bpy.data.objects.remove(obj)


def delete_materials(materials_to_delete=(material_main_name, material_attachments_name)):
    '''
    DELETED MATERIALS
    ONCE COMPLETED RENDER & CHARACTER IS DELETED

    THIS WAS CREATED BECAUSE THE PURGE FUNCTION WAS NOT PICKING UP THESE MATERIALS (FOR SOME REASON)
    '''
    for material in bpy.data.materials:
        if material.name in materials_to_delete:
            bpy.data.materials.remove(bpy.data.materials[material.name])
        else:
            continue


def purge(data_collection):
    '''
    CLEAN UP STEP
    PURGES DATA ACCORDINGLY
    '''
    for data in data_collection:
        if data.users == 0:
            data_collection.remove(data)


def purge_orphans():
    '''
    RUNS PURGE STEP FOR EACH OF THE INPUTS
    '''
    purge(bpy.data.armatures)
    purge(bpy.data.meshes)
    purge(bpy.data.actions)

    # From here purge order is important
    purge(bpy.data.materials)
    purge(bpy.data.textures)
    purge(bpy.data.images)



# FUNCTIONS - 06 PROCESS
def process_portrait(portrait, log, testing_mode, model_file_format='dae', texture_file_format='dds'):
    '''
    RUNS ALL NECESSARY  FUNCTIONS TO CREATE THE RENDER OUTCOME
    USING THE OUTCOME FROM INPUT TEXT FILE PROCESS
    '''

    # INITIAL SETUP
    vis_components = 'na'  # Set to 'default' if want to use default components for human units

    # Sort the 'visible_models' input argument into a valid list
    visible_models = portrait.visible_models.split('\t')
    visible_models_sorted = []
    for i in visible_models:  # Removes empty arguments
        if len(i) != 0:
            visible_models_sorted.append(i)

    # Include id number in portrait if pose is 0
    if portrait.pose_id == 0:
        log.write(f'\n({portrait.portrait_id}){portrait.portrait_file_output} is using pose 0')
        include_id_in_portrait = True
    else:
        include_id_in_portrait = False  # Change to True if required for all protraits


    # TESTING MODE
    if testing_mode:
        '''
        THIS WILL JUST USE THE DEFAULT UNIT IN THE BLENDER SCENE, SET THE POSE & ATTACH THE ID NUMBER
        NO EXTERIAL DATA IS USED FOR THIS
        CURRENTLY DOES NOT SUPPORT ANYTHING OTHER THAN THE HUMAN UNIT.
        '''
        set_frame_to_id(pose_id_number=portrait.pose_id)
        visibility_render_toggle_single_target('portrait_id_3d_text', False)
        update_3d_text(portrait_id_number=portrait.portrait_id)
        render_character(portrait)


    # CREATE PORTRAITS
    else:
        full_model_path = (input_character_models_path + '/' + portrait.game + '/' + portrait.character_model_file + '_lod0')

        if portrait.character_model_file != '/' and os.path.isfile(full_model_path + '.' + model_file_format):  # If the file does not exist the unit will not appear in the portrait
            # Import model
            model_character_import(portrait=portrait, full_model_path=full_model_path, model_file_format=model_file_format, target_collection='Characters')
            
            fix_object_parent_bone_assignment()  # Fix bow skinning
            models_to_hide_from_render()  # Hide any models which should never be visible

            # Texture setup
            if not os.path.exists(portrait.character_texture_main_albedo_file + '.' + texture_file_format):
                material_character_setup(character=portrait,
                    include_albedo=True, include_metal=False, include_normal=False, include_rough=False, texture_file_format=texture_file_format)  # IMPORTRANT! currently does not support pbr texture
            else:  # Include id if cannot find a texture
                include_id_in_portrait = True

            # Set visible components for rendering
            if vis_components == 'default' or len(visible_models_sorted) == 0:  # If there are no items in portrait.visible use a default assignment
                component_assign_human_default()
            else:
                visibility_toggle_render_human_meshes(visible_objects=visible_models_sorted)

            # Link imported human skeleton to reference human already in scene
            link_skeletons()
        
        # If using 'test_man' use the reference human in the render
        elif portrait.character_model_file == 'test_man':
            include_id_in_portrait = True
            visibility_render_toggle_single_target('Ref_Armature', False)


        # SET POSE (set current frame on timeline to the pose id number)
        set_frame_to_id(pose_id_number=portrait.pose_id)


        # ADDITIONAL OBJECTS (mounts, siege)
        if portrait.additional_object_name != '/':
            # Display collection
            visibility_render_toggle_single_target(object_name=(portrait.additional_object_name), hide_from_render=False)

            # Texture setup
            if portrait.additional_object_texture != '/':
                texture_additional_object_import_and_assign(
                    material_name=(portrait.additional_object_name + '_MAT'),
                    texture_name=portrait.additional_object_texture,
                    texture_path=input_additional_object_textures_path,
                    texture_file_format='dds')

            # Variation assignment (MOUNT ONLY)
            if portrait.additional_object_name.startswith('mount_'):
                hide_all_animal_meshes(animal_collection_name=portrait.additional_object_name)
                visibility_toggle_render_animal_meshes(
                    hide_value=False,
                    animal_collection_name=portrait.additional_object_name,
                    visible_objects=visible_models_sorted)

        # INCLUDE ID IN PORTRAIT RENDER
        if include_id_in_portrait == True:
            visibility_render_toggle_single_target('portrait_id_3d_text', False)
            update_3d_text(portrait_id_number=portrait.portrait_id)

        # RENDER OUTPUT
        render_character(portrait)

        # CLEAN UP
        # Hide Additional Object
        if portrait.additional_object_name != '/':
            visibility_render_toggle_single_target(object_name=portrait.additional_object_name, hide_from_render=True)
        elif portrait.additional_object_name == '/' and 200 <= portrait.pose_id <= 299:
            visibility_render_toggle_single_target(object_name='mount_test_horse', hide_from_render=True)
        if portrait.additional_object_name.startswith('mount_'):
                hide_all_animal_meshes(animal_collection_name=portrait.additional_object_name)

        if portrait.character_model_file != '/' and os.path.isfile(full_model_path + '.' + model_file_format):
            delete_character()
            delete_materials()
        elif portrait.character_model_file == 'test_man':
            visibility_render_toggle_single_target('Ref_Armature', True)  # Hide ref character

        if include_id_in_portrait == True:
            visibility_render_toggle_single_target('portrait_id_3d_text', True)  # Hide ref 3d text

        purge_orphans()  # Remove nodes not connected to anything


def process_input_file_data(testing_mode, skip_done, process_counter_boolean, process_num_total):
    '''
    PROCESS EACH LINE OF DATA FROM THE INPUT TEXT FILE.
    EACH LINE REPRESENTS A PORTRAIT AND ARGUMENTS SHOULD BE BROKEN UP WITH A TAB

    THE TEXT FILE MUST BE CONSTRUCTED IN THE SAME WAY AS THE PATTERN BELOW
    THE TEXT FILE COMES FROM COPYING DATA FROM A SPREADSHEET WHICH CAN BE FOUND HERE:
        https://docs.google.com/spreadsheets/d/1k1u6FZlU2NwpVpSLFyJOOWlLZKi5YOvBQ2RjgB4cRus/edit#gid=1330500353

    THIS WILL FILTER THE DATA INTO THE PORTRAIT CLASS AND USE ALL INFORMATION TO CREATE THE PORTRAIT
    '''

    process_num = 0

    pattern = (
        r'(?P<portrait_id>\S*)\t'
        r'(?P<portrait_file_output>\S*)\t'
        r'(?P<game>\S*)\t'
        r'(?P<faction>\S*)\t'
        r'(?P<pose_id>\S*)\t'
        r'(?P<additional_object_name>\S*)\t'
        r'(?P<additional_object_texture>\S*)\t'
        r'(?P<character_model_file>\S*)\t'
        r'(?P<character_texture_main_albedo_file>[\S* ]*)\t'
        r'(?P<character_texture_main_pbr_file>[\S* ]*)\t'
        r'(?P<character_texture_extras_albedo_file>[\S* ]*)\t'
        r'(?P<character_texture_extras_pbr_file>[\S* ]*)\t'
        r'(?P<output_directory>\S*)\t'
        r'(?P<visible_models>.*)'  # Must be last (will contain will remaining assignments)
        r'\n?'
    )

    rx = re.compile(pattern)
    
    with open(input_text_file_path) as file, open(log_file, 'w') as log:
        line = file.readline()

        while line:  # There is still a character to process
            match = rx.search(line)

            if match:
                # Found a character to render
                try:
                    working_portrait = Portrait(
                        int(match.group('portrait_id')),
                        str(match.group('portrait_file_output')),
                        str(match.group('game')),
                        str(match.group('faction')),
                        int(match.group('pose_id')),
                        str(match.group('additional_object_name')),
                        str(match.group('additional_object_texture')),
                        str(match.group('character_model_file')),
                        str(match.group('character_texture_main_albedo_file')),
                        str(match.group('character_texture_main_pbr_file')),
                        str(match.group('character_texture_extras_albedo_file')),
                        str(match.group('character_texture_extras_pbr_file')),
                        str(match.group('output_directory')),
                        str(match.group('visible_models'))  # Must be last
                        )

                except Exception as e:
                    log.write('Error creating a portrait: %s %s \n\n' % (str(match.group('portrait_file_output')), str(e)) )  # This try except is here to deal with missing pose_ids. Delete when all pose_ids are assigned.
                    line = file.readline()
                    continue

                portr_out_full = working_portrait.game + '/unit_info/' + working_portrait.output_directory + '/' + working_portrait.portrait_file_output + '_info.png'
                portr_out_closeup = working_portrait.game + '/units/' + working_portrait.output_directory + '/' + working_portrait.portrait_file_output + '.png'
                
                print('Line ({}) | Unit ({}) | Output Directory ({})'.format(working_portrait.portrait_id, working_portrait.portrait_file_output, working_portrait.output_directory))

                # if not os.path.exists(output_renders_path + portr_out_full) or not os.path.exists(output_renders_path + portr_out_closeup):   # SKIP DONE - BOTH PORTRAITS

                # SKIP BOATS
                if working_portrait.pose_id == 600:
                    print('\nBoat portrait! SKIPPING')
                    line = file.readline()

                    process_num+=1
                    continue

                if skip_done:
                    if not os.path.exists(output_renders_path + portr_out_closeup):   # SKIP DONE
                        print('processing portrait: {} | {}\n'.format(working_portrait.portrait_file_output, working_portrait.output_directory))
                        working_portrait.portrait_details()  # Prints portrait details (each line from input_text_file_path)

                        process_portrait(portrait=working_portrait, log=log, testing_mode=testing_mode)

                    else: print('\nSKIPPING - portrait already exists')
                else:
                    print('processing portrait: {} | {}\n'.format(working_portrait.portrait_file_output, working_portrait.output_directory))
                    working_portrait.portrait_details()  # Prints portrait details (each line from input_text_file_path)

                    # Skip no valid data
                    if working_portrait.character_model_file == '/' and working_portrait.additional_object_name == '/':
                        print(f'\nNo character model file or additioal specified, Skipping ({working_portrait.portrait_file_output})')
                    else:
                        process_portrait(portrait=working_portrait, log=log, testing_mode=testing_mode)

            else:
                log.write('Error: line not matched on line: %s \n\n' % line)
                print('\nFAILED - no line not matched, check log.txt')
                pass

            line = file.readline()

            process_num+=1

            if process_counter_boolean and process_num == process_num_total:
                break  # break cycle to test single character



# FUNCTIONS - 07 RUN
def run_process(testing_mode=False):
    '''
    THE MAIN PROCESS WHICH KICKS EVERYTHING OFF
    '''

    time_start = time.time()

    # PROCESS
    if testing_mode:
        visibility_render_toggle_single_target('Ref_Armature', False)

    process_input_file_data(testing_mode=testing_mode, skip_done=False, process_counter_boolean=False, process_num_total=1)

    if testing_mode:
        visibility_render_toggle_single_target('Ref_Armature', True)

    # Reset options
    update_3d_text(portrait_id_number='id card')  # Reset text
    #set_frame_to_id(0)  # Reset frame

    elapsed_time = (time.time() - time_start) / 60.0

    print('\n\nCompleted!\n\tElapsed Time: (%.2f min)' % (elapsed_time))
    print('\tRenders Output Directory: (%s) ' % output_renders_path)


########################################################################################################################

# RUN PROCESS
if __name__ == '__main__':
    print('\n\n###############################\nPortrait Creator: Start Process\n###############################\n\n')
    run_process()
    print('\n\n##################################\nPortrait Creator: Finished Process\n##################################\n\n')
