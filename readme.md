Prerequisites
Installation and setup

Python 3.9
PostgreSQL
pip for managing Python packages
Installation
Clone this repository:

git clone https://github.com/PragatiBhutal/fastapinew.git
cd fastapinew
Install the required Python packages:

pip install -r requirements.txt
Pokémon API
A FastAPI to manage Pokémon data, including CRUD operations, searching, sorting, and bulk data insertion.

Features
POST /pokemons/ - Creates a new Pokémon with the provided details.
POST /pokemons/post/ - Loads Pokémon data in bulk from a predefined external URL: Pokémon Data.
GET /pokemons/{pokemon_id} - Retrieves a Pokémon by its ID.
PUT /pokemons/{pokemon_id} - Updates an existing Pokémon by its ID.
DELETE /pokemons/{pokemon_id} - Deletes a Pokémon by its ID.