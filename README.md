## QuickTree

a Blender plug-in to quickly create random trees, without sacrificing optional fine-tuning abilities. The trees (or bushwork or plants), including animation, can be exported as Panda3D EGG files fit for tobspr's RenderPipeline.

### Installation

`git clone https://github.com/wolfgangp/quicktree.git ~/.config/blender/2.78/scripts/addons/quicktree`

### Prerequisites

the following are all Blender add-ons and can be installed just like quicktree.

- YABEE****

	`git clone https://github.com/09th/YABEE.git`

- Panda3D Bam Exporter

	`git clone --recursive https://github.com/tobspr/Panda3D-Bam-Exporter.git`

#####Optional

- [RenderPipeline](https://github.com/tobspr/RenderPipeline/wiki/Getting%20Started) by tobspr
	after installation you can run `RP_main_dir/toolkit/render_service/service.py` 

- Sapling 3 (included in Blender 2.78+)

	`git clone https://github.com/abpy/improved-sapling-tree-generator.git`
	
### Usage

1. Enable the Blender plug-in **Sapling Tree Gen**
	Start Blender, press `Ctrl+Alt+U` to open the User Preferences and enter `Sapling`in the search box in the top-left corner. Tick the box next to *Add Curve: Sapling Tree Gen* and click *Save User Settings* in the bottom-left corner.

2. Create a **Sapling Tree**
	Press `Shift+A`, select *Curve* -> *Sapling Tree Gen*

3. Enter the **QuickTree** menu
	While in *Object Mode* press `T` to show the Toolbox. Click on the bottom-most tab called *Misc*.
	
4. Click any of the **randomization** buttons to randomize values in the *Sapling: Add Tree* menu you should see below. Click *View for export* to view the leaves and be able to skip through the animation in the *Timeline*. 

5. Select **texture files** for *Bark Basecolor*, *Bark Normal* and *Leaf Basecolor*.

	Bark Basecolor texture example
	![Bark Basecolor example](https://dl.dropbox.com/u/20090886/bark1.tga)
	
	Bark Normal texture example
	![Bark Normal example](http://dl.dropbox.com/u/20090886/bark1_nmp.tga)

	Leaf Basecolor texture example: it's important the stem of the leaf is in the bottom middle
	![Leaf Basecolor example](http://dl.dropbox.com/u/20090886/ferny_spring1.png) 

6. Export after selecting **EGG file**. Afterwards you may press `F12` to get a preview render.