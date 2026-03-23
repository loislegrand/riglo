import pymel.core as pm
import maya.cmds as cmds
import RigLo.components.shapes as shapes
import RigLo.basic as bs
import RigLo.components.nodes as nd
import RigLo.utils.ribbonSurf as rib
from importlib import reload
from RigLo.baseHierarchy import hierarchy

reload(bs)
reload(rib)

"""
verify the orientation 
duplicate joint chain, if not existing, and an Fk controller chain
rename the duplicated joint chain
create the IkFk blend setup 
add the stretch setup : calculate the length divided length base, mulitiplied by all the scale parameter
add a per limbPart length parameter
add a volume parameter

"""
def LimbDetection():

    # Sur le squelette, lire les labels
    childList = cmds.listRelatives("SKINNING", allDescendents=1, type="joint")
    for child in childList :
        labelTypeStart = cmds.getAttr(child+".otherType")
        
        space = ""
        
        if (cmds.getAttr(child+".side")) == 1 :
            space = "left"
                        
        elif (cmds.getAttr(child+".side")) == 2 :
            space = "right"
        
        elif cmds.getAttr(child+'.side') == 0:
            space = "center"
            
        else:
            space = "none"
    
        # Si un label "arm" est trouvé (...)
        if labelTypeStart == "arm":
            armBase = child
            print("---> Arm joint found : "+armBase+" <---")
            
            # (...) Chercher le label "hand" associé
            grandChildList = cmds.listRelatives(armBase, allDescendents=1, type="joint")
            for grandChild in grandChildList :
                if (cmds.getAttr(grandChild+".otherType")) == "hand":
                    handBase = grandChild                
                    print("---> Hand joint found for "+armBase+" : "+handBase+" <---")
                    
                    forearmBase = cmds.listRelatives(handBase, parent=1)
                    print("---> Forearm joint found for "+armBase+" : "+forearmBase[0]+" <---")


