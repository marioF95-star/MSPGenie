# MSPGenie - Contract-Based Multi-Vendor Billing System

## Übersicht
Moderne, vertragsbasierte Abrechnungsplattform für MSPs mit Multi-Vendor-Support und Bundle-Management. Basierend auf detaillierter Analyse der bestehenden Access-Systeme und Vendor-Datenquellen.

## Kernerkenntnisse aus der Analyse

### 🎯 Hauptprobleme des aktuellen Systems identifiziert:
1. **P1Y Prepaid Revenue Loss**: ~300€/Jahr durch falsche Revenue Recognition
2. **Multi-Commitment-Confusion**: P1M + P1Y werden nicht korrekt getrennt  
3. **Bundle-Complexity**: Kunde sieht Bundle-Artikel, dahinter Multiple-Vendor-Validierung
4. **Dual-Billing-Systems**: Starface Cloud vs Private Cloud völlig verschieden
5. **Missing Contract Foundation**: Keine vertragliche Absicherung der Abrechnungen

## Datenstruktur der ALSO Excel-Dateien

### Dateinamenmuster
- Format: `MB_NETWORKS_GmbH_MM-YYYY.xlsx` (ab 2023)
- Format: `MB_NETWORKS_GmbH_(MM.YYYY).xlsx` (2020-2022, im finish/ Ordner)

### Excel-Struktur
Die Excel-Dateien enthalten 3 Sheets:
- **Pivot Charges** (meist leer)
- **Grouped By Service** (Aggregierte Daten - 6 Spalten)
- **Raw Charges** (Detaillierte Rohdaten - 14 Spalten)

### Hauptdatensheet: "Grouped By Service"

#### Spaltenstruktur
| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| Product name | String | Name des Microsoft-Produkts |
| Attributes | String | Enthält Billing Type und Commitment-Informationen |
| Interval | String | Datumsbereich (DD.MM.YYYY - DD.MM.YYYY) |
| Quantity | Float | Anzahl |
| Price per unit | Float | Preis pro Einheit |
| Total price | Float | Gesamtpreis |

### Detaildatensheet: "Raw Charges" (Empfohlen für Import)

#### Spaltenstruktur - Raw Charges
| Spalte | Typ | Beschreibung | Beispiel |
|--------|-----|-------------|----------|
| Reseller | String | Immer "MB NETWORKS GmbH" | MB NETWORKS GmbH |
| Company | String | Endkunden-Firmenname | Adler Apotheke Stefanie Heckhoff |
| Department | String | Abteilung (meist leer) | N/A |
| Product name | String | Microsoft-Produktname | (NCE) Microsoft 365 Business Standard |
| Vendor | String | Immer "Microsoft" | Microsoft |
| VendorReference | String | **Microsoft Artikel-GUID** | 132b4d75-117b-4a1e-daee-116cd21a23bd |
| Attributes | String | Billing Type und Commitment | Billing Type=Monthly (with 1-year commitment) - P1Y Quantity=1 |
| Account | String | Lizenzanzahl (Kunden-ID) | 1 (1324324) |
| BillingStartDate | Date | Ursprüngliches Start-Datum | 06.12.2022 |
| Priceable item | String | Billing-Typ Beschreibung | Field = Quantity, Billing Type = Monthly (with 1-year commitment) - P1Y |
| Charge | Float | Einzelner Charge-Betrag | 1.57 |
| Interval | String | Abrechnungszeitraum | 01.12.2024 - 06.12.2024 |
| Contract Id | Float | ALSO Vertragsnummer | 123456.0 |
| SecondVendorReference | String | Zweite Vendor-Referenz (meist leer) | N/A |

#### Wichtige Erkenntnisse Raw Charges
- **324 Detaileinträge** vs. 230 aggregierte Einträge
- **VendorReference = Microsoft Artikel-GUID** (eindeutige Produkt-Identifikation)
- **Account-Format:** `Lizenzanzahl (Kunden-ID)` z.B. `9 (1324396)`
- **55 verschiedene Endkunden** in einer Datei
- **5 verschiedene Contract IDs** (ALSO-Verträge)

## Erkennung von monatlichen vs. jährlichen Produkten

