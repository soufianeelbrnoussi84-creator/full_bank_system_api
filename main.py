from fastapi import FastAPI, Depends, HTTPException
from database import create_db_and_tables ,get_session 
from models import Accounts, Transactions,UserRole
from sqlmodel import Session, select
from schemas import AccountUser,AccountRead,BalanceDeposi,BalanceWithdraw,TransactionRead,LoginUser,AccountAdmin
from security import hash_password, verify_password, create_access_token, get_current_user, get_current_admin
from admin_setup import create_main_admin, admin_num




app = FastAPI()



@app.on_event("startup")
def startup_event():
    create_db_and_tables()
    create_main_admin()


    

@app.post("/login")
def login(data: LoginUser, session: Session = Depends(get_session)):
    email = data.email
    password = data.password
    user = session.exec(select(Accounts).where(Accounts.email == email)).first()
        
    if not user:
        raise HTTPException(status_code=400, detail="invalid email")
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail= "invalid password")  
        
    access_token = create_access_token(
        data={"sub": user.email}
    ) 
    return{
        "access_token": access_token,
        "token_type": "bearer"
    } 
          

@app.post("/register")
def creat_user(account:AccountUser,
                  session: Session = Depends(get_session)
    ):
    
    hashed_pw = hash_password(account.password)    
    db_account = Accounts(
        user_name = account.user_name,
        email = account.email,
        balance = account.balance,
        hashed_password = hashed_pw,
    )    
    db_account.user_num() 
    db_account.send_email( 
            to_email= account.email,
            subject= "The account numbre",
        )    
    
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@app.post("/creat_admin")
def creat_admin(
    admin_data: AccountAdmin,
    session: Session = Depends(get_session),
    current_admin: Accounts = Depends(get_current_admin)
):
    existing_user = session.exec(
        select(Accounts).where(Accounts.email == admin_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_admin = Accounts(
        user_name=admin_data.user_name,
        email=admin_data.email,
        compte_num=admin_num(),
        hashed_password=hash_password(admin_data.password),
        role=UserRole.admin
    )
    session.add(new_admin)
    session.commit()

    return {"message": "Admin created successfully"}

@app.put("/deposit", response_model= BalanceDeposi)
def deposit_money(new_balance:BalanceDeposi ,
                  session : Session = Depends(get_session),
                  current_user: str = Depends(get_current_user)
                  ): 
            
    account = session.exec(select(Accounts).where(Accounts.email == current_user )).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if new_balance.deposit <= 0:
        raise HTTPException(status_code=400, detail="this amount is invalid")
    
    amount = account.deposit(new_balance.deposit)
    
    
    new_transaction = Transactions(account_id = account.id,
                                   type = "deposit",
                                   amount = new_balance.deposit
                                   )
    
    session.add(new_transaction)
    session.commit()
    session.refresh(account)
    return {"deposit" : amount}


@app.put("/withdraw", response_model = BalanceWithdraw)
def withdraw_money( new_balance:BalanceWithdraw ,
                   session : Session = Depends(get_session),
                   current_user: str = Depends(get_current_user)
                   ): 
    
    account = session.exec(select(Accounts).where(Accounts.email == current_user)).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
     
    if new_balance.withdraw <= 0:
        raise HTTPException(status_code=400, detail="this amount is invalid")
    
    amount = account.withdraw(new_balance.withdraw)
    
    new_transaction = Transactions(account_id= account.id,
                                   type= "withdraw",
                                   amount = new_balance.withdraw
                                   )
    
    session.add(new_transaction)
    session.commit()
    session.refresh(account)
    return {"withdraw" : amount}
    
    
@app.get("/accounts", response_model=list[AccountRead])
def show_accounts(
    session: Session = Depends(get_session),
    admin: Accounts = Depends(get_current_admin)
    ):
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
def delete_account(
    user_id: int,
    session : Session = Depends(get_session),
    cerent_admin: Accounts = Depends(get_current_admin)
    ):
    account = session.exec(select(Accounts).where(Accounts.id == user_id)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.id == cerent_admin.id:
        raise HTTPException(status_code=400, detail="Admin cannot delete themselves")

    
    session.delete(account)
    session.commit()
    return {"status": "Account deleted"}