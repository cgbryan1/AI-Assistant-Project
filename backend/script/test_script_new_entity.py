from ..entities.entity_base import EntityBase
from backend.database import engine

EntityBase.metadata.drop_all(engine)
EntityBase.metadata.create_all(engine)
print("Tables created!")
