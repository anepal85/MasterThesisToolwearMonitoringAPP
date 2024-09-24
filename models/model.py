from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from database.get_db import DatabaseFactory 
import hashlib

def generate_password_hash(password):
    """Generate a SHA-256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(password_hash, password):
    """Check if the provided password matches the hashed password."""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

Base = declarative_base()

class UserDB(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    label_studio_api_key = Column(String) 

    def __init__(self, name, password, is_admin=False, label_studio_api_key = None):
        self.name = name
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin 
        self.label_studio_api_key = label_studio_api_key

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DinoImageDB(Base):
    __tablename__ = 'dino_image'

    id = Column(Integer, primary_key=True)
    toolwear_damage_id = Column(Integer, ForeignKey('toolwear_damage.id')) 
    image_path = Column(String)
    magnification = Column(Float)
    fovx = Column(Float)
    fovy = Column(Float) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    toolwear_damage = relationship('ToolWearDamageDB')
    
class MLModelDB(Base):
    __tablename__ = 'ml_model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ml_model_path = Column(String)  
    epochs_trained = Column(Integer, default=200)
    input_im_width = Column(Integer, default=512)
    input_im_height = Column(Integer, default=512)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Define the UserInputToolWearData class
class UserInputToolWearDB(Base):
    __tablename__ = 'user_toolwear'

    id = Column(Integer, primary_key=True)
    werkstoff = Column(String)
    definierter_vbmax_value = Column(Float)
    definierter_vbmax_unit = Column(String)
    schnittgeschwindigkeit_value = Column(Float)
    schnittgeschwindigkeit_unit = Column(String)
    vorschub_value = Column(Float)
    vorschub_unit = Column(String)
    schnitttiefe_value = Column(Float)
    schnitttiefe_unit = Column(String)
    kühlung = Column(String)
    werkzeugtyp = Column(String)
    schneidstoff = Column(String)
    schneide = Column(String)
    beschichtung = Column(String)
    surface = Column(String)
    images_folder = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey('user.id'))

    user = relationship('UserDB')

class CompletedProcessNumber(Base):
    __tablename__ = 'completed_process_number'
    process_number = Column(Integer, primary_key=True)

 

class ToolWearDamageDB(Base):
    __tablename__ = 'toolwear_damage'

    id = Column(Integer, primary_key=True)
    ml_model_id = Column(Integer, ForeignKey('ml_model.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user_data_id = Column(Integer, ForeignKey('user_toolwear.id'))  # Add foreign key to UserData table
    damage_area_pixel = Column(Integer)
    damage_area = Column(Float)
    damage_up = Column(Float)
    damage_down = Column(Float)
    process_number = Column(Integer, ForeignKey('completed_process_number.process_number'))
    is_manual = Column(Boolean, default=False)
    y_algo = Column(Integer, default=0)
    y_manual = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    correct_prediction = Column(Boolean, default=True)

    # Define relationships
    model = relationship('MLModelDB')
    user = relationship('UserDB')
    userinput_toolwear_damage  = relationship("UserInputToolWearDB")
    process = relationship('CompletedProcessNumber')

Base.metadata.create_all(DatabaseFactory.create_connection('sqlite'))