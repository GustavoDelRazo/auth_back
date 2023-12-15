CREATE TABLE contactos (
    email varchar(100) PRIMARY KEY,
    nombre varchar(50),
    telefono varchar(12)
);

INSERT INTO contactos (email, nombre, telefono)
VALUES ("juan@example.com", "Juan Pérez", "555-123-4567");

INSERT INTO contactos (email, nombre, telefono)
VALUES ("maria@example.com", "María García", "555-678-9012");

CREATE TABLE usuarios (
    username varchar,
    password varchar,
    token varchar,
    timestamp timestamp
);

INSERT INTO usuarios (username, password, token, timestamp) 
VALUES ('brallan@gmail.com', '202cb962ac59075b964b07152d234b70', '8faa5dc3e625849d45ca9578d32dd683', CURRENT_TIMESTAMP);

INSERT INTO usuarios (username, password, token, timestamp) 
VALUES ('josue@gmail.com', '827ccb0eea8a706c4c34a16891f84e7b', '560faebe9b3219dddc0ac2b34a08371b', CURRENT_TIMESTAMP);