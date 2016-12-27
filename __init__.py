bl_info = {
"name": "QuickTree",
"author": "Wolfgang Pratl",
"version": (0, 0, 4),
"blender": (2, 78, 0),
"location": "View3D > Add > Curve",
"description": ("Quick and randomized use of 'Sapling Tree Gen'. Export for Panda3D with RenderPipeline."),
"category": "Add Curve"}

#Sapling 3 (needed in Blender 2.77 and less)
#https://github.com/abpy/improved-sapling-tree-generator

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    from utils import *
else:
    from quicktree.utils import *

import bpy
# import bmesh  # DUPLI LEAVES
from mathutils import Vector
from math import pi
from os.path import dirname, join, split, splitext, basename

"""
Operator context that will work most of the time.
<ideasman42> you can always do bpy.ops.foo(dict(object=my_obj, scene=my_scene))
"""

class QuickTree(bpy.types.Panel):
    bl_label = "Quick Tree"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("sapling.randomdata",
                     text="Very coarse randomization").mode=1
        
        #row = layout.row(align=True)
        row.operator("sapling.randomdata",
                     text="Coarse randomization").mode=2
        
        row = layout.row(align=True)
        row.operator("sapling.randomdata",
                     text="Leaves randomization").mode=3

        row = layout.row(align=True)
        row.operator("sapling.randomdata",
                     text="Odd branch").mode=4

        row = layout.row(align=True)
        row.operator("sapling.randomdata", text="View for export",
                     icon="COLOR_GREEN").mode=10

        row = layout.box()
        row.prop(context.window_manager, 'bark_base_tex')
        row.prop(context.window_manager, 'bark_normal_tex')
        row.prop(context.window_manager, 'leaf_base_tex')

        row = layout.row(align=True)
        row.prop(context.window_manager, 'egg_fn')
        
        row = layout.row(align=True)
        row.operator("sapling.randomdata", text="Export",
                     icon="EXPORT").mode=20
                     

