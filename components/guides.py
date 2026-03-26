import maya.cmds as cmds
import math
import RigLo.components.shapes as shapes
import RigLo.basic as bs

from importlib import reload
reload(bs)


'''class arm():
    def __init__(self, side='L', part='arm',
                 joint_list=None,
                 alias_list=None,
                 pole_vector=None,
                 remove_guides=False,
                 add_stretch=False,
                 color_dict=False,
                 primary_axis='X',
                 up_axis='Y'):

        # define variables
        self.side = side
        self.part = part
        self.joint_list = joint_list
        self.alias_list = alias_list
        self.pole_vector = pole_vector
        self.remove_guides = remove_guides
        self.add_stretch = add_stretch
        self.color_dict = color_dict
        self.primary_axis = primary_axis
        self.up_axis = up_axis
        self.base_name = self.side + '_' + self.part
        '''

class GuideLoader():
    def __init__(self, side='L', part='arm',
                 joint_list=[],
                 alias_list=None,
                 pole_vector=None,
                 remove_guides=False,
                 add_stretch=False,
                 color_dict=False,
                 primary_axis='X',
                 up_axis='Y'):
        
        # define variables
        self.side = side
        self.part = part
        self.joint_list = joint_list
        self.alias_list = alias_list
        self.pole_vector = pole_vector
        self.remove_guides = remove_guides
        self.add_stretch = add_stretch
        self.color_dict = color_dict
        self.primary_axis = primary_axis
        self.up_axis = up_axis
        self.base_name = self.part + '_' + self.side


    def CnsType(self, *args):

        mtx_enabled = cmds.checkBox('MtxCns', q=True, v=True)

        print("Matrix constraint enabled:", mtx_enabled)

        if mtx_enabled:
            print("Loading matrix version...")
        else:
            print("Loading native version...")


