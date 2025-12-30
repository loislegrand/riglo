# ============================================================
#  CLE Add Skin Layer  (Python conversion of MEL version)
#  Original MEL: Cédric Lenhardt
#  Vérifié pour Maya 2024
#  Update du 2025-11-08 par Loïs Legrand
# ============================================================

import maya.cmds as cmds

# ------------------------------------------------------------
#  Utility: compute bounding-box size
# ------------------------------------------------------------

def CLE_size(sel, axis):
    dup = cmds.duplicate(sel)[0]
    grp = cmds.group(dup)
    bb = cmds.xform(grp, q=True, r=True, boundingBox=True)
    cmds.delete(grp)

    sx = bb[3] - bb[0]
    sy = bb[4] - bb[1]
    sz = bb[5] - bb[2]

    if axis == "x":
        return sx
    if axis == "y":
        return sy
    if axis == "z":
        return sz
    return 0


# ============================================================
#  UI Helpers
# ============================================================

def CLE_selectBaseDoritoMesh(*args):
    sel = cmds.filterExpand(sm=12) or []
    if len(sel) == 0:
        cmds.error("!!! Can't build templates. No mesh selected !!!")
    if len(sel) > 1:
        cmds.error("!!! Select only one mesh !!!")

    cmds.textField("baseMeshField", e=True, text=sel[0])


def CLE_addSkinLayerInfoUI(*args):
    win = "CLE_addSkinLayerInfoUI"
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, t="About CLE Add Skin Layer", w=250, h=150, s=True)
    cmds.columnLayout(co=('both', 20), rs=5)

    cmds.separator(h=10)
    cmds.text(al="left", l="This tool reproduces the Softimage Dorito concept.")
    cmds.text(al="left", l="It adds joints on a base mesh that follow deformations.")
    cmds.text(al="left", l="Base mesh is duplicated into a Skin Layer.")
    cmds.text(al="left", l="Paint weights on the new mesh to adjust controller effects.")
    cmds.text(al="left", l="!!! UVs must be unfolded on the base mesh !!!")
    cmds.text(al="left", l="More info on cedriclenhardt.com")
    cmds.separator(h=10)
    cmds.text(al="right",
              l="MEL script by Cédric Lenhardt // Python port")
    cmds.showWindow(win)


# ============================================================
# UI Main
# ============================================================

def CLE_addSkinLayer(*args):
    win = "CLE_addSkinLayerUI"
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, t="CLE Add Skin Layer", w=250, h=150, s=True)
    cmds.menuBarLayout()
    cmds.menu(label="Help")
    cmds.menuItem(label="Reset", c=CLE_addSkinLayer)
    cmds.menuItem(label="About", c=CLE_addSkinLayerInfoUI)

    cmds.columnLayout(co=('both', 5), rs=5)

    cmds.separator(h=2)
    cmds.frameLayout("Create Skin Layer", cll=True, cl=False, mw=10, mh=10)
    cmds.rowColumnLayout(nc=2, cw=[(1,175),(2,159)], co=[(1,"right",3)], rs=[(1,7)])

    cmds.textField("baseMeshField", w=170)
    cmds.button("selectBaseMeshButton", w=159, l="<<< Select Base Mesh",
                c=CLE_selectBaseDoritoMesh)

    cmds.setParent("..")
    cmds.button(w=335, h=30, bgc=(.25,.3,.25),
                l="Build Controllers Templates",
                c=CLE_buildDoritoTemplates)

    cmds.button(w=335, h=30, bgc=(.3,.4,.3),
                l="Create Controllers From Templates",
                c=CLE_buildDoritoSystems)
    cmds.setParent("..")

    cmds.separator(h=2)

    cmds.frameLayout("Nomenclature", cll=True, cl=True, mw=10, mh=10)
    cmds.rowColumnLayout(nc=2, cw=[(1,110),(2,220)], co=[(1,"right",3)])

    cmds.text(al="right", l="Prefix Root")
    cmds.textField("PrefixRootField", text="R_")
    cmds.text(al="right", l="Prefix Skin")
    cmds.textField("PrefixSkinField", text="sk_")
    cmds.text(al="right", l="Prefix Controllers")
    cmds.textField("PrefixControlersField", text="C_")

    cmds.setParent("..")
    cmds.setParent("..")

    cmds.showWindow(win)


# ============================================================
# STEP 1 — Build Templates
# ============================================================

