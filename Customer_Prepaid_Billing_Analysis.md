# Customer Prepaid Billing System - Critical Business Requirement

## Business Scenario

### Standard MSP Billing (Postpaid)
```
Timeline: Monat → Vendor Rechnung → Kunde Rechnung
Beispiel: November Service → Dezember Vendor Invoice → Dezember Customer Invoice
Risk: Low (bekannte Kosten)
```

### Customer Prepaid Billing (Cash Flow Management)
```
Timeline: Kunde Rechnung (Vorab) → Service Delivery → Vendor Rechnung → Reconciliation
Beispiel: November Kunde Invoice → November Service → Dezember Vendor Invoice → Adjustment
Risk: HIGH (Änderungen = Nachberechnung/Gutschrift)
```

## Das Prepaid Problem im Detail

### Szenario: Nicht solventer Kunde mit 50 Microsoft 365 Lizenzen

#### 1. Prepaid Invoice (November 1, 2024)
```
Customer Invoice:
- 50x Microsoft 365 Business Standard
- Geschätzte Kosten: 50 × 12.50€ = 625€
- Zahlungsziel: Sofort (prepaid)
- Service-Periode: November 2024
```

#### 2. Service Delivery (November 1-30, 2024)
```
Actual Usage (discovered December 1):
- Week 1: 50 Lizenzen (wie geplant)
- Week 2: 45 Lizenzen (5 Mitarbeiter kündigten)
- Week 3: 45 Lizenzen  
- Week 4: 52 Lizenzen (2 neue Mitarbeiter)

ALSO Invoice: MAX = 52 Lizenzen
Customer Prepaid: 50 Lizenzen
Difference: +2 Lizenzen = Nachrechnung nötig
```

#### 3. Reconciliation (December 1, 2024)
```
Vendor Invoice Analysis:
ALSO Raw Charges shows:
- P1Y Quantity=45 (01.11-15.11)  
- P1Y Quantity=52 (15.11-01.12)
→ Korrekte Berechnung: MAX = 52

Customer Adjustment Required:
- Originally billed: 50 × 12.50€ = 625.00€
- Actual vendor cost: 52 × 12.50€ = 650.00€  
- Nachrechnung: +25.00€

MSPGenie Action:
→ Generate Additional Invoice: +25.00€
→ Update contract for next month: 52 base licenses
```

### Alternative Szenario: Usage Reduction
```
Customer Prepaid: 50 Lizenzen (625€)
Actual MAX Usage: 45 Lizenzen  
Vendor Invoice: 45 × 12.50€ = 562.50€

Customer Overpayment: 62.50€
MSPGenie Action:
→ Generate Credit Note: -62.50€
→ Or: Apply credit to next month
→ Update contract for next month: 45 base licenses
```

## MSPGenie Prepaid System Requirements

### 1. Prepaid Contract Management
```php
class PrepaidContract extends Contract
{
    protected $fillable = [
        'prepaid_billing_enabled',
        'prepaid_payment_terms',    // immediate, 7_days, 14_days
        'reconciliation_frequency', // monthly, quarterly
        'adjustment_threshold',     // minimum € for adjustments
        'credit_handling_policy'    // next_month, immediate_refund, credit_account
    ];
    
    public function generatePrepaidInvoice(int $month, int $year)
    {
        // Generate invoice based on projected/contract usage
        $projectedUsage = $this->calculateProjectedUsage($month, $year);
        return $this->createInvoice($projectedUsage, 'PREPAID');
    }
    
    public function reconcileActualUsage(int $month, int $year)
    {
        $prepaidInvoice = $this->getPrepaidInvoice($month, $year);
        $actualUsage = $this->getActualVendorUsage($month, $year);
        
        $adjustment = $this->calculateAdjustment($prepaidInvoice, $actualUsage);
        
        if ($adjustment['amount'] > $this->adjustment_threshold) {
            return $this->processAdjustment($adjustment);
        }
    }
}
```

