from sqlmodel import create_engine, Session, select
from models import Accounts, UserRole
from security import hash_password
import random




DATABASE_URL = "sqlite:///banki.db"



engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}  
)

def admin_num():
       return str(random.randint(10**13, 10**14 - 1))
      

def create_main_admin():
    with Session(engine) as session:
        
        admin_exist = session.exec(
            select(Accounts).where(Accounts.email == "soufianeelbrnoussi84@gmail.com")
        ).first()
        
        if admin_exist:
            print("Admin already exists")
            return
        
        
        admin = Accounts(
            user_name="Mr.Soufiane Elrbnoussi",
            email="soufianeelbrnoussi84@gmail.com",
            hashed_password=hash_password("admin123"),
            balance=0,
            compte_num=admin_num(),
            role=UserRole.admin
        )
        
        session.add(admin)
        session.commit()
        
        print("Admin created successfully")