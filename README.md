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

El catálogo está en `data/catalog.json` y contiene ejemplos de despensa, bebidas, lácteos, cuidado personal y limpieza del hogar, con ubicaciones aproximadas y precios estimados en CLP. No representa tiendas o precios reales ni verificados. El botón «Mi ubicación» ordena las opciones por cercanía a la posición que la persona decida compartir.

Para operar con datos reales hace falta acordar un proveedor o formato de carga, confirmar la zona exacta de cobertura y definir cómo se validan y actualizan los precios. No se debe presentar un precio inferido como confirmado: los datos cargados o estimados deben identificarse por separado.

El mapa usa teselas públicas de OpenStreetMap y requiere conexión a internet.