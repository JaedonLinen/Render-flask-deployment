from config import db
from datetime import datetime, timedelta
import bcrypt

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name =  db.Column(db.String(50), unique=False, nullable=False)
    last_name =  db.Column(db.String(50), unique=False, nullable=False)
    username =  db.Column(db.String(50), unique=True, nullable=False)
    email =  db.Column(db.String(100), unique=False, nullable=False)
    password_hash = db.Column(db.String(255), unique=True, nullable=False)
    role =  db.Column(db.String(11), unique=False, nullable=False)
    date_of_birth =  db.Column(db.Date, unique=False, nullable=False)
    created_at =  db.Column(db.DateTime, default=datetime.now)
    expiration_date =  db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=365))
    isActive =  db.Column(db.String(8), unique=False, nullable=False)
    

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def set_username(self):
        first_name = self.first_name.lower()
        last_name = self.last_name.lower()
        birth_month = str(self.date_of_birth.month).zfill(2)
        birth_year_last_two = str(self.date_of_birth.year)[-2:]

        self.username = f"{first_name}{last_name}{birth_month}{birth_year_last_two}"

    def to_json(self):
        return{
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "email": self.email,
            "passwordHash": self.password_hash,
            "role": self.role,
            "dateOfBirth": self.date_of_birth,
            "createdAt": self.created_at,
            "expiration_date": self.expiration_date,
            "isActive": self.isActive
        }
        
    def reset_table():
        db.metadata.tables["users"].drop(db.engine)  # Drop all tables (or use db.metadata.tables["transactions"].drop(db.engine) for one table)
        db.create_all()  # Recreate all tables
        print("Table 'accounts' has been dropped and recreated.")

class Accounts(db.Model):

    __tablename__ = 'Accounts'

    account_id = db.Column(db.Integer, primary_key=True)  # Unique identifier for account
    account_num = db.Column(db.Integer, nullable=False, unique=True)  # Unique identifier for account
    account_name = db.Column(db.String(50), unique=True,  nullable=False)  # Account name (not unique)
    account_desc = db.Column(db.String(255), nullable=False)  # Description (increased size for flexibility)
    normal_side = db.Column(db.String(10), nullable=False)  # Should be 'Debit' or 'Credit'
    category = db.Column(db.String(50), nullable=False)  # Main category (e.g., Asset, Liability)
    subcategory = db.Column(db.String(50), nullable=False)  # Subcategory (e.g., Current Assets)
    initial_balance = db.Column(db.Float, nullable=False, default=0.0)  # Numeric type for calculations
    debit = db.Column(db.Float, nullable=False, default=0.0)  # Debit amount
    credit = db.Column(db.Float, nullable=False, default=0.0)  # Credit amount
    balance = db.Column(db.Float, nullable=False, default=0.0)  # Current balance
    created_at = db.Column(db.DateTime, default=datetime.now)  # Timestamp when account is created
    account_owner = db.Column(db.Integer, nullable=False)  # Expiration or ownership time
    isActive = db.Column(db.Boolean, nullable=False, default=True)  # Boolean for active/inactive status
    order = db.Column(db.Integer, nullable=True)  # Order for sorting (e.g., Cash = 1)
    statement = db.Column(db.String(2), nullable=True)  # Financial statement type ('IS', 'BS', 'RE')
    comment = db.Column(db.Text, nullable=True)  # Optional comment field

    def place_initial_balance(self):
        if self.normal_side == "Debit":
            self.debit = self.initial_balance
        elif self.normal_side == "Credit":
            self.credit = self.initial_balance

    def place_balance(self):
        if self.normal_side == "Debit":
            self.balance = self.initial_balance
        elif self.normal_side == "Credit":
            self.balance = self.initial_balance

    def check_negative_balance(self):
        if self.balance < 0:
            return True
        else:
            return False
        
    def reflect_entry(self, entry):
        entry_type = entry.get("type", "").lower()  # Safely get the type value

        if entry_type == "credit":
            self.credit = entry.get("amount", 0)  # Get amount safely
        else:
            self.debit = entry.get("amount", 0)

        if entry_type == self.normal_side.lower():
            self.balance = self.balance + entry.get("amount", 0)
        else:
            self.balance = self.balance - entry.get("amount", 0)

        return self.balance
        

    def to_json(self):
        return {
            "account_id": self.account_id,
            "account_num": self.account_num,
            "account_name": self.account_name,
            "account_desc": self.account_desc,
            "normal_side": self.normal_side,
            "category": self.category,
            "subcategory": self.subcategory,
            "initial_balance": self.initial_balance,
            "debit": self.debit,
            "credit": self.credit,
            "balance": self.balance,
            "created_at": self.created_at,
            "account_owner": self.account_owner,
            "isActive": self.isActive,
            "order": self.order,
            "statement": self.statement,
            "comment": self.comment
        }
    
    def reset_table():
        db.metadata.tables["Accounts"].drop(db.engine)  # Drop all tables (or use db.metadata.tables["transactions"].drop(db.engine) for one table)
        db.create_all()  # Recreate all tables
        print("Table 'accounts' has been dropped and recreated.")
    
