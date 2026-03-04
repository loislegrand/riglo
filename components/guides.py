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

        allInfos = bs.getUIsInfos(UiPart='Limb', printInfos=True)

        #spherePts = shapes.curveParameter(curveType='sphere')

        TopGds = self.hierarchyGuides()
        
        guideArm = cmds.joint(n='GD_shoulder_{}_Left'.format(allInfos[1]))
        guideForearm = cmds.joint(n='GD_elbow_{}_Left'.format(allInfos[1]))
        guideHand = cmds.joint(n='GD_wrist_{}_Left'.format(allInfos[1]))

        cmds.xform(guideArm, t=(20, 165, 0), ro=(0,0,-45))
        cmds.xform(guideForearm, t=(25, 0, -2))
        cmds.xform(guideHand, t=(25, 0, 2))

        self.joint_list.append(guideArm)
        self.joint_list.append(guideForearm)
        self.joint_list.append(guideHand)

        print(guideArm)
        if allInfos[2] == 'Right':
            print(guideArm)
            bs.mirror(symmetry=True, jointChain = guideArm)
        
        return self.joint_list


       
    def loadGuidesQuadLeg(self):

        TopGds = self.hierarchyGuides()

        allInfos = bs.getUIsInfos(UiPart='Limb', printInfos=True)
        
        if allInfos[1] == 'Front':
            reverse = 55
            
        else:
            reverse = 45

        guideArm = cmds.joint(p=(9, 95, 53), n='GD_arm_{}_Left'.format(allInfos[1]))
        guideForearm = cmds.joint(p=(9, 48, reverse), n='GD_forearm_{}_Left'.format(allInfos[1]))
        guideHand = cmds.joint(p=(9, 20, 51), n='GD_hand_{}_Left'.format(allInfos[1]))
        guideHandEnd = cmds.joint(p=(9, 8, 58), n='GD_finger_{}_Left'.format(allInfos[1]))
        guideEnd = cmds.joint(p=(9, 0, 60), n='GD_fingerEnd_{}_Left'.format(allInfos[1]))

        OutNode = cmds.spaceLocator(n='LOC_Out_'+allInfos[1])[0]
        InNode = cmds.spaceLocator(n='LOC_In_'+allInfos[1])[0]
        ToeRoll = cmds.spaceLocator(n='LOC_ToeRoll_'+allInfos[1])[0]
        HeelRoll = cmds.spaceLocator(n='LOC_HeelRoll_'+allInfos[1])[0]
        cmds.parent(OutNode, InNode, ToeRoll, HeelRoll, guideEnd)

        if bs.getUIsInfos()[2] == 'Left':
            PosX = 1
        elif bs.getUIsInfos()[2] == 'Right':
            PosX = -1
        else:
            PosX = 0
            
        cmds.setAttr(OutNode+'.translateX',PosX*8)
        cmds.setAttr(InNode+'.translateX',PosX*-6)
        cmds.setAttr(ToeRoll+'.translateZ',9)
        cmds.setAttr(HeelRoll+'.translateZ',-6)

        self.joint_list.append(guideArm)
        self.joint_list.append(guideForearm)
        self.joint_list.append(guideHand)
        self.joint_list.append(guideHandEnd)
        self.joint_list.append(OutNode)
        self.joint_list.append(InNode)
        self.joint_list.append(ToeRoll)
        self.joint_list.append(HeelRoll)

        if allInfos[2] == 'Right':
            print(guideArm)
            bs.mirror(symmetry=True, jointChain = guideArm)
        
        return self.joint_list

        #select a top bones 
        return self.joint_list
    
    def loadGuidesBiLeg(self):
        TopGds = self.hierarchyGuides()

        allInfos = bs.getUIsInfos(UiPart='Limb', printInfos=True)

        guideUpLeg = cmds.joint(p=(9, 90, 2.5), n='GD_upLeg_{}_Left'.format(allInfos[1]))
        guideLowLeg = cmds.joint(p=(9, 50, 2.5), n='GD_lowLeg_{}_Left'.format(allInfos[1]))
        guideFoot = cmds.joint(p=(9, 10, 0), n='GD_foot_{}_Left'.format(allInfos[1]))
        guideToes = cmds.joint(p=(9, 3, 12), n='GD_toes_{}_Left'.format(allInfos[1]))
        guideToesEnd = cmds.joint(p=(9, 3, 20), n='GD_toesEnd_{}_Left'.format(allInfos[1]))

        self.joint_list.append(guideUpLeg)
        self.joint_list.append(guideLowLeg)
        self.joint_list.append(guideFoot)
        self.joint_list.append(guideToes)

        if allInfos[2] == 'Right':
            print(guideUpLeg)
            bs.mirror(symmetry=True, jointChain = guideUpLeg)
        
        return self.joint_list

    def searchConstruct(self):

        list = cmds.ls('GDs_*')

        toBuildLs = []
        for inst in list:
            if cmds.getAttr(inst + '.toBuild'):
                toBuildLs.append(inst)
        
        return toBuildLs