# ségmenter le getInfos dans un modules à part 
# faire un setup qui s'active selon le membre avec la récupération des datas
    def guideType(self):
        type = bs.getUIsInfos(UiPart='Limb')[0]

        if type == 'Arm':
            self.loadGuidesArm()
        
        elif type == 'Quadruped Leg':
            self.loadGuidesQuadLeg()

        elif type == 'Biped Leg':
            self.loadGuidesBiLeg()    

    def hierarchyGuides(self):
        '''
        addAttr as metaData to the topGuides : type, toBuild, blend IkFk, twisties, stretchy, bendies, spacialisation
        list of the limb part
        '''
     
        allInfos = bs.getUIsInfos(UiPart='Limb')

        TopGds = cmds.group(em=True, n='GDs_{}_{}_{}'.format(allInfos[0], allInfos[1], allInfos[2]))
        
        listAttributs = {'type': 'enum', 'toBuild': 'bool', 'BlendIkFk' : 'bool', 'twist': 'bool', 'stretch': 'bool', 'bend': 'bool'}
        
        for i in listAttributs:
            type = listAttributs[i]
            if type == 'enum':
                typeLimb = allInfos[0]
                cmds.addAttr(TopGds, ln=i, at=type, k=True, enumName=typeLimb)
            else:
                
                cmds.addAttr(TopGds, ln=i, at=type, k=True, dv=True)

        return TopGds
        


    def loadGuidesArm(self):
        joint_list = []

        allInfos = bs.getUIsInfos(UiPart='Limb', printInfos=True)

        #spherePts = shapes.curveParameter(curveType='sphere')

        TopGds = self.hierarchyGuides()
        
        guideArm = cmds.joint(n='GD_shoulder_{}_Left'.format(allInfos[1]))
        guideForearm = cmds.joint(n='GD_elbow_{}_Left'.format(allInfos[1]))
        guideHand = cmds.joint(n='GD_wrist_{}_Left'.format(allInfos[1]))
        guideHandEnd = cmds.joint(n='GD_hand_{}_Left'.format(allInfos[1]), p= (5,0,0),r=True)

        cmds.xform(guideArm, t=(20, 165, 0), ro=(0,0,-45))
        cmds.xform(guideForearm, t=(25, 0, -2))
        cmds.xform(guideHand, t=(25, 0, 2))

        joint_list.append(guideArm)
        joint_list.append(guideForearm)
        joint_list.append(guideHand)

        if allInfos[2] == 'Right':
            chain = bs.mirror(symmetry=True, jointChain = guideArm)[0]
            joint_list = (cmds.listRelatives(chain, ad=True, typ='joint') + [chain])[::-1]
        
        bs.BRA_rotatePlane(joint_list[0], joint_list[1], joint_list[2], '_'.join(allInfos[:3]))
        
        self.addLabels(joint_list)

        return joint_list

    def loadGuidesQuadLeg(self):

        joint_list = []

        TopGds = self.hierarchyGuides()

        allInfos = bs.getUIsInfos(UiPart='Limb', printInfos=True)
        print(allInfos)
        
        if allInfos[1] == 'Front':
            reverse = 55
            
        else:
            reverse = 45

        guideArm = cmds.joint(p=(9, 95, 53), n='GDqL_upLeg_{}_Left'.format(allInfos[1]))
        guideForearm = cmds.joint(p=(9, 48, reverse), n='GDqL_midLeg_{}_Left'.format(allInfos[1]))
        guideHand = cmds.joint(p=(9, 20, 51), n='GDqL_lowLeg_{}_Left'.format(allInfos[1]))
        guideHandEnd = cmds.joint(p=(9, 8, 55), n='GDqL_toes_{}_Left'.format(allInfos[1]))
        guideEnd = cmds.joint(p=(9, 0, 60), n='GDqL_toesEnd_{}_Left'.format(allInfos[1]))
        OutNode = cmds.joint(p=(PosX*12, 0, 58), n='LOCqL_ext_{}_{}'.format(allInfos[1], allInfos[2]))
        InNode = cmds.joint(p=(PosX*6, 0, 58), n='LOCqL_int_{}_{}'.format(allInfos[1], allInfos[2]))
        HeelRoll = cmds.joint(p=(9, 0, 52), n='LOCqL_heel_{}_{}'.format(allInfos[1], allInfos[2]))
        cmds.setAttr(guideHandEnd+'.drawStyle', 3)
        
        if allInfos[2] == 'Left':
            PosX = 1
        elif allInfos[2] == 'Right':
            PosX = -1
        else:
            PosX = 0

        cmds.parent(OutNode, InNode, HeelRoll, guideHandEnd)

        joint_list.append(guideArm)
        joint_list.append(guideForearm)
        joint_list.append(guideHand)
        joint_list.append(guideHandEnd)
        joint_list.append(guideEnd)
        joint_list.append(OutNode)
        joint_list.append(InNode)
        joint_list.append(HeelRoll)
        
        if allInfos[2] == 'Right':
            chain = bs.mirror(symmetry=True, jointChain = guideArm)[0]
            joint_list = (cmds.listRelatives(chain, ad=True, typ='joint') + [chain])[::-1]

        bs.BRA_rotatePlane(joint_list[0], joint_list[1], joint_list[2], '_'.join(allInfos[:3]))

        self.addLabels(joint_list)

        return joint_list
    
    def loadGuidesBiLeg(self):
        
        joint_list = []

        TopGds = self.hierarchyGuides()

        allInfos = bs.getUIsInfos(UiPart='Limb', printInfos=True)

        if allInfos[2] == 'Left':
            PosX = 1
        elif allInfos[2] == 'Right':
            PosX = -1
        else:
            PosX = 0

        guideUpLeg = cmds.joint(p=(9, 90, 2.5), n='GDbL_upLeg_{}_Left'.format(allInfos[1]))
        guideLowLeg = cmds.joint(p=(9, 50, 2.5), n='GDbL_lowLeg_{}_Left'.format(allInfos[1]))
        guideFoot = cmds.joint(p=(9, 10, 0), n='GDbL_foot_{}_Left'.format(allInfos[1]))
        guideToes = cmds.joint(p=(9, 3, 12), n='GDbL_toes_{}_Left'.format(allInfos[1]))
        guideEnd = cmds.joint(p=(9, 0, 20), n='GDbL_toesEnd_{}_Left'.format(allInfos[1]))
        OutNode = cmds.joint(p=(PosX*12, 0, 12), n='LOCbL_ext_{}_{}'.format(allInfos[1], allInfos[2]))
        InNode = cmds.joint(p=(PosX*6, 0, 12), n='LOCbL_int_{}_{}'.format(allInfos[1], allInfos[2]))
        HeelRoll = cmds.joint(p=(9, 0, 0), n='LOCbL_heel_{}_{}'.format(allInfos[1], allInfos[2]))
        cmds.setAttr(guideToes+'.drawStyle', 3)

        cmds.parent(OutNode, InNode, HeelRoll, guideToes)

        joint_list.append(guideUpLeg)
        joint_list.append(guideLowLeg)
        joint_list.append(guideFoot)
        joint_list.append(guideToes)
        joint_list.append(guideEnd)
        joint_list.append(OutNode)
        joint_list.append(InNode)
        joint_list.append(HeelRoll)

        if allInfos[2] == 'Right':
            chain = bs.mirror(symmetry=True, jointChain = guideUpLeg)[0]
            joint_list = (cmds.listRelatives(chain, ad=True, typ='joint') + [chain])[::-1]

        bs.BRA_rotatePlane(joint_list[0], joint_list[1], joint_list[2], '_'.join(allInfos[:3]))

        self.addLabels(joint_list)

        return joint_list

    def searchConstruct(self):

        list = cmds.ls('GDs_*')

        toBuildLs = []
        for inst in list:
            if cmds.getAttr(inst + '.toBuild'):
                toBuildLs.append(inst)
        
        return toBuildLs
    
    def baseHierarchy(self):
        geoGrp = cmds.group(name="GEO")
        topNodeGrp = cmds.group(name="guides")
        noTransformGrp = cmds.group(name="NO_TRANSFORM", empty=1)
        skinningGrp = cmds.group(name="SKINNING", empty=1)
        riggingGrp = cmds.group(name="RIGGING", empty=1)
        controlersGrp = cmds.group(name="CONTROLERS", empty=1)

        #Créer C_main/Modifier la couleur de sa shape
        mainCtrl = cmds.circle(name="C_main", normal=(0,1,0), radius=6, constructionHistory=0)
        mainCtrlShape = cmds.listRelatives(mainCtrl, shapes=1)
        cmds.setAttr(mainCtrlShape[0]+".overrideEnabled",1)
        cmds.setAttr(mainCtrlShape[0]+".overrideRGBColors",1)
        cmds.setAttr(mainCtrlShape[0]+".overrideColorR",1)
        cmds.setAttr(mainCtrlShape[0]+".overrideColorG",1)
        cmds.setAttr(mainCtrlShape[0]+".overrideColorB",1)

        #Parentages
        cmds.parent(skinningGrp, riggingGrp, controlersGrp, mainCtrl)
        cmds.parent(mainCtrl, topNodeGrp)
        cmds.parent(noTransformGrp,topNodeGrp)

        #Créer les attributs sur C_main(MESH_LOCK/SKINNING_VISIBILITY/RIGGING_VISIBILITY/CONTROLERS_VISIBILITY/HIDE_ON_PLAYBACK)
        cmds.addAttr(mainCtrl, longName="SKINNING_VISIBILITY", attributeType="bool", defaultValue=1, keyable=1)
        cmds.setAttr(mainCtrl[0]+".SKINNING_VISIBILITY", channelBox=1)

        cmds.addAttr(mainCtrl, longName="RIGGING_VISIBILITY", attributeType="bool", defaultValue=1, keyable=1)
        cmds.setAttr(mainCtrl[0]+".RIGGING_VISIBILITY", channelBox=1)

        cmds.addAttr(mainCtrl, longName="CONTROLERS_VISIBILITY", attributeType="bool", defaultValue=1, keyable=1)
        cmds.setAttr(mainCtrl[0]+".CONTROLERS_VISIBILITY", channelBox=1)

        cmds.addAttr(mainCtrl, longName="HIDE_ON_PLAYBACK", attributeType="bool", keyable=1)
        cmds.setAttr(mainCtrl[0]+".HIDE_ON_PLAYBACK", channelBox=1)

        cmds.addAttr(mainCtrl, longName="MESH_LOCK", attributeType="bool", keyable=1)
        cmds.setAttr(mainCtrl[0]+".MESH_LOCK", channelBox=1)

        #Gestions des attributs du groupe GEO
        cmds.setAttr(geoGrp+".overrideEnabled",1)
        cmds.setAttr(geoGrp+".overrideDisplayType",2)

        #CONNECTIONS
        cmds.connectAttr(mainCtrl[0]+".SKINNING_VISIBILITY" , skinningGrp+".visibility")
        cmds.connectAttr(mainCtrl[0]+".RIGGING_VISIBILITY" , riggingGrp+".visibility")
        cmds.connectAttr(mainCtrl[0]+".CONTROLERS_VISIBILITY" , controlersGrp+".visibility")
        cmds.connectAttr(mainCtrl[0]+".CONTROLERS_VISIBILITY" , noTransformGrp+".visibility")
        cmds.connectAttr(mainCtrl[0]+".MESH_LOCK" , geoGrp+".overrideEnabled")
        cmds.connectAttr(mainCtrl[0]+".HIDE_ON_PLAYBACK", controlersGrp+".hideOnPlayback")
        cmds.connectAttr(mainCtrl[0]+".HIDE_ON_PLAYBACK", noTransformGrp+".hideOnPlayback")

        #Lock and Hide sur les attributs des groupes principaux
        cmds.setAttr(topNodeGrp+".translate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(topNodeGrp+".rotate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(topNodeGrp+".scale", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(topNodeGrp+".visibility", lock=1, keyable=0, channelBox=0)

        cmds.setAttr(geoGrp+".translate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(geoGrp+".rotate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(geoGrp+".scale", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(geoGrp+".visibility", lock=1, keyable=0, channelBox=0)

        cmds.setAttr(noTransformGrp+".translate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(noTransformGrp+".rotate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(noTransformGrp+".scale", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(noTransformGrp+".visibility", lock=1, keyable=0, channelBox=0)

        cmds.setAttr(skinningGrp+".translate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(skinningGrp+".rotate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(skinningGrp+".scale", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(skinningGrp+".visibility", lock=1, keyable=0, channelBox=0)

        cmds.setAttr(riggingGrp+".translate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(riggingGrp+".rotate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(riggingGrp+".scale", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(riggingGrp+".visibility", lock=1, keyable=0, channelBox=0)

        cmds.setAttr(controlersGrp+".translate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(controlersGrp+".rotate", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(controlersGrp+".scale", lock=1, keyable=0, channelBox=0)
        cmds.setAttr(controlersGrp+".visibility", lock=1, keyable=0, channelBox=0)

        #Selection du mainCtrl
        cmds.select(mainCtrl[0])

    def addLabels(self, joints):
        if len(joints) == 0:
            cmds.error('select a joint') 

        for obj in joints:
            if cmds.objectType(obj, i='joint'):
                name = obj.split('_')[1]
                cmds.setAttr(obj+'.drawLabel', 1)
                cmds.setAttr(obj+'.type', 18)
                cmds.setAttr(obj+'.otherType', name, type="string")

    def guideSymetry(self):

        objects = cmds.ls(selection=True, long=True) or []

        toSymList = []
        for obj in objects:
            listParent = cmds.listRelatives(obj, ap=True)
            for parent in listParent:
                if parent.startswith('GDs_'):
                    if not parent.endswith('_Center'):
                        topGuide = parent
                        toSymList.append(topGuide)
                    pass
                else:
                    cmds.warning('No top guide group found')
        

        print(toSymList)
            

