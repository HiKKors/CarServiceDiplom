// static/autoService/js/booking_form.js
let selectedTime = null;

function showErrorMessage(msg) {
    const el = document.getElementById('error-message');
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 5000);
}

function loadBoxes() {
    const serviceId = document.getElementById('service-select').value;
    if (!serviceId) return;

    fetch(`/api/boxes/?service_id=${serviceId}`)
        .then(r => r.json())
        .then(data => {
            const sel = document.getElementById('box-select');
            sel.innerHTML = '<option value="">-- Выберите бокс --</option>';
            data.forEach(b => sel.innerHTML += `<option value="${b.id}">Бокс ${b.number}</option>`);
            document.getElementById('step-box').style.display = 'block';
            document.getElementById('step-date-time').style.display = 'none';
            document.getElementById('confirm-btn').disabled = true;
        });
}

function loadAvailableTimes() {
    console.log('loadAvailableTimes func');
    const boxId = document.getElementById('box-select').value;

    if (!boxId) return;
    console.log('URL:', `/api/available-times/?box_id=${boxId}`);

    fetch(`/api/available-times/?box_id=${boxId}`)
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('time-slots');
            if (data.error) {
                showErrorMessage(data.error);
                container.innerHTML = '';
                return;
            }
            console.log('fetch');
            let html = '';
            if (data.slots.length === 0) {
                html = '<p>Нет свободных слотов</p>';
            } else {
                data.slots.forEach(slot => {
                    html += `
                        <div class="time-slot" 
                             onclick="selectTimeSlot('${slot.start}', '${slot.end}')">
                            ${slot.start}–${slot.end}
                        </div>
                    `;
                });
            }
            container.innerHTML = html;
            document.getElementById('step-date-time').style.display = 'block';
        });
}

function selectTimeSlot(start, end) {
    // Убираем выделение со всех
    document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
    // Выделяем текущий
    event.target.classList.add('selected');
    
    selectedTime = { start, end };
    document.getElementById('confirm-btn').disabled = false;
}

function submitBooking() {
    if (!selectedTime) return;
    
    const boxId = document.getElementById('box-select').value;
    
    // Заполняем скрытую форму
    document.getElementById('selected-box').value = boxId;
    document.getElementById('selected-start').value = 
        document.getElementById('date-picker').value + 'T' + selectedTime.start;
    document.getElementById('selected-end').value = 
        document.getElementById('date-picker').value + 'T' + selectedTime.end;
    
    // Отправляем форму
    document.getElementById('booking-form').submit();
}

