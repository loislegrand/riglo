import maya.cmds as cmds
import RigLo.basic as bs
from importlib import reload

reload(bs)

def multDL(name):
    if bs.MayaNodesVersion():
        node = cmds.createNode('multDoubleLinear', n= 'multDL_' + name)
    else:
        node = cmds.createNode('multiplyDL', n= 'multDL_' + name)
    
    return node

def additionDL(name):
    if bs.MayaNodesVersion():
        node = cmds.createNode('addDoubleLinear ', n= 'addtDL_' + name)
    else:
        node = cmds.createNode('addDL', n= 'addtDL_' + name)
    
    return node

def pMatMult(name):
    if bs.MayaNodesVersion():
        node = cmds.createNode('pointMatrixMult ', n= 'pMat_' + name)
    else:
        node = cmds.createNode('pointMatrixMultDL', n= 'pMat_' + name)

    return node


'''

https://help.autodesk.com/view/MAYAUL/2026/ENU/?guid=Maya_ReleaseNotes_2026_release_notes_known_limitations2026_html

- addDoubleLinear is now "addDL"

- multiplyDoubleLinear is now "multiplyDL"

- pointMatrixMult is now "pointMatrixMultDL"
'''