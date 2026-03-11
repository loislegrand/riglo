import pymel.core as pm
import maya.cmds as cmds
import RigLo.components.shapes as shapes
import RigLo.basic as bs
import RigLo.components.nodes as nd
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

    topNodeName = cmds.listRelatives(objs[0], p=True)[0]
    names = topNodeName.split('_')
    name = ''
    for n in names[1:]:
        name += '_' + n 

    bs.jntOrient(lat='', jntList=objs)

    newChainIk = bs.duplicate(objList=objs)
    cmds.select(cl=True)
    bs.doRename(1, objs=newChainIk, prefix='JNT_Ik_',)
    newChainIk = bs.doRename(0, objs=newChainIk, search='1', replace='')
    newChainCtl = bs.controllers(jntList=objs, ctrlShape='stCircle', name='C_Fk_')
    
    bs.IkFkBlend(objs)

    #change rotate order to xzy ou xyz 
    IkCtl = bs.controllers(jntList=[newChainIk[2]], ctrlShape='cube',name='C_')
    print(IkCtl)

    #Create ctl for the Ik Handle, match wrist orient, parent it 
    ikH = cmds.ikHandle(sj=newChainIk[0], ee=newChainIk[2],sol='ikRPsolver' , n='IkH_')
    print(ikH[0])
    bs.parentCnst(IkCtl[0], childrens=[ikH[0]], off=False, matx=False)

    #On global locator, addAttr length Up & Low limb : mult dL into the translate
    distNode = cmds.createNode('distanceBetween', n='dist_'+name)
    cmds.connectAttr(newChainIk[0] + '.worldMatrix', distNode + '.inMatrix1')
    cmds.connectAttr(IkCtl[0] + '.worldMatrix', distNode + '.inMatrix2')

    distRatio = cmds.createNode('divide', n='div_' + name)
    cmds.setAttr(distRatio+'.input1', cmds.getAttr(distNode +'.distance'))
    
    distMult = nd.multDL(name) #needs to be connected to the global scale parameter
    cmds.setAttr(distMult+'.input1',1)

    cmds.connectAttr(distNode + '.distance', distRatio+'.input2')
    cmds.connectAttr(distRatio + '.output', distMult+'.input2')

    """midMult = nd.multDL('mid'+name)
    cmds.setAttr(midMult+'.input1',cmds.getAttr(objs[1]+'.translateX'))
    cmds.connectAttr(distMult+'.output', midMult+'.input2')
    cmds.connectAttr(midMult+'.output', newChainIk[1]+'.translateX')

    lowMult = nd.multDL('low'+name)
    cmds.setAttr(lowMult+'.input1',cmds.getAttr(objs[2]+'.translateX'))
    cmds.connectAttr(distMult+'.output', lowMult+'.input2')
    cmds.connectAttr(midMult+'.output', newChainIk[2]+'.translateX')
"""

    #On global locator, addAttr thickness Up & Low limb : mult dL into the scale Y & Z
    #create the ribbon btw articulation : create line btw 2 points, match pivot with 1rst object and move a bit forward 
    #merge elbow controller with a roundness parameter : blend rotation of te two ribbons ends, and had pin parameter
    #if GDs Biped leg =>  ajouter les param de inverse foot