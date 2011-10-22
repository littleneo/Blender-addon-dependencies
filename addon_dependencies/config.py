# YOU ABSOLUTELY DON'T WANT TO EDIT THIS VALUE
patch_version = (0, 72)

# but below it's ok :

# more logs
verbose = False

## nerds switches :
# don't change these ones below unless you know what you're doing.
# see README

# (default : False)
# in case you are a nerd and you use blender build from graphicall
# this can help to override version check.
# set this to the patch revision you want to install , e.g. '40791'
# use_user_files will be forced to True to restore the blender build files
# and not the orignal ones from trunk.
fake_revision = False
#fake_revision = '101'

# (default : False)  switch used at unregister(), "remove patch" time :
# when restoring the non-patched files, copy them from the user backup and not
# from original folder (which restore <revision> trunk files)
# use it if you hacked some file and want to restore your own mod.
use_user_files = False

modded = {}

# blender 2.59
modded['39307'] = [
    'modules/addon_utils.py',
    'startup/bl_ui/space_userpref.py'
 ]

# blender 2.60 and previous
# switched userprefs addon op. in wm
# changes in 260 were about typos in comments, so aliased to rc1
# 40791 should work with [40792:41097] revisions
# bundled trunk files are linux 41098
modded['40791'] = [
    'modules/addon_utils.py',
    'startup/bl_operators/wm.py',
    'startup/bl_ui/space_userpref.py'
 ]
modded['41098'] = [ 40791 ]
#modded['41097'] = [ 41098 ]
