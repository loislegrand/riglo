import maya.cmds as cmds
import maya.mel as mel
import os
from importlib import reload
import RigLo.components.arm as arm

reload(arm)

def subMenu(name='Component', color=(0.7,0.7,0.7), dependencies=''):
    '''
    :param name : the name of the layout
    :param color : RGB color of the menu
    :param parent : parent of the layout

    Docstring for SubMenu
    '''
    cmds.frameLayout(name, cll=True, cl=True, bgc=(color), w=500, mw=10, p=dependencies)
    cmds.columnLayout(adjustableColumn=True)
    
    if name == 'Limb':
        LimbType = cmds.optionMenu(name + 'LimbMenu', label='Limb :')
        ItemList = ['Arm', 'Biped Leg', 'Quadruped Leg']

        for item in ItemList:
            it = 0
            cmds.menuItem('Limb'+ item, label=item)
        
    if not name == 'Spine':
        Centralisation = cmds.optionMenu(name + 'Side_02', label='Side :')
        cmds.menuItem(label='Front')
        cmds.menuItem(label='Center')
        cmds.menuItem(label='Rear')

        Lateralisation = cmds.optionMenu(name + 'Side_01', label='Position :')
        cmds.menuItem(label='Left')
        cmds.menuItem(label='Center')
        cmds.menuItem(label='Right')

    #print(name)

    '''
    For tentacle
    Number of joint
    Number controllers
    '''

    
    cmds.columnLayout(adjustableColumn=True)
    cmds.checkBox(name + 'TwistBox', label='Twisty', ann='Or Roll Joints', value=True)
    cmds.checkBox(name + 'StretchBox', label='Stretchy', ann='Strechy limb if checked', value=True)
    cmds.checkBox(name + 'BendBox', label='Bendies', ann='Add bendies if checked', value=False)

    cmds.text(label='  ',al='center')
    cmds.iconTextButton(label='Load Guides',style='iconAndTextVertical',fn='boldLabelFont', 
                        i1='locator.png', i2='fileNew.png',
                        al='center', ann='Create Guides with the wanted spec', bgc=(.4,.4,.4)
                        , c=lambda *args: arm.GuideLoader().loadGuidesArm()
                        )
    
    return name