### 1. Commitment-Pattern in Attributes-Spalte

#### Monatliche Abrechnung (P1M)
```
Billing Type=Monthly (with 1-month commitment) - P1M Quantity=X
```
**Erkennungsmuster:** `P1M` in Attributes

#### Jährliche Abrechnung (P1Y) - Monatliche Zahlung
```
Billing Type=Monthly (with 1-year commitment) - P1Y Quantity=X
```
**Erkennungsmuster:** `P1Y` in Attributes

#### Jährliche Abrechnung (P1Y) - Vorausbezahlung
```
Billing Type=Prepaid (with 1-year commitment) - P1Y Quantity=X
```
**Erkennungsmuster:** `Prepaid` und `P1Y` in Attributes
**Besonderheit:** Interval zeigt das gesamte Jahr (z.B. `27.11.2024 - 27.11.2025`)

### 2. Regex-Pattern für die Erkennung

```regex
# Für P1M (monatlich):
P1M

# Für P1Y (jährlich mit monatlicher Zahlung):
P1Y.*Monthly

# Für P1Y (jährlich mit Vorausbezahlung):
P1Y.*Prepaid

# Vollständiger Billing Type:
Billing Type=([^=]+?)(?:\s|$)

# Commitment Pattern:
(P1[MY])

# Prepaid Pattern:
Billing Type=Prepaid.*P1Y
```

### 3. Verteilung der Produkte (Beispiele)

#### Dezember 2023 (142 Datensätze)
- **P1Y (Jährlich - monatliche Zahlung):** 130 Datensätze (91.5%)
- **P1M (Monatlich):** 4 Datensätze (2.8%)
- **Ohne Pattern:** 8 Datensätze (5.7%)

#### November 2024 (71 Datensätze)
- **P1Y (Jährlich - monatliche Zahlung):** 55 Datensätze (77.5%)
- **P1M (Monatlich):** 12 Datensätze (16.9%)
- **P1Y (Jährlich - Vorausbezahlung):** 1 Datensatz (1.4%)
- **Sonstige:** 3 Datensätze (4.2%)

#### Dezember 2024 (230 Datensätze) - **MIT VORAUSBEZAHLUNG**
- **P1Y (Jährlich - monatliche Zahlung):** 135 Datensätze (58.7%)
- **P1Y (Jährlich - Vorausbezahlung):** 75 Datensätze (32.6%)
- **P1M (Monatlich):** 17 Datensätze (7.4%)
- **Sonstige:** 3 Datensätze (1.3%)

**Wichtige Erkenntnis:** Dezember 2024 zeigt einen signifikanten Anteil an Vorausbezahlungen (32.6%)

## Multi-Vendor Support

### Vendor-Konfiguration
Das System muss für verschiedene Hersteller konfigurierbar sein. Aktuell unterstützt:
- **Microsoft** (99% der Datensätze)
- **Adobe** (1% der Datensätze)

### Vendor-spezifische Parameter

#### Microsoft-Konfiguration
```yaml
microsoft:
  vendor_name: "Microsoft"
  product_prefix: "(NCE)"
  vendor_reference_format: "uuid"  # GUID format
  billing_attributes:
    monthly_pattern: "P1M.*Monthly"
    yearly_monthly_pattern: "P1Y.*Monthly"
    yearly_prepaid_pattern: "P1Y.*Prepaid"
  priceable_item_field: "Quantity"
  commitment_periods: ["P1M", "P1Y"]
  supports_negative_quantities: true
```

#### Adobe-Konfiguration
```yaml
adobe:
  vendor_name: "Adobe"
  product_prefix: "Adobe"
  vendor_reference_format: "custom"  # Custom format ending in NA
  billing_attributes:
    default_pattern: "Level1QuantityDropdown"
  priceable_item_field: "Level1QuantityDropdown"
  commitment_periods: ["N/A"]
  supports_negative_quantities: false
```

#### Zukünftige Vendor-Template
```yaml
vendor_template:
  vendor_name: ""
  product_prefix: ""
  vendor_reference_format: "string|uuid|numeric|custom"
  billing_attributes:
    patterns: []
  priceable_item_field: ""
  commitment_periods: []
  supports_negative_quantities: false
  custom_parsers:
    attributes_parser: "function_name"
    interval_parser: "function_name"
    pricing_parser: "function_name"
```

