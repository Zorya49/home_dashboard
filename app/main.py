from app.db.database import SessionLocal, engine
from app.db.models import Base, Person

from app.services.ingestion import ingest

import json

PEOPLE = {1: "Person1"}



def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as session:
        for person_id, name in PEOPLE.items():
            session.merge(Person(id=person_id, name=name))


if __name__ == "__main__":
    init_db()

    with open("./data/input/workouts_export_1791117041_3017C9B0.json") as file:
        data = json.load(file)
        ingest(data, 1)

    # with open("./data/input/health_export_1791116863_F1C1FAA6.json") as file:
    #     data = json.load(file)
    #     ingest(data, 1)


    