def createIkRpChain(biLeg, objs = []):
    if len(objs) == 0:
        objs = cmds.ls(selection=True)

    """#if there is a base hierarchy no ned to create a new one
    if not cmds.objExists('SKINNING'):
        hierarchy('NEWNAME')"""

    #_____ DETECTION PART _____
    

    print(objs)
    print(cmds.getAttr(cmds.listRelatives(objs[-1], c=True, typ='joint')[0]+'.otherType'))
    
    #_____ BUILD PART _____
    
    topNodeName = cmds.listRelatives(objs[0], p=True)[0]
    names = topNodeName.split('_')
    name = ''
    for n in names[1:]:
        name += '_' + n 

    bs.cJO_orientSel('X', 'Y', True, False, doAuto=False)
    objs = bs.doRename(0, objs=objs, search='GD_', replace='')

    newChainIk = bs.duplicate(objList=objs)
    cmds.select(cl=True)
    bs.doRename(1, objs=newChainIk, prefix='JNT_Ik_',)
    newChainIk = bs.doRename(0, objs=newChainIk, search='1', replace='')
    newChainCtl = bs.controllers(jntList=objs, ctrlShape='stCircle', name='C_Fk_')
    cmds.parent(cmds.listRelatives(newChainCtl[1], p=True)[0], newChainCtl[0] )
    cmds.parent(cmds.listRelatives(newChainCtl[2], p=True)[0], newChainCtl[1] )
    
    ctlAttr = bs.IkFkBlend(objs)

    topCtl = bs.controllers(jntList = [objs[0]] ,ctrlShape='crossArrow', name='C_top_')[0]
    bs.doRename(0, objs=[cmds.listRelatives(topCtl, p=True)[0]], search='GRP_', replace='GRP_up_')[0]

    #change rotate order to xzy ou xyz 
    IkCtl = bs.controllers(jntList=[newChainIk[2]], ctrlShape='cube',name='C_')

    switchCtl = bs.controllers(jntList='', ctrlShape='cross', name='IkSwitch_')
    cmds.move(0, 0, -5, cmds.listRelatives(switchCtl, p=True)[0], r=True, ls=True, wd=True)


    #Create ctl for the Ik Handle, match wrist orient, parent it 
    ikH = cmds.ikHandle(sj=newChainIk[0], ee=newChainIk[2],sol='ikRPsolver' , n='IkH'+name)
    PV = bs.controllers(jntList = ['PV_Previz'+name] ,ctrlShape='diamond', name='C_PV_')[0]
    PV = bs.doRename(0, objs=[PV, cmds.listRelatives(PV, p=True)[0]], search='Previz_', replace='')[0]
    cmds.matchTransform(PV, objs[1], rot=True)
    cmds.poleVectorConstraint(PV, ikH[0])
    linePV = bs.lineBtw(PV, objs[1])

    bs.parentCnst([IkCtl[0]], ikH[0], off=False, matx=False)

    #On global locator, addAttr length Up & Low limb : mult dL into the translate
    cmds.addAttr(ctlAttr[0], at="float", longName="stretch", min=0, max = 1, dv=1, keyable=1)
    cmds.addAttr(ctlAttr[0], at="float", longName="upLimbLength", min=0.05, dv=1, keyable=1)
    cmds.addAttr(ctlAttr[0], at="float", longName="lowLimbLength", min=0.05, dv=1, keyable=1)
    cmds.addAttr(ctlAttr[0], at="float", longName="maxStretch", min=0.05, dv=10, keyable=1)
    cmds.addAttr(ctlAttr[0], at="float",nn="Scale", longName="scaleGlobale", min=0.05, dv=1, keyable=1)
    cmds.addAttr(ctlAttr[0], at="float", longName="bendies", min=0, max=1, dv=0, keyable=1)
    cmds.addAttr(ctlAttr[0], at="float", longName="subBendies", min=0, max=1, dv=0, keyable=1)

    distNode = cmds.createNode('distanceBetween', n='dist_'+name)
    cmds.connectAttr(ctlAttr[0] + '.worldMatrix', distNode + '.inMatrix1')
    cmds.connectAttr(IkCtl[0] + '.worldMatrix', distNode + '.inMatrix2')

    distRatio = cmds.createNode('divide', n='div_' + name)
    
    distMult = nd.multDL(name) #needs to be connected to the global scale parameter
    cmds.setAttr(distMult+'.input1',1)
    cmds.setAttr(distMult+'.input2', cmds.getAttr(objs[1] +'.translateX')+cmds.getAttr(objs[2] +'.translateX'))

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

    if biLeg:

        cmds.addAttr(IkCtl[0], ln="InverseFoot", nn="_____", at="enum", en="_____", k=True)
        cmds.addAttr(IkCtl[0], ln='FootBank',at='float',dv=0,k=True)
        cmds.addAttr(IkCtl[0], ln='FootRoll',at='float',dv=0,k=True)
        cmds.addAttr(IkCtl[0], ln='BallTwist',at='float',dv=0,k=True)
        cmds.addAttr(IkCtl[0], ln='FootTwist',at='float',dv=0,k=True)
        cmds.addAttr(IkCtl[0], ln='ToeRoll',at='float',dv=0,k=True)
        cmds.addAttr(IkCtl[0], ln='ToeTwist',at='float',dv=0,k=True)
        
        #connect attr
        """cmds.connectAttr(ctrl+'.FootBank','RF_int'+'_'+side+'.rotateZ')
        cmds.connectAttr(ctrl+'.FootBank','RF_ext'+'_'+side+'.rotateZ')
        cmds.connectAttr(ctrl+'.FootRoll','RF_heel'+'_'+side+'.rotateX')
        cmds.connectAttr(ctrl+'.FootRoll','RF_toes'+'_'+side+'.rotateX')
        cmds.connectAttr(ctrl+'.ToeRoll','RF_toesEnd'+'_'+side+'.rotateX')
        cmds.connectAttr(ctrl+'.ToeTwist','RF_toesEnd'+'_'+side+'.rotateY')
        cmds.connectAttr(ctrl+'.FootTwist','RF_toes'+'_'+side+'.rotateY')
        cmds.connectAttr(ctrl+'.BallTwist','RF_heel'+'_'+side+'.rotateY')"""

    for l, n in bs.listExtraAttr(ctlAttr[0]).items():
        print(l, n)
        cmds.addAttr(switchCtl, ln = l, nn=n, proxy=ctlAttr[0] + '.' + l )


    #create the ribbon btw articulation : create line btw 2 points, match pivot with 1rst object and move a bit forward 

    crv1tmp = bs.lineBtw(objs[0], objs[1], selectable=True)
    crv2tmp = bs.lineBtw(objs[1], objs[2], selectable=True)

    crvUp1 = cmds.duplicate(crv1tmp, n='CRV_up1'+name)[0]
    crvUp2 = cmds.duplicate(crv1tmp, n='CRV_up2'+name)[0]
    crvDwn1 = cmds.duplicate(crv2tmp, n='CRV_low1'+name)[0]
    crvDwn2 = cmds.duplicate(crv2tmp, n='CRV_low2'+name)[0]
    ribbonCrvTmp = [crvUp1, crvUp2, crvDwn1, crvDwn2]

    cmds.delete(crv1tmp, crv2tmp)

    for crv in ribbonCrvTmp:
        cmds.parent(crv, objs[0])
        cmds.xform(crv, cpc=True) 
        cmds.move(0, 1, 0, r=True, ls=True, wd=True)

    cmds.select(crvUp2, crvDwn2)
    cmds.move(0, -2, 0, r=True, ls=True, wd=True)

    cmds.parent(ribbonCrvTmp, w=True)


    ribUp = rib.createRibbon(crvUp1, crvUp2, name='ribUp'+name, jntNum=4, ctlNum=2)
    ribDwn = rib.createRibbon(crvDwn1, crvDwn2, name='ribDwn'+name, jntNum=4, ctlNum=2)
    cmds.parent(ribUp[0][0], objs[0])
    cmds.parent(ribDwn[0][0], objs[1])

    #aimConstraint to the end ribCtl
    cmds.pointConstraint(ribUp[1][-1], ribUp[1][-3], cmds.listRelatives(ribUp[1][-2], p=True)[0])
    cmds.pointConstraint(ribDwn[1][-1], ribDwn[1][-3], cmds.listRelatives(ribDwn[1][-2], p=True)[0])
    cmds.aimConstraint(ribUp[1][-1], cmds.listRelatives(ribUp[1][-2], p=True)[0], mo=False, aim=(0,0,1), u= (1,0,0), worldUpType="objectrotation",  worldUpVector= (1, 0, 0), worldUpObject= ribUp[1][-1])
    cmds.aimConstraint(ribDwn[1][-1], cmds.listRelatives(ribDwn[1][-2], p=True)[0], mo=False, aim=(0,0,1), u= (1,0,0), worldUpType="objectrotation",  worldUpVector= (1, 0, 0), worldUpObject= ribDwn[1][-1])

    midCtl = bs.controllers(jntList = [objs[1]] ,ctrlShape='crossArrow', name='C_mid_')[0]
    bs.doRename(0, objs=['|'+cmds.listRelatives(midCtl, p=True)[0]], search='GRP_', replace='GRP_mid_')[0]

    pvPtCstrnt = bs.parentCnst([objs[1], PV], cmds.listRelatives(midCtl, p=True)[0])
    cmds.addAttr(midCtl, ln='pvPin', k=True, min=0, max=1)
    if cmds.objectType(pvPtCstrnt) == 'parentConstraint':
        cmds.connectAttr(midCtl +'.pvPin', ctlAttr[1] + '.inputY')
        cmds.connectAttr(ctlAttr[1] + '.outputY', pvPtCstrnt+'.'+objs[1]+"W0")
        cmds.connectAttr(midCtl+".pvPin", pvPtCstrnt+'.'+PV+"W1")
    else:
        cmds.error('Stop being lazy et make the matrix version, 1 day top')

    
    bs.parentCnst([objs[0]], cmds.listRelatives(ribUp[1][-3], p=True)[0],off=True)
    bs.parentCnst([topCtl], ctlAttr[0],off=True)
    bs.parentCnst([midCtl], cmds.listRelatives(ribUp[1][-1], p=True)[0],off=True)
    bs.parentCnst([midCtl], cmds.listRelatives(ribDwn[1][-3], p=True)[0],off=True)
    bs.parentCnst([objs[2]], cmds.listRelatives(ribDwn[1][-1], p=True)[0],off=True)

    subBendies = cmds.listRelatives(ribUp[0][-1], p=True)[0], cmds.listRelatives(ribDwn[0][-1], p=True)[0]
    bendies = cmds.listRelatives(cmds.listRelatives(ribUp[1][-1], p=True)[0], p=True)[0], cmds.listRelatives(cmds.listRelatives(ribDwn[1][-1], p=True)[0], p=True)[0]

    for i in subBendies:
        cmds.connectAttr(ctlAttr[0]+'.subBendies', i + '.visibility')
    for i in bendies:
        cmds.connectAttr(ctlAttr[0]+'.bendies', i + '.visibility')

    bs.parentCnst([objs[2]], switchCtl[0], off=True, matx=True)

    #if GDs Biped leg =>  ajouter les param de inverse foot
    

    #_____ TIDY UP PART _____
    oldGD = cmds.listRelatives(objs[0], p=True)
    cmds.parent(objs[0], 'SKINNING')
    groupIkRig = cmds.group(ribUp[1][:3], ribDwn[1][:3], ctlAttr[0], ikH[0], n='GRP_IkRig'+name)
    cmds.parent(groupIkRig, 'RIGGING')
    cmds.parent(cmds.ls('SURF_*', typ='transform'), linePV, 'NO_TRANSFORM')
    groupIkCtl = cmds.group(cmds.listRelatives(ribUp[0][-1], p=True), cmds.listRelatives(ribDwn[0][-1], p=True),
                         cmds.listRelatives(cmds.listRelatives(ribUp[1][-1], p=True)[0], p=True)[0],
                         cmds.listRelatives(cmds.listRelatives(ribDwn[1][-1], p=True)[0], p=True)[0],
                         cmds.listRelatives(IkCtl, p=True), cmds.listRelatives(PV, p=True),
                         cmds.listRelatives(midCtl, p=True), cmds.listRelatives(topCtl, p=True),
                          n='GRP_IkCtl'+name)
    cmds.parent(cmds.listRelatives(switchCtl, p=True), cmds.listRelatives(newChainCtl[0], p=True), groupIkCtl, 'CONTROLERS')

    cmds.delete('*Previz'+name)
    cmds.delete(oldGD)

    #FkCtl into the group 


    #_____ RENAMING PART _____

