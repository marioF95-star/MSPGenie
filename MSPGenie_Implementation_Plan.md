# MSPGenie - Implementation Plan (Start: 6. September 2025)

## 🎯 Mission: Contract-Based Multi-Vendor Billing System

Entwicklung einer modernen, vertragsbasierten Abrechnungsplattform, die die komplexen Multi-Vendor-MSP-Realitäten in einfache, transparente Kundenverträge übersetzt.

## Phase 1: Foundation & Quick Wins (Woche 1-2)

### Tag 1-2: Laravel Project Setup
```bash
# Laravel 11 mit allen nötigen Packages
composer create-project laravel/laravel msp-genie
cd msp-genie

# Essential Packages
composer require spatie/laravel-permission
composer require spatie/laravel-activitylog  
composer require maatwebsite/excel
composer require barryvdh/laravel-dompdf

# Development Tools
composer require --dev laravel/telescope
composer require --dev barryvdh/laravel-debugbar
```

#### Deliverables:
- ✅ Laravel 11 Setup mit PostgreSQL
- ✅ Authentication System
- ✅ Multi-Tenant Architecture Vorbereitung
- ✅ Excel Import/Export Foundation

### Tag 3-4: Core Database Schema
```sql
-- Contracts System
CREATE TABLE contracts (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    contract_number VARCHAR(50) UNIQUE,
    name VARCHAR(255),
    start_date DATE,
    end_date DATE,
    billing_cycle VARCHAR(20), -- monthly, quarterly, yearly
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Contract Products (Bundle System)
CREATE TABLE contract_products (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT REFERENCES contracts(id),
    vendor VARCHAR(50), -- ALSO, Starface, N-Sight, etc.
    product_name VARCHAR(255),
    product_sku VARCHAR(100),
    commitment_type VARCHAR(20), -- P1M, P1Y, PREPAID, FIXED
    billing_logic VARCHAR(50), -- MAX, SUM, FIXED, BUNDLE
    customer_visible BOOLEAN DEFAULT true,
    bundle_parent_id BIGINT REFERENCES contract_products(id),
    base_price DECIMAL(10,2),
    min_quantity INTEGER DEFAULT 0,
    max_quantity INTEGER,
    overage_allowed BOOLEAN DEFAULT false,
    overage_rate DECIMAL(10,2)
);

-- Usage Data (Normalized from all vendors)
CREATE TABLE usage_records (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT REFERENCES contracts(id),
    contract_product_id BIGINT REFERENCES contract_products(id),
    vendor VARCHAR(50),
    customer_identifier VARCHAR(255),
    period_start DATE,
    period_end DATE,
    quantity DECIMAL(10,2),
    unit_price DECIMAL(10,4),
    total_charge DECIMAL(10,2),
    commitment_type VARCHAR(20),
    service_days INTEGER,
    raw_attributes JSONB,
    billing_month INTEGER,
    billing_year INTEGER,
    created_at TIMESTAMP
);

-- Bundle Validations (N-Sight Style)
CREATE TABLE bundle_validations (
    id BIGSERIAL PRIMARY KEY,
    bundle_product_id BIGINT REFERENCES contract_products(id),
    validation_product_id BIGINT REFERENCES contract_products(id),
    device_identifier VARCHAR(255),
    vendor_sku VARCHAR(100),
    validation_status VARCHAR(20),
    last_validated_at TIMESTAMP
);
```

#### Deliverables:
- ✅ Complete Database Schema
- ✅ Laravel Models mit Relationships
- ✅ Migration Files
- ✅ Factory/Seeder für Test Data

### Tag 5: Multi-Vendor Import Foundation
```python
# Import Engine Structure
/app/Services/ImportEngine/
├── VendorParsers/
│   ├── ALSOExcelParser.php
│   ├── StarfaceCSVParser.php  
│   ├── NSightExcelParser.php
│   └── PDFInvoiceParser.php
├── ContractValidation/
│   ├── CommitmentTypeValidator.php
│   ├── BundleValidator.php
│   └── RevenueRecognitionCalculator.php
└── BillingEngine/
    ├── BillingCalculator.php
    ├── BundleAggregator.php
    └── InvoiceGenerator.php
```

