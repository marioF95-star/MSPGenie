# MSPGenie - START MORGEN (6. September 2025)

## 🚀 Tag 1 Checklist - Sofort starten!

### Vorbereitung (10 Minuten)
```bash
# 1. Arbeitsverzeichnis
cd /mnt/c/Projekte/MSPGenie

# 2. Virtual Environment aktivieren  
source venv/bin/activate

# 3. Git Repository initialisieren
git init
git add .
git commit -m "Initial MSPGenie analysis and planning

📊 Analysis completed:
- ALSO P1M/P1Y/Prepaid billing logic identified
- Starface dual-system (Cloud CSV + Private PDF) mapped
- N-Sight bundle system (IM+ Endpoint Basic) analyzed
- Revenue recognition issues quantified (~300€/year loss)
- Contract-based architecture designed

🎯 Ready for implementation

Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Laravel Setup (30 Minuten)
```bash
# 1. Laravel Projekt erstellen
cd /mnt/c/Projekte/
composer create-project laravel/laravel MSPGenie-Laravel
cd MSPGenie-Laravel

# 2. Essential Packages
composer require maatwebsite/excel
composer require spatie/laravel-permission
composer require spatie/laravel-activitylog
composer require barryvdh/laravel-dompdf

# 3. Development Tools
composer require --dev laravel/telescope
composer require --dev barryvdh/laravel-debugbar

# 4. Database konfigurieren (.env)
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=msp_genie
DB_USERNAME=postgres
DB_PASSWORD=password

# 5. PostgreSQL Database erstellen
createdb msp_genie
```

### Core Models erstellen (60 Minuten)
```bash
# Models generieren
php artisan make:model Customer -m
php artisan make:model Contract -m  
php artisan make:model ContractProduct -m
php artisan make:model UsageRecord -m
php artisan make:model BundleValidation -m
php artisan make:model RevenueRecognitionSchedule -m

# Controllers für API
php artisan make:controller Api/ContractController --api
php artisan make:controller Api/ImportController  
php artisan make:controller Api/UsageController --api

# Services für Business Logic
php artisan make:class Services/ImportEngine/ALSOImportService
php artisan make:class Services/BillingEngine/BillingCalculator
php artisan make:class Services/ContractEngine/ContractValidator
```

### Priority 1: ALSO Import (Rest des Tages)
```php
// app/Services/ImportEngine/ALSOImportService.php
<?php

namespace App\Services\ImportEngine;

use Maatwebsite\Excel\Facades\Excel;
use App\Models\Contract;
use App\Models\ContractProduct; 
use App\Models\UsageRecord;
use Carbon\Carbon;

class ALSOImportService
{
    public function importALSOMonth(string $filePath, int $month, int $year)
    {
        // 1. Read Excel Raw Charges
        $rawCharges = Excel::toArray(null, $filePath)['Raw Charges'] ?? [];
        
        if (empty($rawCharges)) {
            throw new \Exception("No Raw Charges sheet found");
        }
        
        $header = array_shift($rawCharges); // Remove header row
        $processedData = [];
        
        // 2. Process each row
        foreach ($rawCharges as $row) {
            $data = array_combine($header, $row);
            
            // Extract commitment type and quantity
            $commitmentInfo = $this->parseCommitmentType($data['Attributes']);
            
            $processedData[] = [
                'company' => $data['Company'],
                'product_name' => $data['Product name'],
                'vendor_reference' => $data['VendorReference'],
                'commitment_type' => $commitmentInfo['type'],
                'quantity' => $commitmentInfo['quantity'],
                'charge' => $data['Charge'],
                'interval' => $data['Interval'],
                'billing_start_date' => $data['BillingStartDate'],
                'raw_attributes' => $data['Attributes']
            ];
        }
        
        // 3. Group and aggregate correctly
        return $this->aggregateByCustomerProductCommitment($processedData, $month, $year);
    }
    
    private function parseCommitmentType(string $attributes): array
    {
        // P1Y Prepaid Detection
        if (str_contains($attributes, 'Prepaid')) {
            $quantity = $this->extractQuantity($attributes);
            return ['type' => 'P1Y_PREPAID', 'quantity' => $quantity];
        }
        
        // P1M vs P1Y Detection  
        if (str_contains($attributes, 'P1M')) {
            $quantity = $this->extractQuantity($attributes);
            return ['type' => 'P1M', 'quantity' => $quantity];
        }
        
        if (str_contains($attributes, 'P1Y')) {
            $quantity = $this->extractQuantity($attributes);
            return ['type' => 'P1Y', 'quantity' => $quantity];
        }
        
        // Legacy format
        $quantity = $this->extractQuantity($attributes);
        return ['type' => 'P1Y', 'quantity' => $quantity];
    }
    
    private function extractQuantity(string $attributes): int
    {
        // VBA Logic: Right(Attributes,len(Attributes)-InStrRev(Attributes,'='))
        $lastEqualPos = strrpos($attributes, '=');
        if ($lastEqualPos !== false) {
            $quantityStr = substr($attributes, $lastEqualPos + 1);
            return (int) $quantityStr;
        }
        return 0;
    }
    
    private function aggregateByCustomerProductCommitment(array $data, int $month, int $year): array
    {
        $grouped = [];
        
        foreach ($data as $record) {
            $key = $record['company'] . '|' . $record['product_name'] . '|' . $record['commitment_type'];
            
            if (!isset($grouped[$key])) {
                $grouped[$key] = [
                    'company' => $record['company'],
                    'product_name' => $record['product_name'],
                    'commitment_type' => $record['commitment_type'],
                    'quantities' => [],
                    'charges' => [],
                    'intervals' => []
                ];
            }
            
            $grouped[$key]['quantities'][] = $record['quantity'];
            $grouped[$key]['charges'][] = $record['charge'];
            $grouped[$key]['intervals'][] = $record['interval'];
        }
        
        // Apply aggregation logic
        $results = [];
        foreach ($grouped as $group) {
            if ($group['commitment_type'] === 'P1Y_PREPAID') {
                // Prepaid: Calculate monthly revenue recognition
                $billableAmount = $this->calculatePrepaidRevenue($group, $month, $year);
            } else {
                // P1M/P1Y: Maximum quantity
                $billableAmount = max($group['quantities']);
            }
            
            $results[] = [
                'customer' => $group['company'],
                'product' => $group['product_name'],
                'commitment_type' => $group['commitment_type'],
                'billable_quantity' => $billableAmount,
                'total_charge' => array_sum($group['charges'])
            ];
        }
        
        return $results;
    }
}
```

## Sofortige Deliverables (Tag 1)

### ✅ Foundation Setup:
- Laravel 11 Projekt mit PostgreSQL
- Core Models (Customer, Contract, ContractProduct)
- Database Schema implementiert

### ✅ ALSO Import Fix:
- Korrekte P1M/P1Y/Prepaid Recognition
- Revenue Recognition für Prepaid
- 100% accurate aggregation logic

### ✅ Contract Foundation:
- Contract Model mit Bundle Support
- Customer → Contract Relationship
- Billing Logic Framework

## Nächste Schritte (Tag 2)

### Priority Vendor Integrations:
1. **ALSO** (höchste Priorität - Revenue Impact)
2. **Starface** (duales System)  
3. **N-Sight** (Bundle-Beispiel)

### Contract System:
- Contract Templates erstellen
- Bundle Management implementieren
- Customer Portal Grundlagen

---

**READY TO START CODING TOMORROW!** 🎯

Alle Analysen abgeschlossen, Architecture definiert, Implementation Plan steht. Das System kann morgen früh mit der Laravel-Entwicklung beginnen.