def biRevFoot(ctrl, endJoint):
    if cmds.getAttr(cmds.listRelatives(ctrl, p=True)+".otherType") == 'toes':
        toes = cmds.listRelatives(ctrl, p=True)[0]
    childList = cmds.listRelatives(endJoint, allDescendents=1, type="joint")
    for child in childList :
        labelType = cmds.getAttr(child+".otherType")
        if labelType == 'int':
            int = child
        elif labelType == 'out':
            ext = child
        elif labelType == 'heel':
            heel = child

    cmds.setAttr(int+'.drawStyle', 2)
    cmds.setAttr(ext+'.drawStyle', 2)
    cmds.setAttr(heel+'.drawStyle', 2)

    IkSC1 = cmds.ikHandle(sj=toes,ee=cmds.lsitRelatives(toes, p=True),sol='ikSCsolver', n='IkSC_toes_'+side)
    IkScHandle1 = IkSC1[0]
    
    IkSC2 = cmds.ikHandle(sj=legJoint[3],ee=legJoint[4],sol='ikSCsolver', n='IkSC_toesEnd_'+side)
    IkScHandle2 = IkSC2[0]
    
    cmds.parent(IkHandle,'RF_foot'+'_'+side)
    cmds.parent(IkScHandle1,'RF_toes'+'_'+side)
    cmds.parent(IkScHandle2,'RF_toesEnd'+'_'+side)
    
    
    #create attr
    cmds.addAttr(ctrl, min=0, max=1, ln='IKFK',at='float',dv=1.0,k=True)
    cmds.addAttr(ctrl, ln='FootBank',at='float',dv=0,k=True)
    cmds.addAttr(ctrl, ln='FootRoll',at='float',dv=0,k=True)
    cmds.addAttr(ctrl, ln='BallTwist',at='float',dv=0,k=True)
    cmds.addAttr(ctrl, ln='FootTwist',at='float',dv=0,k=True)
    cmds.addAttr(ctrl, ln='ToeRoll',at='float',dv=0,k=True)
    cmds.addAttr(ctrl, ln='ToeTwist',at='float',dv=0,k=True)
    
    #connect attr
    cmds.connectAttr(ctrl+'.FootBank',int+'.rotateZ')
    cmds.connectAttr(ctrl+'.FootBank',ext+'.rotateZ')
    cmds.connectAttr(ctrl+'.FootRoll',heel+'.rotateX')
    cmds.connectAttr(ctrl+'.FootRoll',toes+'.rotateX')
    cmds.connectAttr(ctrl+'.ToeRoll',endJoint+'.rotateX')
    cmds.connectAttr(ctrl+'.ToeTwist',endJoint+'.rotateY')
    cmds.connectAttr(ctrl+'.FootTwist',toes+'.rotateY')
    cmds.connectAttr(ctrl+'.BallTwist',heel+'.rotateY')