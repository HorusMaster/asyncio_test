#"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"

import aiohttp
import asyncio
from random import randint
from time import perf_counter

async def get_random_pokemon():
    async with aiohttp.ClientSession() as session:
        pokemon_id = randint(1,800)
        pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
        async with session.get(pokemon_url) as res:
            pokemon = await res.json()
            pokemon_name = pokemon.get("name")
            return pokemon_name        

async def main():
    time_now = perf_counter()
    tasks = []   
    for _ in range(40):
        tasks.append(asyncio.create_task(get_random_pokemon()))         
    pokemon_names = await asyncio.gather(*tasks)
    print(pokemon_names)  
    print(f"Time took: {perf_counter()-time_now}")
if __name__ == "__main__":
    asyncio.run(main())