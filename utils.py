"""
quick, click-thru
tree creation for games. slightly low-poly anyway.
"""

from random import uniform, randint, choice, seed, gauss

viewing_presets = {
"bevel": True,
"do_update": True,
"showLeaves": False,
"useArm": False,
}

preferences = {
"scale": 10.,
"scaleV": 0.,
"customShape": (0.5, 1, 0.3, 0.5),
"nrings": 0,
"closeTip": False,
"autoTaper": True,
"splitByLen": True,
}

wind = {
"wind": 0.35,
"armLevels": 2  #1
}

export_presets = {
"showLeaves": True,
"useArm": True,
"makeMesh": False,
"armAnim": True,
"frameRate": 30,
"loopFrames": 60
}

lowpoly_presets = {
"handleType": "0",  # Auto (not Vector)
"bevelRes": 1,  # Bevel Resolution
"resU": 2,  # Curve Resolution
"levels": 3,
"curveRes": [3, 4, 3, 1],
}

leaves = {
"leafShape": "rect",
"leafDist": ("6", "4", "10"),  # shapeList4
"leaves": (8, 14),
"leafScale": (0.8, 1.13),
}

"""
######## Very coarse randomization
"""

very_coarse_randomize = {
"shape": ("0", "1", "2", "3", "4", "5", "6", "7", "10"),  # whole tree. shapeList3
"shapeS": "4",  # secondary branches shape. shapeList4
"branches": [0, (5, 30), (5, 22), 0],
"baseSplits": (0, 1),
"baseSize": (0.1, 0.55),
"baseSize_s": (0.2, 1.),
"ratio": (0.009, 0.014),
"downAngle": [90., (55., 130.), (45., 110.), 45.],
}

def very_coarse_rules(vc):
    #is baseSize high, let baseSize_s be under 0.6
    if vc["baseSize"] > 0.35:
        vc["baseSize_s"] = rnd((0.2, 0.6))
    #avoid secondary branches growing towards stem
    if vc["downAngle"][1] > 90.:
        vc["downAngle"][2] = rnd((45., 90.))
    return vc

"""
######## Coarse randomization
"""

coarse_randomize = {
"leafDist": "6",  # leaf distribution. shapeList4
"rootFlare": (1.0, 1.8),
"rMode": ("rotate", "original", "random"),
"nSegSplits": [0., (0., 0.6), (0., 0.6), 0.],
"length": [1., (0.3, 0.5), (0.5, 0.6), 0.45],  # default [1., 0.3, 0.6, 0.45]
}

def coarse_rules(c):
    return c

"""
######## Odd branch
"""
quirk_randomize = {
"lengthV": [0., (0.4, 0.8), 0., 0.]
}

def quirk_rules(q):
    return q

"""
######## Utilities
"""
def rand_dict(d):
    return {k: randomize(v) for k, v in d.items()}

def randomize(var):
    seed()
    #a parameter
    #may be string, so a single one is iterable
    if isinstance(var, list):
        return list(map(rnd, var))
    else:
        return rnd(var)

def rnd(var):
    # a single value
    if isinstance(var, (float, int, str, bool)):
        return var
    else:  # randomize tuple
        if not isinstance(var, tuple):
            print("rnd failure, no tuple")
        if isinstance(var[0], float):
            return uniform(*var)
        elif isinstance(var[0], int):
            return randint(*var)
        else:  # string
            return choice(var)

def merge_dicts(*dicts):
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged

shapeList3 = [('0', 'Conical', ''),
            ('6', 'Inverse Conical', ''),
            ('1', 'Spherical', ''),
            ('2', 'Hemispherical', ''),
            ('3', 'Cylindrical', ''),
            ('4', 'Tapered Cylindrical', ''),
            ('10', 'Inverse Tapered Cylindrical', ''),
            ('5', 'Flame', ''),
            ('7', 'Tend Flame', ''),
            ('8', 'Custom Shape', '')]

shapeList4 = [('0', 'Conical', ''),
            ('6', 'Inverse Conical', ''),
            ('1', 'Spherical', ''),
            ('2', 'Hemispherical', ''),
            ('3', 'Cylindrical', ''),
            ('4', 'Tapered Cylindrical', ''),
            ('10', 'Inverse Tapered Cylindrical', ''),
            ('5', 'Flame', ''),
            ('7', 'Tend Flame', '')]

#bpy.ops.curve.tree_add(do_update=True, bevel=False, prune=False, showLeaves=False, useArm=False, seed=0, handleType='0', levels=2, length=(1, 0.3, 0.6, 0.45), lengthV=(0, 0, 0, 0), taperCrown=0, branches=(0, 50, 30, 10), curveRes=(8, 5, 3, 1), curve=(0, -40, -40, 0), curveV=(20, 50, 75, 0), curveBack=(0, 0, 0, 0), baseSplits=0, segSplits=(0, 0, 0, 0), splitByLen=True, rMode='rotate', splitAngle=(0, 0, 0, 0), splitAngleV=(0, 0, 0, 0), scale=13, scaleV=3, attractUp=(0, 0, 0.5, 0.5), attractOut=(0, 0, 0, 0), shape='7', shapeS='4', customShape=(0.5, 1, 0.3, 0.5), branchDist=1, nrings=0, baseSize=0.4, baseSize_s=0.25, splitHeight=0.2, splitBias=0, ratio=0.015, minRadius=0.0015, closeTip=False, rootFlare=1, autoTaper=True, taper=(1, 1, 1, 1), radiusTweak=(1, 1, 1, 1), ratioPower=1.1, downAngle=(90, 110, 45, 45), downAngleV=(0, 80, 10, 10), useOldDownAngle=False, useParentAngle=True, rotate=(99.5, 137.5, 137.5, 137.5), rotateV=(15, 0, 0, 0), scale0=1, scaleV0=0.1, pruneWidth=0.4, pruneBase=0.3, pruneWidthPeak=0.6, prunePowerHigh=0.5, prunePowerLow=0.001, pruneRatio=1, leaves=25, leafDownAngle=45, leafDownAngleV=10, leafRotate=137.5, leafRotateV=0, leafScale=0.17, leafScaleX=1, leafScaleT=0, leafScaleV=0, leafShape='hex', leafangle=0, horzLeaves=True, leafDist='6', bevelRes=0, resU=4, armAnim=False, previewArm=False, leafAnim=False, frameRate=1, loopFrames=0, wind=1, gust=1, gustF=0.075, af1=1, af2=1, af3=4, makeMesh=False, armLevels=2, boneStep=(1, 1, 1, 1))
