#!/usr/bin/env python3
import obspython as obs
import json, keyboard, configparser, os.path, math

#---- First exec startup

gSettings = None

settings = {}
settings['animating'] = False
settings['sceneCollection'] = None
settings['scene'] = None
settings['tweener'] = None

settings['scenes'] = {}
settings['initial'] = {}
settings['destination'] = {}
settings['boundkeys'] = []

def init(configPath):
    print('Initializing...')
    config = configparser.ConfigParser()
    readConfig = config.read(configPath)
    settings['name'] = config.get('tool', 'name')
    settings['version'] = config.get('tool', 'version')
    if config.has_section('tool'):
        for scene in config.items('scenes'):
            sceneName = scene[0]
            sceneConfig = scene[1]
            if os.path.isfile(sceneConfig):
                with open(sceneConfig) as jsonData:
                    prepareSceneSettings(json.load(jsonData), sceneConfig)
            else:
                print('%s does not exist'%(sceneConfig))
    else:
        print('Bad configuration file format for %s'%(configPath))
    
#---- OBS Specific functions

def script_load(nSettings):
    global gSettings
    gSettings = nSettings

def script_description():
    return "OBS Tweener\n\nby Jordan Banasik\nIdea, code, and help given by @VodBox https://github.com/VodBox/obs-scripts"

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, 'cpath', 'Configuration path', obs.OBS_PATH_FILE, '*.ini', None)
    return props

def script_tick(tick):
    if settings['animating']:
        print('Initial: %s'%(settings['initial']))
        print('Destination: %s'%(settings['destination']))
        settings['animating'] = False

def script_update(nSettings):
    global gSettings
    gSettings = nSettings
    configPath = obs.obs_data_get_string(gSettings, "cpath")
    if len(configPath) > 0 and os.path.isfile(configPath):
        init(configPath)
        print('loaded %s'%(configPath))
    else:
        print('Could not load %s'%(configPath))

def script_unload():
    try:
        settings
    except NameError:
        return
    else:
        for key in settings['boundkeys']:
            capture = keyboard.remove_hotkey(key)
            gSettings = None
            settings = None

#---- Utilities

#t = current time, b = start value, c = change in value, d = duration
def easeInOutQuad(t, b, c, d):
    t /= d/2
    if t < 1:
        return c/2*t*t + b
    t-=1
    return -c/2 * (t*(t-2) - 1) + b

def prepareSceneSettings(sceneData, configFilePath):
    sceneName = sceneData['sceneName']
    scenes = obs.obs_frontend_get_scene_names()
    if scenes is not None and len(scenes) > 0:
        print('Configuring scene %s'%(sceneName))
        tweeners = sceneData['tweeners']
        settings['scenes'][sceneName] = {}
        settings['scenes'][sceneName]['tweeners'] = {}
        for tweener in tweeners:
            tweenerName = tweener['name']
            settings['scenes'][sceneName]['tweeners'][tweenerName] = tweener
        print('%s tweens loaded'%(len(settings['scenes'][sceneName]['tweeners'])))
        print('Setting keybinds for scene %s'%(sceneName))
        for tweener in settings['scenes'][sceneName]['tweeners']:
            tweener = settings['scenes'][sceneName]['tweeners'][tweener]
            bindKey(sceneName, tweener['keybind'], tweener['name'])

def bindKey(scene, key, tweener):#Works
    print('binding %s to %s in %s'%(key, tweener, scene))
    capture = keyboard.add_hotkey(key, lambda: tweenTo(scene, tweener))
    settings['boundkeys'].append(key)

def tweenTo(scene, tweener):#Setup global array values
    settings['initial'] = json.dumps(getSceneData(scene, tweener))
    settings['destination'] = json.dumps(settings['scenes'][scene]['tweeners'][tweener]['items'])
    settings['animating'] = True

def getSceneData(scene, tweener):
    scene = obs.obs_frontend_get_current_scene()
    sceneObject = obs.obs_scene_from_source(scene)
    items = obs.obs_scene_enum_items(sceneObject)
    array = {}
    for item in items:
        name = obs.obs_source_get_name(obs.obs_sceneitem_get_source(item))
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
        array[name] = {"pos": [pos.x, pos.y], "rot": rot, "scale": [scale.x, scale.y], "alignment": alignment, "bounds": [bounds.x, bounds.y], "boundsType": boundsType, "boundsAlignment": boundsAlignment, "crop": [crop.left, crop.right, crop.top, crop.bottom]}
        obs.obs_sceneitem_release(item)
    obs.obs_source_release(scene)
    return array
