Estructura del proyecto

practica-seguridadNoSQL-docker/
├── compose.yaml
├── init_mongo.js
├── init_elastic.sh
├── fastapi-app/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── .gitignore
└── README.md



Ejecución

Requisitos: Docker y Docker Compose.

Configurar las variables de entorno MONGO_USER y MONGO_PASSWORD en un archivo .env local.

Preparar los servicios y los datos iniciales según las instrucciones de la práctica.

Ejecutar los contenedores:

docker compose up -d --build

Consultar el estado:

docker compose ps



Autor

Proyecto académico de Seguridad en Bases de Datos, Blockchain y Big Data de UNIR.
