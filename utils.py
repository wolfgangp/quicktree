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

lowpoly_presets = {
"handleType": "0",  # Auto (not Vector)
"bevelRes": 1,  # Bevel Resolution
"resU": 2,  # Curve Resolution
"levels": 3,
"curveRes": [3, 4, 3, 1],
}

wind = {
"wind": 0.35,
}

export_presets = {
"showLeaves": True,
"useArm": True,
"armLevels": 0,  # means all levels. earlier tried 2 which is n-1
"makeMesh": False,
"armAnim": True,
"frameRate": 30,
"loopFrames": 60
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
    var_type = type(var)
    if var_type in (float, int, str, bool):  # a single value
        return var
    elif var_type is tuple:  # randomize tuple
        first_type = type(var[0])
        if first_type is float:
            return uniform(*var)
        elif first_type is int:
            return randint(*var)
        else:  # string
            return choice(var)
    else:
        print("rnd failure, no tuple")

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
