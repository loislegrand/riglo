'''
Constraint Parent, Point, Orient, Scale
Nodes de Maths
Offest parent


'''

import maya.cmds as cmds

def MayaNodesVersion():
    MVersion = int(cmds.about(v=True))
        
    if MVersion < 2026:
        Old = True
    
    else:
        Old = False
        
    return Old
        
MayaNodesVersion()

def parentCnst(master, childrens=[], off=False, matx=False):

    if len(childrens) == 0:
        cmds.error('You must have child nodes to constraint')

    if master == '':
        cmds.error('You must have parent nodes to constraint')

    if matx == False:
        cmds.parentConstraint(childrens, master, mo=off)

    else:
        print('Idk how to do it yet, it s a WIP')
              
def lineBtw(parentOne, parentTwo):
    #from two string object names
    #create a line attached between to transforms
    CRV = cmds.curve(d=1, p=[(0,0,0), (0,1,0)], n='LinkBtw_' + parentOne + '_' + parentTwo)
    
    #get shape
    shape=cmds.listRelatives(CRV, c=True, s=True)[0]

    #attach to the transforms
    DecMatxOne = cmds.createNode('decomposeMatrix', n='decMatx_'+ parentOne)
    DecMatxTwo = cmds.createNode('decomposeMatrix', n='decMatx_'+ parentTwo)
    cmds.connectAttr(parentOne+'.worldMatrix',DecMatxOne+'.inputMatrix')
    cmds.connectAttr(parentTwo+'.worldMatrix',DecMatxTwo+'.inputMatrix')
    cmds.connectAttr(DecMatxOne + '.outputTranslate', shape  + '.controlPoints[0]', f=True)
    cmds.connectAttr(DecMatxTwo + '.outputTranslate', shape  + '.controlPoints[1]', f=True)

    #reference curve
    cmds.setAttr(shape + ".overrideEnabled",1)
    cmds.setAttr(shape + ".overrideDisplayType", 2)
    
    return CRV

def zeroOut(objects=[]):
    if len(objects) == 0:
        cmds.error('You must have child nodes to constraint')

    for i in objects:
        name = i [4:]
        Prnt = cmds.listRelatives(i, p=True)[0]
        print(name)
        if cmds.objExists('off_'+name) == False:
            Off = cmds.group(em=True, n='off_'+name)
            print('Off')
        elif cmds.objExists('cns_'+name) == False:
            Off = cmds.group(em=True, n='cns_'+name)
            print('cns')
        else:
            cmds.error('Those objects already exists. Stop being dumb.')

        cmds.matchTransform(Off, i)
        cmds.parent(Off, Prnt)
        cmds.parent(i, Off)

def jointOnPoint(objects=[]):
    if len(objects) == 0:
        cmds.error('You must have an object')

def spaceSwitch(master, childrens=[]):
    
    if len(childrens) == 0:
        cmds.error('You must have child nodes to constraint')

    if master == '':
        cmds.error('You must have parent nodes to constraint')