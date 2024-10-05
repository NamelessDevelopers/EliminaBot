import asyncio
import csv
import json
import math
import os

import requests
from guild_copy import Guild
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


async def get_guild_name(guild_id: int) -> str | None:
    headers = {
        "Authorization": f"Bot {os.environ["BOT_TOKEN"]}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://github.com/Rapptz/discord.py 2.3.2)"
    }
    req = requests.get(
        f"https://discord.com/api/v10/guilds/{guild_id}", headers=headers
    )
    res = req.json()
    match req.status_code:
        case 200:
            name = res["name"]
            if "code" in res and res["code"] == 10004:
                return ""
            return name
        case 429:
            await asyncio.wait(math.ceil(res["retry_after"]))
            return None
        case _:
            return None

async def migrate() -> None:
    engine = create_engine(os.environ["DB_URI"])
    with Session(engine) as session:
        with open("channel_sheet.csv") as file:
            sheet = csv.reader(file)
            skip_first_row = True
            for row in sheet:
                if skip_first_row:
                    skip_first_row = False
                    continue
                row = [int(elem.strip()) for elem in row if elem]
                guild_id, delete_delay, image_snipe = row[:3]
                toggled_channels = row[3:]
                guild_name = await get_guild_name(guild_id)
                if not guild_name:
                    print(f"bot not present in {guild_id}. skipping...")
                    continue
                while guild_name is None:
                    guild_name = await get_guild_name(guild_id)
                guild = Guild(
                    id=guild_id,
                    name=guild_name,
                    delete_delay=delete_delay,
                    image_snipe=bool(image_snipe),
                    toggled_channels=json.dumps(toggled_channels)
                )
                print(f"added {guild}")
                session.add(guild)
                session.flush()
            session.commit()

asyncio.run(migrate())
