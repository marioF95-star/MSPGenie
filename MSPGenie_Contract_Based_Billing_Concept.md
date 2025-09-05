# MSPGenie - Contract-Based Billing System Konzept

## Übersicht
Ein modernes, vertragsbasiertes Abrechnungssystem für MSPs, das jede Abrechnung gegen definierte Verträge validiert und vollständige Transparenz für Kunden bietet.

## 1. Architektur-Übersicht

### Core Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Import    │    │  Contract       │    │   Billing       │
│   Engine        │────│  Validation     │────│   Engine        │
│                 │    │  Engine         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Multi-Vendor   │    │   Contract      │    │  Invoice        │
│  Data Sources   │    │   Database      │    │  Generation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 2. Contract Management System

### 2.1 Contract Structure
```php
// Laravel Model: Contract
class Contract extends Model {
    protected $fillable = [
        'customer_id',
        'contract_number',
        'start_date',
        'end_date',
        'billing_cycle', // monthly, quarterly, yearly
        'status',
        'contract_type'
    ];
    
    public function products() {
        return $this->hasMany(ContractProduct::class);
    }
    
    public function billingRules() {
        return $this->hasMany(ContractBillingRule::class);
    }
}
```

### 2.2 Contract Products & Rules
```php
class ContractProduct extends Model {
    protected $fillable = [
        'contract_id',
        'vendor',           // Microsoft, Adobe, Acronis, etc.
        'product_name',
        'product_sku',
        'commitment_type',  // P1M, P1Y, PREPAID
        'min_quantity',
        'max_quantity',
        'base_price',
        'billing_logic',    // MAX, SUM, WEIGHTED_AVERAGE
        'overage_allowed',
        'overage_rate'
    ];
}

class ContractBillingRule extends Model {
    protected $fillable = [
        'contract_id',
        'rule_type',        // REVENUE_RECOGNITION, COMMITMENT_HANDLING, OVERAGE
        'conditions',       // JSON: Regellogik
        'billing_formula'   // Berechnungsformel
    ];
}
```

## 3. Multi-Vendor Import Engine

### 3.1 Vendor-Agnostic Import System
```python
class VendorImportEngine:
    def __init__(self):
        self.parsers = {
            'ALSO': ALSOExcelParser(),
            'STARFACE': StarfaceCSVParser(),
            'TRENDMICRO': TrendMicroExcelParser(),
            'ACRONIS': AcronisCSVParser(),
            'ALTARO': AltaroCSVParser(),
        }
    
    def import_vendor_data(self, vendor: str, file_path: str, period: str):
        parser = self.parsers[vendor]
        raw_usage = parser.parse(file_path)
        
        # Normalisierung in Standard-Format
        normalized_data = self.normalize_usage_data(raw_usage, vendor)
        
        # Contract Validation
        validated_data = self.validate_against_contracts(normalized_data)
        
        return validated_data
```

### 3.2 Standardized Usage Data Format
```python
@dataclass
class UsageRecord:
    customer_identifier: str
    vendor: str
    product_name: str
    product_sku: str
    quantity: Decimal
    billing_period: str
    service_start: datetime
    service_end: datetime
    commitment_type: str  # P1M, P1Y, PREPAID
    unit_price: Decimal
    total_charge: Decimal
    interval_days: int
    raw_attributes: dict
```

## 4. Contract Validation Engine

### 4.1 Validation Pipeline
```python
class ContractValidationEngine:
    def validate_usage_against_contract(self, usage_record: UsageRecord, contract: Contract):
        validation_result = ValidationResult()
        
        # 1. Product Authorization Check
        if not self.is_product_authorized(usage_record, contract):
            validation_result.add_error("UNAUTHORIZED_PRODUCT", 
                f"Product {usage_record.product_name} not in contract")
        
        # 2. Quantity Limits Check  
        if not self.check_quantity_limits(usage_record, contract):
            validation_result.add_warning("QUANTITY_EXCEEDED", 
                f"Quantity {usage_record.quantity} exceeds contract limit")
        
        # 3. Commitment Type Validation
        if not self.validate_commitment_type(usage_record, contract):
            validation_result.add_error("INVALID_COMMITMENT",
                f"Commitment type {usage_record.commitment_type} not allowed")
        
        # 4. Billing Period Check
        if not self.validate_billing_period(usage_record, contract):
            validation_result.add_error("INVALID_PERIOD",
                f"Usage outside contract period")
        
        return validation_result
    
    def calculate_billable_amount(self, usage_records: List[UsageRecord], contract: Contract):
        billing_calculator = BillingCalculator(contract)
        return billing_calculator.calculate(usage_records)
```

