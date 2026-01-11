bl_info = {
    "name": "Comp Wrangler Pro",
    "author": "Onur ÜNLÜ",
    "version": (4, 1),
    "blender": (4, 5, 0),
    "location": "Compositor > N Panel",
    "description": "Multi-Layer Support & Auto-Fetch Camera Clip",
    "category": "Compositing",
}

import bpy
import os
import re

# --- NAMING PRESETS ---
NAMING_PRESETS = {
    'BLENDER': {
        'CRYPTO_OBJ': 'CryptoObject', 'CRYPTO_MAT': 'CryptoMaterial', 'CRYPTO_AST': 'CryptoAsset',
    }, 
    'MAX': { 
        "Image": "RGB_Color", "Depth": "ZDepth", "Mist": "ZDepth_Mist", "DiffCol": "DiffuseFilter",
        "DiffDir": "Lighting", "DiffInd": "GI", "GlossCol": "ReflectionFilter", "GlossDir": "Reflection",
        "GlossInd": "Reflection_GI", "TransCol": "RefractionFilter", "TransDir": "Refraction",
        "Emit": "SelfIllumination", "Env": "Environment", "AO": "AO", "Shadow": "Shadows",
        "Normal": "Normals", "Vector": "Velocity", "IndexOB": "NodeHandle", "IndexMA": "MaterialID",
        'CRYPTO_OBJ': 'CryptomatteObject', 'CRYPTO_MAT': 'CryptomatteMaterial', 'CRYPTO_AST': 'CryptomatteAsset',
    },
    'MAYA': { 
        "Image": "beauty", "Depth": "Z", "Mist": "Z_mist", "DiffCol": "diffuse_albedo",
        "DiffDir": "diffuse_direct", "DiffInd": "diffuse_indirect", "GlossCol": "specular_albedo",
        "GlossDir": "specular_direct", "GlossInd": "specular_indirect", "TransCol": "transmission_albedo",
        "TransDir": "transmission", "Emit": "emission", "Env": "background", "AO": "ambient_occlusion",
        "Shadow": "shadow_matte", "Normal": "N", "Vector": "motion_vector", "IndexOB": "object_id",
        "IndexMA": "material_id",
        'CRYPTO_OBJ': 'crypto_object', 'CRYPTO_MAT': 'crypto_material', 'CRYPTO_AST': 'crypto_asset',
    },
    'C4D': { 
        "Image": "Beauty", "Depth": "Depth", "Mist": "Depth Mist", "DiffCol": "Diffuse Color",
        "DiffDir": "Diffuse Direct", "DiffInd": "Diffuse Indirect", "GlossCol": "Reflection Color",
        "GlossDir": "Reflection Direct", "GlossInd": "Reflection Indirect", "TransCol": "Refraction Color",
        "TransDir": "Refraction", "Emit": "Emission", "Env": "Environment", "AO": "Ambient Occlusion",
        "Shadow": "Shadow", "Normal": "Normal", "Vector": "Motion Vector", "IndexOB": "Object Buffer",
        "IndexMA": "Material ID",
        'CRYPTO_OBJ': 'Cryptomatte Object', 'CRYPTO_MAT': 'Cryptomatte Material', 'CRYPTO_AST': 'Cryptomatte Asset',
    }
}

# --- YARDIMCI FONKSİYONLAR ---

def clean_wrangler_nodes(nodes):
    """Sadece bizim oluşturduğumuz (damgalı) node'ları siler."""
    nodes_to_remove = []
    for n in nodes:
        if 'cw_created' in n.keys():
            nodes_to_remove.append(n)
        elif n.label in ["Video Plate", "Auto Scale", "Auto Alpha", "Auto Normalize", "Auto Denoise"] or n.label.startswith("Export ("):
            nodes_to_remove.append(n)
            
    for n in nodes_to_remove:
        nodes.remove(n)

def tag_node(node):
    """Node'a biz oluşturduk damgası vurur."""
    node['cw_created'] = True
    return node

# --- OPERATORS ---

