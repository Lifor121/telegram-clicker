import os

from aiogram.types import Update
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db.models import User


def setup_routes(app: FastAPI, bot, dp):
    templates = Jinja2Templates(directory=os.getenv('DIR_TEMP'))
    app.mount("/static", StaticFiles(directory=os.getenv('DIR_STAT')))

    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/get_clicks")
    async def get_clicks(id: int):
        user = await User.filter(id=id).first()
        if not user:
            return JSONResponse({"error": "User not found"}, status_code=404)
        return JSONResponse({"clicks": user.clicks})

    @app.websocket("/ws/clicks")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                user_id = data.get("id")
                if user_id:
                    user = await User.filter(id=user_id).first()
                    if user:
                        user.clicks += 1
                        await user.save()
                        await websocket.send_json({"clicks": user.clicks})
                    else:
                        await websocket.send_json({"error": "User not found"})
                else:
                    await websocket.send_json({"error": "Invalid data"})
        except WebSocketDisconnect:
            print("Client disconnected")

    @app.post("/webhook")
    async def webhook(request: Request):
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)