## 5. Advanced Billing Calculator

### 5.1 Multi-Commitment-Type Handling
```python
class BillingCalculator:
    def __init__(self, contract: Contract):
        self.contract = contract
        self.billing_rules = contract.billingRules
    
    def calculate_customer_monthly_bill(self, usage_records: List[UsageRecord]):
        billing_summary = {}
        
        # Gruppiere nach Produkt und Commitment-Type
        grouped_usage = self.group_by_product_and_commitment(usage_records)
        
        for (product, commitment_type), records in grouped_usage.items():
            contract_product = self.get_contract_product(product)
            
            if commitment_type == "P1M":
                billable_qty = self.calculate_p1m_quantity(records)
            elif commitment_type == "P1Y": 
                billable_qty = self.calculate_p1y_quantity(records)
            elif commitment_type == "PREPAID":
                billable_qty = self.calculate_prepaid_quantity(records)
            
            billing_summary[f"{product}_{commitment_type}"] = {
                'quantity': billable_qty,
                'unit_price': contract_product.base_price,
                'total': billable_qty * contract_product.base_price,
                'billing_logic': contract_product.billing_logic
            }
        
        return billing_summary
    
    def calculate_prepaid_quantity(self, records: List[UsageRecord]):
        """Revenue Recognition für Prepaid-Produkte"""
        for record in records:
            # Service-Periode ermitteln
            service_months = self.calculate_service_months(record.service_start, record.service_end)
            
            # Anteilige Verteilung für aktuellen Monat
            current_month_portion = self.calculate_monthly_portion(
                record.service_start, record.service_end, self.billing_month
            )
            
            return record.quantity * current_month_portion
```

## 6. Contract Templates & Automation

### 6.1 Standard Contract Templates
```php
class ContractTemplate extends Model {
    protected $fillable = [
        'name',
        'description', 
        'template_type',    // STANDARD_MSP, ENTERPRISE, STARTUP
        'default_products', // JSON: Standard-Produkte
        'default_rules',    // JSON: Standard-Regeln
        'pricing_model'     // FIXED, USAGE_BASED, TIERED
    ];
}
```

### 6.2 Automated Contract Generation
```python
class ContractGenerator:
    def generate_contract_from_usage_history(self, customer_id: str, months: int = 12):
        """Generiert Vertragsentwurf basierend auf historischer Usage"""
        
        # Analysiere Usage der letzten 12 Monate
        historical_usage = self.analyze_customer_usage(customer_id, months)
        
        # Identifiziere Produkt-Pattern
        product_patterns = self.identify_usage_patterns(historical_usage)
        
        # Generiere Contract Products
        contract_products = []
        for pattern in product_patterns:
            contract_products.append(ContractProduct(
                vendor=pattern.vendor,
                product_name=pattern.product,
                commitment_type=pattern.most_common_commitment,
                min_quantity=pattern.min_usage * 0.8,  # 20% Buffer
                max_quantity=pattern.max_usage * 1.2,  # 20% Overage
                billing_logic=self.determine_billing_logic(pattern)
            ))
        
        return self.create_contract_draft(customer_id, contract_products)
```

## 7. Customer Transparency & Reporting

### 7.1 Usage Dashboard
```vue
<!-- Customer Usage Dashboard -->
<template>
  <div class="usage-dashboard">
    <ContractSummary :contract="currentContract" />
    
    <UsageAnalytics 
      :usage="monthlyUsage"
      :contract="currentContract"
      :validation-results="validationResults" 
    />
    
    <BillingPreview 
      :billing-summary="billingPreview"
      :contract="currentContract"
    />
    
    <ContractCompliance 
      :compliance-status="complianceStatus"
      :warnings="warnings"
    />
  </div>
</template>
```