### Vendor-Parser Interface
```python
class VendorParser:
    def __init__(self, config):
        self.config = config
    
    def parse_attributes(self, attributes_string):
        """Parse vendor-specific attributes"""
        pass
    
    def classify_billing_type(self, attributes_string):
        """Classify billing type based on vendor patterns"""
        pass
    
    def parse_vendor_reference(self, vendor_ref):
        """Parse and validate vendor reference format"""
        pass
    
    def extract_commitment_info(self, attributes_string):
        """Extract commitment period and payment info"""
        pass
```

## Import-Algorithmus

### Schritt 1: Datei-Erkennung
1. Dateiname parsen für Monat/Jahr
2. Sheet "Raw Charges" laden (bevorzugt) oder "Grouped By Service"
3. Spaltenstruktur validieren
4. **Vendor-Erkennung** und Konfiguration laden

### Schritt 2: Vendor-spezifische Datenverarbeitung
```python
class ALSOImporter:
    def __init__(self):
        self.vendor_parsers = {}
        self.load_vendor_configs()
    
    def load_vendor_configs(self):
        """Lade Vendor-Konfigurationen"""
        self.vendor_parsers = {
            'Microsoft': MicrosoftParser(self.get_microsoft_config()),
            'Adobe': AdobeParser(self.get_adobe_config())
        }
    
    def process_record(self, record):
        vendor = record['Vendor']
        parser = self.vendor_parsers.get(vendor)
        
        if not parser:
            raise ValueError(f"Unsupported vendor: {vendor}")
        
        # Vendor-spezifische Verarbeitung
        billing_info = parser.classify_billing_type(record['Attributes'])
        payment_info = parser.extract_commitment_info(record['Attributes'])
        vendor_ref_info = parser.parse_vendor_reference(record['VendorReference'])
        
        return {
            'vendor': vendor,
            'billing_type': billing_info['type'],
            'payment_type': payment_info['payment'],
            'commitment_period': payment_info['commitment'],
            'vendor_reference_validated': vendor_ref_info['valid'],
            **record
        }

class MicrosoftParser(VendorParser):
    def classify_billing_type(self, attributes):
        attr_str = str(attributes)
        
        if 'P1M' in attr_str:
            return {'type': 'monthly', 'pattern': 'P1M'}
        elif 'P1Y' in attr_str and 'Prepaid' in attr_str:
            return {'type': 'yearly_prepaid', 'pattern': 'P1Y_Prepaid'}
        elif 'P1Y' in attr_str and 'Monthly' in attr_str:
            return {'type': 'yearly_monthly', 'pattern': 'P1Y_Monthly'}
        else:
            return {'type': 'unknown', 'pattern': None}

class AdobeParser(VendorParser):
    def classify_billing_type(self, attributes):
        # Adobe hat einfacheres Billing
        return {'type': 'subscription', 'pattern': 'Level1QuantityDropdown'}
    
    def extract_commitment_info(self, attributes):
        # Adobe-spezifische Logik
        return {'payment': 'subscription', 'commitment': 'annual'}
```

### Schritt 3: Datenvalidierung
- Interval-Format: `DD.MM.YYYY - DD.MM.YYYY`
- Numeric-Felder: Quantity, Price per unit, Total price
- Product name: Nicht leer

### Schritt 4: Normalisierung
- Datumsformat standardisieren
- Produktnamen bereinigen (NCE-Prefix behandeln)
- Preise auf 2 Dezimalstellen runden

## Produktkategorisierung

### Microsoft 365 Produkte
- **Teams:** `Microsoft Teams`, `Teams EEA`
- **Office 365:** `Office 365 E3`, `Office 365 E1`
- **Microsoft 365:** `Microsoft 365 Business`, `Microsoft 365 Apps`
- **Exchange:** `Exchange Online`
- **Defender:** `Microsoft Defender for Office 365`

### Erkennungspattern
```regex
# NCE-Produkte (New Commerce Experience):
^\(NCE\)\s+(.+)$

# Legacy-Produkte:
^(Microsoft 365|Office 365|Exchange|Teams|Defender)
```

