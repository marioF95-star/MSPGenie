# Starface Dual-Billing-System Analyse

## Überblick der Starface-Herausforderung

### Das Problem
Starface verwendet ein **duales Billing-System** mit völlig verschiedenen Datenquellen und Abrechnungslogiken, die schwer zu vereinheitlichen sind.

## 1. Die Drei Datenquellen

### 1.1 Access tblUsage (Aktueller Import)
- **737 Usage** über 49 Kunden (November 2024)
- **IDProductclass = 1** (Starface)
- **Quelle**: Unbekannt (vermutlich manuell oder alter Import)

### 1.2 Starface Cloud CSV
- **300 User** über 28 Cloud-Domains
- **Quelle**: Starface Cloud Portal Export
- **Format**: Strukturierte CSV mit Usage-Spalten
- **Billing**: Usage-basiert (User, Premium Apps)

### 1.3 Starface Private Cloud PDF→Excel
- **37 Einträge** über 10 Private Cloud Kunden (Nov 2024)
- **Quelle**: PDF-Rechnungen → Excel-Konvertierung
- **Format**: Komplexe Rechnungszeilen (1653 total)
- **Billing**: Fixed/License-basiert

## 2. Mapping-Probleme identifiziert

### 2.1 CSV Cloud Domain Mapping: 0% Erfolg
```
Problem: CSV-IDs (3092, 3128, etc.) stimmen NICHT mit tblKunden.IDStarface überein

Beispiele:
❌ grenzgang.starface-cloud.com (ID 3092) → Nicht in tblKunden
❌ wagschal.starface-cloud.com (ID 4991) → Nicht in tblKunden  
❌ hinkel.starface-cloud.com (ID 5248) → Nicht in tblKunden

Aber in tblKunden:
✅ Wagschal GmbH → IDStarface: 4991.0
✅ Hinkel & Cie → IDStarface: 5248.0
```

**Root Cause**: Die CSV-Domain-IDs sind KORREKT, aber das Mapping-System funktioniert nicht!

### 2.2 PDF Private Cloud Mapping: 40% Erfolg
```
✅ MTM Ingenieure GmbH → EXACT MATCH
✅ Karl Lubitz GmbH & Co. KG → EXACT MATCH  
✅ Knieper Consulting GmbH → EXACT MATCH
✅ Elektro Froede DLG GmbH → EXACT MATCH

❌ DAHMEN Personalservice GmbH → NICHT GEFUNDEN
❌ Praxis für Gastroenterologie → NICHT GEFUNDEN
```

## 3. Systeme sind sauber getrennt

### ✅ Keine Doppel-Abrechnung
- **0 Überschneidungen** zwischen Cloud und Private Cloud
- Kunden haben ENTWEDER Cloud ODER Private Cloud
- Saubere Trennung der Systeme

### Kunden-Verteilung:
- **Cloud**: 28 Domains (reine Cloud-Kunden)
- **Private**: 10 Kunden (eigene Hardware/VM)
- **Access**: 49 Kunden (Mix aus beiden + Legacy)

## 4. Billing-Logic-Patterns

### 4.1 Starface Cloud (CSV)
```python
Billing_Logic = "usage_based"
Products = [
    "user",                          # Basis-User (300 total)
    "STARFACE Premium App - CLOUD"   # Premium Features (16 total)
]

Calculation = "MAX(monthly_usage_per_domain)"
Contract_Type = "flexible_monthly"
```

### 4.2 Starface Private Cloud (PDF)
```python
Billing_Logic = "license_based"  
Products = [
    "STARFACE 365 PBX 1 Userlizenz",      # 132 Lizenzen
    "STARFACE 365 VM-Edition",            # 8 Server
    "STARFACE 365 Premium App"            # 57 User
]

Calculation = "fixed_monthly_fee + variable_licenses"
Contract_Type = "annual_contract_with_monthly_billing"
```

## 5. MSPGenie Contract-System Design

### 5.1 Dual Contract Templates

#### Cloud Contract Template
```php
ContractTemplate::create([
    'name' => 'Starface Cloud Standard',
    'billing_logic' => 'usage_based',
    'data_source' => 'csv_import',
    'products' => [
        [
            'name' => 'Starface Cloud User',
            'billing_unit' => 'user_month',
            'calculation' => 'MAX',
            'overage_allowed' => true
        ],
        [
            'name' => 'Premium App License', 
            'billing_unit' => 'license_month',
            'calculation' => 'MAX',
            'overage_allowed' => true
        ]
    ]
]);
```

#### Private Cloud Contract Template
```php
ContractTemplate::create([
    'name' => 'Starface Private Cloud Enterprise',
    'billing_logic' => 'fixed_license',
    'data_source' => 'pdf_import', 
    'products' => [
        [
            'name' => 'PBX User License',
            'billing_unit' => 'license_month',
            'calculation' => 'FIXED',
            'overage_allowed' => false
        ],
        [
            'name' => 'VM Edition Server',
            'billing_unit' => 'server_month', 
            'calculation' => 'FIXED',
            'overage_allowed' => false
        ]
    ]
]);
```