class NODE_OT_CompWrangler_Preview(bpy.types.Operator):
    """Ctrl+M: Video Arka Plan Kurulumu"""
    bl_idname = "node.comp_wrangler_preview"
    bl_label = "Setup Background Cam"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.area.type != 'NODE_EDITOR' or context.space_data.tree_type != 'CompositorNodeTree':
            self.report({'WARNING'}, "Sadece Compositor içinde çalışır!")
            return {'CANCELLED'}

        scene = context.scene
        scene.use_nodes = True
        tree = scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # 1. Temizlik
        clean_wrangler_nodes(nodes)

        # 2. Temel Node'lar
        comp_node = next((n for n in nodes if n.type == 'COMPOSITE'), None)
        if not comp_node:
            comp_node = nodes.new('CompositorNodeComposite')
            comp_node.location = (800, 0)
            
        viewer_node = next((n for n in nodes if n.type == 'VIEWER'), None)
        if not viewer_node:
            viewer_node = nodes.new('CompositorNodeViewer')
            viewer_node.location = (800, 200)

        # 3. Render Layer
        rl_node = tag_node(nodes.new('CompositorNodeRLayers'))
        rl_node.location = (0, 400)
        rl_node.layer = context.window.view_layer.name 

        base_x, base_y = rl_node.location

        # 4. Video Node (Movie Clip)
        movie_node = tag_node(nodes.new('CompositorNodeMovieClip'))
        movie_node.location = (base_x - 500, base_y - 200)
        movie_node.label = "Video Plate"
        
        # --- NEW: CAMERA FETCH LOGIC ---
        # Aktif kamerayı bul, içindeki background images'ı tara, movie clip varsa kap getir.
        cam = scene.camera
        if cam and cam.data.background_images:
            for bg in cam.data.background_images:
                # Sadece Movie Clip tipindekileri alıyoruz
                if bg.source == 'MOVIE_CLIP' and bg.clip:
                    movie_node.clip = bg.clip
                    self.report({'INFO'}, f"Kameradan Clip Çekildi: {bg.clip.name}")
                    break
        # -------------------------------
        
        scale_node = tag_node(nodes.new('CompositorNodeScale'))
        scale_node.space = 'RENDER_SIZE'
        scale_node.location = (base_x - 200, base_y - 200)
        scale_node.label = "Auto Scale"
        
        alpha_node = tag_node(nodes.new('CompositorNodeAlphaOver'))
        alpha_node.location = (base_x + 300, base_y)
        alpha_node.label = "Auto Alpha"
        
        # Bağlantılar
        links.new(movie_node.outputs[0], scale_node.inputs[0])
        links.new(scale_node.outputs[0], alpha_node.inputs[1]) # BG
        links.new(rl_node.outputs[0], alpha_node.inputs[2])    # FG
        links.new(alpha_node.outputs[0], comp_node.inputs[0])
        links.new(alpha_node.outputs[0], viewer_node.inputs[0])

        movie_node.select = True
        nodes.active = movie_node
        
        self.report({'INFO'}, "Background Setup Tamamlandı.")
        return {'FINISHED'}


class NODE_OT_CompWrangler_Export(bpy.types.Operator):
    """Ctrl+Shift+E: Tüm View Layerlar için EXR Export"""
    bl_idname = "node.comp_wrangler_export"
    bl_label = "Setup EXR Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.area.type != 'NODE_EDITOR' or context.space_data.tree_type != 'CompositorNodeTree':
            self.report({'WARNING'}, "Sadece Compositor içinde çalışır!")
            return {'CANCELLED'}

        scene = context.scene
        scene.use_nodes = True
        tree = scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # 1. Derin Temizlik
        clean_wrangler_nodes(nodes)

        # 2. Ayarlar
        target_app = scene.comp_wrangler_target_app
        workflow_style = scene.comp_wrangler_workflow
        name_map = NAMING_PRESETS.get(target_app, {})
        
        current_path = scene.render.filepath
        if not current_path: current_path = "//render"
        dirname = os.path.dirname(bpy.path.abspath(current_path))
        basename = os.path.basename(current_path)
        if "." in basename: basename = basename.rsplit(".", 1)[0]

        # 3. Her View Layer İçin Döngü
        view_layers = scene.view_layers
        y_offset = 0

        for layer in view_layers:
            # A. Render Layer
            rl_node = tag_node(nodes.new('CompositorNodeRLayers'))
            rl_node.layer = layer.name
            rl_node.location = (0, 400 + y_offset)
            rl_node.label = f"RL: {layer.name}"

            # B. Export Path
            style_suffix = "_raw" if workflow_style == 'NUKE' else "_norm"
            layer_clean_name = layer.name.replace(" ", "_")
            new_filename = f"{basename}_{layer_clean_name}_export{style_suffix}_"
            final_path = os.path.join(dirname, new_filename)

            # C. Output File Node
            out_node = tag_node(nodes.new('CompositorNodeOutputFile'))
            out_node.location = (600, 400 + y_offset)
            out_node.label = f"Export ({layer.name})"
            out_node.base_path = final_path
            
            out_node.format.file_format = 'OPEN_EXR_MULTILAYER'
            out_node.format.color_depth = '32'
            
            if hasattr(out_node.format, 'exr_codec'):
                 out_node.format.exr_codec = 'ZIP'
            else:
                 out_node.format.codec = 'ZIP' 
            
            out_node.file_slots.clear()

            # D. Pass Bağlantıları
            norm_node = None
            denoise_node = None

            for output in rl_node.outputs:
                if not output.enabled: continue
                
                original_name = output.name
                target_name = name_map.get(original_name, original_name)
                
                # Crypto
                if "Crypto" in original_name:
                    crypto_prefix = ""
                    if "Object" in original_name: crypto_prefix = name_map.get('CRYPTO_OBJ', 'CryptoObject')
                    elif "Material" in original_name: crypto_prefix = name_map.get('CRYPTO_MAT', 'CryptoMaterial')
                    elif "Asset" in original_name: crypto_prefix = name_map.get('CRYPTO_AST', 'CryptoAsset')
                    else: crypto_prefix = original_name
                    
                    suffix_match = re.search(r'\d+$', original_name)
                    suffix = suffix_match.group() if suffix_match else ""
                    target_name = f"{crypto_prefix}{suffix}"
                    
                    out_node.file_slots.new(target_name)
                    links.new(output, out_node.inputs[target_name])
                    continue

                # Depth
                if original_name == "Depth":
                    if workflow_style == 'NUKE':
                        out_node.file_slots.new(target_name)
                        links.new(output, out_node.inputs[target_name])
                    elif workflow_style == 'AE':
                        if not norm_node:
                            norm_node = tag_node(nodes.new('CompositorNodeNormalize'))
                            norm_node.location = (200, 300 + y_offset)
                            norm_node.label = "Auto Normalize"
                        if not denoise_node:
                            denoise_node = tag_node(nodes.new('CompositorNodeDenoise'))
                            denoise_node.location = (400, 300 + y_offset)
                            denoise_node.label = "Auto Denoise"
                        
                        out_node.file_slots.new(target_name) 
                        links.new(output, norm_node.inputs[0])
                        links.new(norm_node.outputs[0], denoise_node.inputs[0])
                        links.new(denoise_node.outputs[0], out_node.inputs[target_name])
                
                # Standard
                else:
                    out_node.file_slots.new(target_name)
                    links.new(output, out_node.inputs[target_name])
            
            y_offset -= 400

        self.report({'INFO'}, f"Export Setup: {len(view_layers)} Layer Hazırlandı.")
        return {'FINISHED'}


