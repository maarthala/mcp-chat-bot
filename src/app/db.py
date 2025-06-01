
import sqlite3
import os

class nwdb():
    def __init__(self, db_path="../../db/northwind.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def total_expense(self, country=None):
        cur = self.conn.cursor()
        if country:
            cur.execute("SELECT SUM(Freight) as total FROM Invoices WHERE Country = ?", (country,))
        else:
            cur.execute("SELECT SUM(Freight) as total FROM Invoices")
        row = cur.fetchone()
        return row["total"] if row["total"] is not None else 0

    def list_countries(self):
        cur = self.conn.cursor()
        cur.execute("select distinct Country from Invoices")
        return [row["Country"] for row in cur.fetchall()]
    
    def find_matching_customer(self, name=None):
        cur = self.conn.cursor()
        if name:
            cur.execute("SELECT CustomerID,CompanyName, Address, Phone, Country FROM Customers WHERE CompanyName LIKE ?", (f"%{name}%",))
        else:
            cur.execute("SELECT CustomerID,CompanyName, Address, Phone, Country FROM Customers")
        return [
            {
            "CustomerID": row["CustomerID"],
            "CompanyName": row["CompanyName"],
            "Address": row["Address"],
            "Phone": row["Phone"],
            "Country" : row["Country"]
            }
            for row in cur.fetchall()
        ]

    def invoice_by_id(self, id=None):
        cur = self.conn.cursor()
        id = int(id)
        cur.execute("""
            SELECT
                c.CompanyName AS CustomerName,
                c.Address,
                c.City,
                c.Country,
                o.OrderDate
            FROM Orders o
            JOIN Customers c ON o.CustomerID = c.CustomerID
            WHERE o.OrderID = ?
        """, (id,))
        order_info = cur.fetchone()

        if not order_info:
            return {}

        cur.execute("""
            SELECT ProductID
            FROM [Order Details]
            WHERE OrderID = ?
        """, (id,))
        products = cur.fetchall()

        product_ids = [row["ProductID"] for row in products]

        address = f"{order_info['Address']} in {order_info['City']}, {order_info['Country']}"

        orderList =  {
            "CustomerName": order_info["CustomerName"],
            "Address": address,
            "OrderDate": str(order_info["OrderDate"]),
            "ProductIDs": product_ids
        }
        print(orderList)
        return orderList 


    def product_details(self, id=None):
        cur = self.conn.cursor()
        id = int(id)
        if id:
            cur.execute("SELECT ProductID, ProductName, SupplierID FROM Products WHERE ProductID =  ?", (id,))
            return [
                {
                    "ProductID": row["ProductID"],
                    "ProductName": row["ProductName"],
                    "SupplierID": row["SupplierID"]
                }
                for row in cur.fetchall()
            ]
        return []

    def order_subtotals(self, id=None):
        cur = self.conn.cursor()
        id = int(id)
        if id:
            cur.execute("SELECT Subtotal FROM 'Order Subtotals' WHERE OrderID =  ?", (id,))
            return [
                {
                    "Subtotal": row["Subtotal"]
                }
                for row in cur.fetchall()
            ]
        return []
    
    def test_mcp(self):
        return os.getcwd()
