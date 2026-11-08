import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Psychologist Web Application on http://127.0.0.1:{port}")
    print(f"Public Website: http://127.0.0.1:{port}/?lang=en or http://127.0.0.1:{port}/?lang=fa")
    print(f"Therapist Admin Portal: http://127.0.0.1:{port}/admin")
    print("Default Admin Credentials: admin / psychologist2026")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)