#### Deliverables:
- ✅ Vendor Parser Interfaces
- ✅ ALSO Excel Parser (Priorität 1)
- ✅ Contract Validation Framework
- ✅ Revenue Recognition Engine

## Phase 2: ALSO Import Perfection (Woche 3-4)

### ALSO Import mit korrekter P1M/P1Y/Prepaid Logic
```php
class ALSOImportService 
{
    public function importMonth(string $filePath, int $month, int $year)
    {
        // 1. Parse Excel Raw Charges
        $rawCharges = $this->parseRawCharges($filePath);
        
        // 2. Extract Commitment Types
        foreach ($rawCharges as $charge) {
            $commitmentType = $this->parseCommitmentType($charge['attributes']);
            $charge['commitment_type'] = $commitmentType;
            $charge['quantity'] = $this->extractQuantity($charge['attributes']);
        }
        
        // 3. Group by Customer + Product + Commitment
        $grouped = $this->groupByCustomerProductCommitment($rawCharges);
        
        // 4. Apply correct aggregation logic
        foreach ($grouped as $group) {
            if ($group['commitment_type'] === 'PREPAID') {
                $billableAmount = $this->calculatePrepaidRevenue($group, $month, $year);
            } else {
                $billableAmount = $group['max_quantity'];
            }
            
            $this->createUsageRecord($group, $billableAmount);
        }
        
        // 5. Contract validation
        $this->validateAgainstContracts($month, $year);
    }
    
    private function calculatePrepaidRevenue($group, $currentMonth, $currentYear) 
    {
        // Revenue Recognition: Distribute over service period
        $serviceStart = Carbon::parse($group['period_start']);
        $serviceEnd = Carbon::parse($group['period_end']);
        $currentPeriod = Carbon::create($currentYear, $currentMonth, 1);
        
        $serviceDaysInMonth = $this->calculateServiceDaysInMonth(
            $serviceStart, $serviceEnd, $currentPeriod
        );
        
        $totalServiceDays = $serviceStart->diffInDays($serviceEnd);
        $monthlyPortion = $serviceDaysInMonth / $totalServiceDays;
        
        return $group['total_charge'] * $monthlyPortion;
    }
}
```

#### Deliverables:
- ✅ Perfekter ALSO Import mit P1M/P1Y/Prepaid
- ✅ Revenue Recognition für Prepaid  
- ✅ Contract Validation Pipeline
- ✅ Customer Portal für ALSO Usage

## Phase 3: Starface Dual-System (Woche 5-6)

### Starface Cloud + Private Cloud Integration
```php
class StarfaceImportService
{
    public function importStarfaceData(int $month, int $year)
    {
        $results = [];
        
        // 1. Cloud CSV Import
        $cloudFile = "data/starface/{$year}{$month}.csv";
        if (file_exists($cloudFile)) {
            $cloudUsage = $this->parseCloudCSV($cloudFile);
            $results['cloud'] = $this->processCloudContracts($cloudUsage);
        }
        
        // 2. Private Cloud PDF Import  
        $pdfData = $this->loadPDFInvoiceData();
        $privateUsage = $this->filterPDFByPeriod($pdfData, $month, $year);
        $results['private'] = $this->processPrivateContracts($privateUsage);
        
        // 3. Ensure no overlap
        $this->validateNoDoubleCharging($results);
        
        return $results;
    }
    
    private function processCloudContracts($cloudUsage)
    {
        foreach ($cloudUsage as $usage) {
            // Create/Update Cloud Contract
            $contract = Contract::firstOrCreate([
                'customer_id' => $usage['customer_id'],
                'contract_type' => 'starface_cloud'
            ]);
            
            // Usage-based products
            foreach ($usage['products'] as $product => $quantity) {
                ContractProduct::updateOrCreate([
                    'contract_id' => $contract->id,
                    'product_name' => $product,
                    'billing_logic' => 'MAX',
                    'customer_visible' => true
                ]);
            }
        }
    }
}
```

#### Deliverables:
- ✅ Starface Cloud CSV Parser mit Domain Mapping
- ✅ Starface Private Cloud PDF Integration
- ✅ Dual Contract Templates
- ✅ No-Double-Charging Validation

