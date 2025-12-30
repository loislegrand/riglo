import maya.cmds as cmds
import maya.mel as mel
import os

attributes = ['translateX', 'translateY', 'translateZ']
end = cmds.playbackOptions(query=True, aet=True)  # get animation end time
end -= 1
endLoop = end-1

def direction(*args):
    #gestion des nomenclature, je recup le chemin du fichier et construit un chemin avec
    currentPath = cmds.file(query=1, expandName=1)
    currentPathList = currentPath.split("/")
    varName = currentPathList[len(currentPathList)-1]
    inputName = cmds.textField('textBoxName', q=1, tx=1)
    customPth = ''
    for i in range(len(currentPathList[:6])):
        customPth = customPth + currentPathList[i] + '/'
    customPth += 'published/fbx/' + inputName
    return(customPth)

#Changer les valeurs des courbes
def transCrv(*args):
    for attr in attributes :
        value= cmds.getAttr("CC_Base_Hip."+attr, time=end) - cmds.getAttr("CC_Base_Hip."+attr, time=0)
        print(attr)
        cmds.keyframe('CC_Base_Hip.'+attr, time=(0,endLoop), e = True, iub = True, r= True, o='over', vc = value)
        if attr == 'translateY':
            attr = 'translateZ'
            value *= -1
        elif attr == 'translateZ':
            attr = 'translateY'
        cmds.keyframe('cut0_main.'+attr, time=(0,endLoop), e = True, iub = True, r= True, o='over', vc = value)
        
    cmds.keyframe('CC_Base_BoneRoot.rotateX', e = True, iub = True, r= True, o='over', vc = 90)
    cmds.keyframe('ActorFBX*.rotateX', e = True, iub = True, r= True, o='over', vc = -90)
    
    direction()

def exportFbx(*args):
    MakeFolder()
    cmds.select(cl=True)
    
    list = cmds.listRelatives('ActorFBXASC*',ad=True, type='joint')
    cmds.select('ActorFBXASC*')
    for object in list:
        cmds.select(object, add=True)
        

    inputName = cmds.textField('textBoxName', q=1, tx=1)
    customPth = cmds.textField('textBoxPath', q=1, tx=1)
    mainpath = customPth + "/" + inputName + ".fbx"
    print(customPth)
    print(inputName)
    print(mainpath)
    
    mel.eval('FBXExportAnimationOnly -q')
    mel.eval( 'FBXExport -f "{0}" -s'.format(mainpath) )
    
    cmds.select('cut0_main')
    mainpath = customPth + "/Cam_" + inputName + ".fbx"
    
    mel.eval( 'FBXExport -f "{0}" -s'.format(mainpath) )
    
    cmds.warning("C'est cool, {0} a été créé".format(inputName))

def make_dir(path):
    """
    input a path to check if it exists, if not, it creates all the path
    :return: path string
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def MakeFolder(*args):
    userInput = cmds.textField('textBoxPath', q=1, tx=1)
    path = make_dir(userInput)
    print('{0} has been created'.format(path))
    
def changeTextField(*args):
    newPath = direction()
    cmds.textField('textBoxPath', edit=True, tx=newPath)
    
def inPlace(*args):
    end = cmds.playbackOptions(query=True, aet=True)
            
    if cmds.checkBox('static', q=True, v=True) == 1:
        inPlace.valuesTx=[]
        inPlace.valuesTy=[]
        for i in range(int(end)):
            cmds.currentTime(i)
            Tx = cmds.getAttr('CC_Base_Hip.translateX')
            inPlace.valuesTx.append(Tx)
            Ty = cmds.getAttr('CC_Base_Hip.translateY')
            inPlace.valuesTy.append(Ty)
            
            cmds.setAttr('CC_Base_Hip.translateX',0)
            cmds.setAttr('CC_Base_Hip.translateY',0)
            
        print('prout')
        print(inPlace.valuesTx)
        print(inPlace.valuesTy)
    else:
        print('tqt')
        print(inPlace.valuesTx)
        print(inPlace.valuesTy)
        for i in range(int(end)):
            cmds.currentTime(i)
            cmds.setAttr('CC_Base_Hip.translateX',inPlace.valuesTx[i])
            cmds.setAttr('CC_Base_Hip.translateY',inPlace.valuesTy[i])
            
