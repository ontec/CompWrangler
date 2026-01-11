# Comp Wrangler Pro 🎬

**Comp Wrangler Pro** is a comprehensive Blender add-on designed to bridge the gap between Blender and professional compositing software like Nuke, After Effects, and Fusion.

It automates two critical stages of the VFX workflow: **Rapid Previz Setup** and **Pipeline-Ready EXR Export**.

![Comp Wrangler Demo](demo_image_placeholder.gif) 
*(Replace this with a screenshot of the N-Panel)*

## 🚀 Features

### 1. Smart Background Setup (Previz)
Stop manually connecting nodes!
* **⚡ One-Click Setup:** Creates a complete node chain with **Ctrl + M**.
* **🎥 Smart Camera Link:** Automatically detects if the active camera has a Background Image (Movie Clip) and loads it into the Compositor instantly. No need to browse files again!
* **📐 Auto-Scaling:** Sets the scale to "Render Size" (Fit) to prevent distortion.
* **🔗 Auto-Wiring:** Connects Movie Clip -> Scale -> Alpha Over -> Composite & Viewer.

### 2. Pipeline Export (Final Output)
Prepare your renders for the big league (Nuke, Fusion, AE) with industry-standard conventions.
* **🚀 Multi-Layer Support:** Detects **all View Layers** in your scene and creates separate export nodes for each one automatically.
* **🏷️ Naming Conventions:** Renames Render Passes to match your target software's expected format:
    * **Blender Native:** Default names.
    * **3ds Max (V-Ray Style):** `ZDepth`, `DiffuseFilter`, `Reflection`, `CryptomatteObject`...
    * **Maya (Arnold Style):** `Z`, `diffuse_albedo`, `specular_direct`, `crypto_object`...
    * **Cinema 4D:** Octane/Standard naming.
* **🧠 Smart Depth Workflow:**
    * **Nuke / Fusion Mode:** Exports **RAW 32-bit Depth** (Metric) for correct ZDefocus/Deep usage.
    * **AE / Photoshop Mode:** Exports **Normalized + Denoised Depth** (0-1 Visual) for easy post-processing.
* **🆔 Cryptomatte Support:** Automatically reformats Cryptomatte layers to match the target software (Snake_case for Maya, CamelCase for Max) while preserving layer ranks (00, 01...).
* **🧹 Deep Clean:** Intelligently removes old nodes created by the add-on before building new ones. No more duplicate node spaghetti!

## 📦 Installation

1.  Download the latest `Comp_Wrangler_Pro.py` file.
2.  Open Blender and go to **Edit > Preferences > Add-ons**.
3.  Click **Install...** and select the downloaded file.
4.  Enable the checkbox next to **Compositing: Comp Wrangler Pro**.
5.  **Save Preferences**.

## 🎮 Usage

Open the **Compositor** workspace and press **`N`** to open the side panel. You will see the **Comp Wrangler** tab.

### 🎥 Setting up Background (Ctrl + M)
1.  Load a reference video into your Camera's "Background Images" setting (optional but recommended).
2.  Press **`Ctrl + M`** (or click **Setup BG** in the panel).
3.  The add-on will build the setup and auto-load the clip from the camera.

### 💾 Setting up Export (Ctrl + Shift + E)
1.  Go to the **Pipeline Export** section in the N-Panel.
2.  **Target Software:** Choose where you will composite (e.g., *Nuke* or *Maya/Arnold* naming).
3.  **Depth Workflow:**
    * Choose **Nuke** for RAW data.
    * Choose **AE** for visual/normalized data.
4.  Press **`Ctrl + Shift + E`**.
5.  The add-on will scan all View Layers and create a tidy `File Output` node tree with `OpenEXR Multilayer (32-bit)` settings.

## ⚙️ Compatibility

* **Blender Version:** 4.5+ (Stable/LTS recommended).
* **Fixes:** Addresses the `exr_codec` API change in newer Blender versions.
* **OS:** Windows, Mac, Linux.

## 👨‍💻 Author

**Onur ÜNLÜ**

---
*Streamline your pipeline today! If you find this tool useful, give it a star on GitHub! ⭐*
