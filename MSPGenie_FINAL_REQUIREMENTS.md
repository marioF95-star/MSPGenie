# MSPGenie - Finales Requirements Specification

**Version**: 1.0  
**Datum**: 5. September 2025  
**Status**: Ready for Implementation

---

## Executive Summary

MSPGenie ist eine **contract-based Multi-Vendor-Billing-Plattform** für Managed Service Provider, die komplexe Vendor-Abrechnungen in transparente, vertragssichere Kundenrechnungen transformiert und **flexibles Prepaid/Postpaid Customer Billing** unterstützt.

### Business Case
- **Revenue Recovery**: ~300€/Jahr durch P1Y Prepaid Revenue Recognition
- **Cash Flow Improvement**: Customer Prepaid Billing für kritische Kunden
- **Risk Mitigation**: Prepaid eliminiert Zahlungsausfälle bei insolventen Kunden
- **Customer Transparency**: 100% nachvollziehbare Abrechnungen mit Adjustment-Explanations
- **Operational Efficiency**: Automatisierte Multi-Vendor-Imports + Reconciliation
- **Zero Disputes**: Contract-based billing mit Prepaid/Postpaid-Flexibilität

## 1. System Architecture

### 1.1 Core Components
```
Contract Management Engine ←→ Multi-Vendor Import Engine
         ↕                           ↕
Customer Portal (Prepaid)  ←→ Billing Calculation Engine
         ↕                           ↕  
Revenue Recognition        ←→ Bundle Validation System
         ↕                           ↕
Prepaid Reconciliation     ←→ Adjustment Processing Engine
```

### 1.2 Technology Stack
- **Backend**: Laravel 11 (PHP 8.3)
- **Frontend**: Vue.js 3 + TypeScript
- **Database**: PostgreSQL 17 (Multi-tenant ready)
- **Import Engine**: Python 3.12 (pandas, openpyxl)
- **Infrastructure**: Docker + GitHub Actions

## 2. Vendor Integration Requirements

### 2.1 Priority 1 Vendors (Core Revenue)

#### ALSO (Microsoft 365) - 43.7% Coverage
**Data Source**: Excel MB_NETWORKS_GmbH_MM-YYYY.xlsx → Sheet "Raw Charges"
**Billing Complexity**: HIGH (P1M/P1Y/Prepaid)

```python
# Critical Business Logic
def process_also_commitment(attributes: str) -> CommitmentType:
    if "Prepaid" in attributes:
        return CommitmentType.P1Y_PREPAID  # 12-month revenue recognition
    elif "P1M" in attributes:
        return CommitmentType.P1M  # Monthly commitment pool
    elif "P1Y" in attributes:
        return CommitmentType.P1Y  # Yearly commitment pool
    
# Aggregation Logic  
customer_billing = {
    "P1M_pool": max(p1m_quantities),
    "P1Y_pool": max(p1y_quantities),
    "PREPAID_monthly": calculate_prepaid_revenue(prepaid_charges, month)
}
total_billable = sum(customer_billing.values())
```

**Requirements**:
- ✅ Separate commitment type pools (P1M + P1Y)
- ✅ Revenue recognition for Prepaid over service period
- ✅ VendorReference GUID tracking for Microsoft products
- ✅ Interval-based service period calculation

#### Starface (Telephony) - 53.8% Coverage  
**Data Source**: Dual-system complexity
- **Cloud**: CSV files (id;domain_name;user;products...)
- **Private**: PDF→Excel via StarfacePDFInvoice tool

```python
# Dual System Architecture
class StarfaceBillingEngine:
    def process_cloud_usage(csv_data):
        # Usage-based: MAX(monthly_users) per domain
        return aggregate_by_domain_and_product(csv_data, "MAX")
    
    def process_private_licenses(pdf_data): 
        # License-based: Fixed monthly fees
        return extract_license_fees(pdf_data)
    
    def ensure_no_double_billing(cloud_results, private_results):
        # Validate customer separation
        assert set(cloud_customers) & set(private_customers) == set()
```

