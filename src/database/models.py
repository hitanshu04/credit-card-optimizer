from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CreditCard(Base):
    __tablename__ = 'credit_cards'

    # Core Information
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_name = Column(String, nullable=False, unique=True)
    network = Column(String) # Visa, Mastercard, etc.
    primary_category = Column(String) # Cashback, Rewards, etc.
    
    # Fees Section
    joining_fee = Column(String)
    renewal_fee = Column(String)
    waiver_threshold = Column(String)
    
    # Rewards Section
    reward_type = Column(String)
    reward_rate = Column(Text)
    reward_multiplier = Column(Text)
    inr_value_per_unit = Column(String)
    reward_expiry = Column(String)
    
    # Perks Section
    lounge_domestic = Column(String)
    lounge_international = Column(String)
    movie_benefits = Column(Text)
    golf_benefits = Column(Text)
    other_perks = Column(Text)
    
    # Other Benefits
    welcome_benefits = Column(Text)
    milestone_benefits = Column(Text)
    special_tie_ups = Column(Text)
    earning_caps = Column(Text)
    redemption_options = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CreditCard(name='{self.card_name}')>"