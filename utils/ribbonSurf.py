import maya.cmds as cmds
import math
import RigLo.components.shapes as shapes
import RigLo.basic as bs


#NEED to define number of ctrl and number of joints
#the number of controller = number of spans 
def createFrstCrv(*args):
    cmds.CreateCurveFromPoly()
    name = cmds.textField("RibbonName", query=True, text=True)
    FrstCrv=cmds.rename('CRV_second_'+name)
    cmds.FreezeTransformations()
    cmds.DeleteHistory()
    cmds.CenterPivot()

    
def createScndCrv(*args):
    cmds.CreateCurveFromPoly()
    name = cmds.textField("RibbonName", query=True, text=True)
    FrstCrv=cmds.rename('CRV_first_'+name)
    cmds.FreezeTransformations()
    cmds.DeleteHistory()
    cmds.CenterPivot()


def createSurface():
    name = cmds.textField("RibbonName", query=True, text=True)
    cmds.select('CRV_first_'+name)
    cmds.select('CRV_second_'+name,add=True)
    Surface=cmds.loft(n='SURF_'+name)[0]
    cmds.FreezeTransformations()
    cmds.DeleteHistory()
    cmds.CenterPivot()

#make work without the UI

def surfaceRibbonsJoint(jointNum, ctrlNum ):
    
    skList=[]
    jointNum = int(cmds.textField("jntNumb", query=True, text=True))
    rebuildNum = int(cmds.textField("ctrlNumb", query=True, text=True))
    #rebuildSurface with the number of controller
    cmds.rebuildSurface(su=1,sv=rebuildNum,du=1,dv=3,kr=0)
        
    name = cmds.textField("RibbonName", query=True, text=True)
    nb_jnts = int(cmds.textField("jntNumb", query=True, text=True))
    sel='SURF_'+name
    shape=cmds.listRelatives(sel,s=True)
    
    for div in range(nb_jnts+1):
        U=0.5
        V=div/nb_jnts
        
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
        ctrl=ctrl=cmds.curve(n='C_'+name+'_0'+str(div),d=1,p= [( -1.5 , 0 , 0 ) , ( -1 , 0 , 0 ) , ( -0.965926 , 0.258819 , 0 ) , ( -0.866026 , 0.5 , 0 ) , ( -0.707107 , 0.707107 , 0 ) , ( -0.5 , 0.866025 , 0 ) , ( -0.258819 , 0.965926 , 0 ) , ( 0 , 1 , 0 ) , ( 0 , 1.5 , 0 ) , ( 0 , 1 , 0 ) , ( 0.258819 , 0.965926 , 0 ) , ( 0.5 , 0.866025 , 0 ) , ( 0.707107 , 0.707107 , 0 ) , ( 0.866025 , 0.5 , 0 ) , ( 0.965926 , 0.258819 , 0 ) , ( 1 , 0 , 0 ) , ( 1.5 , 0 , 0 ) , ( 1 , 0 , 0 ) , ( 0.965926 , -0.258819 , 0 ) , ( 0.866025 , -0.5 , 0 ) , ( 0.707107 , -0.707107 , 0 ) , ( 0.5 , -0.866025 , 0 ) , ( 0.258819 , -0.965926 , 0 ) , ( 0 , -1 , 0 ) , ( 0 , -1.5 , 0 ) , ( 0 , -1 , 0 ) , ( -0.258819 , -0.965926 , 0 ) , ( -0.5 , -0.866025 , 0 ) , ( -0.707107 , -0.707107 , 0 ) , ( -0.866026 , -0.5 , 0 ) , ( -0.965926 , -0.258819 , 0 ) , ( -1 , 0 , 0 ) , ( -0.951057 , 0 , 0.309017 ) , ( -0.809017 , 0 , 0.587785 ) , ( -0.587785 , 0 , 0.809017 ) , ( -0.309017 , 0 , 0.951057 ) , ( -2.98023e-08 , 0 , 1 ) , ( 0 , 0 , 1.5 ) , ( -2.98023e-08 , 0 , 1 ) , ( 0.309017 , 0 , 0.951057 ) , ( 0.587785 , 0 , 0.809017 ) , ( 0.809017 , 0 , 0.587785 ) , ( 0.951057 , 0 , 0.309017 ) , ( 1 , 0 , 0 ) , ( 0.951057 , 0 , -0.309017 ) , ( 0.809018 , 0 , -0.587786 ) , ( 0.587786 , 0 , -0.809017 ) , ( 0.309017 , 0 , -0.951057 ) , ( 0 , 0 , -1 ) , ( 0 , 0 , -1.5 ) , ( 0 , 0 , -1 ) , ( 0 , 0.258819 , -0.965926 ) , ( 0 , 0.5 , -0.866026 ) , ( 0 , 0.707107 , -0.707107 ) , ( 0 , 0.866025 , -0.5 ) , ( 0 , 0.965926 , -0.258819 ) , ( 0 , 1 , 0 ) , ( -7.71341e-09 , 0.965926 , 0.258819 ) , ( -1.49012e-08 , 0.866025 , 0.5 ) , ( -2.10734e-08 , 0.707107 , 0.707107 ) , ( -2.58096e-08 , 0.5 , 0.866026 ) , ( -2.87868e-08 , 0.258819 , 0.965926 ) , ( -2.98023e-08 , 0 , 1 ) , ( -2.87868e-08 , -0.258819 , 0.965926 ) , ( -2.58096e-08 , -0.5 , 0.866026 ) , ( -2.10734e-08 , -0.707107 , 0.707107 ) , ( -1.49012e-08 , -0.866025 , 0.5 ) , ( -7.71341e-09 , -0.965926 , 0.258819 ) , ( 0 , -1 , 0 ) , ( 0 , -0.965926 , -0.258819 ) , ( 0 , -0.866025 , -0.5 ) , ( 0 , -0.707107 , -0.707107 ) , ( 0 , -0.5 , -0.866026 ) , ( 0 , -0.258819 , -0.965926 ) , ( 0 , 0 , -1 ) , ( -0.309017 , 0 , -0.951057 ) , ( -0.587785 , 0 , -0.809017 ) , ( -0.809017 , 0 , -0.587785 ) , ( -0.951057 , 0 , -0.309017 ) , ( -1 , 0 , 0 ) ])
        cmds.DeleteHistory()        
        
        ###shape=cmds.listRelatives(ctrl,shapes=True)
        
        #Créer le groupe de placement
        groupe=cmds.group(ctrl,n='GRP_'+name+'_0'+str(div))
        
        cmds.setAttr(P_on_S+'.parameterU', U)
        cmds.setAttr(P_on_S+'.parameterV', V)
        
        #connect mat to grp !!! MAUVAISE METHODE : la matrice prend le shear en compte et donc non utilisable
        #cmds.connectAttr(Mat_4x4+'.output',groupe+'.offsetParentMatrix')
        
        DecMatX=cmds.createNode('decomposeMatrix', n='DeMatX_'+sel[0]+'_0'+str(div))
        cmds.connectAttr(Mat_4x4+'.output', DecMatX+'.inputMatrix')
        
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
    
    div_grp_sel=cmds.select('GRP_'+name+'*')
    Grp_offset=cmds.group(n='GRP_offset_'+name)
    
    cmds.select(cl=True)
    MastJoint=cmds.joint(n='JNT_Master_'+name)
    cmds.select(sel,add=True)
    cmds.MatchTransform()
    cmds.parent(skList,MastJoint)
    