**Requirements**:
- ✅ Cloud CSV parser (domain→customer mapping)
- ✅ Private PDF invoice integration
- ✅ Dual contract templates (Usage vs License)
- ✅ No double-charging validation

#### N-Sight (Endpoint Protection) - Bundle Paradigm
**Data Source**: CSV/Excel with SKU details
**Billing Complexity**: EXTREME (Customer Bundle + Vendor Validation)

```python
# Bundle Architecture Pattern
class BundleContract:
    customer_facing_product = {
        "name": "IM+ Endpoint Basic",
        "price": 15.00,
        "unit": "endpoint_month",
        "visible_to_customer": True
    }
    
    validation_components = [
        {"sku": "MAXWMXXWXXE", "vendor": "N-Sight", "validation_only": True},
        {"sku": "MAXMAVXWXXE", "vendor": "N-Sight", "validation_only": True}, 
        {"sku": "MAXDEMAWXXE", "vendor": "N-Sight", "validation_only": True}
    ]
    
    def validate_bundle(customer_usage, nsight_data):
        # Each endpoint must have corresponding N-Sight validation
        return cross_reference_validation(customer_usage, nsight_data)
```

**Requirements**:
- ✅ Bundle product management (customer-facing)
- ✅ Component validation system (vendor-facing)
- ✅ Automatic cross-referencing with N-Sight data
- ✅ Transparent bundle explanations for customers

### 2.2 Priority 2 Vendors (Standard Implementation)

#### Altaro (Backup) - 20.9% Coverage
**Data Source**: CSV AltaroBillingUsageReport_YYYYMM.csv
**Billing Logic**: Product + Object Type Matrix

```python
# Altaro Dual Product Logic (from VBA)
def process_altaro_usage(csv_data):
    billable_entries = csv_data[csv_data['Invoice'] == 'Billable']
    
    # Split by backup plan type
    office365_backup = billable_entries[
        (billable_entries['Backup Plan'] != 'Default MSP Plan')
    ]  # IDProductclass 3
    
    vm_backup = billable_entries[
        (billable_entries['Backup Plan'] == 'Default MSP Plan')  
    ]  # IDProductclass 6
    
    return aggregate_backup_plans(office365_backup, vm_backup)
```

#### TrendMicro (Security) - 24.1% Coverage
**Data Source**: XLS CustomerSummary(Month Year).xls
**Billing Logic**: Standard usage-based (Genutzt field)

#### Acronis (Backup) - 10.8% Coverage  
**Data Source**: CSV Bericht_YYYY_MM.csv
**Billing Logic**: Standard usage-based (Gesamtnutzung field)

### 2.3 Priority 3 Vendors (Specialized)

#### Securepoint (UTM) - 4.4% Coverage
**Billing Logic**: License-based with free allowances
**Key Feature**: Kostenpflichtige vs Kostenlose Einheiten

#### Wasabi (Storage) - Storage-based  
**Billing Logic**: TB consumption-based
**Key Metrics**: Active Storage (TB), Bucket organization

## 3. Contract System Requirements

### 3.1 Contract Types Required

#### Standard MSP Contract
```php
// Single vendor, simple billing
ContractTemplate::create([
    'name' => 'Standard MSP Service',
    'vendors' => ['TrendMicro'],
    'billing_logic' => 'usage_based',
    'complexity_tier' => 'STANDARD'
]);
```

#### Multi-Vendor MSP Contract  
```php
// Multiple vendors, coordinated billing
ContractTemplate::create([
    'name' => 'Complete MSP Package', 
    'vendors' => ['ALSO', 'Starface', 'Altaro', 'TrendMicro'],
    'billing_logic' => 'multi_vendor_coordinated',
    'complexity_tier' => 'HIGH'
]);
```

