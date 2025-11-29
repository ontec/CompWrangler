bl_info = {
    "name": "Comp Wrangler",
    "author": "Onur ÜNLÜ",
    "version": (1, 5),
    "blender": (4, 0, 0),
    "location": "Compositor > Ctrl + M",
    "description": "Instantly sets up a background video workflow. Creates a Movie Clip -> Scale (Render Size) -> Alpha Over chain and auto-wires it to Render Layers, Composite, and Viewer nodes.",
    "category": "Compositing",
}

import bpy

class NODE_OT_AdoCompWrangler(bpy.types.Operator):
    """Ado Comp Wrangler: Auto connects Movie Clip, Scale, Alpha Over, Composite and Viewer."""
    bl_idname = "node.ado_comp_wrangler"
    bl_label = "Ado Comp Wrangler"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Ensure we are in the Node Editor and Compositor
        if context.area.type != 'NODE_EDITOR' or context.space_data.tree_type != 'CompositorNodeTree':
            self.report({'WARNING'}, "Please use inside the Compositor!")
            return {'CANCELLED'}

        scene = context.scene
        scene.use_nodes = True
        tree = scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # --- FIND EXISTING NODES ---
        rl_node = None
        comp_node = None
        viewer_node = None

        for n in nodes:
            if n.type == 'R_LAYERS':
                rl_node = n
            elif n.type == 'COMPOSITE':
                comp_node = n
            elif n.type == 'VIEWER':
                viewer_node = n
        
        # --- CREATE MISSING NODES ---
        # If essential nodes are missing, create them at default positions
        if not rl_node:
            rl_node = nodes.new('CompositorNodeRLayers')
            rl_node.location = (0, 400)
        
        if not comp_node:
            comp_node = nodes.new('CompositorNodeComposite')
            comp_node.location = (800, 400)

        if not viewer_node:
            viewer_node = nodes.new('CompositorNodeViewer')
            viewer_node.location = (800, 600)

        # Use Render Layers as the anchor position
        base_x = rl_node.location.x
        base_y = rl_node.location.y

        # --- CREATE NEW CHAIN ---
        
        # 1. Movie Clip Node
        movie_node = nodes.new(type='CompositorNodeMovieClip')
        movie_node.location = (base_x - 500, base_y - 200)
        movie_node.label = "Select Video Here"
        
        # 2. Scale Node (Force set to Render Size)
        scale_node = nodes.new(type='CompositorNodeScale')
        scale_node.space = 'RENDER_SIZE'
        scale_node.location = (base_x - 200, base_y - 200)
        
        # 3. Alpha Over Node
        alpha_node = nodes.new(type='CompositorNodeAlphaOver')
        alpha_node.location = (base_x + 300, base_y)
        
        # --- AUTO WIRING ---
        
        # Connect Movie Clip to Scale
        links.new(movie_node.outputs[0], scale_node.inputs[0])
        
        # Connect Scale to Alpha Over (Input 1: Background)
        links.new(scale_node.outputs[0], alpha_node.inputs[1])
        
        # Connect Render Layers to Alpha Over (Input 2: Foreground)
        links.new(rl_node.outputs[0], alpha_node.inputs[2])
        
        # Connect Output to Composite (Final Render Output)
        links.new(alpha_node.outputs[0], comp_node.inputs[0])

        # Connect Output to Viewer (Realtime Preview)
        links.new(alpha_node.outputs[0], viewer_node.inputs[0])

        # Highlight the Movie Clip node for immediate file selection
        for n in nodes: n.select = False
        movie_node.select = True
        nodes.active = movie_node

        return {'FINISHED'}

# --- KEYMAP REGISTRATION ---

addon_keymaps = []

def register():
    bpy.utils.register_class(NODE_OT_AdoCompWrangler)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        # Shortcut: Ctrl + M
        kmi = km.keymap_items.new(NODE_OT_AdoCompWrangler.bl_idname, 'M', 'PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(NODE_OT_AdoCompWrangler)