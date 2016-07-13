bl_info = {
"name": "Quick Tree",
"author": "Wolfgang Pratl",
"version": (0, 0, 2),
"blender": (2, 77, 0),
"location": "View3D > Add > Curve",
"description": ("Quick and randomized use of Sapling_3. See "
    "https://github.com/abpy/improved-sapling-tree-generator"),
"category": "Add Curve"}

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    from utils import *
else:
    from quicktree.utils import *

import bpy
from os.path import dirname, join, split

"""
Magic operator context that will always work!
#[12:59:12] <ideasman42> you can always do bpy.ops.foo(dict(object=my_obj, scene=mys_cene))
"""


class QuickTree(bpy.types.Panel):
    bl_label = "Quick Tree"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.operator("sapling.randomdata", text="Very coarse randomization").mode=1
        
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.operator("sapling.randomdata", text="Coarse randomization").mode=2
        
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.operator("sapling.randomdata", text="Leaves randomization").mode=3

        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.operator("sapling.randomdata", text="View for export").mode=10

        row = layout.box()
        row.prop(context.window_manager, 'bark_base_tex')
        row.prop(context.window_manager, 'bark_normal_tex')
        row.prop(context.window_manager, 'leaf_base_tex')

        # row = layout.row(align=True)
        # row.alignment = 'LEFT'
        row.operator("sapling.randomdata", text="Export").mode=20

