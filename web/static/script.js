const tg = window.Telegram.WebApp;
const defaultUrl = "https://edeb-178-205-242-112.ngrok-free.app";

async function fetchClicks() {
    try {
        const userId = tg.initDataUnsafe.user.id;
        const response = await fetch(`/get_clicks?id=${userId}`);
        const data = await response.json();
        return data.clicks;
    } catch (error) {
        console.error("Ошибка при получении кликов:", error);
        return 0;
    }
}

async function fetchData(endpoint, data) {
    try {
        const response = await axios.post(`${defaultUrl}/${endpoint}`, data);
        return response.data;
    } catch (error) {
        console.error("Error fetching data:", error);
        return null;
    }
}

async function init() {
    let clicks = await fetchClicks();
    console.log("Текущий счёт:", clicks);

    const scoreElement = document.getElementById('score');
    scoreElement.textContent = clicks;
    const imageElement = document.getElementById('image');

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
        const response = await fetchData('click', { id: tg.initDataUnsafe.user.id });
    }

    imageElement.addEventListener('click', increaseScore);
}

document.addEventListener('DOMContentLoaded', (event) => {
    init();
});
