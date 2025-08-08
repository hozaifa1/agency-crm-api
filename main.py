import sqlite3
from fastapi import FastAPI, HTTPException, status
import database
import schemas

# --- SETUP ---
# Use the correct database name as defined in your database.py
DB_NAME = 'agency.db'

# Initialize the database on startup
database.init_db(DB_NAME)

app = FastAPI(
    title="Agency CRM API",
    description="A complete CRUD API for managing agency customers."
)


# --- HELPER FUNCTION ---
# To avoid repeating connection code. Professionals don't repeat themselves.
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# --- API ENDPOINTS ---

@app.get("/", tags=["Status"])
def home():
    return {"message": "CRM Service is operational."}


@app.post("/customers/", response_model=schemas.Customer, status_code=status.HTTP_201_CREATED, tags=["Customers"])
def create_customer(customer: schemas.CustomerCreate):
    """
    Create a new customer.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO customers (name, email, status) VALUES (?, ?, ?)",
            (customer.name, customer.email, customer.status)
        )
        conn.commit()
        new_customer_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    
    conn.close()
    # Return a complete Customer object, including the new ID.
    return schemas.Customer(id=new_customer_id, **customer.model_dump())


@app.get("/customers/", response_model=list[schemas.Customer], tags=["Customers"])
def read_customers(status: str | None = None):
    """
    Retrieve all customers, optionally filtering by status.
    Path: /customers/ or /customers/?status=active
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM customers"
    params = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
        
    cursor.execute(query, params)
    # Explicitly convert each database row into a Pydantic model.
    customers = [schemas.Customer(**dict(row)) for row in cursor.fetchall()]


    conn.close()
    return customers


@app.get("/customers/{customer_id}", response_model=schemas.Customer, tags=["Customers"])
def read_one_customer(customer_id: int):
    """
    Retrieve a single customer by their ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer_row = cursor.fetchone()
    conn.close()
    
    if customer_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    return schemas.Customer(**dict(customer_row))



@app.put("/customers/{customer_id}", response_model=schemas.Customer, tags=["Customers"])
def update_customer(customer_id: int, update_data: schemas.CustomerUpdate):
    """
    Update an existing customer's details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    existing_customer=cursor.fetchone()
    
    if existing_customer is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    
    # --- STEP 2: MERGE the old data with the new data ---
    # Create a Pydantic model from the existing DB data
    existing_customer = schemas.Customer(**dict(existing_customer))

    # Get the new data from the request, excluding any fields the client didn't send
    update_dict = update_data.model_dump(exclude_unset=True)

    # Create a final, updated customer model by copying the old data
    # and applying the new changes from the update_dict.
    updated_customer = existing_customer.model_copy(update=update_dict)

    # Corrected SQL syntax with commas
    cursor.execute(
        "UPDATE customers SET name = ?, email = ?, status = ? WHERE id = ?",
        (updated_customer.name, updated_customer.email, updated_customer.status, customer_id)
    )
    conn.commit()
     
    
    conn.close()
    return updated_customer


@app.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Customers"])
def delete_customer(customer_id: int):
    """
    Delete a customer from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    
    conn.close()
    return # No content to return on successful deletion