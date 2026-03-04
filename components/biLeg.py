import maya.cmds as cmds
import RigLo.components.shapes as shapes
import RigLo.basic as bs



legPart=['upLeg','lowLeg','foot','toes','toesEnd','heel','ext','int']
side='L'

#Use array for the joint name and 
#Locator placement
def locPlacement (*args):
    for part in legPart:
        cmds.spaceLocator(n='RF_'+part+'_'+side)
    
    cmds.xform('RF_upLeg'+'_'+side, t=(0,12,0))
    cmds.xform('RF_lowLeg'+'_'+side, t=(0,7,1))
    cmds.xform('RF_foot'+'_'+side, t=(0,2,0))
    cmds.xform('RF_toes'+'_'+side, t=(0,1,5))
    cmds.xform('RF_toesEnd'+'_'+side, t=(0,0,8))
    cmds.xform('RF_heel'+'_'+side, t=(0,0,-1))
    cmds.xform('RF_ext'+'_'+side, t=(3,0,4))
    cmds.xform('RF_int'+'_'+side, t=(-3,0,4))
    

#def create joint on main joint orient the joint and keep locators for the reverse foot 
def createJoint ():
    cmds.select(cl=True)
    
    #create joint on locator's position
    list = legPart[:-3]
    legJoint = []
    for loc in list:
        JNT = cmds.joint(n='JNT_IK_'+loc+'_'+side)
        legJoint.append(JNT)
        cmds.matchTransform(JNT,'RF_'+loc+'_'+side)
    
    #orient joint
    for jnt in legJoint[:-1]:
        cmds.joint(jnt,e=True,oj='xzy',sao='zup',zso=True)
    cmds.joint(legJoint[-1:],e=True,oj='none',zso=True)
    
    #duplicate joint chain
    duplicata = cmds.duplicate('JNT_IK_upLeg_'+side,rc=True)
    ite=0
    for main in duplicata:
        name = list[ite]
        cmds.rename(main,name+'_'+side)
        ite= ite + 1
    
    #delete unuseful Locator
    cmds.parent('RF_foot'+'_'+side,'RF_toes'+'_'+side)
    cmds.parent('RF_toes'+'_'+side,'RF_toesEnd'+'_'+side)
    cmds.parent('RF_toesEnd'+'_'+side,'RF_heel'+'_'+side)
    cmds.parent('RF_heel'+'_'+side,'RF_ext'+'_'+side)
    cmds.parent('RF_ext'+'_'+side,'RF_int'+'_'+side)
    cmds.delete('RF_upLeg'+'_'+side)
    cmds.delete('RF_lowLeg'+'_'+side)
    
    #transformation constraint
    cmds.transformLimits('RF_ext'+'_'+side,rz=(-45,0),erz=(0,1))
    cmds.transformLimits('RF_int'+'_'+side,rz=(0,45),erz=(1,0))
    cmds.transformLimits('RF_heel'+'_'+side,rx =(-45,0),erx=(0,1))
    cmds.transformLimits('RF_toes'+'_'+side,rx =(0,45),erx=(1,0))
    
    print(legJoint)
    return(legJoint)
    
    
