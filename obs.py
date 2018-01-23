#!/usr/bin/env python3
import obspython as obs
import json, keyboard, configparser

#---- First exec startup

settings = {}

def init():
    print('Initializing...')
    config = configparser.ConfigParser()
    readConfig = config.read("C:\\Users\\jbanasik\\Documents\\obs-tools\\configuration.ini")
    settings['name'] = config.get('systems', 'name')
    settings['version'] = config.get('systems', 'version')
    settings['scenes'] = config.get('systems', 'scenes').split(',')
    settings['scene'] = {}
    for scene in settings['scenes']:#Switch to configparser items, retrieve every item within [scenes] to make it easier/cleaner
        settings['scene'][scene]['configFilie'] = config.get('scenes', scene)
        with open(settings['scene'][scene]['configFile']) as jsonData:
            settings['scene'][scene]['config'] = json.load(jsonData)
    print('%s scenes loaded.'%(len(settings['scenes'])))
    print('Initialized %s v%s'%(settings['name'], settings['version']))
    
#---- OBS Specific functions

def script_load(settings):
    init()#Read the setting for configuration file from OBS, if it's not set, don't init(), send user instructions instead

def script_description():
    return "OBS Tweener\n\nby Jordan Banasik\nIdea, code, and help given by @VodBox https://github.com/VodBox/obs-scripts"

#---- Utilities

def setupKeybinds():
    print('Setting keybinds...')
