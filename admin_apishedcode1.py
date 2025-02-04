from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DB_FILE = "shedding.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS shed_pricing (id INTEGER PRIMARY KEY AUTOINCREMENT, shed_type TEXT, base_price REAL)")
    conn.commit()
    conn.close()

init_db()

class AdminLogin(BaseModel):
    username: str
    password: str

class OrderUpdate(BaseModel):
    order_id: int
    new_status: str

class PricingUpdate(BaseModel):
    shed_type: str
    new_price: float

def authenticate_admin(username: str, password: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

@app.post("/admin/login")
def admin_login(credentials: AdminLogin):
    if authenticate_admin(credentials.username, credentials.password):
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.put("/admin/update-order")
def update_order_status(update: OrderUpdate, username: str, password: str):
    if not authenticate_admin(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (update.new_status, update.order_id))
    conn.commit()
    conn.close()

    return {"message": f"Order {update.order_id} updated to {update.new_status}"}
