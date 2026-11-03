# Semana 12 - Taller 1: CloudWatch

Proyecto de `api-pelicula` y ejercicio propuesto de la clase **CS2032 Cloud Computing**. El enunciado original está en [`material/`](material/). Se conservaron los siete JSON entregados y las consultas originales en [`consultas/Queries_Logs_Insights_original.txt`](consultas/Queries_Logs_Insights_original.txt).

## Qué pide el taller

1. Registrar logs desde una Lambda que crea películas en DynamoDB.
2. Subir el proyecto a GitHub, configurar `org`, `LabRole` y credenciales Academy, y ejecutar `sls deploy`.
3. Enviar siete películas y revisar sus ejecuciones en CloudWatch.
4. Ejecutar consultas de Logs Insights para métricas, películas, géneros y errores.
5. **Ejercicio propuesto (30 puntos):** agregar `try/except`, emitir cada log como JSON `{"tipo":"INFO|ERROR","log_datos":{...}}`, adaptar las consultas a ese formato y subir evidencias al Padlet.

## Proyecto implementado

- `api-pelicula/CrearPelicula.py` valida la solicitud, escribe en DynamoDB y emite un único log JSON `INFO` por creación o `ERROR` por fallo.
- API Gateway usa integración Lambda proxy. `POST /pelicula/crear` devuelve HTTP 201, 400 o 500 y un cuerpo JSON.
- `ejemplos/pelicula_01.json` a `pelicula_07.json` son siete solicitudes válidas. `pelicula_07_error.json` conserva la clave incorrecta `pelicula_patos` para generar un `ERROR` y HTTP 400.
- [`consultas/Queries_Logs_Insights.txt`](consultas/Queries_Logs_Insights.txt) contiene consultas adaptadas al nuevo formato. Los campos de película ahora están debajo de `log_datos`.

## Desplegar en AWS Academy

Requisitos: cuenta AWS Academy **904208419583**, credenciales vigentes con permiso para CloudFormation, Lambda, API Gateway, DynamoDB y CloudWatch, y Node.js. El `serverless.yml` ya tiene `org: diegoladrondeguevara` y `arn:aws:iam::904208419583:role/LabRole`. Se usa Python 3.11 porque Serverless Framework v3.40.0 rechaza `python3.12` al validar la configuración.

1. Renueva las credenciales de AWS Academy en tu perfil local. No las subas al repositorio.
2. Verifica la cuenta activa: `aws sts get-caller-identity --query Account --output text`. Debe mostrar `904208419583`.
3. Entra a `api-pelicula` y ejecuta `npm ci` y luego `npx serverless deploy --stage dev --region us-east-1`. Si Serverless solicita autenticación por `org`, inicia sesión en tu cuenta Serverless correspondiente.
4. Guarda la URL `POST /pelicula/crear` que imprime el despliegue. El nombre de la tabla es `dev-t_peliculas` y el grupo de logs es `/aws/lambda/api-pelicula-dev-crear`.
5. Desde la raíz del repositorio, ejecuta `python scripts/enviar_ejemplos.py "URL_COMPLETA_DE_POST"`. Espera siete HTTP 201 y un HTTP 400.

El rol de Academy debe permitir escribir en DynamoDB y en CloudWatch Logs. Si el despliegue falla por un permiso del laboratorio, conserva el mensaje exacto para diagnosticarlo.

## Capturas para el documento de evidencia

Toma estas capturas **durante** los pasos indicados; no incluyas claves AWS:

1. **GitHub:** árbol del repositorio con `api-pelicula`, `ejemplos`, `consultas` y `material`.
2. **Despliegue:** terminal al terminar `serverless deploy`, con el endpoint y nombre de la función.
3. **Ejecución correcta:** respuesta HTTP 201 de una película en Postman o el script y, en CloudWatch, el evento JSON con `tipo: INFO`, `log_datos.pelicula_datos` y `uuid`.
4. **Siete películas:** vista de DynamoDB con siete elementos o consulta 3 de Logs Insights con siete resultados.
5. **Métricas:** consulta 2 con `@billedDuration` y `@memorySize`.
6. **Consultas de datos:** consultas 5 y 6 con películas de Terror y conteo por género.
7. **Error controlado:** respuesta HTTP 400 al enviar `pelicula_07_error.json`, su evento JSON con `tipo: ERROR` y resultado de la consulta 7.
8. **Código:** fragmento de `CrearPelicula.py` donde se ven `try/except` y `_registrar`.

Coloca las capturas en un documento con títulos y una breve explicación del resultado, y sube ese documento al Padlet indicado por el docente. No hay un enlace de Padlet en el PDF.

## Prueba local

Desde la raíz del repositorio: `python -m unittest discover -s tests -v`.
