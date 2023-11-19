import shutil

try:
    # remove old files in backend/src/grapycal/webpage
    shutil.rmtree('../backend/src/grapycal/webpage')

    #cp -r frontend/dist/* backend/src/grapycal/webpage
    # but ignore .git
    shutil.copytree('./dist','../backend/src/grapycal/webpage',ignore=shutil.ignore_patterns('.git'))
except PermissionError:
    import traceback
    traceback.print_exc()
    print('A permission error occurred when copying files. Please shut down all Grapycal processes and try again.')