## Zeitraumbehandlung

### Interval-Parsing
Das Interval-Feld enthält den Abrechnungszeitraum:
- **Monatliche Abrechnung:** `01.12.2023 - 04.12.2023` (kurze Zeiträume)
- **Vorausbezahlung:** `02.12.2024 - 02.12.2025` (genau 1 Jahr)

### Erkennung der Zahlungsart anhand Interval
- **P1M:** Zeitraum < 31 Tage
- **P1Y Monthly:** Zeitraum < 31 Tage, monatlich abgerechnet
- **P1Y Prepaid:** Zeitraum = 365/366 Tage, Jahresvorausbezahlung

## Besondere Fälle

### Negative Quantitäten bei Prepaid
In Prepaid-Abrechnungen können negative Quantitäten auftreten:
```
Billing Type=Prepaid (with 1-year commitment) - P1Y Quantity=-3
```
**Bedeutung:** Stornierung oder Rückerstattung von Lizenzen  
**Behandlung:** Als Korrektor-Eintrag verarbeiten (negative Beträge)

## Datenbank-Schema (Empfehlung)

```sql
-- Haupttabelle für ALSO Billing Import
CREATE TABLE also_billing_import (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    import_date DATE,
    billing_month DATE,
    
    -- Vendor-Info
    vendor VARCHAR(50) NOT NULL,
    vendor_config_version VARCHAR(10) DEFAULT '1.0',
    
    -- Grunddaten
    product_name VARCHAR(255),
    product_category VARCHAR(100),
    vendor_reference VARCHAR(255),
    vendor_reference_valid BOOLEAN DEFAULT TRUE,
    
    -- Billing-Klassifikation (vendor-agnostic)
    billing_type VARCHAR(50), -- monthly, yearly_monthly, yearly_prepaid, subscription
    payment_type VARCHAR(50), -- monthly, prepaid, subscription
    commitment_period VARCHAR(20), -- P1M, P1Y, annual, etc.
    billing_pattern VARCHAR(100), -- P1M, P1Y_Prepaid, Level1QuantityDropdown
    
    -- Kunde/Vertrag
    company_name VARCHAR(255),
    customer_id VARCHAR(20), -- aus Account extrahiert
    license_count INT, -- aus Account extrahiert
    contract_id VARCHAR(50), -- ALSO Contract ID
    
    -- Zeiträume
    interval_start DATE,
    interval_end DATE,
    billing_start_date DATE,
    
    -- Beträge
    charge DECIMAL(10,2), -- Einzelner Charge (Raw Charges)
    quantity DECIMAL(10,2),
    price_per_unit DECIMAL(10,2),
    total_price DECIMAL(10,2),
    
    -- Rohdaten
    attributes TEXT,
    priceable_item TEXT,
    source_sheet ENUM('grouped', 'raw'),
    
    -- Metadaten
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indices
    INDEX idx_vendor (vendor),
    INDEX idx_vendor_ref (vendor_reference),
    INDEX idx_customer (customer_id),
    INDEX idx_contract (contract_id),
    INDEX idx_billing_month (billing_month),
    INDEX idx_billing_type (billing_type)
);

-- Vendor-Konfigurationstabelle
CREATE TABLE also_vendor_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    vendor_name VARCHAR(50) UNIQUE NOT NULL,
    version VARCHAR(10) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Konfiguration als JSON
    config JSON NOT NULL,
    
    -- Metadaten
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_vendor_active (vendor_name, is_active)
);

-- Beispiel-Inserts für Vendor-Konfigurationen
INSERT INTO also_vendor_configs (vendor_name, version, config) VALUES 
('Microsoft', '1.0', JSON_OBJECT(
    'product_prefix', '(NCE)',
    'vendor_reference_format', 'uuid',
    'billing_attributes', JSON_OBJECT(
        'monthly_pattern', 'P1M.*Monthly',
        'yearly_monthly_pattern', 'P1Y.*Monthly', 
        'yearly_prepaid_pattern', 'P1Y.*Prepaid'
    ),
    'priceable_item_field', 'Quantity',
    'commitment_periods', JSON_ARRAY('P1M', 'P1Y'),
    'supports_negative_quantities', true
)),
('Adobe', '1.0', JSON_OBJECT(
    'product_prefix', 'Adobe',
    'vendor_reference_format', 'custom',
    'billing_attributes', JSON_OBJECT(
        'default_pattern', 'Level1QuantityDropdown'
    ),
    'priceable_item_field', 'Level1QuantityDropdown',
    'commitment_periods', JSON_ARRAY('annual'),
    'supports_negative_quantities', false
));

-- Mapping-Tabelle für Produktkategorien (optional)
CREATE TABLE also_product_categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    vendor VARCHAR(50),
    product_name VARCHAR(255),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    
    UNIQUE KEY unique_vendor_product (vendor, product_name),
    INDEX idx_vendor_cat (vendor, category)
);
```