def surfaceRibbonsCtrl(*args):
    
    jntList=[]
    ctrlNumber = int(cmds.textField("ctrlNumb", query=True, text=True))
    name = cmds.textField("RibbonName", query=True, text=True)
    nb_jnts = int(cmds.textField("jntNumb", query=True, text=True))
    sel='SURF_'+name
    shape=cmds.listRelatives(sel,s=True)
    
    for div in range(ctrlNumber+1):
        U=0.5
        V=div/ctrlNumber
        
        #build point on surface
        P_on_S=cmds.createNode('pointOnSurfaceInfo',n='PoS_RIB_'+name+'_0'+str(div))
        #node matrice four by four 
        Mat_4x4=cmds.createNode('fourByFourMatrix', n='Mat_RIB_'+name+'_0'+str(div))
        print(Mat_4x4)
        
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
        ctrl=cmds.circle(r=radius*2,s=8,d=2,nr=(1,0,0), ch=False,n='C_'+name+'_0'+str(div))
        parenting=cmds.parentConstraint(ctrl,jnt)
        ###shape=cmds.listRelatives(ctrl,shapes=True)
        
        #Créer le groupe de placement
        groupe=cmds.group(ctrl,n='GRP_C_'+name+'_0'+str(div))
        
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
        #cmds.delete(Mat_4x4)
        #prout=cmds.select('Mat_RIB_*')
        #print(prout)
        
    div_grp_sel=cmds.select('GRP_C_'+name+'*')
    Grp_offset=cmds.group(n='GRP_Master_'+name)
    
    
    #select joint and skin
    print(jntList) 
    cmds.select(jntList)
    cmds.select(sel, add=True)
    SkC=cmds.skinCluster(bindMethod=0, normalizeWeights=1, weightDistribution=0, mi=3, omi=True, dr=4, rui=True, nw=1, n='SkC_'+name)[0]
    



