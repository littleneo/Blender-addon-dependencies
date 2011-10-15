# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# more logs
verbose = False

## nerds switches :
# don't change these ones below unless you know what you're doing.

# (default : False)
# in case you are a nerd and you use blender build from graphicall
# this can help to override version check.
# set this to the patch revision you want to install , e.g. '40791'
# use_user_files will be forced to True to True to restore the blender build files
# and not the orignal ones from trunk.
fake_revision = False
#fake_revision = '40791'

# (default : False)  switch used at unregister() // disable patch time :
# when restoring the non-patched files, copy them from the user backup and not
# from original folder (which restore <revision> trunk files)
# use it if you hacked some file and want to save your work.
use_user_files = False 



bl_info = {
    "name": "addon dependencies",
    "description": "",
    "author": "Littleneo / Jerome Mahieux",
    "version": (0, 72),
    "blender": (2, 59, 0),
    "api": 39307,
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import os
import shutil
from sys import modules
from addon_dependencies.fs_tools import *

modded = {}
modded['39307'] = [
    'modules/addon_utils.py',
    'startup/bl_ui/space_userpref.py'
 ]

modded['40791'] = [
    'modules/addon_utils.py',
    'startup/bl_operators/wm.py',
    'startup/bl_ui/space_userpref.py'
 ]

# Addon dependencies folder
ad_path = clean(modules['addon_dependencies'].__path__[0]) + '/'

# blender python files (/scripts)
bp_path = clean(bpy.utils.script_paths()[0]) + '/'
#paths = [ path, path + 'addons_contrib/' ]
#for path in paths :
#    if isdir(path) : break


## returns state and and a message
# state is either 'ori', 'mod', 'mod mismatch', 'mismatch' or 'missing'
def _checkstate(revision,verbose=False) :
    if verbose : print('    checking file for r%s...'%revision)
    for fid, mod in enumerate(modded[revision]) :
        filename = mod.split('/')[-1]
        # files exist ?
        exist = isfile(bp_path + mod)
        if verbose : print('    %s : %s'%(filename, 'found' if exist else 'missing'))
        if exist == False :
            return 'missing', '%s missing'%filename
        # which version of this file is running ?
        # all files are either modded or original, no mix allowed
        f = open(bp_path + mod)
        modline = f.readlines()[19][:-1]
        f.close()
        # this is a modded file
        if 'lnmod =' in modline :
            if verbose : print('    modded : %s'%modline)
            if modline == 'lnmod = (%s,%s)'%(revision, bl_info["version"]) :
                if fid == 0 : version = 'mod'
                elif version != 'mod' : return 'mismatch', 'original and modded files are mixed !'
            # this is a modded file from a previous version
            else :
                return 'mod mismatch', '%s modded version does not match'%filename

        # else an original user file
        else :
            if verbose : print('    original')
            if fid == 0 : version = 'ori'
            elif version != 'ori' : return 'mismatch', 'original and modded files are mixed !'
    return version, 'currently using the %s files'%('modded' if version == 'mod' else 'original')

def mismatch_log() :
    compat = ''
    for rev in modded.keys() : compat += rev+', '
    M,m,s = bpy.app.version
    print('  version mismatch :')
    print('  this addon is compatible with blender revision%s %s'%('s' if len(modded) > 1 else '', compat))
    print('  but you currently use blender v%s.%s.%s revision %s.'%(M,m,s,bpy.app.build_revision))

def register() :
    print('\naddon dependencies :')
    if fake_revision :
        revision = fake_revision
        print('  ! faked revision switch enabled !')
    else :
        revision = bpy.app.build_revision
    # blender version check. version absolutely needs to match an available patch.
    #double check for an existing revision folder in the mod folder and for an existing key in the 'modded' dict above
    for dir in scandir(ad_path + 'mod', filemode = False) :
        # FOUND
        if revision == dir.split('/')[-1] and revision in modded.keys() :
            print('  blender r%s, patch v.%s.%s'%(revision,bl_info['version'][0],bl_info["version"][1]))

            # which file are currently used ?
            state, log = _checkstate(revision,verbose)
            print('  %s'%log)

            # not the modded ones : install them
            if state != 'mod' :
                revision_path = revision + '/'

                # revision backup directory
                if isdir( ad_path + 'user/' + revision_path ) == False : 
                    os.makedirs( ad_path  + 'user/' + revision_path)

                # backup used files if not already done
                print('  Backing up user files :')
                for file_path in modded[revision] :
                    filename = file_path.split('/')[-1]
                    if isfile( ad_path + 'user/' + revision_path + filename ) == False :
                        print('    copying %s file in user/%s'%(filename, revision))
                        if verbose :
                            print('      from : ' + bp_path + file_path )
                            print('      to   : ' + ad_path + 'user/' + revision_path + filename )
                        shutil.copy2( bp_path + file_path , ad_path + 'user/' + revision_path + filename )

                # copy modded files
                print('  Patching :')
                for file_path in modded[revision] :
                    filename = file_path.split('/')[-1]
                    print('    copying patch from mod/%s/%s'%(revision, filename))
                    if verbose :
                        print('      from : ' + ad_path + 'mod/' + revision_path + filename )
                        print('      to   : ' + bp_path + file_path )
                    shutil.copy2( ad_path + 'mod/' + revision_path + filename, bp_path + file_path )
                print('  patch installed, please restart Blender.\n')
            break
    else :
        # NOT FOUND
        mismatch_log()

def unregister() :
    print('\naddon dependencies :')
    global use_user_files
    if fake_revision :
        revision = fake_revision
        use_user_files = True
        print('  ! faked revision switch enabled !')
    else :
        revision = bpy.app.build_revision

    # blender version check. version absolutely needs to match an available patch.
    #double check for an existing revision folder in the mod folder and for an existing key in the 'modded' dict above
    for dir in scandir(ad_path + 'mod', filemode = False) :
        # FOUND
        if revision == dir.split('/')[-1] and revision in modded.keys() :
            print('  blender r%s, patch v.%s.%s'%(revision,bl_info['version'][0],bl_info["version"][1]))

            # which file are currently used ?
            state, log = _checkstate(revision,verbose)
            print('  %s'%log)

            # not the original ones : install them
            if state != 'ori' :
                revision_path = revision + '/'

                # restore previously backuped user files switch is on
                # some checks before to process
                if use_user_files :
                    print('  Restore from the user backup folder :')
                    # revision backup directory does not exist, abort
                    if isdir( ad_path + 'user/' + revision_path ) == False : 
                        use_user_files = False
                        print("    can't restore user files, revision folder %s is missing in /user"%(revision) )
                    else :

                        # some file are missing in user/revision, abort
                        for file_path in modded[revision] :
                            filename = file_path.split('/')[-1]
                            if isfile(  ad_path + 'user/' + revision_path + filename ) == False :
                                print("    can't restore user files, file %s is missing in /user/%s"%(filename,revision) )
                                use_user_files = False
                                break
                                
                        # all system go
                        else :
                            for file_path in modded[revision] :
                                filename = file_path.split('/')[-1]
                                print('    restoring user/%s/%s'%(revision,filename) )
                                if verbose :
                                    print('      from : ' + ad_path + 'user/' + revision_path + filename )
                                    print('      to   : ' + bp_path + file_path )
                                shutil.copy2( ad_path + 'user/' + revision_path + filename, bp_path + file_path )
                                os.remove( ad_path + 'user/' + revision_path + filename )
                                
                # restore original shipped files
                if use_user_files == False :
                    print('  Restore from the original folder :')
                    for file_path in modded[revision] :
                        filename = file_path.split('/')[-1]
                        print('    restoring ori/%s/%s'%(revision,filename) )
                        if verbose :
                            print('      from : ' + ad_path + 'ori/' + revision_path + filename )
                            print('      to   : ' + bp_path + file_path )
                        shutil.copy2( ad_path + 'ori/' + revision_path + filename, bp_path + file_path )
                print('  patch removed, please restart Blender.\n')

            break
    else :
        # NOT FOUND
        mismatch_log()