#### Enterprise Bundle Contract
```php
// Bundle products, internal validation
ContractTemplate::create([
    'name' => 'Enterprise Endpoint Protection',
    'vendors' => ['N-Sight', 'Internal'],
    'billing_logic' => 'bundle_with_validation',
    'complexity_tier' => 'EXTREME'
]);
```

### 3.2 Contract Features Required

#### Revenue Recognition Engine
```python
class RevenueRecognitionEngine:
    def calculate_prepaid_revenue(prepaid_charge, service_start, service_end, billing_month):
        """
        Distribute prepaid revenue over service period
        Critical for P1Y Prepaid (ALSO) - fixes 300€/year loss
        """
        total_service_days = (service_end - service_start).days
        
        # Calculate portion for billing month
        month_start = billing_month.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
        
        service_days_in_month = calculate_overlap_days(
            service_start, service_end, month_start, month_end
        )
        
        monthly_portion = service_days_in_month / total_service_days
        return prepaid_charge * monthly_portion
```

#### Bundle Management System
```php
class BundleManager 
{
    public function createBundle(Contract $contract, array $bundleConfig)
    {
        // Customer-facing bundle product
        $bundle = ContractProduct::create([
            'contract_id' => $contract->id,
            'name' => $bundleConfig['customer_name'],
            'price' => $bundleConfig['customer_price'], 
            'customer_visible' => true,
            'is_bundle' => true
        ]);
        
        // Internal validation components
        foreach ($bundleConfig['validation_components'] as $component) {
            ContractProduct::create([
                'contract_id' => $contract->id,
                'vendor' => $component['vendor'],
                'product_sku' => $component['sku'],
                'bundle_parent_id' => $bundle->id,
                'customer_visible' => false,
                'validation_only' => true
            ]);
        }
    }
    
    public function validateBundleUsage(Bundle $bundle, array $vendorData)
    {
        foreach ($bundle->validationComponents as $component) {
            $vendorUsage = $this->findVendorUsage($vendorData, $component);
            
            BundleValidation::create([
                'bundle_id' => $bundle->id,
                'component_id' => $component->id,
                'expected_usage' => $bundle->customer_usage,
                'actual_vendor_usage' => $vendorUsage,
                'validation_status' => $this->compareUsage($bundle, $vendorUsage)
            ]);
        }
    }
}
```

#### Multi-Commitment Support  
```php
class CommitmentProcessor
{
    public function processALSOCommitments(array $rawCharges)
    {
        $commitmentPools = ['P1M' => [], 'P1Y' => [], 'PREPAID' => []];
        
        foreach ($rawCharges as $charge) {
            $commitmentType = $this->parseCommitmentType($charge['attributes']);
            $commitmentPools[$commitmentType][] = $charge;
        }
        
        // Separate aggregation per pool
        $billingResults = [];
        foreach ($commitmentPools as $type => $charges) {
            if ($type === 'PREPAID') {
                $billingResults[$type] = $this->calculatePrepaidRevenue($charges);
            } else {
                $billingResults[$type] = $this->aggregateByMaxQuantity($charges);
            }
        }
        
        return $billingResults;
    }
}
```

## 4. Data Quality & Migration

### 4.1 Customer Mapping Success Rates
| Vendor | Current Mapping | Target | Action Required |
|--------|-----------------|---------|-----------------|
| ALSO | 100% | 100% | ✅ Working |  
| Starface Cloud | 0% | 95% | 🔧 Fix domain mapping |
| Starface Private | 40% | 95% | 🔧 Improve fuzzy matching |
| Altaro | 90%* | 95% | 🔧 Validate mapping |
| TrendMicro | 95%* | 95% | ✅ Working |
| Others | TBD | 90% | 🔧 Implementation needed |

### 4.2 Access Database Migration
- **tblKunden** (158 customers) → `customers` table
- **tblProduct** → `contract_products` table  
- **tblUsage** → `usage_records` table
- **tblOwnProducts** → `contract_products` (bundle system)
- **Multi-vendor IDs** → `external_ids` JSONB field

