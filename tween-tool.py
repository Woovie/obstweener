#!/usr/bin/env python3
import obspython as obs
import json, configparser, os.path, math

config = configparser.ConfigParser()
obsSettings = None
scriptSettings = {}
scriptSettings['configs'] = []
scriptSettings['anim'] = {}
scriptSettings['anim']['animating'] = False
scriptSettings['anim']['time'] = math.inf
scriptSettings['anim']['length'] = 10000
scriptSettings['anim']['src'] = None
scriptSettings['anim']['dest'] = None
scriptSettings['anim']['tweener'] = None
scriptSettings['tweenerFunctions'] = []

#---- OBS Specific functions

def script_description():
    return "OBS Tweener"

def script_load(settings):
    obsSettings = settings
    configPath = obs.obs_data_get_string(settings, 'configPath')
    if configPath:
        config.read(configPath)
        if config.has_section('tweenConfigs'):
            for tweener in config.items('tweenConfigs'):
                tweenerConfig = tweener[1]
                if os.path.isfile(tweenerConfig):
                    with open(tweenerConfig) as jsonData:
                        loadConfig(json.load(jsonData))
    obs.obs_hotkey_register_frontend('dumpSceneData', 'tweentool - printSceneData', printSceneData)

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, 'configPath', 'Configuration path', obs.OBS_PATH_FILE, '*.ini', None)
    return props

def script_unload():
    for function in scriptSettings['tweenerFunctions']:
        obs.obs_hotkey_unregister(function)
    obs.obs_hotkey_unregister(dumpSceneData)
    obs.obs_data_release(obsSettings)

def script_update(settings):
    obsSettings = settings

def script_tick(tick):
    if scriptSettings['anim']['animating']:
        scriptSettings['anim']['time'] += tick
        scriptSettings['anim']['time'] = min(scriptSettings['anim']['time'], scriptSettings['anim']['length'])
        initial = scriptSettings['anim']['src']
        destination = scriptSettings['anim']['dest']
        tScale = easeInOutQuad(scriptSettings['anim']['time'] / scriptSettings['anim']['length'], 0, 1, 1)
        scene = obs.obs_frontend_get_current_scene()
        sceneObject = obs.obs_scene_from_source(scene)
        tweenItems = scriptSettings['anim']['tweener']['tweenItems']
        sceneItems = obs.obs_scene_enum_items(sceneObject)
        for sItem in sceneItems:
            sceneItem = obs.obs_sceneitem_get_source(sItem)
            sName = obs.obs_source_get_name(sceneItem)
            for tItem in tweenItems:
                if sName == tItem['name']:
                    pos = obs.vec2()
                    pos.x = tScale*(destination[sName]["pos"][0] - initial[sName]["pos"][0]) + initial[sName]["pos"][0]
                    pos.y = tScale*(destination[sName]["pos"][1] - initial[sName]["pos"][1]) + initial[sName]["pos"][1]
                    rot = tScale*(destination[sName]["rot"] - initial[sName]["rot"]) + initial[sName]["rot"]
                    scale = obs.vec2()
                    scale.x = tScale*(destination[sName]["scale"][0] - initial[sName]["scale"][0]) + initial[sName]["scale"][0]
                    scale.y = tScale*(destination[sName]["scale"][1] - initial[sName]["scale"][1]) + initial[sName]["scale"][1]
                    alignment = destination[sName]["alignment"]
                    bounds = obs.vec2()
                    bounds.x = tScale*(destination[sName]["bounds"][0] - initial[sName]["bounds"][0]) + initial[sName]["bounds"][0]
                    bounds.y = tScale*(destination[sName]["bounds"][1] - initial[sName]["bounds"][1]) + initial[sName]["bounds"][1]
                    boundsType = destination[sName]["boundsType"]
                    boundsAlignment = destination[sName]["boundsAlignment"]
                    crop = obs.obs_sceneitem_crop()
                    crop.left = math.floor(tScale*(destination[sName]["crop"][0] - initial[sName]["crop"][0]) + initial[sName]["crop"][0])
                    crop.right = math.floor(tScale*(destination[sName]["crop"][1] - initial[sName]["crop"][1]) + initial[sName]["crop"][1])
                    crop.top = math.floor(tScale*(destination[sName]["crop"][2] - initial[sName]["crop"][2]) + initial[sName]["crop"][2])
                    crop.bottom = math.floor(tScale*(destination[sName]["crop"][3] - initial[sName]["crop"][3]) + initial[sName]["crop"][3])
                    obs.obs_sceneitem_set_pos(sItem, pos)
                    obs.obs_sceneitem_set_rot(sItem, rot)
                    obs.obs_sceneitem_set_scale(sItem, scale)
                    obs.obs_sceneitem_set_alignment(sItem, alignment)
                    obs.obs_sceneitem_set_bounds(sItem, bounds)
                    obs.obs_sceneitem_set_bounds_type(sItem, boundsType)
                    obs.obs_sceneitem_set_bounds_alignment(sItem, boundsAlignment)
                    obs.obs_sceneitem_set_crop(sItem, crop)
        if scriptSettings['anim']['time'] >= scriptSettings['anim']['length']:
            scriptSettings['anim']['src'] = None
            scriptSettings['anim']['dest'] = None
            scriptSettings['anim']['time'] = math.inf
            scriptSettings['anim']['length'] = 10000
            scriptSettings['anim']['tweener'] = None
            scriptSettings['anim']['animating'] = False
        

#---- My functions

