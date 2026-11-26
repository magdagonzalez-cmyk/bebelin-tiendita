# Vitrina

<<<<<<< HEAD
Vitrina es una aplicación web para comparar precios de productos cotidianos por tienda y zona. Está desarrollada con Python y Flask, y ofrece una interfaz responsive con búsqueda, filtros, ordenamiento y un mapa basado en OpenStreetMap.

## Funcionalidades

- Busca productos por nombre, categoría o alias; tolera errores de escritura.
- Filtra por categoría y ordena los resultados por precio o distancia.
- Muestra comercios y precios de ejemplo en CLP, con datos incluidos en `data/catalog.json`.
- Permite buscar comercios cercanos usando la ubicación del navegador y OpenStreetMap/Overpass.
- Si no se puede consultar Overpass, informa del problema y recurre a los comercios de ejemplo que estén cerca.
=======
Vitrina es una aplicación web para comparar precios de productos cotidianos por tienda y zona. Está desarrollada con Python y Flask, y ofrece búsqueda por producto y categoría, ordenamiento por precio o cercanía y un mapa de OpenStreetMap.

## Funcionalidades

- Busca productos por nombre, categoría o alias; normaliza acentos y tolera errores de escritura.
- Filtra por categoría y ordena los resultados por precio o distancia.
- Muestra comercios y precios de ejemplo en CLP desde `data/catalog.json`.
- Permite buscar hasta 25 comercios cercanos en un radio de 3 km usando la ubicación del navegador y OpenStreetMap/Overpass; las consultas se guardan en caché durante 10 minutos.
- Si Overpass no está disponible, informa del problema y recurre a los comercios de ejemplo que estén cerca.
>>>>>>> develop

Los precios del catálogo son estimados y no representan precios reales verificados. OpenStreetMap proporciona ubicaciones, no precios: para comercios obtenidos del mapa, el precio mostrado es un promedio de referencia del catálogo. La aplicación no necesita una base de datos. El mapa y la búsqueda por ubicación requieren conexión a internet; la búsqueda manual funciona sin compartir la ubicación.

## Requisitos

- Python 3.10 o posterior.
- `pip`.
- Conexión a internet para cargar el mapa y buscar comercios cercanos.

<<<<<<< HEAD
## Instalación y ejecución

Clona el repositorio y entra en su directorio:
=======
## Clonar y ejecutar

Clona la versión funcional de producción (`main`) y entra en el directorio:

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
>>>>>>> develop

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

<<<<<<< HEAD
Instala las dependencias e inicia la aplicación:
=======
Instala las dependencias e inicia el servidor:
>>>>>>> develop

```bash
python -m pip install -r requirements.txt
python app.py
```

<<<<<<< HEAD
Abre <http://127.0.0.1:5000> en el navegador. Si PowerShell bloquea la activación del entorno virtual, puedes ejecutar `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` y `.\.venv\Scripts\python.exe app.py` sin activarlo.

## Pruebas

Con el entorno virtual activado, ejecuta:
=======
Abre <http://127.0.0.1:5000> en el navegador. Si PowerShell bloquea la activación del entorno virtual, puedes ejecutar `\.venv\Scripts\python.exe -m pip install -r requirements.txt` y `\.venv\Scripts\python.exe app.py` sin activarlo.

## Pruebas

Con el entorno virtual activado, ejecuta desde la raíz del proyecto:
>>>>>>> develop

```bash
python -m unittest discover -s tests -v
```

## API

- `GET /`: página principal.
- `GET /api/categories`: categorías disponibles.
- `GET /api/search?q=pan`: busca productos; acepta opcionalmente `category`, `sort`, `lat` y `lng`. Para ordenar por distancia o buscar comercios cercanos, envía ambas coordenadas.

## Ramas

- `main`: versión funcional destinada a producción.
<<<<<<< HEAD
- `develop`: rama para el desarrollo, cambios y correcciones.
=======
- `develop`: rama para el desarrollo, cambios y correcciones.
>>>>>>> develop