class RandomData(bpy.types.Operator):
    """ This ties into sapling and randomizes. """
    bl_idname = 'sapling.randomdata'
    bl_label = 'Randomize sapling parameters'
    #bl_options = {'REGISTER'}  # it's the default anyway

    mode = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        if not context.active_operator:
            return False
        else:
            #return context.active_operator.__class__.__name__ == "AddTree"
            return context.active_operator.__module__ == "add_curve_sapling"

    def execute(self, context):
        sapling = context.active_operator
        """
        sap_props = sapling.as_keywords()
        self.report({'INFO'}, str(sap_props.keys()))
        sapling_props = sapling.rna_type.properties

        it's no error to pass a wrong size tuple when setting a sapling
        property, but resets it to default.
        sapling.properties["taper"] = (.1,.2,.3,.4)
        """

        common = [viewing_presets, preferences, lowpoly_presets, wind]

        if self.mode == 0:
            pass
        elif self.mode == 1:
            vc = very_coarse_rules(rand_dict(very_coarse_randomize))
            for k, v in merge_dicts(*common+[vc]).items():
                setattr(sapling, k, v)
        elif self.mode == 2:
            c = coarse_rules(rand_dict(coarse_randomize))
            for k, v in merge_dicts(*common+[c]).items():
                setattr(sapling, k, v)
        elif self.mode == 3:
            #l = rand_dict(leaves)
            #print(l)
            #for k, v in merge_dicts(*common+[l]).items():
            for k, v in merge_dicts(*common+[rand_dict(leaves)]).items():
                setattr(sapling, k, v)

            """
            # DUPLI LEAVES
            # remove old leaf object
            for ob in context.scene.objects:
                if "leaf" in ob.name:
                    ob.select = True
                    bpy.data.objects.remove(ob, do_unlink=True)
                    bpy.ops.object.delete()
            # recreate the bipart leaf to take into account the new leaf size
            sapling.leafDupliObj = create_bipart_leaf(context)
            sapling.leafShape = "dFace"  # "dVert"            
            """

        elif self.mode == 4:
            q = quirk_rules(rand_dict(quirk_randomize))
            for k, v in merge_dicts(*common+[q]).items():
                setattr(sapling, k, v)
        elif self.mode == 10:
            for k, v in export_presets.items():
                setattr(sapling, k, v)
                #sapling.properties[k] = v

        elif self.mode == 20:
            self.export(context)
            return {'FINISHED'}

        # remove previous curve and armature
        for ob in context.scene.objects:
            ob.select = ((ob.type in ("CURVE", "ARMATURE") and 
                          ob.name.startswith("tree")) or (ob.type == "MESH" and
                          ob.name.startswith("leaves")))
        bpy.ops.object.delete()
        
        # uncomment this for quick preview renders by RenderPipeline after
        # exporting. Run RP_MAIN_DIR/toolkit/render_service/service.py and 
        # press F12 in Blender.
        #context.scene.render.engine = 'P3DPBS'

        # set timeline to animation loop length
        context.scene.frame_start = 0
        context.scene.frame_end = export_presets["loopFrames"]
        # position camera so a quick render with F12 will have our tree in view
        pos = Vector((9, -9, 7.5))
        rot = Vector((90, 0, 45))
        context.scene.camera.rotation_mode = 'XYZ'
        context.scene.camera.rotation_euler = rot / 180 * pi
        context.scene.camera.location = pos

        sapling.execute(context)
        return {'FINISHED'}

    def select_tree(self, context):
        for ob in context.scene.objects:
            ob.select = False
            if ob.type in ("CURVE", "MESH") and ob.name == "tree":
                ob.select = True
                context.scene.objects.active = ob
                tree = ob
        return tree

    def select_leaves(self, context):
        for ob in context.scene.objects:
            #print("select_leaves fail obj: ", ob)
            ob.select = False
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
            if ob.type == "MESH" and ob.name == "leaves":
                leaves = ob
                leaves.select = True
                context.scene.objects.active = leaves
        return leaves
        
    def select_scattered_leaves(self, context):
        "DUPLI LEAVES"
        for ob in context.scene.objects:
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
            ob.select = False
            if ob.type == "MESH" and "leaf" in ob.name:
                leaves = ob
                leaves.select = True
                context.scene.objects.active = leaves
                #print(ob.name, type(ob))
        return leaves

    def export(self, context):
        """ We will not use Sapling's 'Make Mesh' option, as we cannot get nice
        UV coordinates that way. """
        
        sapling = context.active_operator
        
        #load textures
        # print(context.window_manager.bark_base_tex, 
        #       context.window_manager.bark_normal_tex, 
        #       context.window_manager.leaf_base_tex)

        #assert context.window_manager.bark_base_tex

        #REMOVE
        # use some defaults for textures
        if not context.window_manager.bark_base_tex:
            context.window_manager.bark_base_tex = "/home/juzzuj/code/eclipse_workspace/GlideGolf/glidegolf/models/trees/tex/bark1.tga"
        if not context.window_manager.bark_normal_tex:
            context.window_manager.bark_normal_tex = "/home/juzzuj/code/eclipse_workspace/GlideGolf/glidegolf/models/trees/tex/bark1_nmp.tga"
        if not context.window_manager.leaf_base_tex:
            context.window_manager.leaf_base_tex = "/home/juzzuj/code/eclipse_workspace/GlideGolf/glidegolf/models/trees/tex/ferny_spring1.png"
        if not context.window_manager.egg_fn:
            #defaults to parent directory of directory the bark texture is in
            context.window_manager.egg_fn = join(
                dirname(dirname(context.window_manager.bark_base_tex)), 
                "freshtree.egg")

        """ select treeArm -> tree (the curve) and in object mode using
        the data (curve) tab check 'use UV for mapping' """
        tree = self.select_tree(context)
        tree.data.use_uv_as_generated = True
        # Using an override, convert curve to mesh: "Mesh from Curve" (Alt+C)
        bpy.ops.object.convert(dict(object=tree, scene=context.scene),
                               target='MESH')

        """
        obsolete try using Make Mesh:
        try:
            bpy.ops.object.modifier_apply(modifier = "Skin")
        except:
            print('WARNING: can\'t apply Skin modifier.')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        #original_area = bpy.context.area.type
        #bpy.context.area.type = 'IMAGE_EDITOR'
        bpy.context.scene.tool_settings.uv_select_mode = 'ISLAND'
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == "IMAGE EDITOR":
                    override = dict(window=window, screen=screen, area=area)
                    bpy.ops.uv.select_all(override, action='SELECT')
                    #rotate 90
                    bpy.ops.transform.rotate(value=1.5708, axis=(-0, -0, -1))
                    #scale y up massively.
                    bpy.ops.transform.resize(value=(8.57624, 8.57624, 8.57624),
                                             constraint_axis=(False, True, False))
                    #scale x down even more.
                    bpy.ops.transform.resize(value=(0.792738, 0.792738, 0.792738),
                                             constraint_axis=(True, False, False))
                    #scale up uniformly.
                    bpy.ops.transform.resize(value=(2.15924, 2.15924, 2.15924),
                                             constraint_axis=(False, False, False))
                    break
        """
        # in object mode select newly created tree mesh
        # rotate and resize UVs 
        tree = self.select_tree(context)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.context.area.type = 'IMAGE_EDITOR'
        context.scene.tool_settings.uv_select_mode = 'ISLAND'
        bpy.ops.uv.select_all(dict(object=tree, scene=context.scene), 
                                action='TOGGLE')
        # rotate 90
        bpy.ops.transform.rotate(value=1.5708, axis=(0, 0, -1))
        # scale y up massively.
        bpy.ops.transform.resize(value=(8.57624, 8.57624, 8.57624), 
                                 constraint_axis=(False, True, False))
        # scale x down even more.
        bpy.ops.transform.resize(value=(0.792738, 0.792738, 0.792738), 
                                 constraint_axis=(True, False, False))
        # scale up uniformly.
        bpy.ops.transform.resize(value=(2.15924, 2.15924, 2.15924), 
                                 constraint_axis=(False, False, False))

        # bark material + textures
        bark_base_tex = bpy.data.textures.new('bark_base', type='IMAGE')
        bark_base_tex.image = bpy.data.images.load(
            context.window_manager.bark_base_tex)
        bark_normal_tex = bpy.data.textures.new('bark_normal', type='IMAGE')
        bark_normal_tex.image = bpy.data.images.load(
            context.window_manager.bark_normal_tex)

        bark = bpy.data.materials.new('Bark')
        bark.pbepbs.shading_model = 'DEFAULT'
        bark.pbepbs.emissive_factor = 0.
        bark.pbepbs.ior = 1.5
        bark.pbepbs.roughness = 0.85
        bark.pbepbs.normal_strength = 0.8

        for tex in (bark_base_tex, bark_normal_tex):
            slot = bark.texture_slots.add()
            slot.texture = tex
            slot.texture_coords = 'UV'
            slot.mapping = 'FLAT'
            slot.uv_layer = 'Orco'

        context.object.data.materials.append(bark)
        """
        # DUPLI LEAVES
        # we still have DupliFaces and YABEE can't export them.
        # select one of the duplicates
        self.select_leaves(context)
        bpy.ops.object.duplicates_make_real()
        # select all now-real duplicates and join them
        self.select_scattered_leaves(context)
        bpy.ops.object.join()
        # parent joint scattered leaves to leaves.
        custom_leaves = [ob for ob in context.scene.objects
                         if ob.type == "MESH" and "leaf" in ob.name][0]
        custom_leaves.parent = context.scene.objects["tree"]  # self.select_leaves(context)
        # get vertex groups and modifier from (or just like in) leaves over to bipart_leaf
        
        #custom_leaves.data.materials.append(
        #                context.scene.objects["leaves"].data.materials[0])
        mod = custom_leaves.modifiers.new("windSway", "ARMATURE")
        mod.object = context.scene.objects["treeArm"]
        
        mod = custom_leaves.modifiers.new("vertex_grps", "DATA_TRANSFER")
        mod.object = context.scene.objects["leaves"]
        mod.use_vert_data = True
        mod.data_types_verts = {"VGROUP_WEIGHTS"}
        mod.layers_vgroup_select_src = "ALL"
        bpy.ops.object.datalayout_transfer(modifier="vertex_grps")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="vertex_grps")
        # remove leaves object
        context.scene.objects["leaves"].select = True
        bpy.data.objects.remove(context.scene.objects["leaves"], do_unlink=True)
        #bpy.ops.object.delete()
        custom_leaves.name = "leaves"
        """

        #leaf material + texture
        leaf_base_tex = bpy.data.textures.new('leaf_base', type='IMAGE')
        leaf_base_tex.image = bpy.data.images.load(
            context.window_manager.leaf_base_tex)

        leaf = bpy.data.materials.new('Leaf')
        """ this makes all leaves two-sided. no need to call set_two_sided in
        Panda, which would also make the tree two-sided. """
        leaf.game_settings.use_backface_culling = False
        leaf.pbepbs.shading_model = 'FOLIAGE'
        leaf.pbepbs.emissive_factor = 0.
        leaf.pbepbs.ior = 1.3
        leaf.pbepbs.roughness = 0.55
        leaf.pbepbs.normal_strength = 0.0

        slot = leaf.texture_slots.add()
        slot.texture = leaf_base_tex
        slot.texture_coords = 'UV'
        slot.mapping = 'FLAT'
        slot.uv_layer = 'leafUV'  # in case of leafShape rect
        # slot.uv_layer = 'UVMap'  # DUPLI LEAVES

        leaves = self.select_leaves(context)

        context.object.data.materials.append(leaf)

        # bpy.ops.object.shade_smooth(dict(object=ob, scene=context.scene))
        ####### use_auto_smooth must be on to export vertex normals!
        context.area.type = 'VIEW_3D'
        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True

        """
        see
        https://blenderartists.org/forum/showthread.php?284736-Normals-Editing-in-Blender&p=2713763&viewfull=1#post2713763
        
        1. apply modifier to reorient clnors (C-implemented loop normals)
        2. calc_normals_split()
        3. take a peek
            for lidx in C.object.data.polygons[5].loop_indices:
                C.object.data.loops[lidx].normal  # all 0
        4. don't try to assign new vertex normals from the now correct loop normals.
           Instead make YABEE fetch the loop normals as custom vertex normals at export time.

        map_vertex2loop = {C.object.data.loops[lidx].vertex_index: lidx for p in 
          C.object.data.polygons for lidx in p.loop_indices} 

        for p in C.object.data.polygons:
            for lidx in p.loop_indices:
                C.object.data.vertices[C.object.data.loops[lidx].vertex_index].normal = C.object.data.loops[lidx].normal
        """
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        leaves.data.create_normals_split()
        splitnormals_mod = leaves.modifiers.new("Set Split Normals", 
                                                "NORMAL_EDIT")
        """ using a very rough spherical approximation of tree shape here.
        the center from which vertex normals radiate outward is at
        X=0 Y=0 Z=tree scale/2.
        """
        splitnormals_mod.offset[2] = sapling.scale / 2
        #print("Leaves custom split normals:", leaves.data.has_custom_normals)
        bpy.ops.object.modifier_apply(apply_as='DATA', 
                                      modifier="Set Split Normals")
        leaves.data.calc_normals_split()  # now leaves.data.has_custom_normals is True

        """
        At this point "treeArm" is the parent of "tree", which in turn is the 
        parent of "leaves".
        """
        #self.select_leaves(context)
        #bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        # as an approximation of branch (and stem) radii we use the largest, which should be the stem start radius
        # this is mostly from sapling/utils.py#933
        max_stem_radius = (sapling.scale + sapling.scaleV) * sapling.ratio * sapling.scale0 * (1+sapling.scaleV0)
        for bone in context.scene.objects["treeArm"].data.bones:
            bone.envelope_distance = max_stem_radius / 3.
            #pass
            
        """ To make YABEE export the animation correctly we need vertex groups 
        for the tree mesh, too. This armature envelope parent option will keep
        the current parent (=treeArm) / child (=tree) relationship and create
        vertex groups. """
        tree = self.select_tree(context)
        treeArm = context.blend_data.objects["treeArm"]
        treeArm.select = True
        context.scene.objects.active = treeArm
        bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
        #bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        
        """
        # if you choose to unparent tree and leaves from treeArm, follow this.
        # now, all meshes that are to be animated will need an armature modifier
        # on "leaves" it is intact. we create the same one for "tree".
        tree = self.select_tree(context)
        bpy.ops.object.modifier_add(type='ARMATURE')
        bpy.context.object.modifiers["Armature"].name = "windSway"
        bpy.context.object.modifiers["windSway"].object = bpy.data.objects["treeArm"]
        bpy.context.object.modifiers["windSway"].use_vertex_groups = True
        bpy.context.object.modifiers["windSway"].use_bone_envelopes = False  # True  # yeah, maybe.
        """
        
        """ bake the animation/action. it needs a frame_range to be exported
        successfully. as is, no keyframes can be set on it (its f-curves have 
        modifiers) and hence it has no frame_range. 
        This will create a new action called 'Action'. """
        bpy.ops.nla.bake(frame_start=0,
                         frame_end=sapling.loopFrames,
                         only_selected=False, bake_types={'POSE'})
        #print("Actions present after baking:", [action for action in bpy.data.actions])
        #print("Seed:", sapling.seed)
        
        # remove the original action Sapling created, as it's of no use.
        bpy.data.actions.remove(bpy.data.actions["windAction"], do_unlink=True)
        
        bpy.data.actions["Action"].name = "windAction"
        """ we need to do this because otherwise YABEE will export actions 
        twice (once with a .001 postfix). """
        bpy.data.actions["windAction"].use_fake_user = True
        context.area.type = 'DOPESHEET_EDITOR'
        context.space_data.mode = 'ACTION'
        bpy.ops.action.unlink()
        context.area.type = 'VIEW_3D'

        #select stuff for export: leaves, tree and treeArm
        for ob in context.scene.objects:
            ob.select = (ob.type in ("MESH", "ARMATURE") and 
                         ob.name.startswith(("tree", "leaves")))
                         # EXPERIMENTAL
                         #("leaf" in ob.name or ob.name.startswith("tree")))

        context.scene.yabee_settings.opt_tbs_proc = 'NO'
        context.scene.yabee_settings.opt_anims_from_actions = True
        context.scene.yabee_settings.opt_separate_anim_files = True  # False
        context.scene.yabee_settings.opt_copy_tex_files = True
        context.scene.yabee_settings.opt_merge_actor = False
        context.scene.yabee_settings.opt_apply_modifiers = True
        context.scene.yabee_settings.opt_use_loop_normals = True
        context.scene.yabee_settings.opt_export_pbs = True

        """this is important or else all settings above will be overwritten by 
        the default YABEE settings. """
        context.scene.yabee_settings.first_run = False

        #will save to parent directory of directory the bark texture is in
        #bpy.ops.export.panda3d_egg(filepath=join(
        #    dirname(dirname(context.window_manager.bark_base_tex)), 
        #    "freshtree.egg"))
        bpy.ops.export.panda3d_egg(filepath=context.window_manager.egg_fn)

        data = {}
        for a, b in (sapling.as_keywords(ignore=("chooseSet", "presetName", 
            "limitImport", "do_update", "overwrite", "leafDupliObj"))).items():
            # If the property is a vector property then add the slice to the list
            try:
                len(b)
                data[a] = b[:]
            except:  # Otherwise, it is fine so just add it
                data[a] = b

        """ bpy.ops.sapling.exportdata is very hackish. it will only allow
        writing to preset directories, use eval etc. """
        #bpy.ops.sapling.exportdata(data=repr([
        # repr(data), basename(context.window_manager.egg_fn), True]))

        # our implementation saves to a file named like the EGG.
        with open(splitext(context.window_manager.egg_fn)[0] + ".py", "w") as f:
            f.write(repr(data))

        #TODO find a sane solution to the (automatic) vertex group creation
        # problem of the tree mesh. stick with ARMATURE_AUTO and forget about
        # the envelopes. Or use ARMATURE_ENVELOPE after finding a sane size for
        # the envelopes/or even bones sizes.

        #TODO use leaf_DupliObj for non-flat leaves?
        
        #TODO save blend file?
        #TODO seems after using Quicktree's buttons, switching the tabs in Sapling
        # may reset the tree. Maybe we need to redraw the toolbar.
        
        # CodeManX: 
        # tag the appropriate context area.
        # bpy.context.area.tag_redraw() # granted the context area is the one you are working with 

