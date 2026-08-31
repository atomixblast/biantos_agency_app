#!/usr/bin/env python
"""
Setup script to create test data for the order system
Run this with: python manage.py shell < setup_test_data.py
"""

from order.models import Article, Customer, SalesExecutive
from django.db import IntegrityError

print("=" * 60)
print("Setting up test data for Biantos Agency Order System")
print("=" * 60)

# Create Articles
articles_data = [
    {"name": "Tasse personnalisée", "ref": "TASSE-001", "sale_price": 3000},
    {"name": "T-shirt personnalisé", "ref": "TSHIRT-001", "sale_price": 3500},
    {"name": "Éventail personnalisé", "ref": "EVENT-001", "sale_price": 1000},
    {"name": "Casquette personnalisée", "ref": "CAP-001", "sale_price": 2500},
    {"name": "Stylo personnalisé", "ref": "STYLO-001", "sale_price": 500},
    {"name": "Carnet personnalisé", "ref": "CARNET-001", "sale_price": 1500},
]

print("\n📦 Creating Articles...")
for article_data in articles_data:
    try:
        article, created = Article.objects.get_or_create(
            ref=article_data["ref"],
            defaults={
                "name": article_data["name"],
                "sale_price": article_data["sale_price"]
            }
        )
        if created:
            print(f"  ✅ Created: {article.name} - {article.sale_price} FCFA")
        else:
            print(f"  ⏭️  Already exists: {article.name}")
    except IntegrityError as e:
        print(f"  ❌ Error creating {article_data['name']}: {e}")

# Create Customers
customers_data = [
    {"name": "Entreprise ABC", "tel": "+225 07 12 34 56 78"},
    {"name": "Société XYZ", "tel": "+225 05 98 76 54 32"},
    {"name": "Organisation DEF", "tel": "+225 01 23 45 67 89"},
]

print("\n👥 Creating Customers...")
for customer_data in customers_data:
    customer, created = Customer.objects.get_or_create(
        name=customer_data["name"],
        defaults={"tel": customer_data["tel"]}
    )
    if created:
        print(f"  ✅ Created: {customer.name}")
    else:
        print(f"  ⏭️  Already exists: {customer.name}")

# Create Sales Executives
sales_execs_data = [
    {"name": "Jean Kouassi", "tel": "+225 07 11 22 33 44"},
    {"name": "Marie Koné", "tel": "+225 05 55 66 77 88"},
]

print("\n💼 Creating Sales Executives...")
for exec_data in sales_execs_data:
    exec_obj, created = SalesExecutive.objects.get_or_create(
        name=exec_data["name"],
        defaults={"tel": exec_data["tel"]}
    )
    if created:
        print(f"  ✅ Created: {exec_obj.name}")
    else:
        print(f"  ⏭️  Already exists: {exec_obj.name}")

print("\n" + "=" * 60)
print("✅ Test data setup complete!")
print("=" * 60)
print("\nSummary:")
print(f"  📦 Articles: {Article.objects.count()}")
print(f"  👥 Customers: {Customer.objects.count()}")
print(f"  💼 Sales Executives: {SalesExecutive.objects.count()}")
print("\nYou can now:")
print("  1. Navigate to /order/create_order/ to create orders")
print("  2. Navigate to /order/list_orders/ to view orders")
print("=" * 60)
