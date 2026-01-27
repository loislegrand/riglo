
import pymel.core as pm
import maya.cmds as cmds
import RigLo.components.shapes as shapes


'''___________To Do__________
  - split the building part from the guide creation(including the locator for the inverse foot)
  - another function
  - change to class hierarchy
  '''


def loadGuidesQuadLeg():
    #select a top bones 
    TopJoints = cmds.ls(sl=True)
    print(TopJoints)

    for JNT in TopJoints:
        
        if not cmds.objectType(JNT, i='joint'):
            cmds.error('----- Only Joint Type Object Accepted -----')
        
        mainJntChain = cmds.listRelatives(JNT, ad=True, typ='joint')
        mainJntChain.append(JNT)
        mainJntChain = mainJntChain[::-1]
        
        #check existence in list vith the in operator
        if not '*_IK_*' in mainJntChain:
            #if not then create a duplicate with prefix JNT_IK_
            IkTempJntChain = cmds.duplicate(JNT, rc=True)
            print(IkTempJntChain)
            IkJntChain=[]
            
            for n in range(len(mainJntChain)):
                NewName = cmds.rename(IkTempJntChain[n],'JNT_IK_'+mainJntChain[n])
                IkJntChain.append(NewName)
            print(IkJntChain)
        
        
        #create the ikRP
        IkRP = cmds.ikHandle(sj=IkJntChain[0],ee=IkJntChain[2],n='ikH_'+mainJntChain[0])[0]
        print(IkRP)
        
        GrpIkRP = cmds.group(n='GRP_'+IkRP,em=True)
        print(GrpIkRP)
        print(mainJntChain[3])
        cmds.matchTransform(GrpIkRP, mainJntChain[3], pos=True)
        
        cmds.parent(IkRP,GrpIkRP)
        
        
        #getAttr IkHandle PoleVectorZ to orient the PV
        PVValueZ = cmds.getAttr(IkRP+'.poleVectorZ')
        if PVValueZ > 0:
            orientation = 1
        if PVValueZ < 0:
            orientation = -1
        print(orientation)
        
        shapes.createPV(ori=orientation, object=mainJntChain[1])
        
        selPV=cmds.ls(sl=True)[0]
        #create PV constraint
        cmds.poleVectorConstraint(selPV, IkRP)
        
        #create IkSC btw 3 and 4
        IkSC1 = cmds.ikHandle(sj=IkJntChain[2],ee=IkJntChain[3],n='ikH_ankle_'+JNT[-4:], sol='ikSCsolver')[0]
        ballRoll = cmds.group(n='GRP_ballRoll'+IkSC1[-4:],em=True)
        cmds.matchTransform(ballRoll, IkJntChain[2],pos=True)
        ankleRoll = cmds.duplicate(n='GRP_ankleRoll'+JNT[-4:])[0]
        cmds.parent(GrpIkRP,ballRoll)
        cmds.parent(IkSC1,ankleRoll)
        cmds.parent(ankleRoll,GrpIkRP)
        
        IkSC2 = cmds.ikHandle(sj=IkJntChain[2],ee=IkJntChain[3],n='ikH_ball_'+JNT[-4:], sol='ikSCsolver')[0]
        
        IkSC3 = cmds.ikHandle(sj=IkJntChain[3],ee=IkJntChain[4],n='ikH_toe_'+JNT[-4:], sol='ikSCsolver')[0]
        toeBend = cmds.group(n='GRP_toeBend'+IkSC1[-4:],em=True)
        cmds.matchTransform(toeBend, IkJntChain[3],pos=True)
        toeAnkleRoll = cmds.group(n='GRP_toeAnkleRoll'+IkSC1[-4:],em=True, p = toeBend)
        cmds.parent(IkSC3,toeAnkleRoll)
        cmds.parent(IkSC2, ballRoll)
        
        
        
        #create IkSC btw 4 and 5
        
        #create 4 locators In, Out, Toe, Heel
        TopGroupe = cmds.group(em=True, n='GRP_InverseFoot_'+JNT[-4:])
        OriGroupe = cmds.group(em=True, n='GRPori_InverseFoot_'+JNT[-4:], p=TopGroupe)
        OutNode = cmds.spaceLocator(n='LOC_Out_'+JNT[-4:])[0]
        InNode = cmds.spaceLocator(n='LOC_In_'+JNT[-4:])[0]
        ToeRoll = cmds.spaceLocator(n='LOC_ToeRoll_'+JNT[-4:])[0]
        HeelRoll = cmds.spaceLocator(n='LOC_HeelRoll_'+JNT[-4:])[0]
        cmds.parent(OutNode,InNode,ToeRoll,HeelRoll,OriGroupe)
        
        
        cmds.matchTransform(TopGroupe, mainJntChain[3],pos=True)
        cmds.matchTransform(OriGroupe, mainJntChain[4],pos=True)
        
        if cmds.getAttr(JNT+'.translateX')>0:
            PosX = 1
        else:
            PosX = -1
            
        cmds.setAttr(OutNode+'.translateX',PosX*8)
        cmds.setAttr(InNode+'.translateX',PosX*-6)
        cmds.setAttr(ToeRoll+'.translateZ',9)
        cmds.setAttr(HeelRoll+'.translateZ',-6)
        
        cmds.parent(InNode,OutNode)
        cmds.parent(ToeRoll,InNode)
        cmds.parent(HeelRoll,ToeRoll)
        
        cmds.parent(ballRoll,toeBend,HeelRoll)
        
        #controller part, create the controller and its parameters, connect it all
        #DO THE PARAMETER AGAIN !!!!!
        ctrl = shapes.ctrlParameter(curveType='hoof')
        print(ctrl)
        cmds.setAttr(ctrl+".translateY",-3)
        cmds.setAttr(ctrl+".translateX",1)
        cmds.setAttr(ctrl+".translateZ",2)
        CTRL = cmds.rename(ctrl, 'C_leg_'+JNT[-4:])
        cmds.makeIdentity(a=True, t=True)
        GRP_Ctrl = cmds.group(n='GRP_leg_'+JNT[-4:],em=True)
        cmds.matchTransform(CTRL,GRP_Ctrl,piv=True)
        cmds.parent(CTRL,GRP_Ctrl)
        
        cmds.matchTransform(GRP_Ctrl,mainJntChain[3],pos=True)
        
        cmds.parentConstraint(CTRL,TopGroupe)
        
        attrList = ['HeelRoll','ToeRoll','BallRoll','AnkleRoll','HeelTwist','ToeTwist','ToeBend','FootRock']
        cmds.addAttr(CTRL,ln='InverseFoot',at='float',dv=1.0,keyable=1)
        cmds.setAttr(CTRL+'.InverseFoot', lock=True)
        for name in attrList:
            cmds.addAttr(CTRL,ln=name,at='float',dv=0,k=True)
        
        
        cmds.connectAttr(CTRL+'.HeelRoll',HeelRoll+'.rotateX')
        cmds.connectAttr(CTRL+'.ToeRoll',ToeRoll+'.rotateX')
        cmds.connectAttr(CTRL+'.BallRoll',ballRoll+'.rotateX')
        #WEIRD BEHAVIOUR
        cmds.connectAttr(CTRL+'.AnkleRoll',ankleRoll+'.rotateX')
        cmds.connectAttr(CTRL+'.AnkleRoll',toeAnkleRoll+'.rotateX')
        
        cmds.connectAttr(CTRL+'.HeelTwist',HeelRoll+'.rotateY')
        cmds.connectAttr(CTRL+'.ToeTwist',ToeRoll+'.rotateY')
        cmds.connectAttr(CTRL+'.ToeBend',toeBend+'.rotateX')
        cmds.connectAttr(CTRL+'.FootRock',OutNode+'.rotateZ')
        cmds.connectAttr(CTRL+'.FootRock',InNode+'.rotateZ')
        
        cmds.transformLimits(InNode, rz=(0,45), erz=(1,0))
        cmds.transformLimits(OutNode, rz=(-45,0), erz=(0,1))
        
        shapes.ctrlParameter(curveType='cube')
        CtrlPelvis= cmds.rename(ctrl, 'C_pelvis_'+JNT[-4:])
        GrpPelvis = cmds.group(em=True, n='GRP_pelvis_'+JNT[-4:])
        cmds.parent(CtrlPelvis, GrpPelvis)
        
        cmds.matchTransform(GrpPelvis,IkJntChain[0])
        cmds.parentConstraint(CtrlPelvis,IkJntChain[0])
        
        #organize the created setup