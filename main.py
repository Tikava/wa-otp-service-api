from src.app import app
from src.config import settings

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.app_port)