## Phase 4: N-Sight Bundle System (Woche 7-8)

### Advanced Bundle Management
```php
class BundleManagementService 
{
    public function createIMEndpointBasicBundle(Customer $customer)
    {
        // 1. Create customer-facing bundle contract
        $contract = Contract::create([
            'customer_id' => $customer->id,
            'name' => 'IM+ Endpoint Basic Service',
            'contract_type' => 'endpoint_protection_bundle'
        ]);
        
        // 2. Create bundle product (customer sees this)
        $bundleProduct = ContractProduct::create([
            'contract_id' => $contract->id,
            'vendor' => 'MB_NETWORKS',
            'product_name' => 'IM+ Endpoint Basic',
            'billing_logic' => 'BUNDLE',
            'customer_visible' => true,
            'base_price' => 15.00,
            'billing_unit' => 'endpoint_month'
        ]);
        
        // 3. Create validation components (customer doesn't see)
        $validationSKUs = ['MAXWMXXWXXE', 'MAXMAVXWXXE', 'MAXDEMAWXXE'];
        
        foreach ($validationSKUs as $sku) {
            ContractProduct::create([
                'contract_id' => $contract->id,
                'vendor' => 'N-SIGHT',
                'product_sku' => $sku,
                'billing_logic' => 'VALIDATION',
                'customer_visible' => false,
                'bundle_parent_id' => $bundleProduct->id
            ]);
        }
        
        return $contract;
    }
    
    public function validateBundleAgainstNSight(Contract $contract, int $month, int $year)
    {
        $nsightData = $this->loadNSightData($month, $year);
        $bundleProducts = $contract->bundleProducts();
        
        foreach ($bundleProducts as $bundle) {
            $validationComponents = $bundle->validationComponents;
            
            foreach ($validationComponents as $component) {
                $nsightUsage = $this->findNSightUsage(
                    $nsightData, 
                    $component->product_sku, 
                    $contract->customer
                );
                
                BundleValidation::create([
                    'bundle_product_id' => $bundle->id,
                    'validation_product_id' => $component->id,
                    'vendor_usage_found' => !empty($nsightUsage),
                    'validation_status' => $this->validateUsage($bundle, $nsightUsage)
                ]);
            }
        }
    }
}
```

#### Deliverables:
- ✅ Bundle Management System
- ✅ N-Sight Excel Parser
- ✅ Automatic Bundle Validation
- ✅ Customer Bundle Explanations

## Phase 5: Customer Portal & Transparency (Woche 9-10)

### Vue.js Frontend mit Contract Transparency
```vue
<template>
  <div class="contract-dashboard">
    <!-- Contract Overview -->
    <ContractSummary 
      :contract="currentContract"
      :billing-period="currentPeriod"
    />
    
    <!-- Usage Breakdown -->
    <div class="usage-breakdown">
      <h3>Ihre Services im Detail</h3>
      
      <!-- Bundle Products -->
      <div v-for="bundle in bundleProducts" :key="bundle.id" class="bundle-card">
        <div class="bundle-header">
          <h4>{{ bundle.name }}</h4>
          <span class="bundle-price">{{ bundle.calculated_amount }}€</span>
        </div>
        
        <div class="bundle-explanation">
          <p>{{ generateBundleExplanation(bundle) }}</p>
        </div>
        
        <!-- Bundle Components (Expandable) -->
        <details class="bundle-components">
          <summary>Technische Details anzeigen</summary>
          <div v-for="component in bundle.components" class="component">
            <span class="vendor">{{ component.vendor }}</span>
            <span class="sku">{{ component.sku }}</span>
            <span class="status">{{ component.validation_status }}</span>
          </div>
        </details>
      </div>
      
      <!-- Commitment Type Explanations -->
      <CommitmentTypeExplainer 
        :p1m-products="p1mProducts"
        :p1y-products="p1yProducts"
        :prepaid-products="prepaidProducts"
      />
    </div>
    
    <!-- Historical Usage -->
    <UsageHistoryChart 
      :usage-data="historicalUsage"
      :contract="currentContract"
    />
  </div>
</template>
```

#### Deliverables:
- ✅ Customer Portal mit Contract Dashboard
- ✅ Bundle Explanation Engine
- ✅ Usage History Visualization
- ✅ Commitment Type Explanations

