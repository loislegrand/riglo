'''
Constraint Parent, Point, Orient, Scale
Nodes de Maths selon la version de Maya
Offest parent


'''

import maya.cmds as cmds
import RigLo.components.shapes as shapes
from importlib import reload

reload(shapes)


def MayaNodesVersion():
    MVersion = int(cmds.about(v=True))
        
    if MVersion < 2026:
        Old = True
    
    else:
        Old = False
        
    return Old


def parentCnst(masters, children, off=False, matx=False):

    if len(masters) == 0:
        cmds.error('You must have parent nodes to constraint')

    if children == '':
        cmds.error('You must have child node to constraint')

    if matx == False:
        cstrnt = cmds.parentConstraint(masters, children, mo=off)

    else:
        print('Idk how to do it yet, it s a WIP')

    return cstrnt

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
        if cmds.objExists('off_'+name) == False:
            Off = cmds.group(em=True, n='off_'+name)
        elif cmds.objExists('cns_'+name) == False:
            Off = cmds.group(em=True, n='cns_'+name)
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

    #Créer le locator de membre
    locator = cmds.spaceLocator(name="GLOBAL_"+jntList[0])
    #Matcher le locator sur le premier joint du membre
    cmds.matchTransform(locator[0], jntList[0])
    #Ajouter un attribut IKFK (0<x<1)
    cmds.addAttr(locator[0], ln="ParameterIkFk", nn="_____", at="enum", en="_____")
    cmds.addAttr(locator[0], attributeType="float", longName="IkFk", minValue=0, maxValue=1, keyable=1)
    cmds.setAttr(locator[0]+".IkFk", keyable=1)

    #Créer le node reverse
    reverseNode = cmds.createNode("reverse", n='rev_'+jntList[0])

    #Connection locator.IKFK > reverse.inputX
    cmds.connectAttr((locator[0]+".IkFk"),(reverseNode+".inputX"))

    #Pour chaque articulation sélectionnée :
    for object in jntList :
        #Créer une contrainte : C_FK(maitre1) / JNT_IK(maitre2) / Articulation(slave)
        pConstraint = cmds.parentConstraint(("C_Fk_"+object), ("JNT_Ik_"+object), object, maintainOffset=1)
        #Interp Type > "Shortest"
        cmds.setAttr(pConstraint[0]+".interpType", 2)
        #Connection locator.IKFK > contrainte.IK
        cmds.connectAttr((locator[0]+".IkFk"),(pConstraint[0]+".JNT_Ik_"+object+"W1"))
        #Connection reverse.outputX > contrainte.FK
        cmds.connectAttr((reverseNode+".outputX"),(pConstraint[0]+".C_Fk_"+object+"W0"))

    #Parentages : "JNT_IK_" fils de locator GLOBAL / Locator GLOBAL fils de "RIGGING" 
    cmds.parent("JNT_Ik_"+jntList[0], locator[0])

    #Selection du locator GLOBAL
    cmds.select(locator[0])

    return locator


def getUIsInfos(UiPart='', printInfos=False):

        LimbType = cmds.optionMenu(UiPart+'LimbMenu', q=True, v=True)

        Cent = cmds.optionMenu(UiPart+'Side_02', q=True, v=True)

        Lats = cmds.optionMenu(UiPart+'Side_01', q=True, v=True)

        Twist = cmds.checkBox(UiPart+'TwistBox', q=True, v=True)
        Stretch = cmds.checkBox(UiPart+'StretchBox', q=True, v=True)
        Bend = cmds.checkBox(UiPart+'BendBox', q=True, v=True)

        if printInfos == True:
            print('============================================================')

            print('This ' + LimbType + ' goes on ' + Lats + ' ' + Cent )
            print('Twisties ? : ', Twist)
            print('Strechy ? : ', Stretch)
            print('Bendies ? : ', Bend)

        allInfos = [LimbType, Cent, Lats, Twist, Stretch, Bend]

        return allInfos


def mirror(symmetry=False, jointChain = ''):
    
    cmds.select(jointChain)
    cmds.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, searchReplace=( "_Left", "_Right"))
    

    if symmetry == True:
        cmds.delete(jointChain)


