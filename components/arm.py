import maya.cmds as cmds
import math
import RigLo.components.shapes as shapes
import RigLo.basic as base

from importlib import reload
reload(base)


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
        self.base_name = self.part + '_' + self.side


    def CnsType(self, *args):

        mtx_enabled = cmds.checkBox('MtxCns', q=True, v=True)

        print("Matrix constraint enabled:", mtx_enabled)

        if mtx_enabled:
            print("Loading matrix version...")
        else:
            print("Loading native version...")

    def getUIsInfos(self, *args):

        LimbType = cmds.optionMenu('LimbLimbMenu', q=True, v=True)

        Cent = cmds.optionMenu('LimbSide_02', q=True, v=True)

        Lats = cmds.optionMenu('LimbSide_01', q=True, v=True)

        Twist = cmds.checkBox('LimbTwistBox', q=True, v=True)
        Stretch = cmds.checkBox('LimbStretchBox', q=True, v=True)
        Bend = cmds.checkBox('LimbBendBox', q=True, v=True)

        GuideLoader.CnsType(self)

        print('============================================================')

        print('This limb goes is on ' + Lats + ' ' + Cent + LimbType)
        print('Twisties ? : ', Twist)
        print('Strechy ? : ', Stretch)
        print('Bendies ? : ', Bend)

        allInfos = [LimbType, Cent, Lats, Twist, Stretch, Bend]

        return allInfos



# ségmenter le getInfos dans un modules à part 
# faire un setup qui s'active selon le membre avec la récupération des datas

    def loadGuidesArm(self):

        allInfos = self.getUIsInfos()
        print(allInfos)

        spherePts = shapes.curveParameter(curveType='sphere')

        TopGds = cmds.group(em=True, n='GDs_{}_{}_{}'.format(allInfos[0], allInfos[1], allInfos[2]))

        guideShoulder = cmds.curve(p=spherePts, n='GD_shoulder_{}_{}'.format(allInfos[1], allInfos[2]))
        guideElbow = cmds.curve(p=spherePts, n='GD_elbow_{}_{}'.format(allInfos[1], allInfos[2]))
        guideWrist = cmds.curve(p=spherePts, n='GD_wrist_{}_{}'.format(allInfos[1], allInfos[2]))

        base.lineBtw(guideShoulder, guideElbow)
        base.lineBtw(guideElbow, guideWrist)

        cmds.parent(guideShoulder, TopGds) 
        cmds.parent(guideElbow, guideShoulder) 
        cmds.parent(guideWrist, guideElbow)

        cmds.xform(guideShoulder, t=(20, 165, 0), ro=(0,0,-45))
        cmds.xform(guideElbow, t=(25, 0, -2))
        cmds.xform(guideWrist, t=(25, 0, 2))