cd frontend
CALL npm run build
cd ..
rm -rf backend/src/grapycal/webpage
cp -r frontend/dist/* backend/src/grapycal/webpage