def createRibbon(*args):
    ribbon_name = cmds.textField("RibbonName", query=True, text=True)
    jointNumber = int(cmds.textField("jntNumb", query=True, text=True))
    ctrlNumber = int(cmds.textField("ctrlNumb", query=True, text=True))
    #UVdirection = cmds.checkBox("Inverse U and V directions", query=True, text=True)
    
    createSurface()
    surfaceRibbonsJoint()
    surfaceRibbonsCtrl()
    
    #del unused crv
    cmds.select('CRV_first_*')
    cmds.select('CRV_second_*',add=True)
    cmds.delete()
    

def create_ui():
    windowRibbon = "RibbonWindow"
    if cmds.window(windowRibbon, exists=True):
        cmds.deleteUI(windowRibbon)
    cmds.window(windowRibbon, t="Create Two types Ribbons")
    
    cmds.columnLayout(columnAttach=('both', 10), rowSpacing=10, columnWidth=250, adjustableColumn=True)
    cmds.text(label='  ',al='center')
    cmds.text(label='Select continuous/partial edge loop, and a ribbon of it.',al='left', ann='Tip : set to max of controllers to half the number of joints or low.')
    cmds.text(label='  ',al='center')
    cmds.text(label='Name',al='center')
    name = cmds.textField("RibbonName")
    
    cmds.text(label='Create curve',al='center')
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 150), (2, 150)],adj=2,columnOffset=[(2, "left", 3)])
    #cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 150), (2, 159)], columnOffset=[(1, "right", 3)], rowSpacing=(1, 7))
    cmds.button(label='Curve 1', c=createFrstCrv, backgroundColor=(0.2, 0.3, 0.2))
    cmds.button(label='Curve 2', c=createScndCrv, backgroundColor=(0.3, 0.5, 0.3))
    cmds.setParent("..")

    cmds.columnLayout(columnAttach=('both', 10), rowSpacing=10, columnWidth=250,adj=True)
    cmds.separator( h=5)
    cmds.text(label='Number of joints')
    jointNum = cmds.textField("jntNumb")
    
    cmds.text(label='Number of controllers')
    jointNum = cmds.textField("ctrlNumb")
    UVdir=cmds.checkBox(label='Inverse U and V directions',)
    cmds.button(label="Create", command=createRibbon)
    cmds.button(label='Close', command=('cmds.deleteUI(\"' + windowRibbon + '\", window=True)'))
    cmds.text(label='  ',al='center')
    cmds.showWindow(windowRibbon)
    
create_ui()
