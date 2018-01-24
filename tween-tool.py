#!/usr/bin/env python3
import obspython as obs
import json, keyboard, configparser, os.path

#---- First exec startup

gSettings = None
settings = {}

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
    configPath = obs.obs_data_get_string(gSettings, "cpath")
    if len(configPath) > 0 and os.path.isfile(configPath):
        init(configPath)
    else:
        print('%s does not exist'%(configPath))

def script_description():
    return "OBS Tweener\n\nby Jordan Banasik\nIdea, code, and help given by @VodBox https://github.com/VodBox/obs-scripts"

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, 'cpath', 'Configuration path', obs.OBS_PATH_FILE, '*.ini', None)
    return props

def script_tick(tick):
    animating = False
    if animating:
        print('anime')

def script_update(settings):
    global gSettings
    gSettings = settings
    configPath = obs.obs_data_get_string(gSettings, "cpath")
    if len(configPath) > 0 and os.path.isfile(configPath):
        init(configPath)
    else:
        print('Could not load %s'%(configPath))


#---- Utilities

def setupKeybinds():
    print('Setting keybinds...')

def prepareSceneSettings(sceneData):
    print(sceneData)
