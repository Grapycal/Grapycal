cd ../frontend
CALL npm run build:standalone
cd ..
rm -rf backend/src/grapycal/webpage
mkdir "backend/src/grapycal/webpage" 
cp -r frontend/dist/* backend/src/grapycal/webpage
cd ..