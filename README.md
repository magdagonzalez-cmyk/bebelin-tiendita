# Vitrina

Comparador de precios de productos cotidianos por tienda y zona. Está construido con Flask y sirve una interfaz web responsive con mapa de OpenStreetMap.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

En Windows PowerShell, activa el entorno con `.venv\Scripts\Activate.ps1`. Después abre http://127.0.0.1:5000.

## Probar

```bash
python -m unittest discover -s tests -v
```

## Datos

El catálogo está en `data/catalog.json` y contiene ejemplos de despensa, bebidas, lácteos, cuidado personal y limpieza del hogar, con ubicaciones aproximadas y precios estimados en CLP. No representa tiendas o precios reales ni verificados.

La búsqueda tolera hasta dos errores de escritura por palabra. «Buscar cerca de mí» solicita permiso del navegador solo después de pulsarlo; si se concede, consulta OpenStreetMap/Overpass para encontrar hasta 25 comercios en un radio de 3 km y los ordena por cercanía. La consulta se mantiene en caché temporal durante 10 minutos para limitar solicitudes repetidas. La cobertura depende de los datos cartográficos disponibles en cada zona.

OpenStreetMap aporta nombres y ubicaciones, no precios. Para comercios encontrados allí, el precio que aparece es un promedio de los precios de ejemplo del catálogo y está marcado como estimado; no es una cotización real. Si Overpass está ocupado o no responde, la app avisa y solo usa ejemplos de Santiago que estén cerca de la ubicación compartida. Para precios reales falta conectar una fuente comercial o cargar datos verificados y actualizados.

El mapa y la búsqueda de comercios usan servicios públicos de OpenStreetMap y requieren conexión a internet. Si el navegador no concede ubicación, la búsqueda manual sigue disponible.