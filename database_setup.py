from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import datetime
 
Base = declarative_base()

class Category(Base):
    '''
    The category table will be used to record the different categories of the items. 
    It will be identified by the id column and will have a name and description
    The id will be used as foreign-key in the 'items' table, for cross reference
    '''
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=False)

    @property
    def serialize(self):
        return {
                'name': self.name,
                'id' : self.id,
                'desc' : self.description
                }

 
class Item(Base):
    '''
    Any one item belongs only to one category. However, one category may have multiple items (Category: Item = One : Many)
    The Item table will be used to store items of a category. 
    The backref 'items' is equivalent to having an 'items' column in category to refer the items in the category
    '''
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=False)
    creation_time = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref=backref('items', uselist = True, cascade="all,delete"))

    @property
    def serialize(self):
        return {
                'id' : self.id,
                'name' : self.name,
                'desc' : self.description,
                'cat_id' : self.category_id
                }

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=False)



engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)
