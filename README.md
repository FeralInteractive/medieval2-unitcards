![270](https://user-images.githubusercontent.com/113598098/192815802-a79d8052-e824-45f6-a2e2-0e51764647d1.jpg)

# Medieval 2 Blender Portrait Scene 

## Introduction

This document reviews the blender file and accompanying Portrait Creator.py script provided to the modding community.
The intention of this process is to allow for the batch generation of unit cards for Total War: MEDIEVAL II.

![#peasant_crossbowmen](https://user-images.githubusercontent.com/113598098/192804638-93e18d75-fde9-4834-ab15-5fb5614bf07f.png) ![#chivalric_knights](https://user-images.githubusercontent.com/113598098/192813112-94f081e2-f04b-4e60-a553-5ec04190d5da.png) ![#arquebusiers](https://user-images.githubusercontent.com/113598098/192813903-c85a1715-6fce-433a-81fc-69ead077ce94.png) ![#dismounted_broken_lances](https://user-images.githubusercontent.com/113598098/192814103-0f67bfe8-cc14-4a42-9e04-8cf710c47948.png)![#coyote_priests](https://user-images.githubusercontent.com/113598098/192814945-d244ab9c-357a-450d-9bb4-008853476930.png) ![#dismounted_latinkon](https://user-images.githubusercontent.com/113598098/192815404-a0ebe441-984a-4b7b-b9ab-3097916af541.png)











NOTE: This is not a tutorial, simply just instructions and tips to render out a batch of images used for portraits.

## Provided Files

You can find the project root folder here:

* M2_Portrait_Creator_scene.blend
   * This is a base blender scene that can be used to create and render unit cards.
   * This scene was created using Blender version 2.93.0. The scene has been used in Blender versions 2.93.0, 3.0.0, 3.3.0.


* Portrait_creator.py
    * This is a python script Blender uses to produce portraits and save them to a specified directory.


* Inputfile.txt
    * Input text file utilised by the python script to generate unit cards with specified models, textures, poses and factions. Contains a single unit entry as an example. 



<img width="512" alt="Master_Directory" src="https://user-images.githubusercontent.com/113598098/192818635-eaf6e6ba-27fc-4c9d-b686-793790e3f473.PNG">



NOTE: Source assets have not been provided. However a folder structure has been provided for easy interaction with the portrait_creator.py script. The portrait_creator.py script expects a ‘.dae’ format for models and ‘.png’ format for texture files.


## Preparing Assets

When preparing models for use with the portrait creator ensure the assigned material for main character elements (body, arms, legs etc) is named ‘characterlod0__main’. Ensure the assigned material for attachment elements (swords, shields, sheaths etc) is ‘characterlod0__attach’.


<img width="327" alt="characterlod0_main" src="https://user-images.githubusercontent.com/113598098/192818994-d147dab5-2ae8-409d-b622-5b6686f1b8eb.PNG">   <img width="322" alt="characterlod0_attach" src="https://user-images.githubusercontent.com/113598098/192819035-357e77d8-0ea0-49ab-9a17-3dbba9b21393.PNG">



When exporting a .dae model file, ensure the file name includes ‘_lod0’ at the end of the model name. E.g. ‘en_peasant_crossbowmen_lod0.dae’





## How to create a portrait

### 1) Assignments in the Google Sheet

The sheet can be found here

This is the sheet that contains assignments for each portrait(models,textures, factions, poses etc). This information is copied to the inputfile.txt. See details below on how each column of the google sheet works.

![portrait_spreadsheet_doc_resize](https://user-images.githubusercontent.com/113598098/192820233-20631a64-db97-4dea-8348-42ec03a11436.png)


When looking to control the variation of a particular unit for a portrait, use the 'visible_models' section of the sheet. (scroll right on the 'main sheet')

![portrait_spreadsheet_visible_models](https://user-images.githubusercontent.com/113598098/192820896-894bbd8c-3fee-4774-9e79-5ba3af476802.png)

 When a unit's assignments are complete, copy the relevant rows into the inputfile.txt document.

### 2) Posing

Open the 'M2_Portrait_Creator_scene.blend'.

The posing/rendering tab is where unit poses are defined via the reference character. Scrubbing through the timeline represents all the existing poses. 

Here is a list of pose groups based on keyframe number:

-1 = T-Pose
0 = Standing base

1/199 = unit (alone)
200/299 = horse mounted unit
300/349 = elephant mounted unit
350/399 = camel mounted unit
400/449 = chariots & other animals (dogs, pig)
450/499 = /
500/599 = warmachines
600/699 = naval/boats
700/799 = agents

The groups are defined by change in position of the camera. For example the camera will be closer for a single human unit portrait than for an elephant mounted unit portrait.


Weapon references can be enabled in the outliner.


A reference image can be added to the camera. 


Additional assets (animals,siege engines) can be found in the outliner. Ensure visibility for animals is enabled but the Additional assets group visibility is disabled prior to running the script tool. 


Enter pose mode and manipulate the joints to create a new pose. Auto key is on by default. Note manipulating the joints on a frame which already has a pose will overwrite the existing pose! Recommended behaviour - Select an empty frame within one of the ranges listed above (dependent on type of unit) or select a frame outside the range (799+).

The camera's position can also be changed via keyframe animation. Beware manipulating the camera position in any of the ranges listed above as these are positioned specifically for the relevant unit types.


### 3) Running the script tool

Navigate to the Run Tool (scripting) tab.

Select ‘Open’ at the top of the screen and open the ‘portrait_creator.py’.

By default the tool will read ‘inputfile.txt’ for the input file, draw 'unit data' from the 'source assets' folder and its relevant subdirectories. The ‘output_directory’ folder is set as the path for the image render output. These paths can be changed if desired. See image below for details. The script includes comments explaining the process if you require more information.

Before running the script it is recommended you navigate to 'Window' and 'Toggle System Console'. This allows visibility of the scripts progress as well as highlighting any errors.

When running the script if you encounter an error, before restarting the script navigate to the posing/rendering tab. Notice a character model is present below the camera. Under the ‘Characters’ collection - delete the models and armature. Now restart the script.


### 4) Updating in game portraits

Convert the output .png files to .tga. (Recommend using [Magick plugin](https://imagemagick.org/script/download.php))

Simply update the file in game (if replacing an existing asset) or add the file to the relevant directory (if producing for a mod).

**Portrait game directories**
  * Game Directories
    * **BASE** - `...\data\ui\units`
    * **Americas** - `...\mods\americas\data\ui\units`
    * **Britannia** - `...\mods\british_isles\data\ui\units`
    * **Crusades** - `...\mods\crusades\data\ui\units`
    * **Teutonic** - `...\mods\teutonic\data\ui\units`

  







