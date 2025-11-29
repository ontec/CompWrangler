# Comp Wrangler 🎬

**Comp Wrangler** is a lightweight Blender add-on designed to streamline the VFX and Compositing workflow. It automates the tedious process of setting up background plates/videos in the Compositor with a single shortcut.

Stop manually connecting nodes every time you need a background reference!



## 🚀 Features

* **⚡ Instant Setup:** Creates a complete node chain with one hotkey (**Ctrl + M**).
* **📐 Smart Scaling:** Automatically adds a `Scale` node and sets it to **"Render Size"** (Fit) so your footage never looks distorted.
* **🔗 Auto-Wiring:**
    * Connects the Movie Clip to the Background.
    * Finds existing `Render Layers` and connects them to the Foreground.
    * Connects the output to **both** the `Composite` (F12 Render) and `Viewer` (Preview) nodes.
* **🛠️ Context Aware:** If Render Layers, Composite, or Viewer nodes are missing, Comp Wrangler creates them for you automatically.

## 📦 Installation

1.  Download the latest release zip (or the `.py` file).
2.  Open Blender and go to **Edit > Preferences > Add-ons**.
3.  Click **Install...** and select the downloaded file.
4.  Enable the checkbox next to **Compositing: Comp Wrangler**.
5.  Make sure to **Save Preferences**.

## 🎮 Usage

1.  Go to the **Compositing** workspace.
2.  Ensure "Use Nodes" is enabled (the add-on will enable it for you if it's off).
3.  Press **`Ctrl + M`**.
4.  The node setup will appear instantly.
5.  Click the **Open** button on the newly created `Movie Clip` node to load your footage.

## ⚙️ Compatibility

* **Blender Version:** 4.0 and above.
* **OS:** Windows, Mac, Linux.

## 👨‍💻 Author

**Onur ÜNLÜ**

---
*Enjoy faster compositing! If you find this tool useful, give it a star on GitHub! ⭐*
