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
    
    ctlAttr = bs.IkFkBlend(objs)

    #change rotate order to xzy ou xyz 
    IkCtl = bs.controllers(jntList=[newChainIk[2]], ctrlShape='cube',name='C_')
    print(IkCtl)

    switchCtl = bs.controllers(jntList='', ctrlShape='cross', name='IkSwitch_')

    #Create ctl for the Ik Handle, match wrist orient, parent it 
    ikH = cmds.ikHandle(sj=newChainIk[0], ee=newChainIk[2],sol='ikRPsolver' , n='IkH_')
    print(ikH[0])
    bs.parentCnst(IkCtl[0], childrens=[ikH[0]], off=False, matx=False)

    #On global locator, addAttr length Up & Low limb : mult dL into the translate
    cmds.addAttr(ctlAttr, at="float", longName="stretch", min=0, max = 1, dv=1, keyable=1)
    cmds.addAttr(ctlAttr, at="float", longName="upLimbLength", min=0.05, dv=1, keyable=1)
    cmds.addAttr(ctlAttr, at="float", longName="lowLimbLength", min=0.05, dv=1, keyable=1)
    cmds.addAttr(ctlAttr, at="float", longName="maxStretch", min=0.05, dv=10, keyable=1)
    cmds.addAttr(ctlAttr, at="float",nn="Scale", longName="scaleGlobale", min=0.05, dv=1, keyable=1)

    distNode = cmds.createNode('distanceBetween', n='dist_'+name)
    cmds.connectAttr(ctlAttr[0] + '.worldMatrix', distNode + '.inMatrix1')
    cmds.connectAttr(IkCtl[0] + '.worldMatrix', distNode + '.inMatrix2')

    distRatio = cmds.createNode('divide', n='div_' + name)
    
    distMult = nd.multDL(name) #needs to be connected to the global scale parameter
    cmds.setAttr(distMult+'.input1',1)
    cmds.setAttr(distMult+'.input2', cmds.getAttr(distNode +'.distance'))

    lerpStretch = cmds.createNode('lerp', n='lerp'+name)
    cmds.connectAttr(distRatio + '.output', lerpStretch + '.input2')
    cmds.setAttr(lerpStretch + '.input1', 1)

    clampRatio = cmds.createNode('clampRange', n='clamp'+name)
    cmds.connectAttr(distNode + '.distance', distRatio+'.input1')
    cmds.connectAttr(lerpStretch + '.output', clampRatio+'.input')
    cmds.connectAttr(distMult + '.output', distRatio+'.input2')
    cmds.setAttr(clampRatio+'.minimum', 1)
    cmds.setAttr(clampRatio+'.maximum', 10)
    
    globalStretch = nd.multDL('gbl'+name)
    cmds.connectAttr(clampRatio + '.output', globalStretch + '.input2')
    cmds.setAttr(globalStretch + '.input1', 1)
    
    upUntC = cmds.createNode('unitConversion', n='upUntC'+name)
    lowUntC = cmds.createNode('unitConversion', n='lowUntC'+name)
    cmds.setAttr(upUntC+'.conversionFactor',cmds.getAttr(objs[1]+'.translateX'))
    cmds.setAttr(lowUntC+'.conversionFactor',cmds.getAttr(objs[2]+'.translateX'))

    midMult = nd.multDL('mid'+name)
    cmds.connectAttr(midMult+'.output', upUntC+'.input')
    cmds.connectAttr(globalStretch+'.output', midMult+'.input1')
    cmds.connectAttr(upUntC+'.output', newChainIk[1]+'.translateX')

    lowMult = nd.multDL('low'+name)
    cmds.connectAttr(lowMult+'.output',lowUntC+'.input')
    cmds.connectAttr(globalStretch+'.output', lowMult+'.input1')
    cmds.connectAttr(lowUntC+'.output', newChainIk[2]+'.translateX')

    #connect the parameter from the Global ctl to the nodes
    cmds.connectAttr(ctlAttr[0]+'.maxStretch', clampRatio+'.maximum')
    cmds.connectAttr(ctlAttr[0]+'.stretch', lerpStretch + '.weight')
    cmds.connectAttr(ctlAttr[0]+'.scaleGlobale', globalStretch + '.input1')
    cmds.connectAttr(ctlAttr[0]+'.upLimbLength', midMult+'.input2')
    cmds.connectAttr(ctlAttr[0]+'.lowLimbLength', lowMult+'.input2')

    for l, n in bs.listExtraAttr(ctlAttr[0]).items():
        print(l, n)
        cmds.addAttr(switchCtl, ln = l, nn=n, proxy=ctlAttr[0] + '.' + l )

    crv1 = bs.lineBtw(objs[0], objs[1], selectable=True)
    crv2 = bs.lineBtw(objs[1], objs[2], selectable=True)

    cmds.delete(cmds.listConnections(cmds.listRelatives(crv1, s=True)[1]), cmds.listConnections(cmds.listRelatives(crv2, s=True)[1]))

    """
    cmds.delete(cmds.listConnections(cmds.listRelatives(crv2, s=True)))"""

    #create the ribbon btw articulation : create line btw 2 points, match pivot with 1rst object and move a bit forward 
    #merge elbow controller with a roundness parameter : blend rotation of te two ribbons ends, and had pin parameter
    #if GDs Biped leg =>  ajouter les param de inverse foot