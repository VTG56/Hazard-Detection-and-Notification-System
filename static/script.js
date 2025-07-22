// static/script.js

document.addEventListener('DOMContentLoaded', function () {
    const MAX_DATA_POINTS = 20;
    const shownNotificationTimestamps = new Set(); // Track displayed toast alerts

    const chartConfig = (label) => ({
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: label, data: [], borderColor: '#e94560',
                backgroundColor: 'rgba(233, 69, 96, 0.2)',
                borderWidth: 2, fill: true, tension: 0.4
            }]
        },
        options: {
            scales: { y: { beginAtZero: false, ticks: { color: '#888' } } , x: { ticks: { color: '#888' } } },
            plugins: {
                legend: { display: false },
                title: { display: true, text: label, color: '#6c757d' }
            },
            maintainAspectRatio: false
        }
    });

    const soilChart = new Chart(document.getElementById('soilChart'), chartConfig('Coolant & Humidity'));
    const smokeChart = new Chart(document.getElementById('smokeChart'), chartConfig('Atmospheric Purity'));
    const ldrChart = new Chart(document.getElementById('ldrChart'), chartConfig('Ambient Light'));

    function updateChart(chart, label, value) {
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);
        if (chart.data.labels.length > MAX_DATA_POINTS) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        chart.update('none');
    }
    
    async function fetchData() {
        try {
            const [dataRes, notifRes] = await Promise.all([
                fetch('/data'),
                fetch('/notifications')
            ]);
            const data = await dataRes.json();
            const notifications = await notifRes.json();

            const timestamp = new Date().toLocaleTimeString();
            updateChart(soilChart, timestamp, data.soil);
            updateChart(smokeChart, timestamp, data.smoke);
            updateChart(ldrChart, timestamp, data.ldr);

            document.getElementById('soilValue').innerText = data.soil;
            document.getElementById('smokeValue').innerText = data.smoke;
            document.getElementById('ldrValue').innerText = data.ldr;
            
            updateStatusText(data);
            updateFlameAlert(data.flame);
            updateHistoryLog(data);
            updatePushbulletLog(notifications);
            processNotifications(notifications);

        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }

    function updateStatusText(data) {
        const soilStatusEl = document.getElementById('soilStatus');
        if (data.soil < 400) {
            soilStatusEl.innerText = "Status: CRITICAL Fluid Leak Risk";
            soilStatusEl.className = "text-danger fw-bold";
        } else if (data.soil < 600) {
            soilStatusEl.innerText = "Status: Atmospheric Condensation Risk";
            soilStatusEl.className = "text-warning fw-bold";
        } else {
            soilStatusEl.innerText = "Life Support: Nominal Humidity";
            soilStatusEl.className = "text-success fw-bold";
        }

        const smokeStatusEl = document.getElementById('smokeStatus');
        if (data.smoke > 400) {
            smokeStatusEl.innerText = "Status: CRITICAL Air Contamination!";
            smokeStatusEl.className = "text-danger fw-bold";
        } else {
            smokeStatusEl.innerText = "Cabin Air: Nominal";
            smokeStatusEl.className = "text-success fw-bold";
        }

        const ldrStatusEl = document.getElementById('ldrStatus');
        if (data.ldr <= 300) {
            ldrStatusEl.innerText = "Status: Extreme Luminosity Event";
            ldrStatusEl.className = "text-danger fw-bold";
        } else if (data.ldr <= 700) {
            ldrStatusEl.innerText = "Status: Unstable Light Fluctuation";
            ldrStatusEl.className = "text-warning fw-bold";
        } else {
            ldrStatusEl.innerText = "Status: Low Light / Orbital Shadow";
            ldrStatusEl.className = "text-info fw-bold";
        }
    }

    function updateFlameAlert(flameValue) {
        const flameCard = document.getElementById('flameCard');
        const flameIcon = document.getElementById('flameStatusIcon');
        const flameText = document.getElementById('flameStatusText');
        if (flameValue === 0) {
            flameCard.classList.add('flame-active');
            flameIcon.innerHTML = '<i class="fas fa-fire-alt text-danger"></i>';
            flameText.innerText = 'COMBUSTION DETECTED!';
            flameText.className = 'text-danger fw-bold';
        } else {
            flameCard.classList.remove('flame-active');
            flameIcon.innerHTML = '<i class="fas fa-shield-alt text-success"></i>';
            flameText.innerText = 'Thermal Scan: Clear';
            flameText.className = 'text-success fw-bold';
        }
    }

    function updateHistoryLog(data) {
        const historyLog = document.getElementById('historyLog');
        const entry = document.createElement('div');
        entry.className = 'list-group-item list-group-item-action flex-column align-items-start log-entry';
        if(document.body.classList.contains('dark-mode')) entry.classList.add('dark-mode');
        entry.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <small class="text-muted">${data.timestamp}</small>
            </div>
            <p class="mb-1 small">
                💧 Soil: <b>${data.soil}</b> | 💨 Smoke: <b>${data.smoke}</b> | ☀️ LDR: <b>${data.ldr}</b> | 🔥 Flame: <b>${data.flame === 0 ? 'Yes' : 'No'}</b>
            </p>`;
        historyLog.prepend(entry);
        if (historyLog.children.length > 50) {
            historyLog.removeChild(historyLog.lastChild);
        }
    }
    
    function updatePushbulletLog(notifications) {
        const pushbulletLog = document.getElementById('pushbulletLog');
        pushbulletLog.innerHTML = '';
        if (notifications.length === 0) {
            pushbulletLog.innerHTML = '<p class="text-muted p-2">No notifications sent recently.</p>';
            return;
        }
        notifications.forEach(notif => {
            const entry = document.createElement('div');
            entry.className = 'list-group-item list-group-item-action flex-column align-items-start log-entry';
            if(document.body.classList.contains('dark-mode')) entry.classList.add('dark-mode');
            entry.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1"><b>${notif.title}</b></h6>
                    <small>${notif.timestamp.split('.')[0]}</small>
                </div>
                <p class="mb-1 small">${notif.body}</p>`;
            pushbulletLog.appendChild(entry);
        });
    }

    function processNotifications(notifications) {
        notifications.forEach(notif => {
            if (!shownNotificationTimestamps.has(notif.timestamp)) {
                displayToastAlert(notif);
                shownNotificationTimestamps.add(notif.timestamp);
            }
        });
    }

    function displayToastAlert(notif) {
        const container = document.getElementById('alert-container');
        const toast = document.createElement('div');
        const severityClass = 'toast-' + notif.severity; // e.g., toast-critical
        toast.className = `toast-alert ${severityClass}`;
        
        toast.innerHTML = `
            <div class="toast-header">${notif.title}</div>
            <div class="toast-body">${notif.body}</div>
        `;

        container.prepend(toast);
        
        // Trigger the slide-in animation
        setTimeout(() => toast.classList.add('show'), 100);

        // Auto-dismiss after a delay (longer for more severe alerts)
        const delay = notif.severity === 'escalation' ? 20000 : 10000;
        setTimeout(() => {
            toast.classList.remove('show');
            // Remove from DOM after transition ends
            toast.addEventListener('transitionend', () => toast.remove());
        }, delay);
    }

    // --- Dark Mode Toggle ---
    const darkModeToggle = document.getElementById('darkModeToggle');
    function setDarkMode(isDark) {
        document.body.classList.toggle('dark-mode', isDark);
        document.querySelectorAll('.card').forEach(c => c.classList.toggle('dark-mode', isDark));
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
        // Update charts for dark mode
        const tickColor = isDark ? '#e0e0e0' : '#6c757d';
        [soilChart, smokeChart, ldrChart].forEach(chart => {
            chart.options.scales.y.ticks.color = tickColor;
            chart.options.scales.x.ticks.color = tickColor;
            chart.update();
        });
    }
    darkModeToggle.addEventListener('click', () => setDarkMode(darkModeToggle.checked));
    if (localStorage.getItem('darkMode') === 'enabled') {
        darkModeToggle.checked = true;
        setDarkMode(true);
    }

    // Initial fetch and interval
    fetchData();
    setInterval(fetchData, 800);
});