## 5. Implementation Roadmap

### Week 1: Foundation + ALSO
- Day 1-2: Laravel setup + Core models
- Day 3-4: ALSO import with P1M/P1Y/Prepaid logic  
- Day 5: Revenue recognition engine

### Week 2: Multi-Vendor Core
- Day 6-7: Starface dual-system import
- Day 8-9: Altaro product matrix logic
- Day 10: TrendMicro + Acronis standard imports

### Week 3: Advanced Features  
- Day 11-13: N-Sight bundle system
- Day 14-15: Customer portal + contract dashboard
- Day 16-20: Specialized vendors (Securepoint, Wasabi)

### Week 4: Production Ready
- Day 21-25: Testing + Quality assurance
- Day 26-30: Migration tools + Go-live preparation

## 6. Success Criteria

### Technical KPIs:
- ✅ 100% ALSO customer mapping (currently 100%)
- ✅ 0% P1Y Prepaid revenue loss (currently ~300€/year loss)
- ✅ 95%+ Starface customer mapping (currently 0% cloud, 40% private)
- ✅ All vendor imports automated (currently manual/semi-manual)

### Business KPIs:  
- ✅ 100% contract coverage for all customers
- ✅ Customer billing explanations for all invoices
- ✅ Multi-vendor bundle contracts operational
- ✅ Zero billing disputes due to transparency

### Customer Experience KPIs:
- ✅ Real-time usage dashboard for all customers
- ✅ Contract compliance monitoring
- ✅ Proactive overage alerts
- ✅ Bundle service explanations

## 7. Risk Analysis & Mitigation

### High Risk: Revenue Recognition
**Risk**: Continued P1Y Prepaid revenue loss
**Mitigation**: Priority 1 implementation of revenue recognition engine
**Timeline**: Week 1

### Medium Risk: Starface Cloud Mapping
**Risk**: 28 cloud customers not billed (300 users total)
**Mitigation**: Fix CSV domain→customer mapping
**Timeline**: Week 2

### Low Risk: Bundle System Complexity
**Risk**: N-Sight bundle validation complexity
**Mitigation**: Phased implementation, start simple
**Timeline**: Week 3

## 8. Data Architecture

