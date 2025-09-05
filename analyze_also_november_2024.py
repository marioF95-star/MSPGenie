#!/usr/bin/env python3
"""
ALSO November 2024 Billing Analysis
Analyzes the billing interval bug in the VBA ALSO import
"""

import subprocess
import csv
from io import StringIO
import pandas as pd

def export_table(table_name):
    """Export Access table using mdb-export"""
    result = subprocess.run(['mdb-export', 'MSPCalculator.accdb', table_name], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def analyze_november_2024_also():
    """Analyze ALSO data for November 2024"""
    print("=== ALSO November 2024 Billing Analysis ===\n")
    
    # 1. Get ALSO products (IDProductclass = 2)
    products_csv = export_table('tblProduct')
    products_df = pd.read_csv(StringIO(products_csv))
    also_products = products_df[products_df['IDProductclass'] == 2]
    
    print(f"ALSO Products (IDProductclass=2): {len(also_products)}")
    print("Top ALSO Products:")
    print(also_products[['IDProduct', 'Productname']].head(10).to_string())
    print()
    
    # 2. Get November 2024 usage data
    usage_csv = export_table('tblUsage')
    usage_df = pd.read_csv(StringIO(usage_csv))
    
    # Filter November 2024 ALSO data
    also_usage = usage_df[
        (usage_df['Monat'] == 11) & 
        (usage_df['Jahr'] == 2024) &
        (usage_df['IDProduct'].isin(also_products['IDProduct']))
    ]
    
    print(f"November 2024 ALSO Usage Records: {len(also_usage)}")
    
    # 3. Get customer info
    customers_csv = export_table('tblKunden')
    customers_df = pd.read_csv(StringIO(customers_csv))
    
    # 4. Detailed analysis per customer
    customer_analysis = []
    for customer_id in also_usage['IDKunden'].unique():
        customer_data = also_usage[also_usage['IDKunden'] == customer_id]
        customer_name = customers_df[customers_df['IDKunden'] == customer_id]['KundenName'].iloc[0] if not customers_df[customers_df['IDKunden'] == customer_id].empty else f"Unknown-{customer_id}"
        
        # Group by product
        product_summary = {}
        for _, row in customer_data.iterrows():
            product_id = row['IDProduct']
            product_name = also_products[also_products['IDProduct'] == product_id]['Productname'].iloc[0] if not also_products[also_products['IDProduct'] == product_id].empty else f"Product-{product_id}"
            usage = row['Usage']
            detail = row['Detail'] if pd.notna(row['Detail']) else ""
            
            if product_id not in product_summary:
                product_summary[product_id] = {
                    'name': product_name,
                    'usages': [],
                    'details': []
                }
            product_summary[product_id]['usages'].append(usage)
            product_summary[product_id]['details'].append(detail)
        
        # Calculate max usage per product (as VBA does)
        total_max_usage = 0
        products_info = []
        for product_id, info in product_summary.items():
            max_usage = max(info['usages'])
            total_max_usage += max_usage
            products_info.append({
                'product_id': product_id,
                'product_name': info['name'],
                'max_usage': max_usage,
                'usage_count': len(info['usages']),
                'details': info['details']
            })
        
        customer_analysis.append({
            'customer_id': customer_id,
            'customer_name': customer_name,
            'total_max_usage': total_max_usage,
            'product_count': len(product_summary),
            'products': products_info
        })
    
    # Sort by total usage desc
    customer_analysis.sort(key=lambda x: x['total_max_usage'], reverse=True)
    
    print("\nTop 15 Customers by Total Max Usage (November 2024):")
    print("-" * 80)
    for i, customer in enumerate(customer_analysis[:15]):
        print(f"{i+1:2d}. {customer['customer_name'][:30]:30s} | "
              f"Total: {customer['total_max_usage']:6.1f} | "
              f"Products: {customer['product_count']}")
        
        # Show product details for top 5 customers
        if i < 5:
            for product in customer['products']:
                print(f"    -> {product['product_name'][:40]:40s}: {product['max_usage']:5.1f} "
                      f"(from {product['usage_count']} entries)")
    
    print(f"\nTotal Customers with ALSO Usage: {len(customer_analysis)}")
    print(f"Total ALSO Usage Records: {len(also_usage)}")
    
    # 5. Check for potential billing interval issues
    print("\n=== Potential Billing Interval Issues ===")
    suspicious_customers = []
    
    for customer in customer_analysis:
        for product in customer['products']:
            # Check if we have fractional usage that might indicate interval issues
            if product['max_usage'] != int(product['max_usage']):
                suspicious_customers.append({
                    'customer': customer['customer_name'],
                    'product': product['product_name'],
                    'usage': product['max_usage'],
                    'count': product['usage_count']
                })
    
    if suspicious_customers:
        print("Customers with fractional usage (potential interval parsing issues):")
        for item in suspicious_customers[:10]:
            print(f"  {item['customer']}: {item['product']} = {item['usage']}")
    else:
        print("No obvious fractional usage detected.")
    
    return customer_analysis

if __name__ == "__main__":
    analysis = analyze_november_2024_also()