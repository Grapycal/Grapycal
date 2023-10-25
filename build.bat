cd frontend
CALL npm run build
cd ..
cp -r frontend/dist backend/src/grapycal/webpage
cd backend
cz bump 
poetry build