const tg = window.Telegram.WebApp;
const defaultUrl = "baa2-178-205-242-112.ngrok-free.app";

async function fetchClicks() {
    try {
        const userId = tg.initDataUnsafe.user.id;
        const response = await fetch(`https://${defaultUrl}/get_clicks?id=${userId}`);
        const data = await response.json();
        return data.clicks;
    } catch (error) {
        console.error("Ошибка при получении кликов:", error);
        return 0;
    }
}

async function init() {
    let clicks = await fetchClicks();
    scoreElement.textContent = clicks;
    const scoreElement = document.getElementById('score');
    const imageElement = document.getElementById('image');

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
