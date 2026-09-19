#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates sample sales data to test the dashboard generator
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)

# Sample sales data
categories = ["Electronics", "Clothing", "Furniture", "Beauty", "Food", "Books"]
products = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Charger", "Tablet"],
    "Clothing": ["T-Shirt", "Jeans", "Shoes", "Jacket", "Dress"],
    "Furniture": ["Chair", "Desk", "Bed", "Cabinet", "Sofa"],
    "Beauty": ["Face Cream", "Perfume", "Lipstick", "Shampoo", "Makeup Kit"],
    "Food": ["Chocolate", "Juice", "Biscuits", "Coffee", "Tea"],
    "Books": ["Novel", "Science Book", "Kids Book", "Cookbook", "History Book"]
}
cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego"]
status = ["Completed", "Processing", "Cancelled", "Returned"]
payment_methods = ["Cash", "Credit Card", "Digital Wallet", "Bank Transfer"]
customers = ["John Smith", "Sarah Johnson", "Mike Davis", "Emily Brown", "David Wilson", "Lisa Anderson", "James Taylor", "Emma Thomas", "Daniel Jackson", "Olivia White"]

data = []
start_date = datetime(2024,1,1)
for i in range(2000):
    order_date = start_date + timedelta(days=random.randint(0, 365))
    category = random.choice(categories)
    product = random.choice(products[category])
    city = random.choice(cities)
    customer = random.choice(customers)
    quantity = random.randint(1, 10)
    price = random.randint(50, 5000)
    total = quantity * price
    cost = total * random.uniform(0.4, 0.8)
    profit = total - cost
    stat = random.choices(status, weights=[0.7, 0.15, 0.08, 0.07])[0]
    payment = random.choice(payment_methods)
    
    data.append({
        "Order Date": order_date,
        "Order ID": f"ORD-{10000+i}",
        "Customer Name": customer,
        "City": city,
        "Category": category,
        "Product Name": product,
        "Quantity": quantity,
        "Unit Price": price,
        "Total Sales": total,
        "Cost": round(cost, 2),
        "Profit": round(profit, 2),
        "Order Status": stat,
        "Payment Method": payment
    })

df = pd.DataFrame(data)

# Add some missing values to test data cleaning
for _ in range(50):
    idx = random.randint(0, len(df)-1)
    col = random.choice(["Customer Name", "City", "Quantity"])
    df.loc[idx, col] = np.nan

df.to_excel("sample_sales_data.xlsx", index=False)
print("✅ Sample sales data created successfully: sample_sales_data.xlsx")
print("\nFirst 5 rows preview:")
print(df.head())
