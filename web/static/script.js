const tg = window.Telegram.WebApp;
const defaultUrl = "95b2-178-205-246-153.ngrok-free.app";

const MIN_CLICK_INTERVAL = 25; // Минимальный интервал между кликами в миллисекундах

let lastClickTime = 0;

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

async function init() {
    let { clicks, equipped_skin } = await fetchClicks();
    const scoreElement = document.getElementById('score');
    const imageElement = document.getElementById('image');
    const imageContainer = document.querySelector('.image-container');

    scoreElement.textContent = clicks;

    if (equipped_skin && equipped_skin.photo) {
        imageElement.src = equipped_skin.photo;
        imageElement.alt = equipped_skin.name;
    } else {
        imageElement.src = '../static/milkis.png';  // Стандартное изображение, если скин не одет
        imageElement.alt = 'Milkis Image';
    }

    // Предотвращение перетаскивания изображения
    imageElement.addEventListener('dragstart', (e) => e.preventDefault());

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

    function handleInteraction(event) {
        event.preventDefault();
        const currentTime = Date.now();
        if (currentTime - lastClickTime >= MIN_CLICK_INTERVAL) {
            increaseScore(event);
            lastClickTime = currentTime;
        }
    }

    function getRandomTilt() {
        const tiltAngleX = (Math.random() - 0.5) * 20; // Случайный угол от -10 до 10 градусов
        const tiltAngleY = (Math.random() - 0.5) * 20; // Случайный угол от -10 до 10 градусов
        return `rotateX(${tiltAngleX}deg) rotateY(${tiltAngleY}deg)`;
    }

    async function increaseScore(event) {
        clicks++;
        scoreElement.textContent = clicks;
        
        // Эффект нажатия со случайным наклоном
        const randomTilt = getRandomTilt();
        imageElement.style.transform = `scale(0.95) ${randomTilt}`;
        
        // Возврат в исходное положение с небольшой задержкой
        setTimeout(() => {
            imageElement.style.transform = 'scale(1) rotateX(0) rotateY(0)';
        }, 200);
        
        // Эффект круга при клике
        const rect = imageContainer.getBoundingClientRect();
        const x = event.clientX || (event.touches && event.touches[0].clientX) || rect.left + rect.width / 2;
        const y = event.clientY || (event.touches && event.touches[0].clientY) || rect.top + rect.height / 2;
        
        const clickEffect = document.createElement('div');
        clickEffect.classList.add('click-effect');
        clickEffect.style.left = `${x - rect.left}px`;
        clickEffect.style.top = `${y - rect.top}px`;
        imageContainer.appendChild(clickEffect);
        setTimeout(() => clickEffect.remove(), 500);
        
        // Эффект всплывающего "+1"
        const scorePopup = document.createElement('div');
        scorePopup.classList.add('score-popup');
        scorePopup.textContent = '+1';
        scorePopup.style.left = `${x - rect.left}px`;
        scorePopup.style.top = `${y - rect.top}px`;
        imageContainer.appendChild(scorePopup);
        setTimeout(() => scorePopup.remove(), 1000);

        ws.send(JSON.stringify({ id: tg.initDataUnsafe.user.id }));
    }

    imageElement.addEventListener('click', handleInteraction);
    imageElement.addEventListener('touchstart', handleInteraction, { passive: false });
    
    // Предотвращение зума при двойном тапе
    document.addEventListener('dblclick', function(e) {
        e.preventDefault();
    }, { passive: false });

    // Предотвращение зума жестами
    document.addEventListener('gesturestart', function(e) {
        e.preventDefault();
    }, { passive: false });
}

// Предотвращение зума на всей странице
document.addEventListener('touchmove', function(event) {
    if (event.scale !== 1) {
        event.preventDefault();
    }
}, { passive: false });

document.addEventListener('DOMContentLoaded', (event) => {
    init();
});