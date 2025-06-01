from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import db

mcp = FastMCP("northwind mcp")

@mcp.resource("resource://sqlite3")
def db_resource():
    return db.nwdb()

@mcp.tool(description="test mcp")
def test_mcp():
    db_instance = db_resource()
    return db_instance.test_mcp()


@mcp.tool(description="find total expense or total expense by category")
def total_expense(country: str = None):
    db_instance = db_resource()
    """
    Find total expense or total expense by country
    :param country: country to filter by
    :param db: db resource (injected automatically)
    :return: total expense or total expense by country
    """
    return db_instance.total_expense(country)

@mcp.tool(description="find available countries")
def list_countries():
    db_instance = db_resource()
    """
    Find total expense by country
    :param db: db resource (injected automatically)
    :return: list of countries
    """
    return db_instance.list_countries()

@mcp.tool(description="find customer details")
def find_customers(name: str = None):
    db_instance = db_resource()
    """
    Find customer details
    :param db: db resource (injected automatically)
    :return: list of customers
    """
    return db_instance.find_matching_customer(name)


@mcp.tool(description="find order  details by id")
def find_invoice_by_id(id: str = None):
    db_instance = db_resource()
    """
    Find invoice  details by id
    :param id: id to filter by
    :param db: db resource (injected automatically)
    :return: summary of the invoice, if none return reply with  polite message
    """
    return db_instance.invoice_by_id(id)

@mcp.tool(description="find product  details by id")
def find_product_by_id(id: str = None):
    db_instance = db_resource()
    """
    Find product  details by id
    :param ProductID: ProductID to filter by
    :param db: db resource (injected automatically)
    :return: list of products with ProductID, ProductName, SupplierID
    """
    return db_instance.product_details(id)

@mcp.tool(description="find order subtotal by orderId")
def find_order_subtotal(id: str = None):
    db_instance = db_resource()
    """
    Find order  details by OrderId
    :param OrderID: OrderID to filter by
    :param db: db resource (injected automatically)
    :return: order  with OrderId, Subtotal
    """
    return db_instance.order_subtotals(id)

def runmcp():
    """Entry point for the MCP server when run as a script."""
    mcp.run()  # Default: uses STDIO transport
