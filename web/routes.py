import os

from aiogram.types import Update
from fastapi import FastAPI, Request
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

    @app.post("/click")
    async def click(request: Request, data: dict):
        user = await User.filter(id=data["id"]).first()
        user.clicks += 1
        await user.save()

    @app.get("/get_clicks")
    async def get_clicks(id: int):
        user = await User.filter(id=id).first()
        if not user:
            return JSONResponse({"error": "User not found"}, status_code=404)
        return JSONResponse({"clicks": user.clicks})

    @app.post("/webhook")
    async def webhook(request: Request):
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)
