from pydantic import BaseModel, Field
from typing import Optional
import datetime

class AccountUser(BaseModel):
    user_name: str
    email: str
    password:str
    balance: float = Field(ge=0) # Field(ge=0) to stoped the user from enter a negative balance
    admin_code: Optional[str] = None
    
class AccountAdmin(BaseModel):
    user_name: str
    email: str
    password:str
    admin_code: Optional[str] = None
        
    
class AccountRead(BaseModel):
    id: int
    user_name: str
    email: str
    balance: float 
    compte_num: str
    model_config = {
        "from_attributes": True  # ✅ v2 replacement for orm_mode
    }
    
class BalanceDeposi(BaseModel):
    deposit: float 
    
class BalanceWithdraw(BaseModel):
    withdraw: float
    

class TransactionRead(BaseModel):
    account_id: int
    type: str
    amount: float
    date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class LoginUser(BaseModel):
    email: str
    password: str
    

class LoginAdmin(BaseModel):
    admin_num: str
    password: str
    
