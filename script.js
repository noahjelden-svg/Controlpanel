async function updateInfo() {
  try {
    const res = await fetch('/api/system');
    const data = await res.json();

    document.getElementById('cpu').innerHTML = `
      <h2>🧠 CPU</h2>
      Nutzung: ${data.cpu.usage_percent}%<br>
      Kerne: ${data.cpu.cores_physical} phys / ${data.cpu.cores_logical} log<br>
      Frequenz: ${data.cpu.frequency.current} MHz
    `;

    document.getElementById('ram').innerHTML = `
      <h2>💾 RAM</h2>
      Nutzung: ${data.ram.percent}%<br>
      Verwendet: ${data.ram.used_gb} GB<br>
      Gesamt: ${data.ram.total_gb} GB
    `;

    document.getElementById('disk').innerHTML = `
      <h2>🗄️ Festplatte</h2>
      Nutzung: ${data.disk.percent}%<br>
      Verwendet: ${data.disk.used_gb} GB<br>
      Gesamt: ${data.disk.total_gb} GB
    `;

    const gpu = data.gpu.length > 0 ? `
      Name: ${data.gpu[0].name}<br>
      Auslastung: ${data.gpu[0].load}%<br>
      Speicher: ${(data.gpu[0].memoryUsed / 1024).toFixed(2)} GB / ${(data.gpu[0].memoryTotal / 1024).toFixed(2)} GB<br>
      Temperatur: ${data.gpu[0].temperature} °C
    ` : `Keine GPU gefunden`;

    document.getElementById('gpu').innerHTML = `<h2>🎮 GPU</h2>${gpu}`;

    document.getElementById('net').innerHTML = `
      <h2>🌐 Netzwerk</h2>
      Upload: ${data.network.sent_mb} MB<br>
      Download: ${data.network.recv_mb} MB
    `;

    document.getElementById('datetime').innerHTML = `
      <h2>⏰ Zeit</h2>
      Datum: ${data.datetime.date}<br>
      Uhrzeit: ${data.datetime.time}
    `;
  } catch (err) {
    console.error('Fehler beim Abrufen der Daten:', err);
  }
}

// --- Audio Steuerung ---

const volRange = document.getElementById('vol-range');
const muteBtn = document.getElementById('mute-btn');
const playpauseBtn = document.getElementById('playpause-btn');

async function fetchVolume() {
  try {
    const res = await fetch('/api/audio/volume');
    const data = await res.json();

    volRange.value = Math.round(data.volume * 100);
    muteBtn.textContent = data.muted ? 'Unstumm' : 'Stumm';
  } catch (err) {
    console.error('Fehler beim Abrufen der Lautstärke:', err);
  }
}

volRange.addEventListener('input', async () => {
  const newVol = volRange.value / 100;
  await fetch('/api/audio/volume', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({volume: newVol, muted: false})
  });
  muteBtn.textContent = 'Stumm';
});

muteBtn.addEventListener('click', async () => {
  const muted = muteBtn.textContent === 'Stumm';
  await fetch('/api/audio/volume', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({muted: muted})
  });
  muteBtn.textContent = muted ? 'Unstumm' : 'Stumm';
  if (!muted) {
    // Falls entmuten, Lautstärke auf aktuellen Wert setzen (sicherstellen)
    const currentVol = volRange.value / 100;
    await fetch('/api/audio/volume', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({volume: currentVol})
    });
  }
});

playpauseBtn.addEventListener('click', async () => {
  await fetch('/api/audio/playpause', {method: 'POST'});
});

// --- Periodisch alle 1 Sekunde ---

async function mainLoop() {
  await updateInfo();
  await fetchVolume();
}

setInterval(mainLoop, 1000);
window.onload = mainLoop;



