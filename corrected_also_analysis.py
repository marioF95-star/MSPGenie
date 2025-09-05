#!/usr/bin/env python3
"""
KORRIGIERTE ALSO November 2024 Analyse
Berücksichtigt NUR IDProductclass=2 (ALSO) Produkte
"""

import pandas as pd
import subprocess
from io import StringIO

def corrected_analysis():
    print("=== KORRIGIERTE ALSO ANALYSE (nur IDProductclass=2) ===\n")
    
    # 1. Excel-Daten (unverändert)
    excel_data = pd.read_excel('data/Also/MB_NETWORKS_GmbH_11-2024.xlsx', sheet_name='Raw Charges')
    excel_data['Quantity'] = excel_data['Attributes'].apply(lambda x: 
        int(x.split('=')[-1]) if pd.notna(x) and x.split('=')[-1].isdigit() else 0
    )
    
    excel_agg = excel_data.groupby(['Company', 'Product name']).agg({
        'Quantity': 'max'
    }).reset_index()
    
    # 2. Access-Daten - NUR IDProductclass=2
    result = subprocess.run(['mdb-export', 'MSPCalculator.accdb', 'tblUsage'], 
                          capture_output=True, text=True)
    usage_df = pd.read_csv(StringIO(result.stdout))
    
    # November 2024
    nov_2024 = usage_df[(usage_df['Monat'] == 11) & (usage_df['Jahr'] == 2024)]
    
    # Nur ALSO Produkte (IDProductclass=2)
    result = subprocess.run(['mdb-export', 'MSPCalculator.accdb', 'tblProduct'], 
                          capture_output=True, text=True)
    products_df = pd.read_csv(StringIO(result.stdout))
    
    also_products = products_df[products_df['IDProductclass'] == 2]['IDProduct'].tolist()
    also_usage = nov_2024[nov_2024['IDProduct'].isin(also_products)]
    
    # Kundennamen hinzufügen
    result = subprocess.run(['mdb-export', 'MSPCalculator.accdb', 'tblKunden'], 
                          capture_output=True, text=True)
    customers_df = pd.read_csv(StringIO(result.stdout))
    
    also_usage_detailed = also_usage.merge(
        customers_df[['IDKunden', 'IDAlso']], 
        on='IDKunden', how='left'
    )
    
    print(f"Excel: {len(excel_agg)} Einträge, {excel_agg['Quantity'].sum()} Total Quantity")
    print(f"Access (nur ALSO): {len(also_usage_detailed)} Einträge, {also_usage_detailed['Usage'].sum():.0f} Total Usage")
    
    # 3. Vergleich nach Kunden
    excel_customers = set(excel_data['Company'].unique())
    access_customers = set(also_usage_detailed['IDAlso'].dropna().unique())
    
    only_in_excel = excel_customers - access_customers
    only_in_access = access_customers - excel_customers
    common_customers = excel_customers & access_customers
    
    print(f"\nKunden nur in Excel: {len(only_in_excel)}")
    print(f"Kunden nur in Access: {len(only_in_access)}")  
    print(f"Gemeinsame Kunden: {len(common_customers)}")
    
    if len(only_in_excel) > 0:
        print("\nNur in Excel:")
        for customer in sorted(only_in_excel):
            qty = excel_data[excel_data['Company'] == customer]['Quantity'].sum()
            print(f"  - {customer}: {qty}")
    
    # 4. Detailvergleich gemeinsame Kunden
    differences = []
    for customer in common_customers:
        excel_total = excel_data[excel_data['Company'] == customer]['Quantity'].sum()
        access_total = also_usage_detailed[also_usage_detailed['IDAlso'] == customer]['Usage'].sum()
        diff = excel_total - access_total
        
        if abs(diff) > 0.1:
            differences.append({
                'customer': customer,
                'excel': excel_total,
                'access': access_total,
                'diff': diff
            })
    
    if differences:
        print(f"\nKunden mit Abweichungen: {len(differences)}")
        for diff in sorted(differences, key=lambda x: abs(x['diff']), reverse=True)[:5]:
            print(f"  {diff['customer']}: Excel {diff['excel']} vs Access {diff['access']} (Diff: {diff['diff']:+.0f})")
    else:
        print("\n✅ ALLE GEMEINSAMEN KUNDEN STIMMEN ÜBEREIN!")
    
    return len(only_in_excel), len(differences)

if __name__ == "__main__":
    missing, wrong = corrected_analysis()
    print(f"\nFAZIT: {missing} fehlende Kunden, {wrong} falsche Mengen")