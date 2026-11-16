#!/bin/bash

curl -X PUT "http://localhost:9200/articulos"

curl -X POST "http://localhost:9200/articulos/_doc/1" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Portatil","precio":850}'