### 2. Adjustment Processing Engine
```php
class AdjustmentProcessor 
{
    public function processUsageAdjustment(PrepaidContract $contract, array $usageData)
    {
        $adjustment = $this->calculateAdjustment($contract, $usageData);
        
        if ($adjustment['type'] === 'ADDITIONAL_CHARGE') {
            return $this->generateAdditionalInvoice($adjustment);
        } elseif ($adjustment['type'] === 'CREDIT') {
            return $this->generateCreditNote($adjustment);
        }
    }
    
    private function calculateAdjustment(PrepaidContract $contract, array $actualUsage)
    {
        $prepaidAmount = $contract->getPrepaidAmountForPeriod();
        $actualCost = $this->calculateActualVendorCost($actualUsage);
        
        $difference = $actualCost - $prepaidAmount;
        
        return [
            'type' => $difference > 0 ? 'ADDITIONAL_CHARGE' : 'CREDIT',
            'amount' => abs($difference),
            'reason' => $this->generateAdjustmentReason($actualUsage, $contract),
            'supporting_data' => $actualUsage
        ];
    }
    
    private function generateAdditionalInvoice(array $adjustment)
    {
        return Invoice::create([
            'type' => 'ADJUSTMENT_ADDITIONAL',
            'original_invoice_id' => $adjustment['original_invoice_id'],
            'amount' => $adjustment['amount'],
            'description' => "Nachrechnung für zusätzliche Lizenzen: " . $adjustment['reason'],
            'due_date' => now()->addDays(14),
            'adjustment_data' => $adjustment['supporting_data']
        ]);
    }
    
    private function generateCreditNote(array $adjustment)
    {
        return CreditNote::create([
            'type' => 'ADJUSTMENT_CREDIT',
            'original_invoice_id' => $adjustment['original_invoice_id'],
            'amount' => $adjustment['amount'],
            'description' => "Gutschrift für geringere Nutzung: " . $adjustment['reason'],
            'application_method' => 'NEXT_MONTH_CREDIT',
            'credit_data' => $adjustment['supporting_data']
        ]);
    }
}
```

### 3. Customer Communication System
```php
class PrepaidCommunicationEngine
{
    public function notifyCustomerOfAdjustment(Contract $contract, array $adjustment)
    {
        $explanation = $this->generateAdjustmentExplanation($adjustment);
        
        if ($adjustment['type'] === 'ADDITIONAL_CHARGE') {
            return $this->sendAdditionalChargeNotification($contract, $adjustment, $explanation);
        } else {
            return $this->sendCreditNotification($contract, $adjustment, $explanation);
        }
    }
    
    private function generateAdjustmentExplanation(array $adjustment)
    {
        $explanation = new CustomerExplanation();
        
        $explanation->addSection("Ihre Prepaid-Abrechnung wurde angepasst", [
            "reason" => $adjustment['reason'],
            "original_amount" => $adjustment['original_amount'],
            "actual_usage" => $adjustment['actual_usage'],
            "adjustment_amount" => $adjustment['amount']
        ]);
        
        $explanation->addSection("Detaillierte Aufschlüsselung", [
            "vendor_invoice_details" => $adjustment['vendor_data'],
            "usage_breakdown" => $adjustment['usage_breakdown'],
            "calculation_method" => "Maximum gleichzeitiger Lizenzen im Abrechnungsmonat"
        ]);
        
        $explanation->addSection("Nächste Schritte", [
            "next_month_adjustment" => "Ihr Vertrag wurde für kommende Monate angepasst",
            "payment_terms" => $adjustment['payment_terms'],
            "contact_info" => "Bei Fragen wenden Sie sich an..."
        ]);
        
        return $explanation;
    }
}
```

## Customer Prepaid Dashboard Features

