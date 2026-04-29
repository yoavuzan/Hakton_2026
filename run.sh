#!/bin/bash

# Install Backend Dependencies
echo \"Installing Backend dependencies...\"
cd BackEnd && pip install -r requirements.txt && cd ..

# Install Frontend Dependencies
echo \"Installing Frontend dependencies...\"
cd FrontEnd && npm install && cd ..

# Install Root Dependencies (concurrently)
echo \"Installing Root dependencies...\"
npm install

# Start both using concurrently
npx concurrently \"cd BackEnd && uvicorn BackEnd.main:app --host 0.0.0.0 --port 8000\" \"cd FrontEnd && npm run dev -- --host 0.0.0.0\"
