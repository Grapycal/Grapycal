cd backend
cz bump 
poetry build
cd ..
cd extensions/grapycal_builtin
poetry build
cd ../..