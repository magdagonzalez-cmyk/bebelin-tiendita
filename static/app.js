const initialPoint = [-33.4489, -70.6693];
const searchForm = document.querySelector("#search-form");
const searchInput = document.querySelector("#search-input");
const categoryList = document.querySelector("#category-list");
const sortSelect = document.querySelector("#sort-select");
const resultsList = document.querySelector("#results-list");
const resultCount = document.querySelector("#result-count");
const emptyState = document.querySelector("#empty-state");
const locateButton = document.querySelector("#locate-button");
const locationHelp = document.querySelector("#location-help");
const areaName = document.querySelector("#area-name");
const mapAreaLabel = document.querySelector("#map-area-label");
const dataNoticeText = document.querySelector("#data-notice-text");

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
    const popup = document.createElement("div");
    const storeName = document.createElement("strong");
    storeName.textContent = result.store_name;
    const neighborhood = document.createElement("div");
    neighborhood.textContent = result.neighborhood;
    const productPrice = document.createElement("div");
    productPrice.textContent = `${result.product_name}: ${formatPrice(result.price)} (estimado)`;
    popup.append(storeName, neighborhood, productPrice);
    marker.bindPopup(popup);
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
    item.style.setProperty("--item-index", index);
    item.tabIndex = 0;
    item.setAttribute("role", "button");
    item.setAttribute("aria-label", `${result.store_name}, ${result.neighborhood}, ${formatPrice(result.price)}. Ver en el mapa`);
    const storeDetails = document.createElement("div");
    const storeName = document.createElement("p");
    storeName.className = "result-store";
    storeName.textContent = result.store_name;
    const neighborhood = document.createElement("p");
    neighborhood.className = "result-neighborhood";
    neighborhood.textContent = result.neighborhood;
    const distance = document.createElement("span");
    distance.className = "result-distance";
    distance.textContent = formatDistance(result.distance_km);
    neighborhood.append(distance);
    storeDetails.append(storeName, neighborhood);

    const price = document.createElement("div");
    price.className = "result-price";
    price.textContent = formatPrice(result.price);

    const meta = document.createElement("div");
    meta.className = "result-meta";
    const productDetails = document.createElement("span");
    productDetails.textContent = `${result.product_name} · ${result.detail}`;
    const estimateTag = document.createElement("span");
    estimateTag.className = "estimate-tag";
    estimateTag.textContent = "Precio estimado";
    meta.append(productDetails, estimateTag);
    if (result.store_source === "openstreetmap") {
      const storeSourceTag = document.createElement("span");
      storeSourceTag.className = "store-source-tag";
      storeSourceTag.textContent = "OpenStreetMap";
      meta.append(storeSourceTag);
    }
    item.append(storeDetails, price, meta);

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
    dataNoticeText.textContent = data.data_notice;
    if (userLocation) {
      const storeCount = data.store_count === 1 ? "1 comercio" : `${data.store_count} comercios`;
      locationHelp.textContent = data.store_source === "openstreetmap"
        ? `${storeCount} de OpenStreetMap dentro de 3 km. Los precios se estiman con el promedio de referencia.`
        : "No se pudo consultar OpenStreetMap. Se muestran solo tiendas de ejemplo cercanas, si hay alguna.";
    }
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
  areaName.textContent = "Cerca de ti";
  mapAreaLabel.textContent = "CERCA DE TI";
  locationHelp.textContent = "Buscando hasta 25 comercios dentro de 3 km...";
  const distanceOption = sortSelect.querySelector('option[value="distance"]');
  distanceOption.disabled = false;
  distanceOption.textContent = "Más cercanas";
  sortSelect.value = "distance";
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
    const message = "Tu navegador no permite compartir la ubicación.";
    locationHelp.textContent = message;
    resultCount.textContent = message;
    return;
  }

  locateButton.disabled = true;
  locationHelp.textContent = "Tu navegador te pedirá permiso para compartir la ubicación.";
  resultCount.textContent = "Solicitando ubicación...";
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      locateButton.disabled = false;
      setUserLocation(coords.latitude, coords.longitude);
    },
    (error) => {
      locateButton.disabled = false;
      const message = error.code === 1
        ? "No diste permiso de ubicación. Puedes seguir viendo la lista de ejemplo de Santiago."
        : "No pudimos obtener tu ubicación. Revisa los permisos del navegador e inténtalo otra vez.";
      locationHelp.textContent = message;
      resultCount.textContent = message;
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
  );
});

initializeMap();
loadResults();