### Real-Time Usage Monitoring
```vue
<template>
  <div class="prepaid-dashboard">
    <!-- Current Month Status -->
    <PrepaidStatusCard>
      <div class="billing-status">
        <h3>{{ currentMonth }} {{ currentYear }} - Prepaid Status</h3>
        <div class="usage-vs-prepaid">
          <div class="prepaid-amount">
            <label>Bereits bezahlt (Prepaid)</label>
            <span class="amount">{{ contract.prepaid_amount }}€</span>
          </div>
          
          <div class="projected-cost" :class="projectionStatus">
            <label>Voraussichtliche Kosten</label>  
            <span class="amount">{{ projected_cost }}€</span>
            <span class="difference">{{ adjustment_amount > 0 ? '+' : '' }}{{ adjustment_amount }}€</span>
          </div>
        </div>
      </div>
      
      <!-- Real-time usage tracking -->
      <div class="current-usage">
        <h4>Aktuelle Nutzung (Stand: {{ last_sync }})</h4>
        <div v-for="product in prepaid_products" :key="product.id">
          <div class="product-usage">
            <span>{{ product.name }}</span>
            <div class="usage-bar">
              <div class="prepaid-bar" :style="{width: (product.prepaid_qty / product.current_qty * 100) + '%'}"></div>
              <div class="current-usage-bar" :style="{width: '100%'}"></div>
            </div>
            <span>{{ product.current_qty }} / {{ product.prepaid_qty }} ({{ product.difference > 0 ? '+' : '' }}{{ product.difference }})</span>
          </div>
        </div>
      </div>
      
      <!-- Adjustment forecast -->  
      <div v-if="adjustment_forecast" class="adjustment-forecast">
        <h4>Voraussichtliche Anpassung</h4>
        <div class="forecast-alert" :class="adjustment_type">
          <span v-if="adjustment_type === 'additional'">
            📈 Nachrechnung erwartet: +{{ adjustment_amount }}€
          </span>
          <span v-else>
            📉 Gutschrift erwartet: {{ adjustment_amount }}€
          </span>
        </div>
      </div>
    </PrepaidStatusCard>
    
    <!-- Historical adjustments -->
    <PrepaidHistoryCard :adjustments="historical_adjustments" />
    
    <!-- Contract adjustment recommendations -->
    <ContractOptimizationCard :recommendations="contract_recommendations" />
  </div>
</template>
```

## Reconciliation Workflow

### Monthly Reconciliation Process
```python
class PrepaidReconciliationWorkflow:
    def execute_monthly_reconciliation(self, month: int, year: int):
        """
        Execute complete prepaid reconciliation for all prepaid customers
        """
        prepaid_contracts = Contract.where('prepaid_billing_enabled', True).get()
        
        reconciliation_results = []
        
        for contract in prepaid_contracts:
            # 1. Get prepaid invoice for period
            prepaid_invoice = contract.getPrepaidInvoice(month, year)
            if not prepaid_invoice:
                continue
            
            # 2. Get actual vendor usage
            actual_usage = self.getAllVendorUsageForCustomer(
                contract.customer_id, month, year
            )
            
            # 3. Calculate adjustment
            adjustment = self.calculateDetailedAdjustment(
                prepaid_invoice, actual_usage, contract
            )
            
            # 4. Process adjustment if significant
            if abs(adjustment['amount']) >= contract.adjustment_threshold:
                adjustment_result = self.processAdjustment(contract, adjustment)
                reconciliation_results.append(adjustment_result)
                
                # 5. Update contract for future months
                self.updateContractProjections(contract, actual_usage)
            
            # 6. Customer notification
            self.notifyCustomerOfReconciliation(contract, adjustment)
        
        return reconciliation_results
    
    def calculateDetailedAdjustment(self, prepaid_invoice, actual_usage, contract):
        """
        Calculate detailed adjustment including vendor-specific logic
        """
        adjustments_by_vendor = {}
        total_adjustment = 0
        
        for vendor, usage_data in actual_usage.items():
            if vendor == 'ALSO':
                # Apply P1M/P1Y/Prepaid logic
                vendor_cost = self.calculateALSOActualCost(usage_data)
            elif vendor == 'Starface':
                # Apply Cloud vs Private logic  
                vendor_cost = self.calculateStarfaceActualCost(usage_data)
            elif vendor == 'N-Sight':
                # Apply Bundle validation logic
                vendor_cost = self.calculateNSightBundleCost(usage_data, contract)
            else:
                # Standard usage-based calculation
                vendor_cost = self.calculateStandardUsageCost(usage_data)
            
            prepaid_amount = prepaid_invoice.getAmountForVendor(vendor)
            vendor_adjustment = vendor_cost - prepaid_amount
            
            adjustments_by_vendor[vendor] = {
                'prepaid_amount': prepaid_amount,
                'actual_cost': vendor_cost,
                'adjustment': vendor_adjustment,
                'usage_details': usage_data
            }
            
            total_adjustment += vendor_adjustment
        
        return {
            'total_adjustment': total_adjustment,
            'vendor_breakdown': adjustments_by_vendor,
            'type': 'ADDITIONAL_CHARGE' if total_adjustment > 0 else 'CREDIT',
            'customer_explanation': self.generateCustomerExplanation(adjustments_by_vendor)
        }
```