## Database Schema Design

### Complete Schema DDL
```sql
-- ==========================================
-- MSPGenie Contract-Based Billing Schema
-- ==========================================

-- Customers
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    external_ids JSONB, -- {starface: "7024", lexware: "10309", also: "Kunde Name"}
    billing_address JSONB,
    contact_info JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Contracts (Core Entity)
CREATE TABLE contracts (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(id) ON DELETE CASCADE,
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    contract_type VARCHAR(50), -- standard_msp, enterprise, bundle_contract
    start_date DATE NOT NULL,
    end_date DATE,
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    auto_renew BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'active',
    total_monthly_value DECIMAL(10,2),
    contract_template_id BIGINT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Contract Products (Bundle-aware)
CREATE TABLE contract_products (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT REFERENCES contracts(id) ON DELETE CASCADE,
    vendor VARCHAR(50) NOT NULL, -- ALSO, STARFACE, N-SIGHT, ACRONIS, etc.
    product_name VARCHAR(255) NOT NULL,
    product_sku VARCHAR(100),
    product_description TEXT,
    
    -- Bundle Management
    is_bundle BOOLEAN DEFAULT false,
    bundle_parent_id BIGINT REFERENCES contract_products(id),
    customer_visible BOOLEAN DEFAULT true,
    validation_only BOOLEAN DEFAULT false,
    
    -- Billing Logic
    commitment_type VARCHAR(20), -- P1M, P1Y, PREPAID, FIXED, USAGE_BASED
    billing_logic VARCHAR(50), -- MAX, SUM, FIXED, BUNDLE, VALIDATION
    billing_unit VARCHAR(50), -- license_month, user_month, endpoint_month
    
    -- Pricing
    base_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    margin_percent DECIMAL(5,2),
    
    -- Limits & Overages  
    min_quantity INTEGER DEFAULT 0,
    max_quantity INTEGER,
    included_quantity INTEGER DEFAULT 0,
    overage_allowed BOOLEAN DEFAULT false,
    overage_rate DECIMAL(10,2),
    
    -- Service Period
    service_start_date DATE,
    service_end_date DATE,
    
    -- External References
    external_product_id VARCHAR(100),
    vendor_product_guid VARCHAR(255),
    lexware_artikel VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage Records (Vendor Data Normalized)  
CREATE TABLE usage_records (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT REFERENCES contracts(id),
    contract_product_id BIGINT REFERENCES contract_products(id),
    customer_id BIGINT REFERENCES customers(id),
    
    -- Period & Timing
    billing_month INTEGER NOT NULL,
    billing_year INTEGER NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    service_days_in_month INTEGER,
    
    -- Usage Data
    raw_quantity DECIMAL(10,2),
    calculated_quantity DECIMAL(10,2), -- After business logic
    billable_quantity DECIMAL(10,2),   -- Final billable amount
    
    -- Pricing
    unit_price DECIMAL(10,4),
    total_charge DECIMAL(10,2),
    calculated_revenue DECIMAL(10,2),
    
    -- Vendor Info
    vendor VARCHAR(50) NOT NULL,
    vendor_customer_id VARCHAR(255),
    vendor_product_id VARCHAR(100),
    commitment_type VARCHAR(20),
    
    -- Raw Data (for audit)
    raw_attributes JSONB,
    import_metadata JSONB,
    
    -- Status
    validation_status VARCHAR(20) DEFAULT 'pending',
    billing_status VARCHAR(20) DEFAULT 'pending',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Revenue Recognition (for Prepaid)
CREATE TABLE revenue_recognition_schedule (
    id BIGSERIAL PRIMARY KEY,
    usage_record_id BIGINT REFERENCES usage_records(id),
    contract_product_id BIGINT REFERENCES contract_products(id),
    
    total_prepaid_amount DECIMAL(10,2),
    service_start_date DATE,
    service_end_date DATE,
    total_service_months INTEGER,
    
    recognition_month INTEGER,
    recognition_year INTEGER,
    monthly_recognition_amount DECIMAL(10,2),
    days_in_month INTEGER,
    recognition_percentage DECIMAL(5,4),
    
    status VARCHAR(20) DEFAULT 'scheduled',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bundle Validations
CREATE TABLE bundle_validations (
    id BIGSERIAL PRIMARY KEY,
    bundle_usage_record_id BIGINT REFERENCES usage_records(id),
    validation_usage_record_id BIGINT REFERENCES usage_records(id),
    
    device_identifier VARCHAR(255),
    vendor_sku VARCHAR(100),
    expected_quantity DECIMAL(10,2),
    actual_quantity DECIMAL(10,2),
    validation_result VARCHAR(20), -- VALID, MISSING, OVERAGE, ERROR
    
    validated_at TIMESTAMP DEFAULT NOW()
);

-- Audit Trail
CREATE TABLE billing_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT REFERENCES contracts(id),
    billing_month INTEGER,
    billing_year INTEGER,
    
    process_type VARCHAR(50), -- IMPORT, VALIDATION, CALCULATION, INVOICE
    process_status VARCHAR(20),
    
    input_data JSONB,
    output_data JSONB,
    validation_results JSONB,
    error_messages JSONB,
    
    processed_by VARCHAR(100),
    processed_at TIMESTAMP DEFAULT NOW()
);

-- Contract Templates
CREATE TABLE contract_templates (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50), -- standard_msp, enterprise, startup, bundle
    
    default_products JSONB, -- Template product configurations
    default_billing_rules JSONB,
    pricing_model VARCHAR(50), -- fixed, usage_based, tiered, bundle
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Development Roadmap - Next 10 Days

### 🚀 Tag 1 (Morgen - 6. September):
- [ ] Laravel 11 Project Setup
- [ ] PostgreSQL Database konfigurieren  
- [ ] Core Models erstellen (Customer, Contract, ContractProduct)
- [ ] Erste Migration ausführen

### Tag 2-3:
- [ ] ALSO Excel Parser entwickeln
- [ ] P1M/P1Y/Prepaid Detection implementieren
- [ ] Revenue Recognition Calculator
- [ ] Erste Contract Templates

### Tag 4-5:
- [ ] Usage Records System
- [ ] Contract Validation Pipeline
- [ ] Bundle System Foundation
- [ ] Basic Web Interface

### Tag 6-7:
- [ ] Starface Dual Import System
- [ ] N-Sight Bundle Validation
- [ ] Customer Portal Grundlagen
- [ ] Billing Explanation Engine

### Tag 8-9:
- [ ] Complete Frontend (Vue.js)
- [ ] Advanced Reporting
- [ ] Multi-Tenant Vorbereitung
- [ ] Error Handling & Logging

### Tag 10:
- [ ] Testing & Quality Assurance
- [ ] Documentation & Deployment Prep
- [ ] Migration Strategy from Access
- [ ] Go-Live Preparation

## Technical Stack Finalized

### Backend:
- **Laravel 11** (PHP 8.3)
- **PostgreSQL 17** (Partitioned tables)
- **Redis** (Cache & Queues)
- **Maatwebsite/Laravel-Excel** (Import/Export)

### Frontend:
- **Vue.js 3 + TypeScript**
- **Tailwind CSS + Headless UI**
- **Chart.js** (Usage Analytics)
- **Axios** (API Communication)

### DevOps:
- **Docker + Docker Compose**
- **GitHub Actions** (CI/CD) 
- **Laravel Sail** (Development)
- **PostgreSQL Backup Strategy**

## Success Metrics

### Week 1 KPIs:
- ✅ ALSO Import funktioniert zu 100% (aktuell 97.3%)
- ✅ P1Y Prepaid Revenue Recognition korrekt
- ✅ 0 Kundennamen-Mapping-Fehler

### Week 2 KPIs:
- ✅ Starface Dual-System Integration
- ✅ Bundle System für N-Sight operational
- ✅ Customer Portal mit Contract Transparency

### Go-Live Readiness:
- ✅ Migration von Access-System ohne Datenverlust
- ✅ Alle Vendor-Imports automatisiert
- ✅ Contract-based Billing für alle Kunden
- ✅ Customer Portal für Transparency

---

**Ready to Code!** 🚀 Das System ist vollständig durchdacht und kann morgen mit der Implementierung starten.