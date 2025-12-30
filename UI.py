import maya.cmds as cmds
import maya.mel as mel
import os
import RigLo.FbxExport as FbEx
import RigLo.builderDialog as Bd
from importlib import reload

reload(Bd)

def InfoUI():
    version = "2025-12-03"

    # Delete window if it already exists
    if cmds.window("InfoUI", exists=True):
        cmds.deleteUI("InfoUI")

    # Create window
    window = cmds.window("InfoUI", 
                         title="About this tool", 
                         widthHeight=(350, 200), 
                         sizeable=False, 
                         menuBar=True)

    cmds.columnLayout(columnAttach=("both", 20), rowSpacing=5)

    cmds.separator(height=10,vis=False)
    
    cmds.text(label="Dev of a basic autorig.",
              align="left", width=310, wordWrap=True, height=20)
    cmds.text(label="Ain't perfect but should work out well. DM if any problem",
              align="left", width=310, wordWrap=True, height=20)
    cmds.separator(height=20)

    cmds.text(label=f"Python script by Loïs Legrand //  v.{version}         lois.legrand38@gmail.com",
              align="right", width=310, wordWrap=True, height=40)

    cmds.separator(height=20,vis=False)

    cmds.setParent("..")
    cmds.showWindow(window)
    

def create_ui():
    windowFbx = "RigLoWindow"
    if cmds.window(windowFbx, exists=True):
        cmds.deleteUI(windowFbx)
    cmds.window(windowFbx, t="RigLo Builder",menuBar=True, wh=(500,250),s=1)
    
    # Create Help Menu
    cmds.menu(label="  Help  ", tearOff=False)
    cmds.menuItem(label="Reset", command=lambda *args: create_ui())
    cmds.menuItem(label="About", command=lambda *args: InfoUI())
    
    cmds.columnLayout(columnAttach=('both', 10), rowSpacing=5, columnWidth=250, adjustableColumn=True)
    cmds.text(label='  ',al='center')
    cmds.text(label='Create Guides, then hit "Build" to create the setup',al='left', ann="Si ça marche pas, mets moi un message")
    cmds.text(label='  ',al='center')

    cmds.checkBox('MtxCns', label='Matrix Constraint', ann='Create Matrix constraint instead of Maya nativ constraint system', value=False)


    cmds.separator(h=2)
    cmds.frameLayout("Components", cll=True, cl=False, mw=10, mh=10)
    cmds.rowColumnLayout(nc=1, rs=[(1,10)], bgc=(.2,.2,.2))

    Bd.subMenu(name='Limb', color=(0.5,0.3,0.3))
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    Bd.subMenu(name='Spine', color=(0.3,0.5,0.3))
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    Bd.subMenu(name='Tentacle', color=(0.3,0.3,0.5))
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    Bd.subMenu(name='Facial', color=(0.3,0.3,0.5))
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.setParent("..")
    cmds.setParent("..")

    cmds.separator( h=5)
    
    cmds.text( label='Name' )
    tName = cmds.textField('textBoxName', tx='toto', cc=FbEx.changeTextField)
    cmds.text( label="Path Direction" )
    tb = cmds.textField('textBoxPath', tx='', en=False)
    
    cmds.separator( h=5)
    cmds.button(label='Reorient', c=FbEx.transCrv, backgroundColor=(0.2, 0.4, 0.2) ,al='center', ann='Replace le squelette de Flow Studio au centre du monde avec la cam')
    cmds.button(label='Build', c=FbEx.exportFbx, backgroundColor=(0.2, 0.3, 0.2) ,al='center', ann='Exporte les bones et la caméra dans 2 fichiers séparés dans le dossier défini plus haut. ')
    cmds.setParent("..")
    
    cmds.showWindow(windowFbx)

    print(windowFbx)