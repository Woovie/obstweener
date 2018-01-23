#!/usr/bin/env python3
import obspython as obs
import json, keyboard, configparser

#---- First exec startup

settings = {}

def init(configPath):
    print('Initializing...')
    config = configparser.ConfigParser()
    readConfig = config.read(configPath)
    settings['name'] = config.get('systems', 'name')
    settings['version'] = config.get('systems', 'version')
    settings['scene'] = {}
    for scene in config.items('scenes'):#Switch to configparser items, retrieve every item within [scenes] to make it easier/cleaner
        sceneName = scene[0]
        sceneConfig = scene[1]
        settings['scene'][sceneName] = {}
        settings['scene'][sceneName]['configFile'] = sceneConfig
        with open(settings['scene'][sceneName]['configFile']) as jsonData:
            settings['scene'][sceneName]['config'] = json.load(jsonData)
        print('loaded %s'%(sceneConfig))
    print('%s scenes loaded.'%(len(settings['scene'])))
    print('Initialized %s v%s'%(settings['name'], settings['version']))
    
#---- OBS Specific functions

def script_load(settings):
    settings['obsSettings'] = settings
    configPath = obs.obs_data_get_string(settings['obsSettings'], "cpath")
    print(type(configPath))
    if len(configPath) > 0:
        init(configPath)

def script_description():
    return "OBS Tweener\n\nby Jordan Banasik\nIdea, code, and help given by @VodBox https://github.com/VodBox/obs-scripts"

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, 'cpath', 'Configuration path', obs.OBS_PATH_FILE, '*.ini', None)
    return props

def script_tick(tick):
    animating = False
    if animating:
        print('animating')
    print(tick)

def script_update(settings):
    settings['obsSettings'] = settings    

#---- Utilities

def setupKeybinds():
    print('Setting keybinds...')
