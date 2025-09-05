#!/usr/bin/env python3
"""
Vendor Analysis Template
Systematische Analyse aller MSPGenie Vendor-Datenquellen
"""

import pandas as pd
import os
from pathlib import Path

def analyze_vendor_directory(vendor_path: str, vendor_name: str):
    """Analysiere einen Vendor-Ordner systematisch"""
    print(f"=== {vendor_name.upper()} VENDOR ANALYSIS ===\n")
    
    if not os.path.exists(vendor_path):
        print(f"❌ Directory {vendor_path} not found")
        return {}
    
    # 1. File inventory
    files = []
    for root, dirs, filenames in os.walk(vendor_path):
        for filename in filenames:
            if filename.endswith(('.csv', '.xlsx', '.xls')):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, vendor_path)
                files.append({
                    'filename': filename,
                    'relative_path': rel_path,
                    'full_path': full_path,
                    'size': os.path.getsize(full_path),
                    'extension': filename.split('.')[-1].lower()
                })
    
    files.sort(key=lambda x: x['filename'])
    
    print(f"📁 File Inventory: {len(files)} files")
    print(f"   Extensions: {set(f['extension'] for f in files)}")
    
    # Group by year/period
    periods = set()
    for f in files:
        # Extract year/month from filename
        filename = f['filename']
        if any(year in filename for year in ['2020', '2021', '2022', '2023', '2024', '2025']):
            periods.add(filename)
    
    print(f"   Time periods: {len(periods)} files")
    print(f"   Total size: {sum(f['size'] for f in files) / (1024*1024):.1f} MB")
    
    # 2. Analyze latest file structure
    if files:
        latest_file = max(files, key=lambda x: x['filename'])
        print(f"\n📊 Latest file analysis: {latest_file['filename']}")
        
        try:
            if latest_file['extension'] == 'csv':
                # Try different encodings
                for encoding in ['utf-8', 'iso-8859-1', 'cp1252']:
                    try:
                        df = pd.read_csv(latest_file['full_path'], encoding=encoding, nrows=5)
                        print(f"   ✅ Successfully read with {encoding}")
                        print(f"   Columns ({len(df.columns)}): {list(df.columns)}")
                        print(f"   Rows: {len(df)} (sample)")
                        break
                    except:
                        continue
                else:
                    print("   ❌ Could not read CSV file")
                    
            elif latest_file['extension'] in ['xlsx', 'xls']:
                try:
                    excel_file = pd.ExcelFile(latest_file['full_path'])
                    print(f"   ✅ Excel sheets: {excel_file.sheet_names}")
                    
                    # Analyze first/main sheet
                    main_sheet = excel_file.sheet_names[0]
                    df = pd.read_excel(latest_file['full_path'], sheet_name=main_sheet, nrows=5)
                    print(f"   Main sheet '{main_sheet}': {len(df.columns)} columns")
                    print(f"   Columns: {list(df.columns)}")
                    
                except Exception as e:
                    print(f"   ❌ Could not read Excel: {e}")
        
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
    
    return {
        'vendor': vendor_name,
        'file_count': len(files),
        'total_size_mb': sum(f['size'] for f in files) / (1024*1024),
        'extensions': list(set(f['extension'] for f in files)),
        'time_coverage': periods,
        'files': files
    }

def main():
    """Hauptanalyse aller Vendor-Verzeichnisse"""
    base_path = "/mnt/c/Projekte/MSPGenie/data"
    
    vendors = [
        "Also", "Acronis", "Altaro", "N-Sight", 
        "Securepoint", "starface", "TrendMicro", "Wasabi"
    ]
    
    vendor_analysis = {}
    
    for vendor in vendors:
        vendor_path = os.path.join(base_path, vendor)
        analysis = analyze_vendor_directory(vendor_path, vendor)
        vendor_analysis[vendor] = analysis
        print("\n" + "="*80 + "\n")
    
    # Summary
    print("=== VENDOR OVERVIEW SUMMARY ===")
    print(f"{'Vendor':<15} {'Files':<8} {'Size(MB)':<10} {'Extensions':<15} {'Latest'}")
    print("-" * 70)
    
    for vendor, data in vendor_analysis.items():
        if data:
            latest = max(data['files'], key=lambda x: x['filename'])['filename'] if data['files'] else 'N/A'
            ext_str = ','.join(data['extensions'])
            print(f"{vendor:<15} {data['file_count']:<8} {data['total_size_mb']:<10.1f} {ext_str:<15} {latest[:20]}")
    
    return vendor_analysis

if __name__ == "__main__":
    analysis = main()