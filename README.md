# Vitrina

Vitrina es un comparador web de precios de productos cotidianos por tienda y zona. Está construido con Flask y ofrece búsqueda por producto y categoría, orden por precio o cercanía, y un mapa interactivo basado en OpenStreetMap.

## Qué hace y cómo funciona

La aplicación sirve la interfaz desde Flask y busca coincidencias en un catálogo local. La búsqueda normaliza acentos y tolera hasta dos errores de escritura por palabra. Al solicitar tiendas cercanas, el navegador pide permiso para compartir la ubicación y el servidor consulta OpenStreetMap/Overpass para encontrar hasta 25 comercios en un radio de 3 km. Los resultados se pueden ordenar por precio o distancia; la consulta de tiendas se guarda en caché durante 10 minutos.

El catálogo está en `data/catalog.json` e incluye ejemplos de despensa, bebidas, lácteos, cuidado personal y limpieza, con ubicaciones aproximadas y precios estimados en CLP. No son tiendas ni precios reales o verificados. OpenStreetMap aporta nombres y ubicaciones, no precios: para comercios encontrados allí se muestra un promedio del catálogo, marcado como estimado. Si el servicio cartográfico no está disponible, la app avisa y usa los ejemplos cercanos disponibles. La búsqueda manual funciona aunque no se comparta la ubicación.

## Clonar y ejecutar

Se necesita Python 3 y conexión a internet para cargar el mapa y consultar OpenStreetMap. Clona la versión de producción (`main`) y entra al directorio:

```bash
git clone --branch main https://github.com/magdagonzalez-cmyk/bebelin-tiendita.git
cd bebelin-tiendita
```

Crea y activa un entorno virtual. En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instala las dependencias e inicia el servidor:

```bash
python -m pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000 en el navegador.

## Desarrollo y pruebas

Los cambios se trabajan en `develop`; `main` contiene la versión funcional de producción. Después de clonar, cambia a la rama de desarrollo con `git switch develop`.

Ejecuta las pruebas desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -v
```