def createCtrl ():
    list = ['JNT_IK_foot_L']
    radius = cmds.getAttr(list[0] + '.radius')
    for i in list:
        #Créer une curve(axeX)
        ctrl=cmds.curve(d=1,p=[ ( 1 , -1 , 1 ) , ( 1 , 1 , 1 ) , ( 1 , 1 , -1 ) , ( 1 , -1 , -1 ) , ( -1 , -1 , -1 ) , ( -1 , 1 , -1 ) , ( -1 , 1 , 1 ) , ( -1 , -1 , 1 ) , ( 1 , -1 , 1 ) , ( 1 , -1 , -1 ) , ( -1 , -1 , -1 ) , ( -1 , -1 , 1 ) , ( -1 , 1 , 1 ) , ( 1 , 1 , 1 ) , ( 1 , 1 , -1 ) , ( -1 , 1 , -1 ) ] ,n='C_IK_'+i)
        shape=cmds.listRelatives(ctrl,shapes=True)
        cmds.xform(ctrl,s=(radius,radius,radius))
        cmds.makeIdentity(ctrl,a=True,s=True)
        cmds.setAttr(shape[0]+'.overrideEnabled', 1)
    
        cmds.setAttr(shape[0]+'.overrideRGBColors', 1)
        
        groupe=cmds.group(ctrl,n='GRP_'+i)
        
        #MatchTransform du groupe de placement sur le joint
        cmds.matchTransform(groupe,i)
        cmds.xform(groupe, ro=(0,0,0))
        
        RorL=cmds.getAttr(groupe+'.translateX')
        
        if RorL > 0.1:
            cmds.setAttr(shape[0]+'.overrideColorR',0.7)
            cmds.setAttr(shape[0]+'.overrideColorG',0)
            cmds.setAttr(shape[0]+'.overrideColorB',0)
        elif RorL < -0.1:
            cmds.setAttr(shape[0]+'.overrideColorR',0)
            cmds.setAttr(shape[0]+'.overrideColorG',0.7)
            cmds.setAttr(shape[0]+'.overrideColorB',0)
        else:
            cmds.setAttr(shape[0]+'.overrideColorR',0.75)
            cmds.setAttr(shape[0]+'.overrideColorG',0.75)
            cmds.setAttr(shape[0]+'.overrideColorB',0)
            
        cmds.parent('RF_int'+'_'+side,ctrl)
        
        #create attr
        cmds.addAttr(ctrl, min=0, max=1, ln='IKFK',at='float',dv=1.0,k=True)
        cmds.addAttr(ctrl, ln='FootBank',at='float',dv=0,k=True)
        cmds.addAttr(ctrl, ln='FootRoll',at='float',dv=0,k=True)
        cmds.addAttr(ctrl, ln='BallTwist',at='float',dv=0,k=True)
        cmds.addAttr(ctrl, ln='FootTwist',at='float',dv=0,k=True)
        cmds.addAttr(ctrl, ln='ToeRoll',at='float',dv=0,k=True)
        cmds.addAttr(ctrl, ln='ToeTwist',at='float',dv=0,k=True)
        
        #connect attr
        cmds.connectAttr(ctrl+'.FootBank','RF_int'+'_'+side+'.rotateZ')
        cmds.connectAttr(ctrl+'.FootBank','RF_ext'+'_'+side+'.rotateZ')
        cmds.connectAttr(ctrl+'.FootRoll','RF_heel'+'_'+side+'.rotateX')
        cmds.connectAttr(ctrl+'.FootRoll','RF_toes'+'_'+side+'.rotateX')
        cmds.connectAttr(ctrl+'.ToeRoll','RF_toesEnd'+'_'+side+'.rotateX')
        cmds.connectAttr(ctrl+'.ToeTwist','RF_toesEnd'+'_'+side+'.rotateY')
        cmds.connectAttr(ctrl+'.FootTwist','RF_toes'+'_'+side+'.rotateY')
        cmds.connectAttr(ctrl+'.BallTwist','RF_heel'+'_'+side+'.rotateY')
    

#create the ctrl on main joint
#create the reverse foot and add the attr
def reverseFoot(legJoint):
    
    IkH = cmds.ikHandle(sj=legJoint[0],ee=legJoint[2],sol='ikRPsolver', n='IkH_leg_'+side)
    IkHandle = IkH[0]
    
    IkSC1 = cmds.ikHandle(sj=legJoint[2],ee=legJoint[3],sol='ikSCsolver', n='IkSC_toes_'+side)
    IkScHandle1 = IkSC1[0]
    
    IkSC2 = cmds.ikHandle(sj=legJoint[3],ee=legJoint[4],sol='ikSCsolver', n='IkSC_toesEnd_'+side)
    IkScHandle2 = IkSC2[0]
    
    cmds.parent(IkHandle,'RF_foot'+'_'+side)
    cmds.parent(IkScHandle1,'RF_toes'+'_'+side)
    cmds.parent(IkScHandle2,'RF_toesEnd'+'_'+side)
    
    
def setupCreation(*args):
    reverseFoot(createJoint())
    createCtrl()


def create_ui():
    windowRibbon = "ReverseFootWindow"
    if cmds.window(windowRibbon, exists=True):
        cmds.deleteUI(windowRibbon)
    cmds.window(windowRibbon, t="Create a reverse foot setup")
    
    cmds.columnLayout(columnAttach=('both', 10), rowSpacing=10, columnWidth=250, adjustableColumn=True)
    cmds.text(label='  ',al='center')
    cmds.text(label='Place the locator and hit create to set up.',al='left', ann='Tip : Tqt je fais genre en vrai')
    cmds.text(label='  ',al='center')
    cmds.text(label='Side',al='center')
    name = cmds.textField("side")
    
    cmds.separator( h=5)
    cmds.button(label='Create Locators',command=locPlacement, backgroundColor=(0.2, 0.2, 0.4))

    UVdir=cmds.checkBox(label='Inverse Foot bank',)
    cmds.button(label="Create", command=setupCreation)
    cmds.button(label='Close', command=('cmds.deleteUI(\"' + windowRibbon + '\", window=True)'))
    cmds.text(label='  ',al='center')
    cmds.showWindow(windowRibbon)
    
create_ui()