def loadConfig(jsonData):
    for collection in jsonData:
        if collection['sceneCollection'] == obs.obs_frontend_get_current_scene_collection():
            if collection['sceneName'] == obs.obs_source_get_name(obs.obs_frontend_get_current_scene()):
                scriptSettings['configs'].append(collection)
                for tweener in collection['tweeners']:
                    tweenerFunction = createTweenerFunction(tweener['tweenName'])
                    scriptSettings['tweenerFunctions'].append(tweenerFunction)
                    obs.obs_hotkey_register_frontend(tweener['tweenName'], 'Tweener - %s'%(tweener['tweenName']), tweenerFunction)

def printBaseData(pressedState):
    if pressedState:
        sceneCollection = obs.obs_frontend_get_current_scene_collection()
        sceneName = obs.obs_source_get_name(obs.obs_frontend_get_current_scene())
        baseArray = [{'sceneCollection': sceneCollection, 'sceneName': sceneName, 'tweeners':[]}]
        print(json.dumps(baseArray))

def printSceneData(pressedState):
    if pressedState:
        nameOfTweener = None
        items = obs.obs_scene_enum_items(obs.obs_scene_from_source(obs.obs_frontend_get_current_scene()))
        for item in items:
            sceneItem = obs.obs_sceneitem_get_source(item)
            name = obs.obs_source_get_name(sceneItem)
            if "tweentool:" in name:
                nameOfTweener = name.split(':')[1]
                tweenTime = float(name.split(':')[3])
            name = obs.obs_source_get_name(sceneItem)
        if nameOfTweener:
            print(json.dumps({'tweenName': nameOfTweener, 'length': tweenTime, 'tweenItems': dumpSceneData()}))
        else:
            print('Please create the appropriate source at the top of the source list for your naming. See instructions for further details.')

def createTweenerFunction(tweenerName):
    def _function(pressed):
        if pressed:
            switchToTweener(tweenerName)
    return _function

def dumpSceneData():
    scene = obs.obs_frontend_get_current_scene()
    sceneObject = obs.obs_scene_from_source(scene)
    items = obs.obs_scene_enum_items(sceneObject)
    itemArray = []
    for item in items:
        sceneItem = obs.obs_sceneitem_get_source(item)
        name = obs.obs_source_get_name(sceneItem)
        if "tweentool:" not in name:
            pos = obs.vec2()
            obs.obs_sceneitem_get_pos(item, pos)
            rot = obs.obs_sceneitem_get_rot(item)
            scale = obs.vec2()
            obs.obs_sceneitem_get_scale(item, scale)
            alignment = obs.obs_sceneitem_get_alignment(item)
            bounds = obs.vec2()
            obs.obs_sceneitem_get_bounds(item, bounds)
            boundsType = obs.obs_sceneitem_get_bounds_type(item)
            boundsAlignment = obs.obs_sceneitem_get_bounds_alignment(item)
            crop = obs.obs_sceneitem_crop()
            obs.obs_sceneitem_get_crop(item, crop)
            itemArray.append({"name": name,"pos": [pos.x, pos.y], "rot": rot, "scale": [scale.x, scale.y], "alignment": alignment, "bounds": [bounds.x, bounds.y], "boundsType": boundsType, "boundsAlignment": boundsAlignment, "crop": [crop.left, crop.right, crop.top, crop.bottom]})
    return itemArray

def switchToTweener(tweenerName):
    currentCollection = obs.obs_frontend_get_current_scene_collection()
    currentSceneName = obs.obs_source_get_name(obs.obs_frontend_get_current_scene())
    for collection in scriptSettings['configs']:
        if collection['sceneCollection'] == currentCollection and collection['sceneName'] == currentSceneName:
            for tweener in collection['tweeners']:
                if tweener['tweenName'] == tweenerName:
                    srcArray = {}
                    for item in dumpSceneData():
                        name = item['name']
                        pos = item['pos']
                        rot = item['rot']
                        scale = item['scale']
                        alignment = item['alignment']
                        bounds = item['bounds']
                        boundsType = item['boundsType']
                        boundsAlignment = item['boundsAlignment']
                        crop = item['crop']
                        srcArray[name] = {"pos": pos, "rot": rot, "scale": scale, "alignment": alignment, "bounds": bounds, "boundsType": boundsType, "boundsAlignment": boundsAlignment, "crop": crop}
                    scriptSettings['anim']['src'] = srcArray
                    destArray = {}
                    for item in tweener['tweenItems']:
                        name = item['name']
                        pos = item['pos']
                        rot = item['rot']
                        scale = item['scale']
                        alignment = item['alignment']
                        bounds = item['bounds']
                        boundsType = item['boundsType']
                        boundsAlignment = item['boundsAlignment']
                        crop = item['crop']
                        destArray[name] = {"pos": pos, "rot": rot, "scale": scale, "alignment": alignment, "bounds": bounds, "boundsType": boundsType, "boundsAlignment": boundsAlignment, "crop": crop}
                    scriptSettings['anim']['dest'] = destArray
                    scriptSettings['anim']['time'] = 0
                    scriptSettings['anim']['length'] = tweener['length']/1000
                    scriptSettings['anim']['tweener'] = tweener
                    scriptSettings['anim']['animating'] = True
#---- Utilities

def easeInOutQuad(t, b, c, d):
    t /= d/2
    if t < 1:
        return c/2*t*t + b
    t-=1
    return -c/2 * (t*(t-2) - 1) + b