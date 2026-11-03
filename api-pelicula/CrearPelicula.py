"""Lambda del taller: guarda peliculas y emite logs JSON para CloudWatch."""

import json
import os
import uuid

import boto3


def _respuesta(status, datos):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(datos, ensure_ascii=False),
    }


def _registrar(tipo, datos):
    print(json.dumps({"tipo": tipo, "log_datos": datos}, ensure_ascii=False))


def _leer_pelicula(event):
    if not isinstance(event, dict):
        raise ValueError("La solicitud debe ser un objeto JSON")

    cuerpo = event.get("body", event)
    if isinstance(cuerpo, str):
        try:
            cuerpo = json.loads(cuerpo)
        except json.JSONDecodeError as exc:
            raise ValueError("El body no contiene JSON valido") from exc
    if not isinstance(cuerpo, dict):
        raise ValueError("El body debe ser un objeto JSON")

    tenant_id = cuerpo.get("tenant_id")
    datos = cuerpo.get("pelicula_datos")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id es obligatorio")
    if not isinstance(datos, dict):
        raise ValueError("pelicula_datos es obligatorio y debe ser un objeto")
    for campo in ("nombre", "genero"):
        if not isinstance(datos.get(campo), str) or not datos[campo].strip():
            raise ValueError(f"pelicula_datos.{campo} es obligatorio")
    for campo in ("fecha", "duracion_minutos"):
        valor = datos.get(campo)
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            raise ValueError(f"pelicula_datos.{campo} debe ser un entero positivo")

    return tenant_id.strip(), datos


def lambda_handler(event, context):
    request_id = getattr(context, "aws_request_id", None)
    try:
        tenant_id, datos = _leer_pelicula(event)
        pelicula = {
            "tenant_id": tenant_id,
            "uuid": str(uuid.uuid4()),
            "pelicula_datos": datos,
        }
        tabla = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
        tabla.put_item(Item=pelicula)
        _registrar("INFO", {**pelicula, "request_id": request_id})
        return _respuesta(201, {"pelicula": pelicula})
    except ValueError as exc:
        _registrar("ERROR", {"error": str(exc), "request_id": request_id})
        return _respuesta(400, {"error": str(exc)})
    except Exception as exc:
        _registrar("ERROR", {
            "error": str(exc),
            "error_tipo": type(exc).__name__,
            "request_id": request_id,
        })
        return _respuesta(500, {"error": "No se pudo crear la pelicula"})
