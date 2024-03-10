1. check the version of objectsync and topicsync is the newest
1. update frontend\src\version.ts (check version with cz bump --dry-run )
1. temporary copy readme.md to backend\readme.md so that it can be published 
1. bump version with `cz bump` 
1. pip install -e backend -e extensions\grapycal_builtin 
1. update and copy the example file to backend\src\grapycal\Welcome.grapycal
1. poerty build with `build.bat`
1. delete grapycal config file in appdata
1. test_build.bat 
1. publish: `publish.bat`
1. test_build_pypi.bat 
1. update and push the example files
