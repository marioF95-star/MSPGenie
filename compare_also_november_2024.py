#!/usr/bin/env python3
"""
Detaillierter Vergleich: Excel ALSO November 2024 vs Access tblUsage
Findet genaue Unterschiede zwischen Soll (Excel) und Ist (Access)
"""

import pandas as pd
import subprocess
from io import StringIO

def load_excel_data():
    """Lade und verarbeite Excel November 2024 ALSO Daten"""
    print("=== EXCEL DATEN (SOLL) ===")
    
    # Raw Charges Sheet laden
    raw_charges = pd.read_excel('data/Also/MB_NETWORKS_GmbH_11-2024.xlsx', sheet_name='Raw Charges')
    
    # Quantity aus Attributes extrahieren
    def extract_quantity(attr_str):
        if pd.isna(attr_str):
            return 0
        # Nimm alles nach dem letzten '=' (wie VBA)
        last_equal_pos = attr_str.rfind('=')
        if last_equal_pos != -1:
            quantity_str = attr_str[last_equal_pos + 1:]
            try:
                return int(quantity_str)
            except ValueError:
                return 0
        return 0
    
    raw_charges['Quantity'] = raw_charges['Attributes'].apply(extract_quantity)
    
    # Korrekte Aggregierung: MAX Quantity pro Company + Product
    excel_agg = raw_charges.groupby(['Company', 'Product name']).agg({
        'Quantity': 'max',  # Maximum quantity für dieses Produkt
        'Charge': 'sum',
        'Interval': 'first',
        'VendorReference': 'first'
    }).reset_index()
    
    print(f"Excel Rohdaten: {len(raw_charges)} Einträge")
    print(f"Nach Aggregierung: {len(excel_agg)} Einträge")
    print(f"Kunden: {excel_agg['Company'].nunique()}")
    print(f"Total Quantity: {excel_agg['Quantity'].sum()}")
    
    return excel_agg, raw_charges

def load_access_data():
    """Lade Access tblUsage November 2024 ALSO Daten"""
    print("\n=== ACCESS DATEN (IST) ===")
    
    # tblUsage exportieren
    result = subprocess.run(['mdb-export', 'MSPCalculator.accdb', 'tblUsage'], 
                          capture_output=True, text=True)
    usage_df = pd.read_csv(StringIO(result.stdout))
    
    # November 2024 filtern
    nov_2024 = usage_df[(usage_df['Monat'] == 11) & (usage_df['Jahr'] == 2024)]
    
    # ALSO Produkte identifizieren (IDProductclass = 2)
    result = subprocess.run(['mdb-export', 'MSPCalculator.accdb', 'tblProduct'], 
                          capture_output=True, text=True)
    products_df = pd.read_csv(StringIO(result.stdout))
    also_products = products_df[products_df['IDProductclass'] == 2]['IDProduct'].tolist()
    
    # Nur ALSO Produkte
    also_usage = nov_2024[nov_2024['IDProduct'].isin(also_products)]
    
    # Kundennamen hinzufügen
    result = subprocess.run(['mdb-export', 'MSPCalculator.accdb', 'tblKunden'], 
                          capture_output=True, text=True)
    customers_df = pd.read_csv(StringIO(result.stdout))
    
    # Merge customer names und product names
    also_usage_detailed = also_usage.merge(
        customers_df[['IDKunden', 'KundenName']], 
        left_on='IDKunden', right_on='IDKunden', how='left'
    ).merge(
        products_df[['IDProduct', 'Productname']], 
        left_on='IDProduct', right_on='IDProduct', how='left'
    )
    
    print(f"Access tblUsage November 2024: {len(also_usage_detailed)} Einträge")
    print(f"Kunden: {also_usage_detailed['KundenName'].nunique()}")
    print(f"Total Usage: {also_usage_detailed['Usage'].sum()}")
    
    return also_usage_detailed, customers_df, products_df