def jntOrient(lat='', jntList=[]):
    if len(jntList) == 0:
        jntList = cmds.ls(sl=True)

    if lat == '':
        if cmds.getAttr(jntList[0]+'.translateX')<0:
            lat='Right'
        else:
            lat='Left'

    reference = cmds.group(em=True)

    for jnt in jntList[:-1]:
        cmds.select(jnt)
        cmds.FreezeTransformations()
        cmds.joint(jnt, edit=True, oj='xzy', secondaryAxisOrient='zup')

        if lat == 'Right':
            value = cmds.getAttr(jnt+'.jointOrientY')
            value += 180
            cmds.setAttr(jnt+'.jointOrientY', value)
            
            cmds.matchTransform(child, reference, pos=True, rot=False)

            child = cmds.listRelatives(jnt, children=True)
            cmds.matchTransform(reference, child)

    cmds.FreezeTransformations(jntList[-1:][0])
    cmds.setAttr(jntList[-1:][0] + '.jointOrientX', 0)
    cmds.setAttr(jntList[-1:][0] + '.jointOrientY', 0)
    cmds.setAttr(jntList[-1:][0] + '.jointOrientZ', 0)

    cmds.delete(reference)


def controllers(jntList=[], ctrlShape='stCircle', name='C_'):

    if len(jntList) == 0:
        jntList = cmds.ls(selection=True)
        if len(jntList) == 0:
            cmds.error('select at least one joint.')
    else:
        pass


    # Checker si des joints sont selectionnes
    """for t in jntList:
        type=cmds.objectType(t)
        if type == 'joint':
            pass
        else:
            cmds.error('select joint object.')"""

    ctlGrp = []
    # Pour chaque joint selectionné :
    for i in jntList:
        #Créer un nurbsCircle(axeX)
        if cmds.objectType(i) == 'joint':
            radius=cmds.getAttr(i+'.radius')
        else:
            radius = 1
        ctrl=shapes.shapeMkr(curveType=ctrlShape,name=name+i)

        shape=cmds.listRelatives(ctrl,shapes=True)
        shape=cmds.listRelatives(ctrl,shapes=True)
        
        cmds.setAttr(shape[0]+'.overrideEnabled', 1)
        
        cmds.setAttr(shape[0]+'.overrideRGBColors', 1)
        
        #Créer le groupe de placement
        groupe=cmds.group(ctrl,n='GRP_'+i)
        #DeleteHistory (chercher dans la commande du nurbsCicle)    
        #MatchTransform du groupe de placement sur le joint
        cmds.matchTransform(groupe,i)
        RorL=cmds.getAttr(groupe+'.translateX')
        
        if RorL > 0.1:
            cmds.setAttr(shape[0]+'.overrideColorR',0.286)
            cmds.setAttr(shape[0]+'.overrideColorG',0.627)
            cmds.setAttr(shape[0]+'.overrideColorB',0.380)
        elif RorL < -0.1:
            cmds.setAttr(shape[0]+'.overrideColorR',0.247)
            cmds.setAttr(shape[0]+'.overrideColorG',0.569)
            cmds.setAttr(shape[0]+'.overrideColorB',0.557)
        else:
            cmds.setAttr(shape[0]+'.overrideColorR',1)
            cmds.setAttr(shape[0]+'.overrideColorG',1)
            cmds.setAttr(shape[0]+'.overrideColorB',0)
        
        ctlGrp.append(ctrl)
    
    return ctlGrp


def duplicate(objList = []):
    
    if len(objList) == 0:
        objList = cmds.ls(selection=True, long=True) or []

    dupChain = []
    prnt = cmds.spaceLocator(n='LOC_' + objList[0])
    for obj in objList:
        cmds.select(obj)
        duplicata = cmds.duplicate(po=True)[0]
        dupChain.append(duplicata)
        cmds.parent(duplicata, prnt)
        prnt = duplicata
        
    return dupChain