## Fehlerbehandlung

### Häufige Probleme
1. **Leere Sheets:** Prüfung auf DataFrame.shape[0] > 0
2. **Fehlende Spalten:** Spalten-Validierung vor Import
3. **Ungültige Datumsformate:** Try-catch bei Datum-Parsing
4. **Encoding-Probleme:** UTF-8 Behandlung

### Logging-Anforderungen
- Importierte Datensätze pro Datei
- Übersprungene/fehlerhafte Datensätze
- Unbekannte Billing Types
- Performance-Metriken

## Konfiguration

### Import-Parameter
```yaml
also_import:
  source_directory: "data/also"
  supported_extensions: [".xlsx"]
  preferred_sheet: "Raw Charges"  # Fallback: "Grouped By Service"
  date_format: "%d.%m.%Y"
  decimal_places: 2
  
  # Multi-Vendor Support
  vendor_config_source: "database"  # database|file
  vendor_config_cache_ttl: 3600  # seconds
  
  # Unbekannte Vendor behandlung
  unknown_vendor_action: "error"  # error|skip|import_basic
  
  # Validierung
  validate_vendor_references: true
  strict_billing_pattern_matching: false
```

### Neue Vendor hinzufügen

#### Schritt 1: Konfiguration in Datenbank
```sql
INSERT INTO also_vendor_configs (vendor_name, version, config) VALUES 
('Google', '1.0', JSON_OBJECT(
    'product_prefix', 'Google',
    'vendor_reference_format', 'string',
    'billing_attributes', JSON_OBJECT(
        'subscription_pattern', 'Google Workspace.*',
        'annual_pattern', 'Annual.*Subscription'
    ),
    'priceable_item_field', 'Seats',
    'commitment_periods', JSON_ARRAY('monthly', 'annual'),
    'supports_negative_quantities', false,
    'custom_parsers', JSON_OBJECT(
        'attributes_parser', 'GoogleAttributesParser',
        'interval_parser', 'StandardIntervalParser'
    )
));
```

#### Schritt 2: Parser-Klasse implementieren
```python
class GoogleParser(VendorParser):
    def classify_billing_type(self, attributes):
        attr_str = str(attributes)
        
        if 'Annual' in attr_str:
            return {'type': 'annual_subscription', 'pattern': 'Annual'}
        elif 'Monthly' in attr_str:
            return {'type': 'monthly_subscription', 'pattern': 'Monthly'}
        else:
            return {'type': 'subscription', 'pattern': 'Standard'}
    
    def parse_vendor_reference(self, vendor_ref):
        # Google-spezifische Referenz-Validierung
        return {'valid': bool(vendor_ref), 'format': 'string'}
```

#### Schritt 3: Parser registrieren
```python
# In ALSOImporter.load_vendor_configs()
self.vendor_parsers['Google'] = GoogleParser(self.get_vendor_config('Google'))
```

## Testing

### Testdaten
- **2020-2022:** Älteres Format ohne NCE-Prefix
- **2023-2025:** Neues Format mit NCE-Prefix
- **Verschiedene Monate:** Unterschiedliche Datenmengen

### Validierung
1. Import von Beispieldateien
2. Verifikation der Billing-Type-Klassifizierung
3. Summen-Validierung (Total price)
4. Datum-Konsistenz prüfen