## Contract Extensions for Prepaid Support

### Extended Contract Model
```php
class Contract extends Model 
{
    protected $fillable = [
        // ... existing fields ...
        
        // Prepaid Configuration
        'billing_model',              // POSTPAID, PREPAID, HYBRID
        'prepaid_payment_terms',      // IMMEDIATE, 7_DAYS, 14_DAYS
        'reconciliation_policy',      // MONTHLY, QUARTERLY, THRESHOLD_BASED
        'adjustment_threshold',       // Minimum amount for adjustments (€)
        'credit_handling',            // NEXT_MONTH, IMMEDIATE_REFUND, CREDIT_ACCOUNT
        'prepaid_risk_level',         // LOW, MEDIUM, HIGH (affects terms)
        
        // Projection & Planning
        'usage_projection_method',    // HISTORICAL_AVERAGE, CONTRACT_FIXED, LAST_MONTH
        'overage_buffer_percent',     // Buffer for usage increases (10%, 20%)
        'underage_refund_policy',     // AUTOMATIC, MANUAL_APPROVAL, CREDIT_ONLY
    ];
    
    public function generatePrepaidProjection(int $targetMonth, int $targetYear)
    {
        $historicalUsage = $this->getHistoricalUsage(3); // Last 3 months
        $seasonalAdjustment = $this->calculateSeasonalAdjustment($targetMonth);
        
        $baseProjection = $this->projectUsageFromHistory($historicalUsage);
        $adjustedProjection = $this->applySeasonalAdjustment($baseProjection, $seasonalAdjustment);
        $bufferedProjection = $this->applyOverageBuffer($adjustedProjection);
        
        return $bufferedProjection;
    }
}
```

### Prepaid Invoice Management
```php
class PrepaidInvoice extends Invoice
{
    protected $fillable = [
        'invoice_type',        // PREPAID_PROJECTION, ADJUSTMENT_ADDITIONAL, ADJUSTMENT_CREDIT
        'projection_basis',    // HISTORICAL, CONTRACT, CUSTOM
        'reconciliation_month',
        'reconciliation_year', 
        'original_invoice_id', // For adjustments
        'adjustment_reason',
        'vendor_breakdown',    // JSONB: per-vendor costs
        'usage_projection',    // JSONB: projected quantities
        'actual_usage',        // JSONB: actual quantities (for reconciliation)
    ];
    
    public function reconcileWithActualUsage(array $actualUsage)
    {
        $reconciliation = new PrepaidReconciliation();
        
        foreach ($this->vendor_breakdown as $vendor => $prepaid_data) {
            $actual_vendor_usage = $actualUsage[$vendor] ?? [];
            $adjustment = $reconciliation->calculateVendorAdjustment(
                $prepaid_data, $actual_vendor_usage, $vendor
            );
            
            if (abs($adjustment['amount']) >= $this->contract->adjustment_threshold) {
                $reconciliation->addAdjustment($vendor, $adjustment);
            }
        }
        
        return $reconciliation->process();
    }
}
```

