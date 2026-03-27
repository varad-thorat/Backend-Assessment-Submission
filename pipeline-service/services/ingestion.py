import requests
from typing import List, Dict
from datetime import datetime
from decimal import Decimal
from models.customer import Customer
from sqlalchemy.orm import Session
import os

FLASK_API_URL = os.getenv("FLASK_API_URL", "http://localhost:5000")

def fetch_all_customers_from_flask() -> List[Dict]:
    """
    Fetch all customers from Flask API with pagination handling
    """
    all_customers = []
    page = 1
    limit = 10
    
    while True:
        try:
            # Make request to Flask API
            response = requests.get(
                f"{FLASK_API_URL}/api/customers",
                params={"page": page, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            customers = data.get("data", [])
            
            # If no more customers, break
            if not customers:
                break
            
            all_customers.extend(customers)
            
            # Check if we've fetched all pages
            total_pages = data.get("total_pages", 0)
            if page >= total_pages:
                break
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching from Flask API: {str(e)}")
    
    return all_customers

def upsert_customer(db: Session, customer_data: Dict) -> Customer:
    """
    Upsert a customer into the database (insert or update if exists)
    """
    # Check if customer exists
    existing_customer = db.query(Customer).filter(
        Customer.customer_id == customer_data["customer_id"]
    ).first()
    
    # Parse dates and timestamps
    date_of_birth = None
    if customer_data.get("date_of_birth"):
        date_of_birth = datetime.fromisoformat(customer_data["date_of_birth"]).date()
    
    created_at = None
    if customer_data.get("created_at"):
        created_at = datetime.fromisoformat(customer_data["created_at"])
    
    # Parse account balance
    account_balance = None
    if customer_data.get("account_balance") is not None:
        account_balance = Decimal(str(customer_data["account_balance"]))
    
    if existing_customer:
        # Update existing customer
        existing_customer.first_name = customer_data["first_name"]
        existing_customer.last_name = customer_data["last_name"]
        existing_customer.email = customer_data["email"]
        existing_customer.phone = customer_data.get("phone")
        existing_customer.address = customer_data.get("address")
        existing_customer.date_of_birth = date_of_birth
        existing_customer.account_balance = account_balance
        existing_customer.created_at = created_at
        return existing_customer
    else:
        # Create new customer
        new_customer = Customer(
            customer_id=customer_data["customer_id"],
            first_name=customer_data["first_name"],
            last_name=customer_data["last_name"],
            email=customer_data["email"],
            phone=customer_data.get("phone"),
            address=customer_data.get("address"),
            date_of_birth=date_of_birth,
            account_balance=account_balance,
            created_at=created_at
        )
        db.add(new_customer)
        return new_customer

def ingest_customers(db: Session) -> int:
    """
    Main ingestion function: fetch from Flask and upsert into PostgreSQL
    Returns the number of records processed
    """
    try:
        # Fetch all customers from Flask
        customers = fetch_all_customers_from_flask()
        
        # Upsert each customer
        for customer_data in customers:
            upsert_customer(db, customer_data)
        
        # Commit all changes
        db.commit()
        
        return len(customers)
        
    except Exception as e:
        db.rollback()
        raise e