def BRA_rotatePlane(pointA, pointB, pointC) :
    
    # Si le groupe "PREVIZ" n'existe pas, le créer
    totalPreviz = "PREVIZ"  
    if not cmds.ls(totalPreviz) :
        totalPreviz = cmds.group(name= totalPreviz, empty=1)
    
    # Création du locator de previz et de son groupe de placement
    locPreviz = cmds.spaceLocator(name="PV_Previz_"+pointB)
    grpPreviz = cmds.group(locPreviz[0], name="GRP_Previz_"+pointB)

    # Création du plan de previz
    planePreviz = cmds.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)], constructionHistory=0, name="RP_Previz_"+pointB)
    planeShape = cmds.listRelatives(planePreviz[0], shapes=1)
    cmds.setAttr(planeShape[0]+".overrideEnabled", 1)
    cmds.setAttr(planeShape[0]+".overrideColor", 14)
    
    # Rangement
    cmds.parent(grpPreviz, planePreviz, totalPreviz)
    
    # Création des nodes
    aimMatrixNode = cmds.createNode("aimMatrix")
    cmds.setAttr(aimMatrixNode+".secondaryMode",1)
    
    distanceNode = cmds.createNode("distanceBetween")
    
    multNodeX = cmds.createNode("multDoubleLinear")
    cmds.setAttr(multNodeX+".input2",0.5)
    
    multNodeZ = cmds.createNode("multDoubleLinear")
    cmds.setAttr(multNodeZ+".input2",0.75)
        
    decomposeMatrixA = cmds.createNode("decomposeMatrix")
    decomposeMatrixB = cmds.createNode("decomposeMatrix")
    decomposeMatrixC = cmds.createNode("decomposeMatrix")
    
    # Connections
    cmds.connectAttr(pointA+".worldMatrix[0]", aimMatrixNode+".inputMatrix")
    cmds.connectAttr(pointB+".worldMatrix[0]", aimMatrixNode+".secondaryTargetMatrix")
    cmds.connectAttr(pointC+".worldMatrix[0]", aimMatrixNode+".primaryTargetMatrix")
    cmds.connectAttr(aimMatrixNode+".outputMatrix", grpPreviz+".offsetParentMatrix")
    cmds.connectAttr(pointA+".worldMatrix[0]", distanceNode+".inMatrix1")
    cmds.connectAttr(pointC+".worldMatrix[0]", distanceNode+".inMatrix2")
    cmds.connectAttr(distanceNode+".distance", multNodeX+".input1")
    cmds.connectAttr(multNodeX+".output", locPreviz[0]+".translateX")
    cmds.connectAttr(distanceNode+".distance", multNodeZ+".input1")
    cmds.connectAttr(multNodeZ+".output", locPreviz[0]+".translateY")
    cmds.connectAttr(pointA+".worldMatrix[0]", decomposeMatrixA+".inputMatrix")
    cmds.connectAttr(locPreviz[0]+".worldMatrix[0]", decomposeMatrixB+".inputMatrix")
    cmds.connectAttr(pointC+".worldMatrix[0]", decomposeMatrixC+".inputMatrix")
    cmds.connectAttr(decomposeMatrixA+".outputTranslate", planeShape[0]+".controlPoints[0]")
    cmds.connectAttr(decomposeMatrixB+".outputTranslate", planeShape[0]+".controlPoints[1]")
    cmds.connectAttr(decomposeMatrixC+".outputTranslate", planeShape[0]+".controlPoints[2]")
    
    # Paramétrage du look du Locator
    locShape = cmds.listRelatives(locPreviz[0], shapes=1)
    locSize = cmds.getAttr(distanceNode+".distance")/20
    cmds.setAttr(locShape[0]+".localScale", locSize, locSize, locSize)
    cmds.setAttr(locShape[0]+".overrideEnabled", 1)
    cmds.setAttr(locShape[0]+".overrideColor", 14)
    
    # Lock Channels
    for obj in [planePreviz[0], locPreviz[0], grpPreviz] :
        cmds.setAttr(obj+".translate", lock=1)
        cmds.setAttr(obj+".rotate", lock=1)
        cmds.setAttr(obj+".scale", lock=1)
    
    # Selection (et Return) du Locator de Previz / Print de confirmation
    cmds.select(locPreviz[0])
    return locPreviz[0], planePreviz[0]
    print("---> Previz Rotate Plane created between "+pointA+", "+pointB+", "+pointC+"<---")


def BRA_rotatePlaneSelection() :
    
    # Definir les trois points via la selection
    selList = cmds.ls(sl=1)
    if len(selList) != 3 :
        cmds.error("!!! Please select 3 transforms in the right order to preview the Rotate Plane !!!")
    
    BRA_rotatePlane(selList[0], selList[1], selList[2])


def listExtraAttr(obj):
    attrs = cmds.listAttr(obj,ud= True)

    niceNameList = {}
    for a in attrs:
        l = cmds.attributeName("{0}.{1}".format(obj, a), l= True)
        n= cmds.attributeName("{0}.{1}".format(obj, a), n= True)
        niceNameList[l] = n  

    return niceNameList

# converted script from mel to python, and adapted for stand alone use
# Michael B. Comet - comet@comet-cartoons.com
# Copyright ©2003 Michael B. Comet - All Rights Reserved.

