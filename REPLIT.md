# Replit Deployment Guide

To get this project running on Replit, follow these steps:

1. **Import the Project**: Upload your files or connect your GitHub repository.
2. **Environment Variables (Secrets)**:
   - Open the **Secrets** tool in Replit.
   - Add your `GOOGLE_API_KEY`.
   - Add `LLM_PROVIDER=gemini`.
   - Add `VITE_API_URL`. You can find this after the app starts. It will likely be `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co:8000` or similar.
3. **Run**: Click the **Run** button. Replit will use the `.replit` and `replit.nix` files to set up the environment and execute `run.sh`.

### Notes
- The `run.sh` script installs dependencies for both the Backend and Frontend on the first run.
- We use `concurrently` to run the FastAPI backend (port 8000) and the Vite frontend (port 5173) at the same time.
