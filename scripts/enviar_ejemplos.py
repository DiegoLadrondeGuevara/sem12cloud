"""Envia las siete peliculas y luego el caso de error para CloudWatch."""

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


EJEMPLOS = Path(__file__).resolve().parents[1] / "ejemplos"


def enviar(url, archivo):
    contenido = archivo.read_bytes()
    solicitud = Request(
        url,
        data=contenido,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        respuesta = urlopen(solicitud, timeout=35)
    except HTTPError as exc:
        respuesta = exc
    with respuesta:
        cuerpo = json.loads(respuesta.read().decode("utf-8"))
        return respuesta.status, cuerpo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL de POST /pelicula/crear obtenida de sls deploy")
    args = parser.parse_args()
    url = args.url.rstrip("/")
    archivos = [EJEMPLOS / f"pelicula_{i:02d}.json" for i in range(1, 8)]
    archivos.append(EJEMPLOS / "pelicula_07_error.json")
    fallos = []
    for archivo in archivos:
        esperado = 400 if archivo.name.endswith("_error.json") else 201
        codigo, cuerpo = enviar(url, archivo)
        print(f"{archivo.name}: HTTP {codigo} - {json.dumps(cuerpo, ensure_ascii=False)}")
        if codigo != esperado:
            fallos.append(archivo.name)
    if fallos:
        raise SystemExit(f"Respuestas inesperadas: {', '.join(fallos)}")


if __name__ == "__main__":
    main()
