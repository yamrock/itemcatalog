from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Item, Base
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine



DBSession = sessionmaker(bind=engine)
session = DBSession()
cat1 = Category(name= "Balls", description = "Spherical objects")
cat2 = Category(name = "Bats", description = "Hand held ball whackers")

item1 = Item(name = "football", description = "Leather sphere with patterns", category = cat1)
#item1.creation_time
item2 = Item(name = "Bowling ball", description = "Plastic sphere heavy", category = cat1)
#item2.creation_time
item3 = Item(name = "Cricket Bat", description = "Wooden and heavy ", category = cat2)
#item3.creation_time
item4 = Item(name = "badminton bat", description = "light and netty", category = cat2)
#item4.creation_time

session.add_all([cat1, cat2])
session.commit()
session.add_all([cat1, cat2])
session.add_all([item1, item2])
session.add_all([item3, item4])
session.commit()