### 5.2 Import Pipeline Design

```python
class StarfaceImportEngine:
    def __init__(self):
        self.cloud_parser = StarfaceCloudCSVParser()
        self.private_parser = StarfacePDFInvoiceParser()
    
    def import_starface_data(self, period: str):
        results = []
        
        # 1. Cloud Import (CSV)
        csv_file = f"data/starface/{period}.csv"
        if os.exists(csv_file):
            cloud_data = self.cloud_parser.parse(csv_file)
            cloud_contracts = self.map_to_cloud_contracts(cloud_data)
            results.extend(cloud_contracts)
        
        # 2. Private Cloud Import (PDF→Excel)  
        pdf_excel = "StarfacePDFInvoice/Output/ExtractedData.xlsx"
        if os.exists(pdf_excel):
            private_data = self.private_parser.parse_period(pdf_excel, period)
            private_contracts = self.map_to_private_contracts(private_data)
            results.extend(private_contracts)
        
        return results
```

## 6. Customer Mapping Solutions

### 6.1 Cloud Domain Mapping Fix
```python
def fix_cloud_domain_mapping():
    """
    Problem: CSV-IDs stimmen mit tblKunden.IDStarface überein, 
    aber String-Conversion oder Format-Problem
    """
    
    domain_mappings = {
        'grenzgang.starface-cloud.com': 'GRENZGANG Houchmand & Fiebig GbR',
        'wagschal.starface-cloud.com': 'Wagschal GmbH', 
        'hinkel.starface-cloud.com': 'Hinkel & Cie. Vermögensverwaltung AG',
        'dahmenpbx.starface-cloud.com': 'DAHMEN Zentrale',
        # ... weitere Mappings
    }
    
    return domain_mappings
```

### 6.2 PDF Customer Fuzzy Matching
```python
def improve_pdf_customer_matching():
    """
    Bessere Fuzzy-Matching-Logik für PDF-Kundennamen
    """
    
    pdf_customer_mappings = {
        'DAHMEN Personalservice GmbH': 'DAHMEN Zentrale',
        'Zahnärztliche Gemeinschaftspraxis KÖ55': 'Zahnärzte Kö',
        'Praxis für Gastroenterologie Düsseldorf-Mitte GbR': 'Gastroenterologische Praxis Düsseldorf Mitte GbR',
        # ... weitere Mappings
    }
    
    return pdf_customer_mappings
```

## 7. Implementation Roadmap

### Phase 1: Data Source Integration
1. **Fix Cloud CSV Mapping** - Domain-to-Customer Resolution
2. **Improve PDF Parsing** - Better Customer Name Matching  
3. **Unified Import Pipeline** - Handle both sources

### Phase 2: Contract System
1. **Cloud Contract Templates** - Usage-based Billing
2. **Private Contract Templates** - Fixed License Billing
3. **Automated Contract Assignment** - Based on data source

### Phase 3: Billing Logic
1. **Cloud Billing Engine** - MAX usage calculation
2. **Private Billing Engine** - Fixed license fees
3. **Unified Invoice Generation** - Combine both systems

## 8. Business Impact

### Current Issues:
- **Incomplete Cloud Data**: 0/28 Cloud-Kunden werden nicht importiert
- **Mixed Billing Logic**: Verschiedene Systeme, eine Rechnung
- **Manual Overhead**: PDF-Konvertierung + manuelle Zuordnung

### MSPGenie Solution Benefits:
- **100% Automated Import** für beide Systeme
- **Transparent Billing** mit Contract-Validation
- **Unified Customer View** über alle Starface-Services
- **Scalable Architecture** für weitere Starface-Produkte

## 9. Technical Requirements

### Data Processing:
- **CSV Parser**: Encoding iso-8859-1, Separator ';'
- **Excel Parser**: PDF→Excel conversion + data normalization
- **Customer Resolution**: Fuzzy matching + manual override

### Contract Modeling:
- **Cloud Contracts**: Usage-based, flexible, overage-allowed
- **Private Contracts**: License-based, fixed, enterprise-grade
- **Hybrid Support**: Customers mit beiden Services (future)

### Integration Points:
- **Starface Cloud API**: Potentielle direkte Integration
- **PDF Invoice Tool**: Automatisierung der Konvertierung
- **Access Migration**: Smooth transition von current system

---

**Fazit**: Starface ist das komplexeste Billing-System mit zwei völlig verschiedenen Datenquellen. MSPGenie muss ein duales Contract-System entwickeln, das beide Welten (Cloud + Private) nahtlos vereint.