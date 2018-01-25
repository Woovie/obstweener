#!/usr/bin/env python3
import obspython as obs
import json, keyboard, configparser, os.path

#---- First exec startup

gSettings = None
settings = {}
settings['animating'] = False
settings['animinfo'] = {
    'initial': [],
    'destination': [],
    'animtime': math.inf,
    'stoptime': 1000,
    'scene': None
}


def init(configPath):
    print('Initializing...')
    config = configparser.ConfigParser()
    readConfig = config.read(configPath)
    if config.has_section('tool'):
        settings['name'] = config.get('tool', 'name')
        settings['version'] = config.get('tool', 'version')
        settings['scene'] = {}
        for scene in config.items('scenes'):
            sceneName = scene[0]
            sceneConfig = scene[1]
            if os.path.isfile(sceneConfig):
                with open(sceneConfig) as jsonData:
                    prepareSceneSettings(json.load(jsonData), sceneConfig)
            else:
                print('%s does not exist'%(sceneConfig))
        print('%s scenes loaded.'%(len(settings['scene'])))
        print('Initialized %s v%s'%(settings['name'], settings['version']))
    else:
        print('Bad configuration file format for %s'%(configPath))
    
#---- OBS Specific functions

def script_load(settings):
    global gSettings
    gSettings = settings

def script_description():
    return "OBS Tweener\n\nby Jordan Banasik\nIdea, code, and help given by @VodBox https://github.com/VodBox/obs-scripts"

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, 'cpath', 'Configuration path', obs.OBS_PATH_FILE, '*.ini', None)
    return props

def script_tick(tick):
    if settings['animating']:
        
        if settings['scene'] == 
        settings['animating'] = False

def script_update(settings):
    global gSettings
    gSettings = settings
    configPath = obs.obs_data_get_string(gSettings, "cpath")
    if len(configPath) > 0 and os.path.isfile(configPath):
        init(configPath)
        print('loaded %s'%(configPath))
    else:
        print('Could not load %s'%(configPath))


#---- Utilities

#t = current time, b = start value, c = change in value, d = duration
def easeInOutQuad(t, b, c, d):
    t=/d/2
    if t<1:
        return c/2*t*t+b
    t-=1
    return -c/2*(t*(t-2)-1)+b)

def prepareSceneSettings(sceneData, configFilePath):
    sceneName = sceneData['sceneName']
    scenes = obs.obs_frontend_get_scene_names()
    if scenes is not None and len(scenes) > 0:
        print('Configuring scene %s'%(sceneName))
        tweeners = sceneData['tweeners']
        settings['scene'][sceneName] = {}
        settings['scene'][sceneName]['tweeners'] = {}
        for tweener in tweeners:
            tweenerName = tweener['name']
            settings['scene'][sceneName]['tweeners'][tweenerName] = tweener
        print('%s tweens loaded'%(len(settings['scene'][sceneName]['tweeners'])))
        print('Setting keybinds for scene %s'%(sceneName))
        for tweener in settings['scene'][sceneName]['tweeners']:
            tweener = settings['scene'][sceneName]['tweeners'][tweener]
            bindKey(sceneName, tweener['keybind'], tweener['name'])


def initTween():
    settings['animInfo'] = {}
    currentScene = obs.obs_frontend_get_current_scene()
    sceneName = obs.obs_source_get_name(currentScene)
    if settings['scene'][sceneName]:
        print('Found %s scene data.'%(sceneName))
        sceneObject = obs.obs_scene_from_source(currentScene)
        sceneItems = obs.obs_scene_enum_items(sceneObject)

def bindKey(scene, key, tweener):
    print('binding %s to %s in %s'%(key, tweener, scene))
    capture_return = keyboard.add_hotkey(key, lambda: tweenTo(scene, tweener))

def tweenTo(scene, tweener):
    settings['animating'] = True
    settings['scene'] = scene
    settings['tweener'] = tweener