def create_bipart_leaf(context):
    "# DUPLI LEAVES"
    leaf_name = "bipart_leaf"  # must always contain "leaf"
    sapling = context.active_operator
    # this creates UVs which seem ok
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=3,
                                    y_subdivisions=2,
                                    radius=sapling.leafScale/2,
                                    calc_uvs=True,
                                    view_align=False, 
                                    enter_editmode=True,
                                    location=(0, 0, 0),
                                    layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

    context.scene.objects.active.name = leaf_name
    bm = bmesh.from_edit_mesh(context.scene.objects.active.data)
    
    # raise the vertices of the central edge
    for edge in bm.edges:
        if not edge.is_boundary:
            for vert in edge.verts:
                vert.co.z += sapling.leafScale/8

    #~ # Create mesh
    #~ me = bpy.data.meshes.new('bipart_leaf')
    #~ # Create object
    #~ ob = bpy.data.objects.new('bipart_leaf', me) 
    #~ ob.location = (-8, 0, 0)
    #~ ob.show_name = True
    #~ # Link object to scene
    #~ context.scene.objects.link(ob)
    
    # Get a BMesh representation
    #bm = bmesh.new() # create an empty BMesh
    #bm.from_mesh(me) # fill it in from a Mesh

        
    # Hot to create vertices
    #vertex1 = bm.verts.new( (0.0, 0.0, 3.0) )
    #vertex2 = bm.verts.new( (2.0, 0.0, 3.0) )
    #vertex3 = bm.verts.new( (2.0, 2.0, 3.0) )
    #vertex4 = bm.verts.new( (0.0, 2.0, 3.0) )

    # Initialize the index values of this sequence.
    #bm.verts.index_update()

    # How to create edges 
    #bm.edges.new( (vertex1, vertex2) )
    #bm.edges.new( (vertex2, vertex3) )
    #bm.edges.new( (vertex3, vertex4) )
    #bm.edges.new( (vertex4, vertex1) )

    # How to create a face
    # it's not necessary to create the edges before, I made it only to show how create 
    # edges too
    #bm.faces.new( (vertex1, vertex2, vertex3, vertex4) )

    # Finish up, write the bmesh back to the mesh
    #bm.to_mesh(me)
    
    #TODO get origin right
    
    # Finish up, write the bmesh back to the mesh
    bmesh.update_edit_mesh(context.scene.objects.active.data, False, False)
    # Set mode back to object. Sapling operator will not be active otherwise.
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    # Apply location.
    #bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    return leaf_name

def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.bark_base_tex = bpy.props.StringProperty(
        name="Bark Basecolor Texture", subtype="FILE_PATH")
    bpy.types.WindowManager.bark_normal_tex = bpy.props.StringProperty(
        name="Bark Normal Texture", subtype="FILE_PATH")
    bpy.types.WindowManager.leaf_base_tex = bpy.props.StringProperty(
        name="Leaf Basecolor Texture", subtype="FILE_PATH")
    bpy.types.WindowManager.egg_fn = bpy.props.StringProperty(
        name="EGG File", subtype="FILE_PATH")

def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()