class transactions(db.Model):

    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)  # Unique transaction ID
    transaction_type = db.Column(db.String(12), nullable=True)  # Name of the affected table
    description = db.Column(db.String(250), nullable=False)  # Name of the affected table
    transaction_date = db.Column(db.Date, unique=False, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  # ID of user who made the change
    status = db.Column(db.String(10), nullable=False)  # Name of the affected table
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now)
    updated_by = db.Column(db.Integer, nullable=True)  # ID of user who made the change
    comment = db.Column(db.Text, nullable=True)  # Optional comment field

    def to_json(self):
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "description": self.description,
            "transaction_date": self.transaction_date,
            "user_id": self.user_id,
            "status": self.status,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
            "updated_by": self.updated_by,
            "comment" : self.comment
        }
    
    def reset_table():
        db.metadata.tables["transactions"].drop(db.engine)  # Drop all tables (or use db.metadata.tables["transactions"].drop(db.engine) for one table)
        db.create_all()  # Recreate all tables
        print("Table 'accounts' has been dropped and recreated.")
    
class transaction_entries(db.Model):

    __tablename__ = 'transaction_entries'

    transaction_entry_id = db.Column(db.Integer, primary_key=True)  # Unique transaction ID
    transaction_id = db.Column(db.Integer, nullable=False)  # ID of user who made the change
    account_id = db.Column(db.Integer, nullable=False)  # ID of user who made the change
    amount = db.Column(db.Float, nullable=False)  # ammount
    type = db.Column(db.String(10), nullable=False)  # Should be 'Debit' or 'Credit']
    reflected = db.Column(db.String(5), nullable=False, default=False)  # Should be 'Debit' or 'Credit'

    def to_json(self):
        return {
            "transaction_entry_id": self.transaction_entry_id,
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "amount": self.amount,
            "type": self.type,
            "reflected": self.reflected
        }
    
    def set_reflected(self):
        self.reflected = True
    
    def reset_table():
        db.metadata.tables["transaction_entries"].drop(db.engine)  # Drop all tables (or use db.metadata.tables["transactions"].drop(db.engine) for one table)
        db.create_all()  # Recreate all tables
        print("Table 'accounts' has been dropped and recreated.")
    
class document_entries(db.Model):

    __tablename__ = 'document_entries'

    document_entry_id = db.Column(db.Integer, primary_key=True)  # Unique transaction ID
    transaction_id = db.Column(db.Integer, nullable=False)  # ID of user who made the change
    account_id = db.Column(db.Integer, nullable=False)  # ID of user who made the change
    filename = db.Column(db.String(255), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)  # BLOB Column for storing file data

    def to_json(self):
        return {
            "document_entry_id": self.document_entry_id,
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "filename": self.filename,
            "file_data": self.file_data
        }
    
    def reset_table():
        db.metadata.tables["document_entries"].drop(db.engine)  # Drop all tables (or use db.metadata.tables["transactions"].drop(db.engine) for one table)
        db.create_all()  # Recreate all tables
        print("Table 'accounts' has been dropped and recreated.")
    
class event_log(db.Model):

    __tablename__ = 'event_logs'

    event_id = db.Column(db.Integer, primary_key=True)  # Unique event ID
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)  # Date & time of event
    user_id = db.Column(db.Integer, nullable=False)  # ID of user who made the change
    table_name = db.Column(db.String(50), nullable=False)  # Name of the affected table
    column_name = db.Column(db.String(50), nullable=True)  # Name of the changed column
    old_value = db.Column(db.Text, nullable=True)  # Previous value before change
    new_value = db.Column(db.Text, nullable=True)  # New value after change
    action = db.Column(db.String(250), nullable=False)  # Type of action ('INSERT', 'UPDATE', 'DELETE')
    comment = db.Column(db.Text, nullable=True)  # Optional comment (e.g., reason for change)

    def to_json(self):
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "action": self.action,
            "comment": self.comment
        }
    def reset_table():
        db.metadata.tables["event_logs"].drop(db.engine)  # Drop all tables (or use db.metadata.tables["transactions"].drop(db.engine) for one table)
        db.create_all()  # Recreate all tables
        print("Table 'accounts' has been dropped and recreated.")