def stringReplace(s, search, replace):
    
    if search == "" or s == "":
        return s

    ret = []
    i = 0
    len_s = len(search)
    len_str = len(s)

    while i < len_str:
        # if the substring from i matches search, append replacement and skip
        if i + len_s <= len_str and s[i:i+len_s] == search:
            ret.append(replace)
            i += len_s
        else:
            ret.append(s[i])
            i += 1

    return "".join(ret)


def getShortName(obj):
    """
    Given a DAG path (may contain '|'), return the short name (after last '|').
    """
    if not obj:
        return ""
    parts = obj.split("|")
    return parts[-1] if parts else obj


def chop(s):
    """
    Remove last character from string (returns empty string if length <= 1).
    """
    if not s or len(s) <= 1:
        return ""
    return s[:-1]


def doRename(mode, objs=[], search='', replace='', prefix='', suffix='', rename_base='', start=1, padding=0):
    """
    Do rename ops on selected objects.
    mode: 0 = Search & Replace
          1 = Add Prefix
          2 = Add Suffix
          3 = Rename & Number
    """

    if len(objs) == 0:
        objs = cmds.ls(selection=True, long=True) or []
        
    objCnt = len(objs)

    # replaced UI filed by function parameter :
    """search = cmds.textField('tfSearch', q=True, text=True) if cmds.textField('tfSearch', q=True, exists=True) else ""
    replace = cmds.textField('tfReplace', q=True, text=True) if cmds.textField('tfReplace', q=True, exists=True) else ""
    prefix = cmds.textField('tfPrefix', q=True, text=True) if cmds.textField('tfPrefix', q=True, exists=True) else ""
    suffix = cmds.textField('tfSuffix', q=True, text=True) if cmds.textField('tfSuffix', q=True, exists=True) else ""
    rename_base = cmds.textField('tfRename', q=True, text=True) if cmds.textField('tfRename', q=True, exists=True) else ""
    start = cmds.intField('ifNumber', q=True, value=True) if cmds.intField('ifNumber', q=True, exists=True) else 1
    padding = cmds.intField('ifPadding', q=True, value=True) if cmds.intField('ifPadding', q=True, exists=True) else 0
    """

    if objCnt == 0:
        cmds.warning("No objects selected.")
        return

    # Work through objects (note: objs contains long names)
    for i in range(objCnt):
        obj = objs[i]
        shortName = getShortName(obj)

        # compute new short name depending on mode
        if mode == 0:  # Search & Replace
            if search == "":
                cmds.warning("Can't search and replace, search entry field is blank!")
                return
            newShortName = stringReplace(shortName, search, replace)

        elif mode == 1:  # Prefix
            if prefix == "":
                cmds.warning("Can't add prefix, prefix entry field is blank!")
                return
            newShortName = prefix + shortName

        elif mode == 2:  # Suffix
            if suffix == "":
                cmds.warning("Can't add suffix, suffix entry field is blank!")
                return
            newShortName = shortName + suffix

        elif mode == 3:  # Rename & Number
            if rename_base == "":
                cmds.warning("Can't rename and number, rename entry field is blank!")
                return
            n = i + start
            # format number with zero padding if requested
            if padding and padding > 0:
                numStr = str(n).zfill(padding)
            else:
                numStr = str(n)
            newShortName = rename_base + numStr

        else:
            cmds.warning("Unknown mode: %s" % str(mode))
            return

        # Perform rename. cmds.rename returns the new (possibly short) name.
        try:
            newName = cmds.rename(obj, newShortName)
        except Exception as e:
            cmds.warning("Failed to rename '%s' -> '%s' : %s" % (obj, newShortName, e))
            continue

        # select to get the full long path of the renamed object
        cmds.select(newName, replace=True)
        newLongNames = cmds.ls(selection=True, long=True) or []
        newLongName = newLongNames[0] if newLongNames else newName

        # Update the stored list of objects so subsequent renames that reference
        # other objects in the list keep correct full names
        for j in range(objCnt):
            tmp = objs[j] + "|"  # append '|' like original MEL to make replace unique
            # replace occurrences of the old long name + '|' with '|' + newLongName + '|'
            tmp = tmp.replace(obj + "|", "|" + newLongName + "|")
            tmp = chop(tmp)
            objs[j] = tmp

    # reselect final set
    try:
        cmds.select(objs, replace=True)
    except Exception:
        # fallback: select none if error
        cmds.select(clear=True)
    
    finalNames = []
    for obj in objs:
        tmp = getShortName(obj)
        finalNames.append(tmp)

    return finalNames