# --- N PANEL ---
class NODE_PT_CompWranglerPanel(bpy.types.Panel):
    """Compositor N Panel"""
    bl_label = "Comp Wrangler"
    bl_idname = "NODE_PT_comp_wrangler"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Comp Wrangler"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CompositorNodeTree'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        box1 = layout.box()
        box1.label(text="Background", icon="CAMERA_DATA")
        row = box1.row()
        row.operator("node.comp_wrangler_preview", text="Setup BG (Ctrl+M)")
        
        layout.separator()
        
        box2 = layout.box()
        box2.label(text="Pipeline Export (32-bit)", icon="OUTPUT")
        
        col = box2.column(align=True)
        col.label(text="Target Software:")
        col.prop(scene, "comp_wrangler_target_app", text="")
        
        col.separator()
        col.label(text="Depth Workflow:")
        col.prop(scene, "comp_wrangler_workflow", text="")
        
        col.separator()
        col.operator("node.comp_wrangler_export", text="Setup EXR (Ctrl+Shft+E)", icon="FILE_MOVIE")

# --- REGISTER ---
addon_keymaps = []

classes = (
    NODE_OT_CompWrangler_Preview,
    NODE_OT_CompWrangler_Export,
    NODE_PT_CompWranglerPanel
)

def register():
    bpy.types.Scene.comp_wrangler_target_app = bpy.props.EnumProperty(
        name="Target App",
        description="Choose naming convention",
        items=[
            ('BLENDER', "Blender (Native)", "Standard Blender names"),
            ('MAX', "3ds Max (V-Ray)", "ZDepth, DiffuseFilter, CryptomatteObject..."),
            ('MAYA', "Maya (Arnold)", "Z, diffuse_albedo, crypto_object..."),
            ('C4D', "Cinema 4D", "C4D/Octane names"),
        ],
        default='BLENDER'
    )
    
    bpy.types.Scene.comp_wrangler_workflow = bpy.props.EnumProperty(
        name="Workflow",
        description="Choose Depth Channel Handling",
        items=[
            ('NUKE', "Nuke / Fusion (Raw)", "Exports RAW Depth & Standard Crypto"),
            ('AE', "AE / Photoshop (Visual)", "Exports Norm/Denoise Depth"),
        ],
        default='NUKE'
    )

    for cls in classes:
        bpy.utils.register_class(cls)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi1 = km.keymap_items.new(NODE_OT_CompWrangler_Preview.bl_idname, 'M', 'PRESS', ctrl=True)
        kmi2 = km.keymap_items.new(NODE_OT_CompWrangler_Export.bl_idname, 'E', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi1))
        addon_keymaps.append((km, kmi2))

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.comp_wrangler_target_app
    del bpy.types.Scene.comp_wrangler_workflow
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
