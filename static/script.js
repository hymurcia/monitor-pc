const maxDataPoints = 60;
const history = { cpu: [], ram: [], disk: [], labels: [] };
let chartInstance = null;

function getLevelClass(value) {
    if (value < 50) return 'level-low';
    if (value < 70) return 'level-medium';
    if (value < 90) return 'level-high';
    return 'level-critical';
}

function updateProgress(id, value) {
    const bar = document.getElementById(id);
    const displayValue = value.toFixed(1);
    bar.style.width = displayValue + '%';
    bar.textContent = displayValue + '%';

    const levelClass = getLevelClass(value);
    bar.className = `progress ${levelClass}`;

    const metricValueSpan = document.getElementById(id.replace('-progress', '-value'));
    if (metricValueSpan) {
        metricValueSpan.textContent = displayValue + '%';
        // Add a visual flash to indicate update
        metricValueSpan.style.transition = 'color 0.2s';
        metricValueSpan.style.color = levelClass === 'level-critical' ? '#f44336' :
            levelClass === 'level-high' ? '#ff9800' :
            levelClass === 'level-medium' ? '#ffc107' : '#28a745';
    }
}

function showAlertIfNeeded(cpu, ram, disk) {
    const alertBox = document.getElementById('alert-box');
    const isCritical = cpu > 90 || ram > 90 || disk > 90;

    if (isCritical) {
        alertBox.style.display = 'block';
        setTimeout(() => { alertBox.style.display = 'none'; }, 3000);
    }
}

function initChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.labels,
            datasets: [
                { label: 'CPU %', data: history.cpu, borderColor: '#ff9800', backgroundColor: 'rgba(255, 152, 0, 0.1)', borderWidth: 2, tension: 0.4 },
                { label: 'RAM %', data: history.ram, borderColor: '#2196f3', backgroundColor: 'rgba(33, 150, 243, 0.1)', borderWidth: 2, tension: 0.4 },
                { label: 'Disco %', data: history.disk, borderColor: '#f44336', backgroundColor: 'rgba(244, 67, 54, 0.1)', borderWidth: 2, tension: 0.4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { color: '#666' } },
                x: { ticks: { color: '#666' } }
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: '#666' } }
            },
            animation: { duration: 300 }
        }
    });
}

function updateChart(cpu, ram, disk) {
    const now = new Date().toLocaleTimeString();
    history.cpu.push(cpu);
    history.ram.push(ram);
    history.disk.push(disk);
    history.labels.push(now);

    if (history.cpu.length > maxDataPoints) {
        history.cpu.shift();
        history.ram.shift();
        history.disk.shift();
        history.labels.shift();
    }

    if (chartInstance) chartInstance.update();
}

async function fetchData() {
    try {
        const response = await fetch('/data');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        // Log values to console for debugging
        console.log('Fetched data:', data);

        updateProgress('cpu-progress', data.cpu);
        updateProgress('ram-progress', data.ram);
        updateProgress('disk-progress', data.disk_activity); // Use activity for the bar

        // Update disk space text separately
        document.getElementById('disk-space-value').textContent = data.disk_space.toFixed(1) + '%';

        // For the chart, we might want to show disk activity or space? 
        // Let's show disk activity in the chart for now, or create a 4th dataset.
        // To keep it simple, I'll just pass disk_activity to the chart for the 3rd line.
        // But the chart function expects cpu, ram, disk. 
        // We can update the chart to show disk activity instead of space.
        updateChart(data.cpu, data.ram, data.disk_activity);

        showAlertIfNeeded(data.cpu, data.ram, data.disk_activity);

        document.getElementById('last-update').textContent = 'Última actualización: ' + new Date().toLocaleTimeString();
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialize progress bars
    updateProgress('cpu-progress', window.initialData.cpu);
    updateProgress('ram-progress', window.initialData.ram);
    updateProgress('disk-progress', 0); // Initial disk activity is 0

    // Update disk space text
    document.getElementById('disk-space-value').textContent = window.initialData.disk.toFixed(1) + '%';

    // Initialize chart data
    const initialCPU = window.initialData.cpu;
    const initialRAM = window.initialData.ram;
    const initialDisk = 0; // Start disk activity at 0

    // Pre-fill history with initial data to show a line immediately
    for (let i = 0; i < 20; i++) {
        history.cpu.push(initialCPU);
        history.ram.push(initialRAM);
        history.disk.push(initialDisk);
        history.labels.push(new Date(Date.now() - (20 - i) * 2000).toLocaleTimeString());
    }

    initChart();

    // Start fetching data every 2 seconds
    setInterval(fetchData, 2000);

    // Immediate first fetch to update chart quickly
    fetchData();

    document.getElementById('last-update').textContent = 'Última actualización: ' + new Date().toLocaleTimeString();
});