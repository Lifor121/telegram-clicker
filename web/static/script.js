const tg = window.Telegram.WebApp;
const defaultUrl = "7946-188-225-127-225.ngrok-free.app";

async function fetchClicks() {
    try {
        const userId = tg.initDataUnsafe.user.id;
        const response = await fetch(`https://${defaultUrl}/get_clicks?id=${userId}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Ошибка при получении кликов:", error);
        return 0;
    }
}

async function init() {
    let { clicks, equipped_skin } = await fetchClicks();
    const scoreElement = document.getElementById('score');
    const imageElement = document.getElementById('image');

    scoreElement.textContent = clicks;

    if (equipped_skin && equipped_skin.photo) {
        imageElement.src = equipped_skin.photo;
        imageElement.alt = equipped_skin.name;
    } else {
        imageElement.src = '../static/milkis.png';  // Стандартное изображение, если скин не одет
        imageElement.alt = 'Milkis Image';
    }

    const ws = new WebSocket(`wss://${defaultUrl}/ws/clicks`);

    ws.onopen = () => {
        console.log("WebSocket connection established");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.clicks !== undefined) {
            clicks = data.clicks;
            scoreElement.textContent = clicks;
        } else if (data.error) {
            console.error(data.error);
        }
    };

    ws.onerror = (error) => {
        console.error(`WebSocket error: ${error}`);
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed");
    };

    function handleTouchStart(event) {
        event.preventDefault();
        for (let i = 0; i < event.touches.length; i++) {
            increaseScore();
        }
    }

    async function increaseScore() {
        clicks++;
        scoreElement.textContent = clicks;
        imageElement.style.transform = 'scale(0.9)';
        setTimeout(() => {
            imageElement.style.transform = 'scale(1)';
        }, 100);
        ws.send(JSON.stringify({ id: tg.initDataUnsafe.user.id }));
    }

    imageElement.addEventListener('click', increaseScore);
}

document.addEventListener('DOMContentLoaded', (event) => {
    init();
});
