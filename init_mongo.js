db = db.getSiblingDB("tienda");

db.usuarios.insertMany([
    {username: "alice", password: "1234"},
    {username: "bob", password: "5678"}
]);

db.pedidos.insertMany([
    {producto: "Portatil", cantidad: 2},
    {producto: "Monitor", cantidad: 1}
]);
