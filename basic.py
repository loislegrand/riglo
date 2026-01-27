'''
Constraint Parent, Point, Orient, Scale
Nodes de Maths selon la version de Maya
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
              
def lineBtw(parentOne, parentTwo, selectable=False):
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
    if selectable == False :
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

def IkFkBlend(jntList=[]):

    #idk
    print('toto')
    #Créer le locator de membre
    locator = cmds.spaceLocator(name="GLOBAL_"+jntList[0])
    #Matcher le locator sur le premier joint du membre
    cmds.matchTransform(locator[0], jntList[0])
    #Ajouter un attribut IKFK (0<x<1)
    cmds.addAttr(locator[0], attributeType="float", longName="IKFK", minValue=0, maxValue=1, keyable=1)
    cmds.setAttr(locator[0]+".IKFK", keyable=1)

    #Créer le node reverse
    reverseNode = cmds.createNode("reverse")

    #Connection locator.IKFK > reverse.inputX
    cmds.connectAttr((locator[0]+".IKFK"),(reverseNode+".inputX"))

    #Pour chaque articulation sélectionnée :
    for object in jntList :
        #Créer une contrainte : C_FK(maitre1) / JNT_IK(maitre2) / Articulation(slave)
        pConstraint = cmds.parentConstraint(("C_FK_"+object), ("JNT_IK_"+object), object, maintainOffset=1)
        #Interp Type > "Shortest"
        cmds.setAttr(pConstraint[0]+".interpType", 2)
        #Connection locator.IKFK > contrainte.IK
        cmds.connectAttr((locator[0]+".IKFK"),(pConstraint[0]+".JNT_IK_"+object+"W1"))
        #Connection reverse.outputX > contrainte.FK
        cmds.connectAttr((reverseNode+".outputX"),(pConstraint[0]+".C_FK_"+object+"W0"))

    #Parentages : "JNT_IK_" fils de locator GLOBAL / Locator GLOBAL fils de "RIGGING" 
    cmds.parent("JNT_IK_"+selList[0], locator[0])

    #Selection du locator GLOBAL
    cmds.select(locator[0])