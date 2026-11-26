# Vitrina

Vitrina es una aplicación web para comparar precios de productos cotidianos por tienda y zona. Está desarrollada con Python y Flask, y ofrece una interfaz responsive con búsqueda, filtros, ordenamiento y un mapa basado en OpenStreetMap.

## Funcionalidades

- Busca productos por nombre, categoría o alias; tolera errores de escritura.
- Filtra por categoría y ordena los resultados por precio o distancia.
- Muestra comercios y precios de ejemplo en CLP, con datos incluidos en `data/catalog.json`.
- Permite buscar comercios cercanos usando la ubicación del navegador y OpenStreetMap/Overpass.
- Si no se puede consultar Overpass, informa del problema y recurre a los comercios de ejemplo que estén cerca.

Los precios del catálogo son estimados y no representan precios reales verificados. OpenStreetMap proporciona ubicaciones, no precios: para comercios obtenidos del mapa, el precio mostrado es un promedio de referencia del catálogo. La aplicación no necesita una base de datos. El mapa y la búsqueda por ubicación requieren conexión a internet; la búsqueda manual funciona sin compartir la ubicación.

## Requisitos

- Python 3.10 o posterior.
- `pip`.
- Conexión a internet para cargar el mapa y buscar comercios cercanos.

## Instalación y ejecución

Clona el repositorio y entra en su directorio:

```bash
git clone https://github.com/magdagonzalez-cmyk/bebelin-tiendita.git
cd bebelin-tiendita
```

Crea y activa un entorno virtual. En Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala las dependencias e inicia la aplicación:

```bash
python -m pip install -r requirements.txt
python app.py
```

Abre <http://127.0.0.1:5000> en el navegador. Si PowerShell bloquea la activación del entorno virtual, puedes ejecutar `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` y `.\.venv\Scripts\python.exe app.py` sin activarlo.

## Pruebas

Con el entorno virtual activado, ejecuta:

```bash
python -m unittest discover -s tests -v
```

## API

- `GET /`: página principal.
- `GET /api/categories`: categorías disponibles.
- `GET /api/search?q=pan`: busca productos; acepta opcionalmente `category`, `sort`, `lat` y `lng`. Para ordenar por distancia o buscar comercios cercanos, envía ambas coordenadas.

## Ramas

- `main`: versión funcional destinada a producción.
- `develop`: rama para el desarrollo, cambios y correcciones.