class RandomData(bpy.types.Operator):
    #"""This ties into sapling and randomizes"""
    bl_idname = 'sapling.randomdata'
    bl_label = 'Randomize sapling parameters'
    #bl_options = {'REGISTER'}  # it's the default anyway

    mode = bpy.props.IntProperty()
    # view_export = bpy.props.BoolProperty(name='View for export', description=
    #     'Show leaves and armature', default=False)
    bark_normal_tex = bpy.props.StringProperty(name="Bark Normal Texture",
        subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        #return context.active_operator.__module__ == "add_curve_sapling_3"
        return context.active_operator.__class__.__name__ == "AddTree"

    def execute(self, context):
        # via context.window_manager.operators you can get there, too
        sapling3 = context.active_operator
        #sap_props = sapling3.as_keywords()
        #self.report({'INFO'}, str(sap_props.keys()))
        sapling3_props = sapling3.rna_type.properties
        
        #self.last_props = copy.copy(sapling3.properties)
        """
        #two ways
        sapling3.bevel = True
        sapling3.properties["scale"] = 50.
        #float vector property
        # print(sapling3.properties["taper"][:])
        # also: len(sapling3.properties["taper"])  # 4
        #one
        sapling3.properties["taper"][1] = .2
        #all
        sapling3.properties["taper"] = (.1,.2,.3,.4)
        #it's no error to pass a wrong size tuple, but resets it to default
        """

        common = [viewing_presets, preferences, lowpoly_presets, wind]
        #print(common)
        if self.mode == 0:
            pass
        elif self.mode == 1:
            vc = very_coarse_rules(rand_dict(very_coarse_randomize))
            for k, v in merge_dicts(*common+[vc]).items():
                setattr(sapling3, k, v)
        elif self.mode == 2:
            c = coarse_rules(rand_dict(coarse_randomize))
            for k, v in merge_dicts(*common+[c]).items():
                setattr(sapling3, k, v)
        elif self.mode == 3:
            #leaves = {k: randomize(v) for k, v in leaves.items()}
            l = rand_dict(leaves)
            #print(l)
            for k, v in merge_dicts(*common+[l]).items():
                setattr(sapling3, k, v)

        elif self.mode == 10:
            for k, v in export_presets.items():
                sapling3.properties[k] = v

        elif self.mode == 20:
            self.export(context)
            return {'FINISHED'}
        # else:
        #     for k, v in export_presets.items():
        #         sapling3.properties[k] = not v

        # props = context.window_manager.quicktree_props
        # if props.view_export:
        #     print("should be viewing for export in execute")

        #remove previous curve and armature
        for ob in context.scene.objects:
            ob.select = (((ob.type == "CURVE" or ob.type == "ARMATURE") and 
                           ob.name.startswith("tree")) or (ob.type == "MESH" and
                           ob.name.startswith("leaves")))

        bpy.ops.object.delete()
        #context.active_operator.execute(context)
        sapling3.execute(context)
        #maybe
        #context.scene.update()
        return {'FINISHED'}

    def select_tree(self, context):
        for ob in context.scene.objects:
            ob.select = False
            if (ob.type == "CURVE" or ob.type == "MESH") and ob.name == "tree":
                ob.select = True
                ####bpy.context.scene.objects.active = ob
                context.scene.objects.active = ob
                ####ob.data.use_uv_as_generated = True
                tree = ob
        return tree

    def select_leaves(self, context):
        for ob in context.scene.objects:
            ob.select = False
            # context.scene.objects.active = ob
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
            if ob.type == "MESH" and ob.name == "leaves":
                leaves = ob
                leaves.select = True
                context.scene.objects.active = leaves
                # context.scene.objects.active = ob
                #ob.data.use_uv_as_generated = True

        return leaves

    def export(self, context):
        """ select treeArm -> tree (the curve) and in object mode using 
        the data (curve) tab check 'use UV for mapping' """
        tree = self.select_tree(context)
        tree.data.use_uv_as_generated = True

        # #use alt+c to convert to mesh: "Mesh from Curve"
        bpy.ops.object.convert(dict(object=tree, scene=context.scene), target='MESH')

        #bpy.ops.object.convert({'selected_objects': context['selected_objects']}, target='MESH')
        
        #edit UVs
        #bpy.ops.object.editmode_toggle()
        #bpy.ops.object.mode_set(mode='EDIT')

        #with object mode selected newly created tree mesh
        #edit mode
        #select all
        #select all uvs

        tree = self.select_tree(context)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.context.area.type = 'IMAGE_EDITOR'
        context.scene.tool_settings.uv_select_mode = 'ISLAND'
        bpy.ops.uv.select_all(dict(object=tree, scene=context.scene), 
                                action='TOGGLE')
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

        #bark material + textures
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
        # bark.pbepbs.normal_strength = 1.0

        for tex in (bark_base_tex, bark_normal_tex):
            slot = bark.texture_slots.add()
            slot.texture = tex
            slot.texture_coords = 'UV'
            slot.mapping = 'FLAT'
            slot.uv_layer = 'Orco'

        context.object.data.materials.append(bark)

        #leaf material + texture
        leaf_base_tex = bpy.data.textures.new('leaf_base', type='IMAGE')
        leaf_base_tex.image = bpy.data.images.load(
            context.window_manager.leaf_base_tex)

        leaf = bpy.data.materials.new('Leaf')
        leaf.pbepbs.shading_model = 'FOLIAGE'
        leaf.pbepbs.emissive_factor = 0.
        leaf.pbepbs.ior = 1.5
        leaf.pbepbs.roughness = 0.55
        leaf.pbepbs.normal_strength = 0.0

        slot = leaf.texture_slots.add()
        slot.texture = leaf_base_tex
        slot.texture_coords = 'UV'
        slot.mapping = 'FLAT'
        slot.uv_layer = 'leafUV'

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
        # bpy.ops.object.mode_set(mode='OBJECT')
        # context.scene.objects.active = leaves
        # leaves.select = True
        #maybe remove windSway modifier
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        leaves.data.create_normals_split()
        splitnormals_mod = leaves.modifiers.new("Set Split Normals", "NORMAL_EDIT")
        # using a very rough spherical approximation of veggie shape here.
        # the center from which vertex normals radiate outward is at X=0 Y=0 Z=half veggie scale.
        # print("Split mod data:", dir(splitnormals_mod), splitnormals_mod.offset)
        splitnormals_mod.offset[2] = preferences["scale"] / 2
        #print("Leaves custom split normals data: ", leaves.data.has_custom_normals)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Set Split Normals")
        leaves.data.calc_normals_split()  # now leaves.data.has_custom_normals is True
        #print("Leaves custom split normals data: ", leaves.data.has_custom_normals)

        #select stuff for export: leaves, tree and treeArm
        for ob in context.scene.objects:
            ob.select = ((ob.type == "MESH" or ob.type == "ARMATURE") and 
                         ob.name.startswith(("tree", "leaves")))

        context.scene.yabee_settings.opt_tbs_proc = 'NO'
        context.scene.yabee_settings.opt_anims_from_actions = True
        context.scene.yabee_settings.opt_separate_anim_files = False
        context.scene.yabee_settings.opt_copy_tex_files = True
        context.scene.yabee_settings.opt_merge_actor = True
        context.scene.yabee_settings.opt_apply_modifiers = False  # True
        context.scene.yabee_settings.opt_use_loop_normals = True
        context.scene.yabee_settings.opt_export_pbs = True

        #this is important or else all settings above will be overwritten by default YABEE settings.
        context.scene.yabee_settings.first_run = False

        #bpy.ops.export.panda3d_egg(filepath=export_fn_egg)
        #will save to parent directory of directory the bark texture is in
        bpy.ops.export.panda3d_egg(filepath=join(
            dirname(dirname(context.window_manager.bark_base_tex)), 
            "freshtree.egg"))


def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.bark_base_tex = bpy.props.StringProperty(name="Bark Basecolor Texture", subtype="FILE_PATH")
    bpy.types.WindowManager.bark_normal_tex = bpy.props.StringProperty(
        name="Bark Normal Texture", subtype="FILE_PATH")
    bpy.types.WindowManager.leaf_base_tex = bpy.props.StringProperty(name="Leaf Basecolor Texture", subtype="FILE_PATH")

def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()