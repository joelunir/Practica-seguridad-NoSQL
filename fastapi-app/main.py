from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, HTTPException, Query
from pydantic import BaseModel, ConfigDict, StrictStr
from pymongo import MongoClient
import os, requests
import logging

# Configuracion del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seguridad_api")

#Creación FastAPI
app = FastAPI(title="API NoSQL (protegida)")

#Rate Limiting
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

#Conexión autenticada a MongoDB
mongo = MongoClient(
    host=os.getenv("MONGO_HOST", "mongo"),
    port=27017,
    username=os.environ["MONGO_USER"],
    password=os.environ["MONGO_PASSWORD"],
    authSource="tienda"
)
db = mongo[os.getenv("MONGO_DATABASE", "tienda")]

# Validación de entradas mediante Pydantic
class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: StrictStr
    password: StrictStr

class Pedido(BaseModel):
    producto: str
    cantidad: int

# Middleware para registrar peticiones HTTP
@app.middleware("http")
async def registrar_peticion(request: Request, call_next):
    response = await call_next(request)

    logger.info(
        "Peticion HTTP: metodo=%s ruta=%s estado=%s",
        request.method,
        request.url.path,
        response.status_code
    )

    return response

#Endpoint de autenticación MongoDB con Rate Limiting
@app.post("/login_mongo")
@limiter.limit("5/minute")
def login(request: Request, data: Login):
    user = db.usuarios.find_one(
        {
            "username": data.username,
            "password": data.password
        },
        {"_id": 0}
    )
    if user:
        logger.info(
            "Autenticacion correcta en /login_mongo"
        )
        return {"msg": "ok"}

    logger.warning(
        "Intento de autenticacion fallido en /login_mongo"
    )

    raise HTTPException(
        status_code=401,
        detail="Bad creds"
    )



# Endpoint de busqueda en Elasticsearch

@app.get("/articulos")
def art_search(
    q: str = Query(default="", max_length=100),
    page: int = Query(default=1, ge=1, le=100),
    size: int = Query(default=10, ge=1, le=50)
):
    inicio = (page - 1) * size

    if q.strip():
        consulta = {
            "match": {
                "nombre": q.strip()
            }
        }
    else:
        consulta = {
            "match_all": {}
        }

    cuerpo = {
        "query": consulta,
        "from": inicio,
        "size": size
    }

    try:
        response = requests.post(
            "http://elasticsearch:9200/articulos/_search",
            json=cuerpo,
            timeout=10
        )
        response.raise_for_status()

    except requests.RequestException:
        logger.exception("Error al consultar Elasticsearch")
        raise HTTPException(
            status_code=502,
            detail="Error al consultar el servicio de busqueda"
        )

    resultado = response.json()

    return {
        "pagina": page,
        "tamano_pagina": size,
        "total": resultado["hits"]["total"]["value"],
        "articulos": [
            hit["_source"]
            for hit in resultado["hits"]["hits"]
        ]
    }