def compare_data(excel_data, access_data):
    """Detaillierter Vergleich zwischen Excel und Access"""
    print("\n=== DETAILLIERTER VERGLEICH ===")
    
    differences = []
    
    # 1. Kunden die in Excel aber nicht in Access sind
    excel_customers = set(excel_data['Company'].unique())
    access_customers = set(access_data['KundenName'].dropna().unique())
    
    only_in_excel = excel_customers - access_customers
    only_in_access = access_customers - excel_customers
    
    print(f"\nKunden nur in Excel: {len(only_in_excel)}")
    for customer in sorted(only_in_excel):
        customer_data = excel_data[excel_data['Company'] == customer]
        total_qty = customer_data['Quantity'].sum()
        print(f"  - {customer}: {total_qty} Quantity")
        differences.append({
            'type': 'CUSTOMER_MISSING_IN_ACCESS',
            'customer': customer,
            'excel_quantity': total_qty,
            'access_usage': 0,
            'difference': total_qty
        })
    
    print(f"\nKunden nur in Access: {len(only_in_access)}")
    for customer in sorted(only_in_access):
        customer_data = access_data[access_data['KundenName'] == customer]
        total_usage = customer_data['Usage'].sum()
        print(f"  - {customer}: {total_usage} Usage")
        differences.append({
            'type': 'CUSTOMER_MISSING_IN_EXCEL',
            'customer': customer,
            'excel_quantity': 0,
            'access_usage': total_usage,
            'difference': -total_usage
        })
    
    # 2. Gemeinsame Kunden vergleichen
    common_customers = excel_customers & access_customers
    print(f"\nGemeinsame Kunden: {len(common_customers)}")
    
    customer_differences = []
    
    for customer in sorted(common_customers):
        excel_customer = excel_data[excel_data['Company'] == customer]
        access_customer = access_data[access_data['KundenName'] == customer]
        
        excel_total = excel_customer['Quantity'].sum()
        access_total = access_customer['Usage'].sum()
        diff = excel_total - access_total
        
        if abs(diff) > 0.1:  # Nur signifikante Unterschiede
            customer_differences.append({
                'customer': customer,
                'excel_total': excel_total,
                'access_total': access_total,
                'difference': diff,
                'excel_products': len(excel_customer),
                'access_products': len(access_customer)
            })
    
    # Sortiere nach größter Differenz
    customer_differences.sort(key=lambda x: abs(x['difference']), reverse=True)
    
    print(f"\nKunden mit Unterschieden: {len(customer_differences)}")
    print("\nTop 10 größte Unterschiede:")
    print("=" * 80)
    for i, diff in enumerate(customer_differences[:10]):
        print(f"{i+1:2d}. {diff['customer'][:35]:35s}")
        print(f"    Excel: {diff['excel_total']:6.1f} ({diff['excel_products']} Produkte)")
        print(f"    Access: {diff['access_total']:6.1f} ({diff['access_products']} Produkte)")
        print(f"    Differenz: {diff['difference']:+7.1f}")
        print()
    
    # 3. Produkt-Level-Analyse für größte Abweichungen
    print("\n=== PRODUKT-LEVEL-ANALYSE (Top 3 Kunden) ===")
    
    for i, diff in enumerate(customer_differences[:3]):
        customer = diff['customer']
        print(f"\n{i+1}. {customer}")
        print("-" * 50)
        
        excel_customer = excel_data[excel_data['Company'] == customer]
        access_customer = access_data[access_data['KundenName'] == customer]
        
        print("Excel Produkte:")
        for _, row in excel_customer.iterrows():
            print(f"  {row['Product name'][:40]:40s}: {row['Quantity']:3.0f}")
        
        print("Access Produkte:")
        for _, row in access_customer.iterrows():
            print(f"  {row['Productname'][:40]:40s}: {row['Usage']:3.0f}")
    
    # 4. Zusammenfassung
    total_excel = excel_data['Quantity'].sum()
    total_access = access_data['Usage'].sum()
    total_diff = total_excel - total_access
    
    print(f"\n=== ZUSAMMENFASSUNG ===")
    print(f"Excel Total:   {total_excel:8.1f}")
    print(f"Access Total:  {total_access:8.1f}")
    print(f"Differenz:     {total_diff:+8.1f} ({total_diff/total_excel*100:+.1f}%)")
    
    return differences, customer_differences

def main():
    """Hauptfunktion"""
    print("ALSO November 2024 Vergleich: Excel vs Access\n")
    
    # Daten laden
    excel_agg, excel_raw = load_excel_data()
    access_data, customers_df, products_df = load_access_data()
    
    # Vergleichen
    differences, customer_diffs = compare_data(excel_agg, access_data)
    
    print(f"\nAnalyse abgeschlossen. {len(differences)} Unterschiede gefunden.")

if __name__ == "__main__":
    main()