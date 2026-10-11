from app.db.database import engine
from app.db.models import Base

from app.services.ingestion import ingest

import json



def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database created")

    with open("./data/input/workouts_export_1791117041_3017C9B0.json") as file:
        data = json.load(file)

        ingest(data, 1)


    
