import asyncio
import flet as ft

async def main(page: ft.Page) -> None:
    page.title = "Milkis Clicker"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#708090"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = {"HomeVideo": "HomeVideo-Regular.ttf"}
    page.theme = ft.Theme(font_family="HomeVideo")

    async def score_up(event: ft.ContainerTapEvent) -> None:
        score.data += 1
        score.value = str(score.data)
        
        image.scale = 0.9
        await page.add_async()

        await asyncio.sleep(0.1)
        image.scale = 1
        await page.add_async()

    score = ft.Text(value="0", size=100, data=0)
    score_counter = ft.Text(
        size=50, 
        animate_opacity=ft.Animation(
            duration=600,
            curve=ft.AnimationCurve.BOUNCE_IN
        )
    )
    image = ft.Image(
        src="milkis.png",
        fit=ft.ImageFit.CONTAIN,
        animate_scale=ft.Animation(
            duration=400,
            curve=ft.AnimationCurve.EASE
        )
    )

    await page.add_async(
        score,
        ft.Container(
            content=ft.Stack(controls=[image, score_counter]),
            on_click=score_up,
        )
    )

if __name__ == "__main__":
    ft.app(target=main, view=None, port=8080)