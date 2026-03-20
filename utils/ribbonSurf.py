import maya.cmds as cmds
import math
import RigLo.components.shapes as shapes
import RigLo.basic as bs


def createSurface(name, crv1, crv2):
    cmds.select(crv1)
    cmds.select(crv2,add=True)
    Surface=cmds.loft(n='SURF_'+name)[0]
    cmds.FreezeTransformations()
    cmds.DeleteHistory()
    cmds.CenterPivot()

#make work without the UI

def surfaceRibbonsJoint(jointNum, ctrlNum, name):
    
    skList=[]
    #rebuildSurface with the number of controller
    cmds.rebuildSurface(su=1,sv=ctrlNum,du=1,dv=3,kr=0)
        
    sel='SURF_'+name
    shape=cmds.listRelatives(sel,s=True)

       
    for div in range(jointNum+1):
        U=0.5
        V=div/jointNum
        
        #build point on surface
        P_on_S=cmds.createNode('pointOnSurfaceInfo',n='PoS_'+sel[0]+'_0'+str(div))
        #node matrice four by four 
        Mat_4x4=cmds.createNode('fourByFourMatrix', n='Mat_'+sel[0]+'_0'+str(div))
        
        #connect attr
        cmds.connectAttr(P_on_S+'.result.position.positionX',Mat_4x4+'.in30')
        cmds.connectAttr(P_on_S+'.result.position.positionY',Mat_4x4+'.in31')
        cmds.connectAttr(P_on_S+'.result.position.positionZ',Mat_4x4+'.in32')
        
        cmds.connectAttr(P_on_S+'.result.normalizedNormal.normalizedNormalX',Mat_4x4+'.in00')
        cmds.connectAttr(P_on_S+'.result.normalizedNormal.normalizedNormalY',Mat_4x4+'.in01')
        cmds.connectAttr(P_on_S+'.result.normalizedNormal.normalizedNormalZ',Mat_4x4+'.in02')
        
        cmds.connectAttr(P_on_S+'.result.normalizedTangentU.normalizedTangentUX',Mat_4x4+'.in10')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentU.normalizedTangentUY',Mat_4x4+'.in11')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentU.normalizedTangentUZ',Mat_4x4+'.in12')
        
        cmds.connectAttr(P_on_S+'.result.normalizedTangentV.normalizedTangentVX',Mat_4x4+'.in20')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentV.normalizedTangentVY',Mat_4x4+'.in21')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentV.normalizedTangentVZ',Mat_4x4+'.in22')
        
        cmds.connectAttr(shape[0]+'.worldSpace[0]',P_on_S+'.inputSurface', force=1)
        
        jnt=cmds.joint(n='SK_'+name+'_0'+str(div),rad=0.5)
        skList.append(jnt)
        radius=cmds.getAttr(jnt+'.radius')
        ctrl=cmds.curve(n='C_'+name+'_0'+str(div),d=1,p= [( -1.5 , 0 , 0 ) , ( -1 , 0 , 0 ) , ( -0.965926 , 0.258819 , 0 ) , ( -0.866026 , 0.5 , 0 ) , ( -0.707107 , 0.707107 , 0 ) , ( -0.5 , 0.866025 , 0 ) , ( -0.258819 , 0.965926 , 0 ) , ( 0 , 1 , 0 ) , ( 0 , 1.5 , 0 ) , ( 0 , 1 , 0 ) , ( 0.258819 , 0.965926 , 0 ) , ( 0.5 , 0.866025 , 0 ) , ( 0.707107 , 0.707107 , 0 ) , ( 0.866025 , 0.5 , 0 ) , ( 0.965926 , 0.258819 , 0 ) , ( 1 , 0 , 0 ) , ( 1.5 , 0 , 0 ) , ( 1 , 0 , 0 ) , ( 0.965926 , -0.258819 , 0 ) , ( 0.866025 , -0.5 , 0 ) , ( 0.707107 , -0.707107 , 0 ) , ( 0.5 , -0.866025 , 0 ) , ( 0.258819 , -0.965926 , 0 ) , ( 0 , -1 , 0 ) , ( 0 , -1.5 , 0 ) , ( 0 , -1 , 0 ) , ( -0.258819 , -0.965926 , 0 ) , ( -0.5 , -0.866025 , 0 ) , ( -0.707107 , -0.707107 , 0 ) , ( -0.866026 , -0.5 , 0 ) , ( -0.965926 , -0.258819 , 0 ) , ( -1 , 0 , 0 ) , ( -0.951057 , 0 , 0.309017 ) , ( -0.809017 , 0 , 0.587785 ) , ( -0.587785 , 0 , 0.809017 ) , ( -0.309017 , 0 , 0.951057 ) , ( -2.98023e-08 , 0 , 1 ) , ( 0 , 0 , 1.5 ) , ( -2.98023e-08 , 0 , 1 ) , ( 0.309017 , 0 , 0.951057 ) , ( 0.587785 , 0 , 0.809017 ) , ( 0.809017 , 0 , 0.587785 ) , ( 0.951057 , 0 , 0.309017 ) , ( 1 , 0 , 0 ) , ( 0.951057 , 0 , -0.309017 ) , ( 0.809018 , 0 , -0.587786 ) , ( 0.587786 , 0 , -0.809017 ) , ( 0.309017 , 0 , -0.951057 ) , ( 0 , 0 , -1 ) , ( 0 , 0 , -1.5 ) , ( 0 , 0 , -1 ) , ( 0 , 0.258819 , -0.965926 ) , ( 0 , 0.5 , -0.866026 ) , ( 0 , 0.707107 , -0.707107 ) , ( 0 , 0.866025 , -0.5 ) , ( 0 , 0.965926 , -0.258819 ) , ( 0 , 1 , 0 ) , ( -7.71341e-09 , 0.965926 , 0.258819 ) , ( -1.49012e-08 , 0.866025 , 0.5 ) , ( -2.10734e-08 , 0.707107 , 0.707107 ) , ( -2.58096e-08 , 0.5 , 0.866026 ) , ( -2.87868e-08 , 0.258819 , 0.965926 ) , ( -2.98023e-08 , 0 , 1 ) , ( -2.87868e-08 , -0.258819 , 0.965926 ) , ( -2.58096e-08 , -0.5 , 0.866026 ) , ( -2.10734e-08 , -0.707107 , 0.707107 ) , ( -1.49012e-08 , -0.866025 , 0.5 ) , ( -7.71341e-09 , -0.965926 , 0.258819 ) , ( 0 , -1 , 0 ) , ( 0 , -0.965926 , -0.258819 ) , ( 0 , -0.866025 , -0.5 ) , ( 0 , -0.707107 , -0.707107 ) , ( 0 , -0.5 , -0.866026 ) , ( 0 , -0.258819 , -0.965926 ) , ( 0 , 0 , -1 ) , ( -0.309017 , 0 , -0.951057 ) , ( -0.587785 , 0 , -0.809017 ) , ( -0.809017 , 0 , -0.587785 ) , ( -0.951057 , 0 , -0.309017 ) , ( -1 , 0 , 0 ) ])
        cmds.DeleteHistory()        
        
        ###shape=cmds.listRelatives(ctrl,shapes=True)
        
        #Créer le groupe de placement
        groupe=cmds.group(ctrl,n='GRP_'+name+'_0'+str(div))
        
        cmds.setAttr(P_on_S+'.parameterU', U)
        cmds.setAttr(P_on_S+'.parameterV', V)
        
        #connect mat to grp !!! MAUVAISE METHODE : la matrice prend le shear en compte et donc non utilisable
        #cmds.connectAttr(Mat_4x4+'.output',groupe+'.offsetParentMatrix')
        
        DecMatX=cmds.createNode('decomposeMatrix', n='DeMatX_'+sel[0]+'_0'+str(div))
        MultMatGrp = cmds.createNode('multMatrix', n='MultGrp_'+sel[0]+'_0'+str(div))
        cmds.connectAttr(Mat_4x4+'.output', MultMatGrp+'.matrixIn[0]')
        cmds.connectAttr(groupe + '.parentInverseMatrix', MultMatGrp+'.matrixIn[1]')
        cmds.connectAttr(MultMatGrp+'.matrixSum', DecMatX+'.inputMatrix')

        
        #connect outputs T,R,S to grp
        cmds.connectAttr(DecMatX+'.outputTranslate', groupe+'.translate')
        cmds.connectAttr(DecMatX+'.outputRotate', groupe+'.rotate')
        
        
        #trop lourd comme set up, passer plutôt sur du calcul de matrice parenting=cmds.parentConstraint(ctrl,jnt)
        cmds.select([jnt,ctrl])
        cmds.MatchTransform()
        MultMatX=cmds.createNode('multMatrix')
        cmds.connectAttr(ctrl+'.worldMatrix[0]',MultMatX+'.matrixIn[0]' )
        cmds.connectAttr(jnt+'.parentInverseMatrix[0]',MultMatX+'.matrixIn[1]')
        decMatxJnt=cmds.createNode('decomposeMatrix')
        cmds.connectAttr(MultMatX+'.matrixSum',decMatxJnt+'.inputMatrix')
        cmds.connectAttr(decMatxJnt+'.outputRotate',jnt+'.rotate')
        cmds.connectAttr(decMatxJnt+'.outputTranslate',jnt+'.translate')
        cmds.setAttr(jnt+'.inheritsTransform',0)

        if not jnt == 'SK_'+name+'_00':
            cmds.parent(jnt, jointOld)
        jointOld = jnt
    
    div_grp_sel=cmds.ls('GRP_'+name+'*')
    Grp_offset=cmds.group(div_grp_sel, n='GRP_offset_'+name)
    skList += div_grp_sel

    return skList
    
    
