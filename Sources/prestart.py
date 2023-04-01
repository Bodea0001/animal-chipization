from models.schemas import AccountAdding, Role
from controllers.password import get_password_hash
from db.database import SessionLocal
from db.crud import exists_account_with_email, create_account_with_role


if __name__=="__main__":
    with SessionLocal() as db:
        admin_account = exists_account_with_email(db, "admin@simbirsoft.com")
        chipper_account = exists_account_with_email(db, "chipper@simbirsoft.com")
        user_account = exists_account_with_email(db, "user@simbirsoft.com")

    password = get_password_hash("qwerty123")

    if not admin_account:
        admin_account_data = AccountAdding(
            firstName = "adminFirstName",
            lastName = "adminLastName",
            email = "admin@simbirsoft.com",
            password = password,
            role = Role.ADMIN
        )
        create_account_with_role(db, admin_account_data)
    
    if not chipper_account:
        chipper_account_data = AccountAdding(
            firstName = "chipperFirstName",
            lastName = "chipperLastName",
            email = "chipper@simbirsoft.com",
            password = password,
            role = Role.CHIPPER
        )
        create_account_with_role(db, chipper_account_data)
    
    if not user_account:
        user_account_data = AccountAdding(
            firstName = "userFirstName",
            lastName = "userLastName",
            email = "user@simbirsoft.com",
            password = password,
            role = Role.USER
        )
        create_account_with_role(db, user_account_data)
