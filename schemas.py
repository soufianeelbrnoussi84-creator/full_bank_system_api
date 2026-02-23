from pydantic import BaseModel, Field
import datetime

class AccountAdd(BaseModel):
    user_name : str
    email : str
    password :str
    balance : float = Field(ge=0) # Field(ge=0) to stoped the user from enter a negative balance 
    
    
class AccountRead(BaseModel):
    id : int
    user_name : str
    email : str
    balance : float 
    compte_num : str
    model_config = {
        "from_attributes": True  # ✅ v2 replacement for orm_mode
    }
    
class BalanceDeposi(BaseModel):
    deposit : float 
    
class BalanceWithdraw(BaseModel):
    withdraw : float
    

class TransactionRead(BaseModel):
     account_id : int
     type : str
     amount : float
     date : datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
     