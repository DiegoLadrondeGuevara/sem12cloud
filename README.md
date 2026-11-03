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

## Desplegar desde la EC2 de AWS Academy

Requisitos: cuenta AWS Academy **904208419583**, credenciales temporales vigentes con permiso para CloudFormation, Lambda, API Gateway, DynamoDB y CloudWatch, además de Git, Node.js, npm y Python 3 en la EC2. El `serverless.yml` ya tiene `org: diegoladrondeguevara` y `arn:aws:iam::904208419583:role/LabRole`. Ese ARN identifica el rol de ejecución de Lambda; **no sustituye** las credenciales temporales necesarias para que Serverless haga el despliegue. Se usa Python 3.11 porque Serverless Framework v3.40.0 rechaza `python3.12` al validar la configuración.

1. En la EC2, clona el repositorio: `git clone https://github.com/DiegoLadrondeGuevara/sem12cloud.git` y `cd sem12cloud/api-pelicula`.
2. En `~/.aws/credentials`, agrega un perfil `[academy]` con los tres valores temporales obtenidos de **AWS Academy > AWS Details > AWS CLI**: `aws_access_key_id`, `aws_secret_access_key` y `aws_session_token`. Conserva cualquier perfil anterior. No compartas ese archivo ni lo subas a GitHub. Ejecuta `chmod 600 ~/.aws/credentials`.
3. Si la EC2 tiene variables AWS de otra cuenta, ejecuta `unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN`. Verifica: `aws sts get-caller-identity --profile academy --query Account --output text`. Debe mostrar **904208419583**. Si muestra otra cuenta, detente y corrige el perfil antes de desplegar.
4. En `api-pelicula`, ejecuta `npm ci` y `AWS_PROFILE=academy npx serverless deploy --stage dev --region us-east-1`. Si Serverless solicita autenticación por `org`, inicia sesión en la organización Serverless correspondiente. Este inicio de sesión es distinto de las credenciales AWS Academy.
5. Copia la URL completa de `POST /pelicula/crear` que imprime el despliegue. El nombre de la tabla es `dev-t_peliculas` y el grupo de logs es `/aws/lambda/api-pelicula-dev-crear`.
6. Regresa a la raíz (`cd ..`) y ejecuta `python3 scripts/enviar_ejemplos.py "URL_COMPLETA_DE_POST"`. Espera **siete HTTP 201** y después **un HTTP 400** del ejemplo con error.
7. En la consola AWS, revisa la tabla DynamoDB, el grupo de logs y las consultas de [`consultas/Queries_Logs_Insights.txt`](consultas/Queries_Logs_Insights.txt). Usa cada consulta por separado en Logs Insights.

El rol de Academy debe permitir escribir en DynamoDB y CloudWatch Logs. Si el despliegue falla por un permiso del laboratorio, conserva el mensaje exacto para diagnosticarlo.

## Capturas para el documento de evidencia

Toma estas capturas **durante** los pasos indicados; no incluyas claves AWS:

1. **Ahora, antes de usar la EC2:** árbol de GitHub con `api-pelicula`, `ejemplos`, `consultas` y `material`; y fragmento de `CrearPelicula.py` con `try/except` y `_registrar`.
2. **Al terminar el paso 4:** terminal con `serverless deploy` exitoso, endpoint y nombre de la función.
3. **Al terminar el paso 6:** salida del script con siete HTTP 201 y un HTTP 400. Si usas Postman, captura una respuesta 201 y la respuesta 400 del ejemplo con error.
4. **En el paso 7:** tabla DynamoDB con siete elementos; evento CloudWatch `INFO` con `log_datos.pelicula_datos` y `uuid`; evento `ERROR` con `log_datos.error`.
5. **En el paso 7, Logs Insights:** consulta 2 para `@billedDuration` y `@memorySize`; consultas 5 y 6 para Terror y conteo por género; consulta 7 para errores. Captura el texto de cada consulta y su resultado.

**No tomes capturas** del archivo `~/.aws/credentials`, del proceso de pegar credenciales, de `npm ci` ni de la simple verificación de cuenta. Estos pasos no demuestran el resultado del ejercicio y podrían exponer datos sensibles.

Coloca las capturas en un documento con títulos y una breve explicación del resultado, y sube ese documento al Padlet indicado por el docente. No hay un enlace de Padlet en el PDF.

## Prueba local

Desde la raíz del repositorio: `python -m unittest discover -s tests -v`.