### Adjustment Types & Processing
```php
class AdjustmentType
{
    const ADDITIONAL_LICENSES = 'additional_licenses';
    const REDUCED_LICENSES = 'reduced_licenses'; 
    const COMMITMENT_CHANGE = 'commitment_change';    // P1M → P1Y or vice versa
    const SERVICE_UPGRADE = 'service_upgrade';        // Business Basic → Business Premium
    const BUNDLE_MODIFICATION = 'bundle_modification'; // Added/removed bundle components
    
    public static function getCustomerExplanation(string $type): string
    {
        return match($type) {
            self::ADDITIONAL_LICENSES => 
                "Sie haben mehr Lizenzen genutzt als in der Prepaid-Rechnung veranschlagt.",
            self::REDUCED_LICENSES => 
                "Sie haben weniger Lizenzen genutzt als bezahlt. Gutschrift wird erstellt.",
            self::COMMITMENT_CHANGE => 
                "Ihr Commitment-Type hat sich geändert, was zu anderen Preisen führt.",
            self::SERVICE_UPGRADE => 
                "Sie haben Services auf ein höheres Level geupgradet.",
            self::BUNDLE_MODIFICATION => 
                "Ihre Bundle-Konfiguration wurde angepasst.",
        };
    }
}
```

## Customer Risk Management

### Risk-Based Prepaid Terms
```php
class PrepaidRiskAssessment
{
    public function assessCustomerRisk(Customer $customer): string
    {
        $score = 0;
        
        // Payment history
        $latePayments = $customer->getLatePaymentCount(12);
        $score += $latePayments * 10;
        
        // Usage volatility  
        $usageVolatility = $customer->calculateUsageVolatility(12);
        $score += $usageVolatility * 5;
        
        // Contract value
        $monthlyValue = $customer->getMonthlyContractValue();
        if ($monthlyValue > 1000) $score += 5;
        
        // Multi-vendor complexity
        $vendorCount = $customer->getActiveVendorCount();
        $score += ($vendorCount - 1) * 3;
        
        return match(true) {
            $score >= 30 => 'HIGH_RISK',    // Sofort-Zahlung, tägliche Reconciliation
            $score >= 15 => 'MEDIUM_RISK',  // 7-Tage-Zahlung, wöchentliche Reconciliation  
            default => 'LOW_RISK'          // 14-Tage-Zahlung, monatliche Reconciliation
        };
    }
    
    public function getPrepaidTermsForRisk(string $riskLevel): array
    {
        return match($riskLevel) {
            'HIGH_RISK' => [
                'payment_terms' => 'IMMEDIATE',
                'reconciliation_frequency' => 'DAILY',
                'adjustment_threshold' => 10.00,
                'overage_buffer' => 5,  // 5% buffer only
                'credit_policy' => 'IMMEDIATE_REFUND'
            ],
            'MEDIUM_RISK' => [
                'payment_terms' => '7_DAYS',
                'reconciliation_frequency' => 'WEEKLY', 
                'adjustment_threshold' => 25.00,
                'overage_buffer' => 10, // 10% buffer
                'credit_policy' => 'NEXT_MONTH_CREDIT'
            ],
            'LOW_RISK' => [
                'payment_terms' => '14_DAYS',
                'reconciliation_frequency' => 'MONTHLY',
                'adjustment_threshold' => 50.00,
                'overage_buffer' => 20, // 20% buffer  
                'credit_policy' => 'CREDIT_ACCOUNT'
            ]
        };
    }
}
```

## Integration with Vendor Systems

### Real-time Usage Monitoring (Future)
```php
class UsageMonitoringService
{
    public function enableRealTimeMonitoring(Contract $contract)
    {
        // For high-risk prepaid customers
        if ($contract->prepaid_risk_level === 'HIGH_RISK') {
            
            // Setup vendor API monitoring
            foreach ($contract->vendors as $vendor) {
                match($vendor) {
                    'ALSO' => $this->setupMicrosoftAPIMonitoring($contract),
                    'Starface' => $this->setupStarfaceAPIMonitoring($contract),
                    'N-Sight' => $this->setupNSightAPIMonitoring($contract),
                    // ... other vendors
                };
            }
            
            // Setup threshold alerts
            $this->setupUsageThresholdAlerts($contract, [
                'warning_at' => 90,  // 90% of prepaid amount
                'critical_at' => 100, // 100% of prepaid amount  
                'emergency_at' => 110 // 110% of prepaid amount
            ]);
        }
    }
    
    private function setupUsageThresholdAlerts(Contract $contract, array $thresholds)
    {
        // Daily usage check for prepaid customers
        $this->scheduleDaily(function() use ($contract, $thresholds) {
            $currentUsage = $this->getCurrentMonthUsage($contract);
            $prepaidAmount = $contract->getCurrentMonthPrepaidAmount();
            
            $usagePercentage = ($currentUsage / $prepaidAmount) * 100;
            
            if ($usagePercentage >= $thresholds['emergency_at']) {
                $this->sendEmergencyAlert($contract, $currentUsage, $prepaidAmount);
            } elseif ($usagePercentage >= $thresholds['critical_at']) {
                $this->sendCriticalAlert($contract, $currentUsage, $prepaidAmount);
            } elseif ($usagePercentage >= $thresholds['warning_at']) {
                $this->sendWarningAlert($contract, $currentUsage, $prepaidAmount);
            }
        });
    }
}
```

