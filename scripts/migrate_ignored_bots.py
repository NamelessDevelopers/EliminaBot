import asyncio
import csv
import json
import os

from guild_copy import Guild
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


async def migrate() -> None:
    engine = create_engine(os.environ["DB_URI"])
    with Session(engine) as session:
        with open("bot_sheet.csv") as file:
            sheet = csv.reader(file)
            skip_first_row = True
            for row in sheet:
                if skip_first_row:
                    skip_first_row = False
                    continue
                row = [int(elem.strip()) for elem in row if elem]
                guild_id = row[0]
                ignored_bots = row[1:]
                guild = session.get(Guild, {"id": guild_id})
                if not guild:
                    continue
                guild.ignored_bots = json.dumps(ignored_bots)
                session.flush()
                print(f"updated {guild}")
            session.commit()


asyncio.run(migrate())
