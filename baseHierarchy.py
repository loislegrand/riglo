import maya.cmds as cmds

def hierarchy(assetName):

    #Créer les groupes SKINNING / RIGGING / CONTROLERS / GEO / TOPNODE / NO_TRANFSORMS
    geoGrp = cmds.group(name="GEO")
    topNodeGrp = cmds.group(name=assetName)
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
