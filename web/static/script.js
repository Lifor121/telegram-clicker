const tg = window.Telegram.WebApp;
const defaultUrl = "8862-178-207-26-204.ngrok-free.app";

const MIN_CLICK_INTERVAL = 25; // Минимальный интервал между кликами в миллисекундах

let lastClickTime = 0;
let ws;
let reconnectInterval;

function updateUI(clicks, equipped_skin) {
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
}

async function fetchClicks() {
    try {
        const userId = tg.initDataUnsafe.user.id;
        const response = await fetch(`https://${defaultUrl}/get_clicks?id=${userId}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Ошибка при получении кликов:", error);
        return { clicks: 0, equipped_skin: null };
    }
}

function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        return;
    }

    ws = new WebSocket(`wss://${defaultUrl}/ws/clicks`);

    ws.onopen = () => {
        console.log("WebSocket connection established");
        clearInterval(reconnectInterval);
        ws.send(JSON.stringify({ id: tg.initDataUnsafe.user.id }));
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.clicks !== undefined) {
            updateUI(data.clicks, data.equipped_skin);
        } else if (data.error) {
            console.error(data.error);
        }
    };

    ws.onerror = (error) => {
        console.error(`WebSocket error: ${error}`);
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed. Reconnecting...");
        reconnectInterval = setInterval(connectWebSocket, 5000);
    };
}

function getRandomTilt() {
    const tiltAngleX = (Math.random() - 0.5) * 20;
    const tiltAngleY = (Math.random() - 0.5) * 20;
    return `rotateX(${tiltAngleX}deg) rotateY(${tiltAngleY}deg)`;
}

function handleInteraction(event) {
    event.preventDefault();
    const currentTime = Date.now();
    if (currentTime - lastClickTime >= MIN_CLICK_INTERVAL) {
        increaseScore(event);
        lastClickTime = currentTime;
    }
}

function increaseScore(event) {
    const imageElement = document.getElementById('image');
    const imageContainer = document.querySelector('.image-container');
    
    const randomTilt = getRandomTilt();
    imageElement.style.transform = `scale(0.95) ${randomTilt}`;
    
    setTimeout(() => {
        imageElement.style.transform = 'scale(1) rotateX(0) rotateY(0)';
    }, 200);
    
    const rect = imageContainer.getBoundingClientRect();
    const x = event.clientX || (event.touches && event.touches[0].clientX) || rect.left + rect.width / 2;
    const y = event.clientY || (event.touches && event.touches[0].clientY) || rect.top + rect.height / 2;
    
    const clickEffect = document.createElement('div');
    clickEffect.classList.add('click-effect');
    clickEffect.style.left = `${x - rect.left}px`;
    clickEffect.style.top = `${y - rect.top}px`;
    imageContainer.appendChild(clickEffect);
    setTimeout(() => clickEffect.remove(), 500);
    
    const scorePopup = document.createElement('div');
    scorePopup.classList.add('score-popup');
    scorePopup.textContent = '+1';
    scorePopup.style.left = `${x - rect.left}px`;
    scorePopup.style.top = `${y - rect.top}px`;
    imageContainer.appendChild(scorePopup);
    setTimeout(() => scorePopup.remove(), 1000);

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ id: tg.initDataUnsafe.user.id, action: 'click' }));
    } else {
        console.error("WebSocket is not open. Reconnecting...");
        connectWebSocket();
    }
}

async function init() {
    const { clicks, equipped_skin } = await fetchClicks();
    updateUI(clicks, equipped_skin);

    const imageElement = document.getElementById('image');

    imageElement.addEventListener('dragstart', (e) => e.preventDefault());

    connectWebSocket();

    imageElement.addEventListener('click', handleInteraction);
    imageElement.addEventListener('touchstart', handleInteraction, { passive: false });
    
    document.addEventListener('dblclick', function(e) {
        e.preventDefault();
    }, { passive: false });

    document.addEventListener('gesturestart', function(e) {
        e.preventDefault();
    }, { passive: false });

    // Поддержание WebSocket соединения
    setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ id: tg.initDataUnsafe.user.id, action: 'ping' }));
        } else {
            connectWebSocket();
        }
    }, 3000);  // Пинг каждые 30 секунд
}

document.addEventListener('touchmove', function(event) {
    if (event.scale !== 1) {
        event.preventDefault();
    }
}, { passive: false });

document.addEventListener('DOMContentLoaded', init);

// Обработка видимости страницы
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        connectWebSocket();
    }
});