### 8.1 Customer Data Model
```sql
-- Unified customer with multi-vendor IDs
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    external_ids JSONB NOT NULL DEFAULT '{}', 
    -- {
    --   "starface": "7024",
    --   "lexware": "10309", 
    --   "also": "Hinkel & Cie. Vermögensverwaltung AG",
    --   "trendmicro": "King Car Germany GmbH",
    --   "altaro": "King Car Germany GmbH"
    -- }
    billing_address JSONB,
    contact_info JSONB,
    contract_preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 8.2 Contract Product Model (Bundle-Aware)
```sql
CREATE TABLE contract_products (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT REFERENCES contracts(id),
    
    -- Product Identity
    vendor VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_sku VARCHAR(100),
    
    -- Bundle Management  
    is_bundle BOOLEAN DEFAULT false,
    bundle_parent_id BIGINT REFERENCES contract_products(id),
    customer_visible BOOLEAN DEFAULT true,
    validation_only BOOLEAN DEFAULT false,
    
    -- Billing Logic
    commitment_type VARCHAR(20), -- P1M, P1Y, PREPAID, FIXED, USAGE
    billing_logic VARCHAR(50),   -- MAX, SUM, FIXED, BUNDLE, VALIDATION
    billing_unit VARCHAR(50),    -- user_month, endpoint_month, tb_month
    
    -- Pricing & Limits
    base_price DECIMAL(10,2),
    min_quantity INTEGER DEFAULT 0,
    max_quantity INTEGER,
    overage_allowed BOOLEAN DEFAULT false,
    
    -- External References
    vendor_product_guid VARCHAR(255), -- ALSO VendorReference
    external_product_id VARCHAR(100),
    lexware_artikel VARCHAR(50),
    nsight_artikel VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 8.3 Usage Records (Multi-Vendor Normalized)
```sql
CREATE TABLE usage_records (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT REFERENCES contracts(id),
    contract_product_id BIGINT REFERENCES contract_products(id),
    customer_id BIGINT REFERENCES customers(id),
    
    -- Billing Period
    billing_month INTEGER NOT NULL,
    billing_year INTEGER NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Usage Data (Normalized across all vendors)
    raw_quantity DECIMAL(10,2),        -- From vendor data
    calculated_quantity DECIMAL(10,2), -- After business logic
    billable_quantity DECIMAL(10,2),   -- Final customer charge
    
    -- Financial Data
    vendor_unit_price DECIMAL(10,4),   -- Vendor's unit price
    customer_unit_price DECIMAL(10,4), -- Customer contract price
    total_vendor_charge DECIMAL(10,2),
    total_customer_charge DECIMAL(10,2),
    
    -- Vendor Context
    vendor VARCHAR(50) NOT NULL,
    vendor_customer_id VARCHAR(255),
    commitment_type VARCHAR(20),
    service_days_in_month INTEGER,
    
    -- Audit Trail
    raw_attributes JSONB, -- Original vendor data
    business_logic_applied JSONB, -- Applied rules
    validation_results JSONB, -- Bundle validations
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 9. Customer Portal Requirements

### 9.1 Contract Dashboard
```vue
<ContractDashboard>
  <ContractSummary 
    :contract="activeContract"
    :billing-period="currentPeriod" 
  />
  
  <UsageBreakdown>
    <!-- ALSO Products -->
    <CommitmentTypeSection 
      :p1m-products="p1mProducts"
      :p1y-products="p1yProducts" 
      :prepaid-products="prepaidProducts"
    />
    
    <!-- Bundle Products -->  
    <BundleSection
      :bundles="bundleProducts"
      :show-components="userWantsDetails"
    />
    
    <!-- Standard Products -->
    <StandardProductsSection 
      :starface="starfaceUsage"
      :altaro="altaroUsage"
      :trendmicro="trendmicroUsage"
    />
  </UsageBreakdown>
  
  <BillingExplanations 
    :explanations="generatedExplanations"
  />
</ContractDashboard>
```

### 9.2 Billing Transparency Features
- **Commitment Type Explanations**: Why P1M vs P1Y pricing differs
- **Prepaid Revenue Distribution**: How yearly charges spread over months  
- **Bundle Component Breakdown**: What's included in bundle pricing
- **Usage Threshold Alerts**: Proactive overage warnings
- **Historical Usage Trends**: Usage patterns over time

## 10. Quality Assurance Requirements

### 10.1 Data Validation Rules
```python
# Vendor Data Validation
class VendorDataValidator:
    def validate_also_import(excel_data):
        # Check required sheets
        assert 'Raw Charges' in excel_data.sheet_names
        
        # Validate required columns  
        required = ['Company', 'Product name', 'Attributes', 'Charge', 'Interval']
        assert all(col in excel_data['Raw Charges'].columns for col in required)
        
        # Business logic validation
        for row in excel_data['Raw Charges']:
            commitment = parse_commitment_type(row['Attributes'])
            assert commitment in ['P1M', 'P1Y', 'P1Y_PREPAID']
            
            if commitment == 'P1Y_PREPAID':
                # Validate prepaid interval
                assert validate_prepaid_interval(row['Interval'])
    
    def validate_customer_mapping(vendor, vendor_data, customers_df):
        # Ensure all vendor customers can be mapped
        mapping_success_rate = calculate_mapping_success(vendor_data, customers_df)
        assert mapping_success_rate >= 0.90, f"Mapping success {mapping_success_rate:.1%} below threshold"
```

### 10.2 Contract Validation Rules
```php
class ContractValidator 
{
    public function validateContractCompleteness(Contract $contract)
    {
        // Every customer must have contract coverage
        $missingProducts = $this->findMissingProductCoverage($contract);
        if (!empty($missingProducts)) {
            throw new ContractValidationException("Missing product coverage: " . implode(', ', $missingProducts));
        }
        
        // Bundle integrity
        foreach ($contract->bundleProducts as $bundle) {
            $this->validateBundleIntegrity($bundle);
        }
        
        // Price consistency
        $this->validatePriceConsistency($contract);
    }
}
```

## 11. Customer Prepaid Billing (Critical Addition)

### 11.1 Prepaid vs Postpaid Customer Models

#### Standard Postpaid (Current Model)
- **Timeline**: Service → Vendor Invoice → Customer Invoice
- **Risk**: Low (bekannte Kosten)
- **Cash Flow**: MSP vorfinanziert

#### Customer Prepaid (Risk Management)
- **Timeline**: Customer Invoice → Service → Vendor Invoice → Reconciliation
- **Risk**: Medium (Usage-Änderungen = Adjustments)
- **Cash Flow**: Customer vorfinanziert
- **Target**: Nicht-solvente oder High-Risk Kunden

### 11.2 Prepaid Reconciliation Engine
```php
class PrepaidReconciliationEngine 
{
    public function reconcileMonth(Contract $contract, int $month, int $year)
    {
        $prepaidInvoice = $contract->getPrepaidInvoice($month, $year);
        $actualUsage = $this->getActualVendorUsage($contract, $month, $year);
        
        $adjustment = $this->calculateAdjustment($prepaidInvoice, $actualUsage);
        
        if (abs($adjustment['amount']) >= $contract->adjustment_threshold) {
            return $adjustment['amount'] > 0 
                ? $this->generateAdditionalInvoice($adjustment)
                : $this->generateCreditNote($adjustment);
        }
    }
}
```

### 11.3 Risk-Based Prepaid Terms
- **HIGH_RISK**: Sofortzahlung, tägliche Reconciliation
- **MEDIUM_RISK**: 7-Tage-Zahlung, wöchentliche Reconciliation  
- **LOW_RISK**: 14-Tage-Zahlung, monatliche Reconciliation

## 12. Deployment & Migration Strategy

### 11.1 Phased Migration from Access
```bash
# Phase 1: Parallel Operation (Month 1)
- MSPGenie runs alongside Access
- Data validation against Access results
- Customer preview access to new portal

# Phase 2: Gradual Transition (Month 2)  
- New contracts created in MSPGenie
- Import validation against Access
- Staff training on new system

# Phase 3: Full Cutover (Month 3)
- All billing through MSPGenie
- Access system archived
- Customer communication about new transparency
```

### 11.2 Success Validation
- **Billing Accuracy**: 99.5%+ match with Access during parallel period
- **Customer Satisfaction**: No increase in billing disputes
- **Operational Efficiency**: 50%+ reduction in manual billing tasks
- **Revenue Recovery**: P1Y Prepaid revenue fully captured

---

## 13. Final Recommendation

MSPGenie represents a **fundamental shift** from vendor-centric to **customer-centric billing**. The contract-based architecture solves the core MSP challenge: **translating complex multi-vendor realities into simple, transparent customer relationships**.

### Key Differentiators:
1. **Contract-First Design** - Every charge validated against customer agreement
2. **Bundle Transparency** - Customers see simple products, system handles complexity
3. **Revenue Recognition** - Proper accounting for Prepaid and complex commitments  
4. **Multi-Vendor Coordination** - Unified customer view across all services
5. **Audit Completeness** - Full traceability from vendor data to customer invoice

### Business Impact:
- **Immediate**: ~300€/year revenue recovery (P1Y Prepaid)
- **Short-term**: 100% billing transparency, zero disputes
- **Long-term**: Scalable platform for MSP growth and new vendor integration

**Ready for implementation start: September 6, 2025** 🚀

---

*This specification is based on comprehensive analysis of 366 vendor data files, Access database with 158 customers, and detailed billing logic review. All technical requirements are validated against real data patterns.*