from fastapi import FastAPI, Depends, HTTPException
from database import create_db_and_tables ,get_session 
from models import Accounts, Transactions
from sqlmodel import Session, select
from schemas import AccountAdd,AccountRead,BalanceDeposi,BalanceWithdraw,TransactionRead


app = FastAPI()

@app.on_event("startup")
def startup_event():
    create_db_and_tables()
    

@app.get("/")
def the_welcome_space():
    return {"version":"0.0.0"}

@app.post("/create_accounts")
def creat_account(account:AccountAdd,
                  session: Session = Depends(get_session)
    ):
    db_account = Accounts(
        user_name = account.user_name,
        email = account.email,
        balance = account.balance,
    )    
    db_account.user_password()
    db_account.user_num() 
    db_account.send_email( 
            to_email= account.email,
            subject= "The account numbre",
        )    
    
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account



@app.put("/deposit/{user_id}", response_model= BalanceDeposi)
def deposit_money(user_id: int, new_balance:BalanceDeposi ,session : Session = Depends(get_session)): 
            
    account = session.exec(select(Accounts).where(Accounts.id == user_id)).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if new_balance.deposit <= 0:
        raise HTTPException(status_code=400, detail="this amount is invalid")
    
    amount = account.deposit(new_balance.deposit)
    
    
    new_transaction = Transactions(account_id = user_id,
                                   type = "deposit",
                                   amount = new_balance.deposit
                                   )
    
    session.add(new_transaction)
    session.commit()
    session.refresh(account)
    return {"deposit" : amount}


@app.put("/withdraw/{user_id}", response_model = BalanceWithdraw)
def withdraw_money(user_id: int, new_balance:BalanceWithdraw ,session : Session = Depends(get_session)): 
    
    account = session.exec(select(Accounts).where(Accounts.id == user_id)).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
     
    if new_balance.withdraw <= 0:
        raise HTTPException(status_code=400, detail="this amount is invalid")
    
    amount = account.withdraw(new_balance.withdraw)
    
    new_transaction = Transactions(account_id= user_id,
                                   type= "withdraw",
                                   amount = new_balance.withdraw
                                   )
    
    session.add(new_transaction)
    session.commit()
    session.refresh(account)
    return {"withdraw" : amount}
    
    
@app.get("/accounts", response_model=list[AccountRead])
def show_accounts(session: Session = Depends(get_session)):
    accounts = session.exec(select(Accounts)).all()
    return [AccountRead.from_orm(a) for a in accounts]  # ✅ Convert each


@app.get("/accounts/by-number", response_model = AccountRead)
def account_information(compte_num: str, session : Session = Depends(get_session)): 
    account = session.exec(select(Accounts).where(Accounts.compte_num == compte_num)).first()
    if not account :
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.get("/transaction/{user_id}", response_model = list[TransactionRead])
def transaction(user_id: int, session : Session = Depends(get_session)):
    transaction = session.exec(select(Transactions).where(Transactions.account_id == user_id)).all()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return transaction
    

@app.delete("/delete/{user_id}")
def delete_account(user_id: int, session : Session = Depends(get_session)):
    account = session.exec(select(Accounts).where(Accounts.id == user_id)).first()
    if not account:
         raise HTTPException(status_code=404, detail="Account not found")
    
    session.delete(account)
    session.commit()
    return {"status": "Account deleted"}

    