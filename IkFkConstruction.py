import pymel.core as pm
import maya.cmds as cmds
import RigLo.components.shapes as shapes
import RigLo.basic as bs
from importlib import reload

reload(bs)

"""
verify the orientation 
duplicate joint chain, if not existing, and an Fk controller chain
rename the duplicated joint chain
create the IkFk blend setup 
add the stretch setup : calculate the length divided length base, mulitiplied by all the scale parameter
add a per limbPart length parameter
add a volume parameter

"""

def createIkRpChain(objs = []):

    if len(objs) == 0:
        objs = cmds.ls(selection=True)
    
    bs.jntOrient(lat='', jntList=objs)

    newChainIk = bs.duplicate(objList=objs)
    cmds.select(cl=True)
    bs.doRename(1, objs=newChainIk, prefix='JNT_Ik_',)
    newChainIk = bs.doRename(0, objs=newChainIk, search='1', replace='')
    newChainCtl = bs.controllers(jntList=objs, ctrlShape='stCircle', name='C_Fk_')
    
    bs.IkFkBlend(objs)

    #change rotate order to xzy ou xyz 
    bs.controllers(jntList=[newChainIk[2]], ctrlShape='cube',sol='ikRPsolver' ,name='C_')

    #Create ctl for the Ik Handle, match wrist orient, parent it 
    cmds.ikHandle(sj=newChainIk[0], ee=newChainIk[2],sol='ikRPsolver' , n='IkH_')
    
    #On global locator, addAttr length Up & Low limb : mult dL into the translate
    #On global locator, addAttr thickness Up & Low limb : mult dL into the scale Y & Z
    #create the ribbon btw articulation : create line btw 2 points, match pivot with 1rst object and move a bit forward 
    #merge elbow controller with a roundness parameter : blend rotation of te two ribbons ends, and had pin parameter
    #if GDs Biped leg =>  ajouter les param de inverse foot

    