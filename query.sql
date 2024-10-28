
-- For creating table in database--
CREATE TABLE pokemons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type1 VARCHAR(100) NOT NULL,
    type2 VARCHAR(100),
    total INT NOT NULL,
    hp INT NOT NULL,
    attack INT NOT NULL,
    defense INT NOT NULL,
    sp_attack INT NOT NULL,
    sp_defense INT NOT NULL,
    speed INT NOT NULL
);



-- inserting values to the table --
INSERT INTO pokemons (name, type1, type2, total, hp, attack, defense, sp_attack, sp_defense, speed) VALUES
    ('Pikachu', 'Electric', NULL, 320, 35, 55, 40, 50, 50, 90),
    ('Jigglypuff', 'Normal', 'Fairy', 270, 115, 45, 20, 45, 25, 20),
    ('Zubat', 'Poison', 'Flying', 245, 40, 45, 40, 30, 40, 55);