### 7.2 Automated Explanations
```python
class BillingExplanationEngine:
    def generate_billing_explanation(self, customer_usage: dict, contract: Contract):
        explanation = BillingExplanation()
        
        for product, usage_data in customer_usage.items():
            if usage_data['commitment_type'] == 'PREPAID':
                explanation.add_section(f"""
                **{product} (Prepaid-Jahresabonnement)**
                
                Ihr Jahresabonnement läuft vom {usage_data['start_date']} bis {usage_data['end_date']}.
                Der Gesamtpreis von {usage_data['total_charge']}€ wird gleichmäßig über 12 Monate verteilt:
                
                - Monatlicher Anteil: {usage_data['monthly_portion']}€
                - Service-Tage im aktuellen Monat: {usage_data['service_days']}
                - Anteilige Berechnung: {usage_data['calculated_amount']}€
                """)
            
            elif usage_data['commitment_type'] == 'P1M':
                explanation.add_section(f"""
                **{product} (Monatlich kündbar)**
                
                Flexible Lizenzen mit monatlicher Kündigungsmöglichkeit.
                Abrechnung basiert auf der höchsten Lizenzanzahl im Abrechnungsmonat:
                
                - Verschiedene Nutzungsperioden: {usage_data['intervals']}
                - Maximale gleichzeitige Nutzung: {usage_data['max_quantity']} Lizenzen
                - Abrechnungsmenge: {usage_data['billable_quantity']} Lizenzen
                """)
        
        return explanation
```

## 8. Implementation Roadmap

### Phase 1: Foundation (Monate 1-3)
1. **Contract Management System**
   - Laravel Backend für Contract CRUD
   - Contract Templates System
   - Basic Validation Engine

2. **Multi-Vendor Import Framework**
   - Vendor-agnostic Import Interface
   - ALSO Excel Parser (Priorität 1)
   - Standardized Usage Data Format

### Phase 2: Core Billing (Monate 4-6)
1. **Advanced Billing Calculator**
   - P1M/P1Y/Prepaid Logic
   - Revenue Recognition für Prepaid
   - Contract Validation Pipeline

2. **Customer Portal**
   - Usage Dashboard
   - Contract Compliance Monitoring
   - Billing Explanations

### Phase 3: Automation (Monate 7-9)
1. **Automated Contract Generation**
   - Historical Usage Analysis
   - Contract Optimization Recommendations
   - Bulk Contract Management

2. **Advanced Reporting**
   - Revenue Recognition Reports
   - Contract Performance Analytics
   - Predictive Usage Modeling

### Phase 4: Enterprise Features (Monate 10-12)
1. **Multi-Tenant Architecture**
   - MSP-zu-MSP White-Label
   - Reseller Management
   - Advanced Permission System

2. **Integration APIs**
   - CRM Integration (HubSpot, Salesforce)
   - Accounting Integration (Lexware, DATEV)
   - Ticketing Integration (TANSS, ConnectWise)

## 9. Technical Stack

### Backend
- **Laravel 11** (PHP 8.3)
- **PostgreSQL 17** (Multi-tenant ready)
- **Redis** (Caching, Queue)
- **Laravel Queue** (Background processing)

### Frontend  
- **Vue.js 3** + **TypeScript**
- **Tailwind CSS** + **Headless UI**
- **Chart.js** (Usage Analytics)
- **Vue Router** (SPA)

### Import Engine
- **Python 3.12** (pandas, openpyxl)
- **Celery** (Distributed task processing)
- **FastAPI** (Import API endpoints)

### Infrastructure
- **Docker** + **Docker Compose**
- **GitHub Actions** (CI/CD)
- **PostgreSQL Partitioning** (Scalability)
- **Nginx** (Load balancing)

## 10. Compliance & Auditability

### Audit Trail
```php
class BillingAuditLog extends Model {
    protected $fillable = [
        'customer_id',
        'contract_id', 
        'billing_period',
        'original_usage_data',     // JSON: Raw import data
        'contract_rules_applied',  // JSON: Applied rules
        'validation_results',      // JSON: Validation output
        'calculated_amounts',      // JSON: Billing calculations
        'final_invoice_data',      // JSON: Final invoice
        'processed_by',
        'processed_at'
    ];
}
```

### Customer Communication
- **Automated Billing Explanations** für jede Rechnung
- **Contract Change Notifications**
- **Usage Threshold Alerts**
- **Overage Warnings** vor Rechnungsstellung

## 11. Competitive Advantages

1. **100% Contract-Based** - Keine Überraschungen für Kunden
2. **Multi-Vendor-Ready** - Ein System für alle Vendor-Daten  
3. **Revenue Recognition Compliant** - Korrekte Prepaid-Behandlung
4. **Customer Transparency** - Vollständige Nachvollziehbarkeit
5. **Automated Contract Management** - Weniger manueller Aufwand
6. **Scalable Architecture** - Multi-Tenant ready

Dieses System löst die fundamentalen Probleme des aktuellen Access-Systems und bietet eine moderne, skalierbare Basis für professionelles MSP-Billing.