## Financial Reporting Requirements

### Prepaid Revenue Tracking
```sql
-- Prepaid Financial Reporting
CREATE VIEW prepaid_revenue_analysis AS
SELECT 
    c.id as contract_id,
    c.name as contract_name,
    cust.name as customer_name,
    
    -- Prepaid tracking
    SUM(CASE WHEN i.invoice_type = 'PREPAID_PROJECTION' THEN i.amount ELSE 0 END) as total_prepaid,
    SUM(CASE WHEN i.invoice_type = 'ADJUSTMENT_ADDITIONAL' THEN i.amount ELSE 0 END) as additional_charges,
    SUM(CASE WHEN i.invoice_type = 'ADJUSTMENT_CREDIT' THEN i.amount ELSE 0 END) as credit_notes,
    
    -- Actual vendor costs
    SUM(ur.total_vendor_charge) as actual_vendor_costs,
    
    -- Reconciliation metrics
    (SUM(CASE WHEN i.invoice_type = 'PREPAID_PROJECTION' THEN i.amount ELSE 0 END) + 
     SUM(CASE WHEN i.invoice_type = 'ADJUSTMENT_ADDITIONAL' THEN i.amount ELSE 0 END) - 
     SUM(CASE WHEN i.invoice_type = 'ADJUSTMENT_CREDIT' THEN i.amount ELSE 0 END)) as total_customer_revenue,
     
    -- Variance analysis
    ((total_customer_revenue - SUM(ur.total_vendor_charge)) / SUM(ur.total_vendor_charge) * 100) as margin_percent
    
FROM contracts c
JOIN customers cust ON c.customer_id = cust.id  
JOIN invoices i ON c.id = i.contract_id
JOIN usage_records ur ON c.id = ur.contract_id
WHERE c.billing_model IN ('PREPAID', 'HYBRID')
GROUP BY c.id, c.name, cust.name;
```

## Updated Implementation Priority

### Phase 1 (Week 1): Foundation + Critical Revenue Fixes
1. **ALSO P1M/P1Y/Prepaid** (Revenue recovery)
2. **Customer Prepaid Billing** (Cash flow management)  
3. **Revenue Recognition Engine** (Compliance)

### Phase 2 (Week 2): Multi-Vendor Core + Adjustments
4. **Starface Dual-System** (Coverage)
5. **Adjustment Processing Engine** (Prepaid reconciliation)
6. **Customer Communication System** (Transparency)

### Phase 3 (Week 3): Advanced Features
7. **N-Sight Bundle System** (Innovation)
8. **Real-time Usage Monitoring** (High-risk customers)
9. **Advanced Reporting** (Financial analysis)

---

## Critical Success Update

The **customer prepaid billing** requirement adds significant business value:

### Immediate Benefits:
- **Cash Flow Improvement**: Prepaid billing improves MSP cash flow
- **Risk Mitigation**: Prepaid reduces customer default risk
- **Customer Flexibility**: Customers can choose billing model

### Technical Complexity:
- **Reconciliation Engine**: Monthly actual vs prepaid comparison
- **Adjustment Processing**: Automated additional charges/credit notes
- **Real-time Monitoring**: Usage threshold alerts for high-risk customers

### Business Differentiation:
- **Flexible Billing Options**: Postpaid vs Prepaid customer choice
- **Transparent Adjustments**: Clear explanations for all adjustments
- **Risk-Based Terms**: Customized payment terms based on customer risk

This prepaid capability transforms MSPGenie from a billing system into a **complete customer financial relationship management platform**.