from faker import Faker

fake = Faker()


def generate_pokemon_data():
    return {
        "name": fake.word(),
        "type1": fake.word(),
        "type2": fake.word(),
        "total": fake.random_int(min=200, max=600),
        "hp": fake.random_int(min=30, max=150),
        "attack": fake.random_int(min=30, max=150),
        "defense": fake.random_int(min=30, max=150),
        "sp_atk": fake.random_int(min=30, max=150),
        "sp_def": fake.random_int(min=30, max=150),
        "speed": fake.random_int(min=30, max=150),
        "generation": fake.random_int(min=1, max=7),
        "legendary": fake.boolean(),
    }
