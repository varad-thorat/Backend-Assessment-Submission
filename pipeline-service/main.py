from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import get_db, init_db
from models.customer import Customer
from services.ingestion import ingest_customers

# Create FastAPI app
app = FastAPI(
    title="Customer Data Pipeline API",
    description="FastAPI service for ingesting and managing customer data",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database tables on startup"""
    init_db()
    print("Database initialized successfully")

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fastapi-pipeline"
    }

@app.post("/api/ingest")
def ingest_data(db: Session = Depends(get_db)):
    """
    Ingest customer data from Flask API into PostgreSQL
    """
    try:
        records_processed = ingest_customers(db)
        return {
            "status": "success",
            "records_processed": records_processed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
def get_customers(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of customers from database
    """
    try: # Validate parameters
        
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        
        
        offset = (page - 1) * limit # Calculate offset
        
        
        total = db.query(Customer).count() # Query total count
        
        
        customers = db.query(Customer).offset(offset).limit(limit).all() # Query paginated data
        
        
        customers_data = [customer.to_dict() for customer in customers] # Convert to dict
        
        return {
            "data": customers_data,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Get a single customer by ID from database
    """
    try:
        customer = db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
        
        if customer is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer not found: {customer_id}"
            )
        
        return customer.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)