def CLE_buildDoritoTemplates(*args):

    meshBase = cmds.textField("baseMeshField", q=True, text=True)
    if not cmds.objExists(meshBase):
        cmds.error("// No base mesh selected! //")

    sel = cmds.filterExpand(sm=31) or []
    if not sel:
        cmds.error("// Select vertices first! //")

    # check vertices belong to meshBase
    if sel[0].split('.')[0] != meshBase:
        cmds.error("// Selected vertices must belong to Base Mesh! //")

    # find or create skinLayer mesh
    attrs = cmds.listAttr(meshBase, st="layerDorito") or []
    if attrs:
        meshDorito = cmds.getAttr(meshBase + ".layerDorito")
    else:
        meshDorito = cmds.duplicate(meshBase, n=meshBase + "_skinLayer1")[0]
        cmds.addAttr(meshBase, ln="layerDorito", dt="string")
        cmds.setAttr(meshBase + ".layerDorito", meshDorito, type="string")
        cmds.connectAttr(meshBase + ".outMesh", meshDorito + ".inMesh")

    size = CLE_size(meshBase, "y")

    # create template controllers
    for vtx in sel:

        jnt = cmds.createNode("joint")
        root = cmds.group(jnt)

        cmds.setAttr(jnt + ".radius", 0)
        cmds.setAttr(jnt + ".drawStyle", 2)

        cmds.select(vtx, root)
        cmds.pointOnPolyConstraint()

        cmds.addAttr(jnt, ln="layerDorito", dt="string")
        cmds.connectAttr(meshBase + ".layerDorito", jnt + ".layerDorito")

        # circles
        shapes = []
        for nr in [(1,0,0),(0,1,0),(0,0,1)]:
            circle = cmds.circle(ch=False, o=True, nr=nr, r=size*0.03, s=6)[0]
            shp = cmds.listRelatives(circle, s=True)[0]
            cmds.parent(shp, jnt, r=True, s=True)
            cmds.setAttr(shp + ".overrideEnabled", 1)
            cmds.setAttr(shp + ".overrideColor", 13)
            cmds.delete(circle)
            shapes.append(shp)


# ============================================================
# STEP 2 — Build Final Dorito Controllers
# ============================================================

def CLE_buildDoritoSystems(*args):

    meshBase = cmds.textField("baseMeshField", q=True, text=True)
    if not cmds.objExists(meshBase):
        cmds.error("// No base mesh selected! //")

    attrs = cmds.listAttr(meshBase, st="layerDorito") or []
    if not attrs:
        cmds.error("// No dorito layer found. Create templates first. //")

    meshDorito = cmds.getAttr(meshBase + ".layerDorito")

    joints = cmds.listConnections(meshBase + ".layerDorito") or []
    if not joints:
        cmds.error("// No templates found! //")

    skinPrefix = cmds.textField("PrefixSkinField", q=True, text=True)
    rootPrefix = cmds.textField("PrefixRootField", q=True, text=True)
    ctrlPrefix = cmds.textField("PrefixControlersField", q=True, text=True)

    # freeze transforms of roots + joints
    for j in joints:
        root = cmds.listRelatives(j, p=True)[0]
        cmds.makeIdentity(j, a=True, s=True)
        cmds.makeIdentity(root, a=True, s=True)

    # check/create skinCluster
    skinCl = cmds.listConnections(meshDorito + ".inMesh",
                                  s=True, d=False, t="skinCluster") or []

    if skinCl:
        sc = skinCl[0]
        for j in joints:
            cmds.skinCluster(sc, e=True, ai=j, lw=False, wt=False)
    else:
        zeroJnt = cmds.joint(n=skinPrefix + "zeroInfluence_controlerLayer")
        sc = cmds.skinCluster(joints + [zeroJnt], meshDorito, tsb=True)[0]

    # finalize each controller
    for j in joints:
        root = cmds.listRelatives(j, p=True)[0]
        constraint = cmds.listRelatives(root, c=True, type="pointOnPolyConstraint")[0]
        shapes = cmds.listRelatives(j, s=True)

        # matrix connection extraction
        mat = cmds.listConnections(j + ".worldMatrix[0]", p=True, d=True, s=False)[0]
        idx = mat.split("bindPreMatrix")[1]  # unique id

        cmds.connectAttr(root + ".worldInverseMatrix[0]",
                         sc + ".bindPreMatrix" + idx,
                         f=True)

        cmds.disconnectAttr(meshBase + ".layerDorito", j + ".layerDorito")
        cmds.deleteAttr(j + ".layerDorito")

        cmds.rename(root, rootPrefix + j)
        newJ = cmds.rename(j, ctrlPrefix + skinPrefix + j)

        cmds.rename(constraint, newJ + "_pointOnPolyConstraint1")

        # rename shapes
        for i, shp in enumerate(shapes, 1):
            cmds.rename(shp, newJ + "Shape" + str(i))

    print(" ---> Controllers created ! <---")

