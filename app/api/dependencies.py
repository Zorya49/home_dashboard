from sqlalchemy import select
from typing import Annotated
from fastapi import Header, HTTPException, Depends

from app.db.database import SessionLocal
from app.db.models import Person
from app.config import ingestion_token_me, ingestion_token_spouse

def authenticated_person_id(authorization: Annotated[str | None, Header()] = None) -> int:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing credentials")

    scheme, separator, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not separator or not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if token == ingestion_token_me():
        external_identifier = "me"
    elif token == ingestion_token_spouse():
        external_identifier = "spouse"
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

    with SessionLocal() as session:
        person_id = session.scalar(
            select(Person.id).where(Person.external_identifier == external_identifier)
        )

    if person_id is None:
        raise HTTPException(status_code=500, detail="Authenticated person does not exist")

    return person_id