def surfaceRibbonsCtrl(jointNum, ctrlNum, name):
    
    jntList = []
    ctlList = []
    sel='SURF_'+name
    shape=cmds.listRelatives(sel,s=True)
    
    for div in range(ctrlNum+1):
        U=0.5
        V=div/ctrlNum
        
        #build point on surface
        P_on_S=cmds.createNode('pointOnSurfaceInfo',n='PoS_RIB_'+name+'_0'+str(div))
        #node matrice four by four 
        Mat_4x4=cmds.createNode('fourByFourMatrix', n='Mat_RIB_'+name+'_0'+str(div))
        
        #connect attr
        cmds.connectAttr(P_on_S+'.result.position.positionX',Mat_4x4+'.in30')
        cmds.connectAttr(P_on_S+'.result.position.positionY',Mat_4x4+'.in31')
        cmds.connectAttr(P_on_S+'.result.position.positionZ',Mat_4x4+'.in32')
        
        cmds.connectAttr(P_on_S+'.result.normalizedNormal.normalizedNormalX',Mat_4x4+'.in00')
        cmds.connectAttr(P_on_S+'.result.normalizedNormal.normalizedNormalY',Mat_4x4+'.in01')
        cmds.connectAttr(P_on_S+'.result.normalizedNormal.normalizedNormalZ',Mat_4x4+'.in02')
        
        cmds.connectAttr(P_on_S+'.result.normalizedTangentU.normalizedTangentUX',Mat_4x4+'.in10')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentU.normalizedTangentUY',Mat_4x4+'.in11')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentU.normalizedTangentUZ',Mat_4x4+'.in12')
        
        cmds.connectAttr(P_on_S+'.result.normalizedTangentV.normalizedTangentVX',Mat_4x4+'.in20')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentV.normalizedTangentVY',Mat_4x4+'.in21')
        cmds.connectAttr(P_on_S+'.result.normalizedTangentV.normalizedTangentVZ',Mat_4x4+'.in22')
        
        cmds.connectAttr(shape[0]+'.worldSpace[0]',P_on_S+'.inputSurface', force=1)
        
        jnt=cmds.joint(n='SK_RIB_'+name+'_0'+str(div),rad=1)
        jntList.append(jnt)
        radius=cmds.getAttr(jnt+'.radius')
        ctrl=cmds.circle(r=radius*2,s=8,d=2,nr=(0,0,1), ch=False,n='C_master_'+name+'_0'+str(div))
        parenting=cmds.parentConstraint(ctrl,jnt)
        ###shape=cmds.listRelatives(ctrl,shapes=True)
        
        #Créer le groupe de placement
        groupe=cmds.group(ctrl,n='GRP_master'+name+'_0'+str(div))
        ctlList.append(ctrl[0])
        
        cmds.setAttr(P_on_S+'.parameterU', U)
        cmds.setAttr(P_on_S+'.parameterV', V)
        
        DecMatX=cmds.createNode('decomposeMatrix', n='DeMatX_'+name+'_0'+str(div))
        cmds.connectAttr(Mat_4x4+'.output', DecMatX+'.inputMatrix')
        
        LOC=cmds.spaceLocator(n='LOC_C_'+name+'_0'+str(div))[0]
        
        #connect outputs T,R,S to grp
        cmds.connectAttr(DecMatX+'.outputTranslate', LOC+'.translate')
        cmds.connectAttr(DecMatX+'.outputRotate', LOC+'.rotate')
        
        cmds.select(groupe)
        cmds.select(LOC, add=True)
        cmds.MatchTransform()
        
        #del useless nodes
        cmds.delete(DecMatX)
        cmds.delete(LOC)
        
    div_grp_sel=cmds.select('GRP_master'+name+'*')
    Grp_offset=cmds.group(n='GRP_master_'+name)
    
    
    #select joint and skin
    cmds.select(jntList)
    cmds.select(sel, add=True)
    SkC=cmds.skinCluster(bindMethod=0, normalizeWeights=1, weightDistribution=0, mi=3, omi=True, dr=4, rui=True, nw=1, n='SkC_'+name)[0]

    jntList += ctlList

    return jntList


def createRibbon(crv1, crv2, name, jntNum, ctlNum):
    
    createSurface(name, crv1, crv2)
    jnts = surfaceRibbonsJoint(jntNum, ctlNum, name)
    grps = surfaceRibbonsCtrl(jntNum, ctlNum, name)
    
    #del unused crv
    cmds.select(crv1)
    cmds.select(crv2,add=True)
    cmds.delete()
    
    return jnts, grps