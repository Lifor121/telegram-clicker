import os

from aiogram.types import Update
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db.models import User

async def send_user_data(user):
    if hasattr(user, 'websocket') and user.websocket:
        skin_data = None
        if user.equipped_skin:
            collection = await user.equipped_skin.collection
            skin_data = {
                "name": user.equipped_skin.name,
                "description": user.equipped_skin.description,
                "photo": f"/skins/{collection.folder_name}/{user.equipped_skin.photo}",
            }
        await user.websocket.send_json({
            "clicks": user.clicks,
            "equipped_skin": skin_data
        })

def setup_routes(app: FastAPI, bot, dp):
    templates = Jinja2Templates(directory=os.getenv('DIR_TEMP'))
    app.mount("/static", StaticFiles(directory=os.getenv('DIR_STAT')))
    app.mount("/skins", StaticFiles(directory="db/skins"), name="skins")

    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/get_clicks")
    async def get_clicks(id: int):
        user = await User.filter(id=id).prefetch_related('equipped_skin__collection').first()
        if not user:
            return JSONResponse({"error": "User not found"}, status_code=404)
        skin = user.equipped_skin
        if skin:
            collection_folder = skin.collection.folder_name
            photo_path = os.path.join(collection_folder, skin.photo)
            skin_data = {
                "name": skin.name,
                "description": skin.description,
                "photo": f"/skins/{photo_path}",
            }
        else:
            skin_data = None
        return JSONResponse({"clicks": user.clicks, "equipped_skin": skin_data})

    @app.websocket("/ws/clicks")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        user_id = None
        try:
            while True:
                data = await websocket.receive_json()
                user_id = data.get("id")
                if user_id:
                    user = await User.filter(id=user_id).prefetch_related('equipped_skin__collection').first()
                    if user:
                        user.websocket = websocket
                        if data.get("action") == "click":
                            user.clicks += 1
                            await user.save()
                        await send_user_data(user)
                    else:
                        await websocket.send_json({"error": "User not found"})
                else:
                    await websocket.send_json({"error": "Invalid data"})
        except WebSocketDisconnect:
            print(f"Client disconnected: {user_id}")
        finally:
            if user_id:
                user = await User.filter(id=user_id).first()
                if user:
                    user.websocket = None
                    await user.save()

    @app.post("/webhook")
    async def webhook(request: Request):
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)