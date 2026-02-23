from fastapi import HTTPException
from sqlmodel import SQLModel, Field
from typing import Optional
import random
import smtplib
from email.message import EmailMessage
import datetime
from dotenv import load_dotenv
import os
import security



load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

class Accounts(SQLModel, table=True):
    id: Optional[int] = Field(default = None, primary_key=True)
    user_name : str
    email : str
    balance : float 
    compte_num : str
    hashed_password :str
    
    def deposit(self, amount : float):
        if amount <= 0:
            raise HTTPException(status_code=400, detail="this amount is invalid")
        self.balance += amount    
        return amount
    def withdraw(self, amount : float):
        if amount <= 0:
            raise HTTPException(status_code=400, detail="this amount is invalid")
        
        if amount > self.balance:
            raise HTTPException(status_code=409, detail="You have no money in your account")
        
        self.balance -= amount
        return amount
    

    def user_num(self):
        self.compte_num = str(random.randint(10**13, 10**14 - 1))
#  Random account number
#  Used random.randint with str conversion to generate 14-digit account number
#  Works well with emails and Pydantic

    
    def send_email(self, to_email: str,  subject: str):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = "soufianeelbrnoussi84@gmail.com"
        msg["To"] = to_email
        msg.set_content(f"Your account number is: {self.compte_num}")


        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            

class Transactions(SQLModel, table=True):
    id : Optional[int] = Field(default= None, primary_key=True)
    account_id : int = Field(foreign_key="accounts.id")
    type : str
    amount : float
    date : datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
