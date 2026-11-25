const initialPoint = [-33.4489, -70.6693];
const searchForm = document.querySelector("#search-form");
const searchInput = document.querySelector("#search-input");
const categoryList = document.querySelector("#category-list");
const sortSelect = document.querySelector("#sort-select");
const resultsList = document.querySelector("#results-list");
const resultCount = document.querySelector("#result-count");
const emptyState = document.querySelector("#empty-state");
const locateButton = document.querySelector("#locate-button");

let activeCategory = "";
let userLocation = null;
let map;
let markerLayer;
let currentLocationMarker;
let currentResults = [];

function formatPrice(price) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(price);
}

function formatDistance(distance) {
  if (distance === null) return "Distancia disponible al compartir tu ubicación";
  if (distance < 1) return `${Math.round(distance * 1000)} m aprox.`;
  return `${distance.toFixed(1).replace(".", ",")} km aprox.`;
}

function updateMap(results) {
  markerLayer.clearLayers();
  if (!results.length) return;

  const bestPrice = Math.min(...results.map((result) => result.price));
  for (const result of results) {
    const markerIcon = L.divIcon({
      className: "",
      html: `<span class="price-marker${result.price === bestPrice ? " is-best" : ""}">${formatPrice(result.price)}</span>`,
      iconSize: [54, 38],
      iconAnchor: [27, 35],
    });
    const marker = L.marker([result.lat, result.lng], { icon: markerIcon });
    marker.bindPopup(`<strong>${result.store_name}</strong><br>${result.neighborhood}<br>${result.product_name}: ${formatPrice(result.price)}`);
    marker.addTo(markerLayer);
  }

  if (!userLocation) {
    const bounds = markerLayer.getBounds();
    if (bounds.isValid()) map.fitBounds(bounds, { padding: [32, 32], maxZoom: 13 });
  }
}

function renderResults(results) {
  currentResults = results;
  resultsList.replaceChildren();
  emptyState.hidden = results.length > 0;
  resultsList.hidden = results.length === 0;
  resultCount.textContent = results.length === 1
    ? "1 opción de referencia"
    : `${results.length} opciones de referencia`;

  for (const [index, result] of results.entries()) {
    const item = document.createElement("article");
    item.className = "result-item";
    item.tabIndex = 0;
    item.setAttribute("role", "button");
    item.setAttribute("aria-label", `${result.store_name}, ${result.neighborhood}, ${formatPrice(result.price)}. Ver en el mapa`);
    item.innerHTML = `
      <div>
        <p class="result-store">${result.store_name}</p>
        <p class="result-neighborhood">${result.neighborhood}<span class="result-distance">${formatDistance(result.distance_km)}</span></p>
      </div>
      <div class="result-price">${formatPrice(result.price)}</div>
      <div class="result-meta"><span>${result.product_name} · ${result.detail}</span><span class="estimate-tag">Estimado</span></div>
    `;

    const focusMarker = () => {
      map.flyTo([result.lat, result.lng], 15, { duration: 0.45 });
      const marker = markerLayer.getLayers()[index];
      if (marker) marker.openPopup();
    };
    item.addEventListener("click", focusMarker);
    item.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        focusMarker();
      }
    });
    resultsList.append(item);
  }

  updateMap(results);
}

async function loadResults() {
  resultsList.setAttribute("aria-busy", "true");
  resultCount.textContent = "Buscando opciones...";
  const parameters = new URLSearchParams({
    q: searchInput.value.trim(),
    category: activeCategory,
    sort: sortSelect.value,
  });
  if (userLocation) {
    parameters.set("lat", userLocation.lat);
    parameters.set("lng", userLocation.lng);
  }

  try {
    const response = await fetch(`/api/search?${parameters}`);
    if (!response.ok) throw new Error("No fue posible buscar.");
    const data = await response.json();
    renderResults(data.results);
  } catch {
    resultCount.textContent = "No pudimos cargar los precios. Revisa tu conexión e inténtalo de nuevo.";
    resultsList.replaceChildren();
    emptyState.hidden = true;
  } finally {
    resultsList.setAttribute("aria-busy", "false");
  }
}

function setUserLocation(latitude, longitude) {
  userLocation = { lat: latitude, lng: longitude };
  const distanceOption = sortSelect.querySelector('option[value="distance"]');
  distanceOption.disabled = false;
  distanceOption.textContent = "Más cercanas";
  currentLocationMarker?.remove();
  currentLocationMarker = L.circleMarker([latitude, longitude], {
    radius: 8,
    color: "#ffffff",
    weight: 3,
    fillColor: "#3985bb",
    fillOpacity: 1,
  }).addTo(map).bindPopup("Estás aquí");
  map.flyTo([latitude, longitude], 13);
  loadResults();
}

function initializeMap() {
  map = L.map("map", { scrollWheelZoom: false }).setView(initialPoint, 12);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  markerLayer = L.featureGroup().addTo(map);
}

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadResults();
});

categoryList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-category]");
  if (!button) return;

  activeCategory = button.dataset.category;
  for (const chip of categoryList.querySelectorAll("button")) {
    const isActive = chip === button;
    chip.classList.toggle("is-active", isActive);
    chip.setAttribute("aria-pressed", String(isActive));
  }
  loadResults();
});

sortSelect.addEventListener("change", loadResults);

locateButton.addEventListener("click", () => {
  if (!navigator.geolocation) {
    resultCount.textContent = "Tu navegador no permite compartir la ubicación.";
    return;
  }

  locateButton.disabled = true;
  resultCount.textContent = "Buscando tu ubicación...";
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      locateButton.disabled = false;
      setUserLocation(coords.latitude, coords.longitude);
    },
    () => {
      locateButton.disabled = false;
      resultCount.textContent = "No se pudo obtener tu ubicación. Puedes seguir viendo Santiago.";
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
  );
});

initializeMap();
loadResults();