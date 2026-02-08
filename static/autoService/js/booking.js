// static/autoService/js/booking.js
document.addEventListener('DOMContentLoaded', function () {
    const btnArrived = document.getElementById('btn-arrived');
    const btnCompleted = document.getElementById('btn-completed');
    const errorMessage = document.getElementById('error-message');

    // Функция для получения CSRF-токена из cookie (стандарт Django)
    function getCsrfToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async function sendAction(url, button) {
        // Блокируем кнопку во время запроса
        button.disabled = true;
        errorMessage.style.display = 'none';

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({}) // даже пустое тело нужно для POST
            });

            const data = await response.json();

            if (response.ok) {
                // Успех: обновляем статус на странице
                location.reload(); // Самый простой способ для диплома!
                // Или можно обновлять DOM без перезагрузки — но reload проще и надёжнее
            } else {
                // Ошибка от сервера
                showErrorMessage(data.error || 'Неизвестная ошибка');
            }
        } catch (err) {
            showErrorMessage('Ошибка сети: не удалось подключиться к серверу');
        } finally {
            button.disabled = false;
        }
    }

    function showErrorMessage(msg) {
        errorMessage.textContent = msg;
        errorMessage.style.display = 'block';
        // Автоматически скроем через 5 секунд
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    // Назначаем обработчики
    if (btnArrived) {
        btnArrived.addEventListener('click', () => {
            sendAction(`/mark_arrived/${window.bookingId}`, btnArrived);
        });
    }

    if (btnCompleted) {
        btnCompleted.addEventListener('click', () => {
            sendAction(`/mark_completed/${window.bookingId}`, btnCompleted);
        });
    }
});