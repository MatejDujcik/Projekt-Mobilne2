const API_BASE = "http://localhost:9005/api";

document.addEventListener("DOMContentLoaded", loadCities);


function loadCities() {
  fetch(`${API_BASE}/mesta`)
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById("cityCards");
      container.innerHTML = ""; 
      data.forEach(mesto => {
        const card = document.createElement("div");
        card.className = "mb-4 d-flex justify-content-center";
        card.innerHTML = `
          <div class="card shadow-sm city-card text-center">
            <div class="card-body">
              <h5 class="card-title">${mesto.nazov}</h5>
              <button class="btn btn-primary" onclick="showMestoDetail(${mesto.id})">Vstúpiť</button>
            </div>
          </div>
        `;
        container.appendChild(card);
      });
    })
    .catch(error => console.log('Chyba pri načítaní miest:', error));
}


function backToCities() {
  const container = document.getElementById("main-content");
  container.innerHTML = `
    <div class="row" id="cityCards">
      <!-- Dynamicky sa sem načítajú karty miest -->
    </div>
  `;
  loadCities();
}

function showMestoDetail(id) {
  fetch(`${API_BASE}/mesto/${id}`)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("main-content");
      container.innerHTML = `
        <div class="container-center position-relative">
          <div class="weather-bg" id="weather-animation"></div>
          <div class="card shadow-sm position-relative" style="width: 22rem; z-index: 1;">
            <div class="card-body">
              <h2 class="card-title">${data.nazov}</h2>
              <p><strong>Sila vetra:</strong> ${data.sila_vetra} km/h</p>
              <p><strong>Zrážky:</strong> ${data.mm_zrazky} mm</p>
              <p><strong>Teplota:</strong> ${data.teplota} °C</p>
              <button class="btn btn-secondary" onclick="backToCities()">Späť na zoznam miest</button>
            </div>
          </div>
        </div>
      `;
      const weatherBg = document.getElementById("weather-animation");
      const { sila_vetra, mm_zrazky, teplota } = data;

      let animation = "";
      if (mm_zrazky >= 10 && teplota > 0) {
        animation = "rain.gif";
      } else if (mm_zrazky >= 10 && teplota <= 0) {
        animation = "snow.gif";
      } else if (mm_zrazky <= 10 && sila_vetra > 5) {
        animation = "wind.gif";
      } else if (mm_zrazky >= 0 && sila_vetra <= 5) {
        animation = "sun.gif";
      }

      weatherBg.style.backgroundImage = `url('animations/${animation}')`;
    })
    .catch(error => console.log(error));
}

document.getElementById("addBtn").addEventListener("click", () => {
  const nazov = document.getElementById("cityName").value;
  const sila_vetra = parseFloat(document.getElementById("wind").value);
  const mm_zrazky = parseFloat(document.getElementById("rain").value);
  const teplota = parseFloat(document.getElementById("temp").value);

  if (!nazov || isNaN(sila_vetra) || isNaN(mm_zrazky) || isNaN(teplota)) {
    alert("Vyplň všetky polia!");
    return;
  }

  fetch(`${API_BASE}/mesto`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nazov, sila_vetra, mm_zrazky, teplota })
  })
    .then(res => {
      if (res.ok) return res.json();
      throw new Error("Nepodarilo sa pridať mesto.");
    })
    .then(() => {
      loadCities();
      clearInputs();
    })
    .catch(err => alert(err.message));
});

document.getElementById("editBtn").addEventListener("click", () => {
  const nazov = document.getElementById("cityName").value;

  fetch(`${API_BASE}/mesta`)
    .then(res => res.json())
    .then(data => {
      const mesto = data.find(m => m.nazov.toLowerCase() === nazov.toLowerCase());
      if (!mesto) {
        alert("Mesto nenájdené");
        return;
      }

      const id = mesto.id;
      const sila_vetra = parseFloat(document.getElementById("wind").value);
      const mm_zrazky = parseFloat(document.getElementById("rain").value);
      const teplota = parseFloat(document.getElementById("temp").value);

      if (isNaN(sila_vetra) || isNaN(mm_zrazky) || isNaN(teplota)) {
        alert("Vyplň všetky číselné hodnoty!");
        return;
      }

      fetch(`${API_BASE}/mesto/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sila_vetra, mm_zrazky, teplota })
      })
        .then(res => {
          if (res.ok) return res.json();
          throw new Error("Nepodarilo sa upraviť mesto.");
        })
        .then(() => {
          loadCities();
          clearInputs();
        })
        .catch(err => alert(err.message));
    });
});

document.getElementById("deleteBtn").addEventListener("click", () => {
  const nazov = document.getElementById("cityName").value;

  fetch(`${API_BASE}/mesta`)
    .then(res => res.json())
    .then(data => {
      const mesto = data.find(m => m.nazov.toLowerCase() === nazov.toLowerCase());
      if (!mesto) {
        alert("Mesto nenájdené");
        return;
      }

      const id = mesto.id;

      fetch(`${API_BASE}/mesto/${id}`, {
        method: "DELETE"
      })
        .then(res => {
          if (res.ok) return res.json();
          throw new Error("Nepodarilo sa vymazať mesto.");
        })
        .then(() => {
          loadCities();
          clearInputs();
        })
        .catch(err => alert(err.message));
    });
});

function clearInputs() {
  document.getElementById("cityName").value = "";
  document.getElementById("wind").value = "";
  document.getElementById("rain").value = "";
  document.getElementById("temp").value = "";
}
