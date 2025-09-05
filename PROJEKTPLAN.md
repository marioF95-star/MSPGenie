# MSP Genie - Projektplan & Erkenntnisse

## Projektziel
Entwicklung einer Multi-Tenant MSP-Verwaltungs- und Abrechnungssoftware mit Laravel 11, fokussiert auf automatisierte Eingangsrechnungsverarbeitung und Vertragsverwaltung.

## Marktanalyse - Konkurrierende Produkte

### Deutsche Lösungen
- **Fokus MSP**: Systemhaus-One mit automatisierter Abrechnung, Vertragsverwaltung
- **mars services**: MSP Abrechnungs-Manager mit automatisierter Lizenzverarbeitung
- **MSP Marketplace**: Zentraler Zugriff auf 23+ Produkte, deutsche Rechtssicherheit

### Internationale Marktführer
- **Kaseya BMS**: Fortgeschrittene Multi-Tenant-Architektur, Parent-Child-Strukturen
- **ConnectWise**: Umfassendes PSA/RMM-Ökosystem mit Skalierungslimitationen
- **Autotask PSA**: Cloud-native, 170+ Integrationen, usage-based billing
- **Atera**: All-in-one RMM+PSA Single-Code-basiert

## Technische Architektur

### Multi-Tenant-Setup
- **Package**: `tenancy/tenancy` (stancl/tenancy v3)
- **Vorteile**: Automatische Tenant-Switching, umfangreiche Features, 99% Package-Kompatibilität
- **Architektur**: Database-per-Tenant mit automatischer Verbindungsumschaltung

### UI Framework
- **Minia Bootstrap 5**: Laravel 11 kompatibel, 10+ Layouts, responsive, SCSS-basiert
- **Frontend**: Vue.js 3, Composition API, Axios

### Technischer Stack
```
Backend:
- Laravel 11 + tenancy/tenancy
- MySQL 8.x (Multi-Tenant)
- Redis (Queues, Cache)

Frontend:
- Minia Bootstrap 5 Template
- Vue.js 3 + Composition API
- Axios für API-Calls

Import-System:
- Laravel Queues
- Spatie/SimpleExcel (CSV/XLS)
- Smalot/PdfParser (PDF)
- League/Csv

Reporting:
- Laravel-Excel
- DomPDF/wkhtmltopdf
- Chart.js/ApexCharts
```

## Spezifische Datenquellen (aus Pflichtenheft)

### Anbieter mit Formaten
| Anbieter | Aktuell | Geplant | Priorität |
|----------|---------|---------|-----------|
| Starface | CSV, PDF | - | Phase 1 |
| ALSO | XLSX | REST-API | Phase 1 |
| TrendMicro | XLS | - | Phase 2 |
| Altaro | CSV | JSON | Phase 2 |
| Acronis | CSV | - | Phase 1 |
| TANSS | XML | - | Phase 3 |
| N-Sigth | CSV | REST-API | Phase 4 |
| WASABI | CSV | - | Phase 2 |
| Securepoint | XLSX | - | Phase 2 |

## Datenmodell

### Core-Entitäten
```php
// Customers (Multi-Tenant)
- CustomerID, Name, Address, Contacts
- Tenant-isolated

// Contracts (erweiterte Logik)
- ContractID, CustomerID, StartDate, EndDate
- BillingInterval, ContractType (Flatrate/Contingent/Usage)
- AutoRenewal, CancellationPeriod
- Discounts, SpecialConditions

// VendorInvoices (Eingangsrechnungen)
- InvoiceID, Vendor, InvoiceNumber, Date, Amount
- DataSource, ImportMethod, Status
- ValidationResult, ApprovalStatus

// CustomerInvoices (Ausgangsrechnungen)
- InvoiceID, CustomerID, Period, TotalAmount
- PDFPath, Status, GeneratedDate
```

### Import-System Architektur
```php
// Abstract Import-Adapter
abstract class ImportAdapter {
    abstract public function supports(string $format): bool;
    abstract public function parse(string $filePath): Collection;
    abstract public function validate(array $data): ValidationResult;
}

// Status-Management
enum InvoiceStatus: string {
    case PENDING = 'pending';
    case VALIDATED = 'validated';
    case APPROVED = 'approved';
    case REJECTED = 'rejected';
    case BILLED = 'billed';
}

// Queue Jobs für Import
class ProcessVendorInvoiceJob implements ShouldQueue {
    public function handle(ImportService $service) {
        $service->processFile($this->filePath, $this->vendor);
    }
}
```

## Entwicklungsplan

### Phase 1: Foundation & Core (Monate 1-3)
**1.1 Multi-Tenant-Architektur**
- Laravel 11 + tenancy/tenancy Setup
- Database-per-Tenant Architektur
- Minia Template Integration
- Basis-Authentifizierung & Rollen

**1.2 Datenmodell**
- Migrations für alle Entitäten
- Eloquent Models mit Relationships
- Tenant-Isolation

**1.3 Import-Engine (Laravel Jobs)**
- Queue-basierte Verarbeitung
- Format-spezifische Parser (CSV, XLS, PDF, XML)
- Duplicate-Detection
- Error-Handling & Logging

### Phase 2: Import-System & Validation (Monate 4-6)
**2.1 Datenquellen-Integration**
- ImportAdapters für jeden Anbieter
- Starface, ALSO, Acronis (CSV/XLSX)

**2.2 Validation-Engine**
- Contract-basierte Validierung
- Abweichungs-Detection
- Approval-Workflow
- Status-Management

**2.3 Multi-Source-Import**
- File-System Monitoring
- FTP/SFTP Integration
- REST-API Consumers
- Scheduled Import Jobs

### Phase 3: Billing & Reporting (Monate 7-9)
**3.1 Erweiterte Abrechnungslogik**
- Flatrate vs. Usage-based
- Kontingent-Management
- Preis-Kalkulationen
- Rabatt-System

**3.2 Invoice Generation**
- PDF-Generation
- Template-System
- Multi-Language Support
- Automatische Nummerierung

**3.3 Reporting & Analytics**
- Financial Dashboards
- Customer Analytics
- Vendor Analysis
- Export-Funktionen

### Phase 4: Advanced Features (Monate 10-12)
**4.1 API-Ecosystem**
- RESTful APIs für alle Funktionen
- Webhook-System
- Third-party Integrations
- API-Documentation

**4.2 Erweiterte Integrationen**
- CRM-Systeme (Salesforce, HubSpot)
- ERP-Systeme (SAP, Dynamics)
- Buchhaltung (DATEV, Lexware)
- Ticketsysteme (Freshdesk, Zendesk)

## Integrations-Strategie

### API-First-Ansatz
- RESTful APIs für alle Core-Funktionen
- Webhook-System für Real-time-Updates
- GraphQL optional für komplexe Abfragen

### Geplante Integrationen
1. **CRM-Systeme**: Salesforce, HubSpot, Pipedrive
2. **ERP-Systeme**: SAP, Microsoft Dynamics, Odoo
3. **Ticketsysteme**: Freshdesk, Zendesk, ServiceNow
4. **Buchhaltung**: DATEV, Lexware, QuickBooks
5. **Monitoring**: Nagios, Zabbix, PRTG
6. **Backup**: Veeam, Acronis, Carbonite

### Integrations-Architektur
- Adapter-Pattern für verschiedene APIs
- Queue-System für async Processing
- Rate-Limiting für API-Calls
- Fehlerbehandlung: Retry-Logic & Logging

## MVP-Features

### Core-Module (Phase 1)
1. **Multi-Tenant-Management**
   - Tenant-Registrierung & -Verwaltung
   - Benutzer-/Rollenverwaltung pro Tenant
   - Tenant-Isolation & Sicherheit

2. **Vertragsverwaltung**
   - Vertragsvorlagen & -erstellung
   - Versionskontrolle & Änderungshistorie
   - Kündigungsfristen & Renewals
   - Dokumentenanhänge

3. **Basis-Abrechnung**
   - Recurring Services (monatlich/jährlich)
   - Time & Material Tracking
   - Rechnungserstellung & -versand
   - Basis-Reporting

4. **Kundenverwaltung**
   - Kunden-/Kontaktverwaltung
   - Standort-Management
   - Basis-Asset-Tracking

### Erweiterte Features (Phase 2)
5. **Erweiterte Abrechnung**
   - Usage-based Billing
   - Automatische Lizenzerfassung
   - Preiskalkulationen & Margen
   - Finanz-Dashboards

6. **Ticketsystem-Integration**
   - API-Framework für externe Systeme
   - Webhook-Support
   - Basis-Ticket-Management

7. **Reporting & Analytics**
   - Finanz-Reports
   - Kunden-Dashboards
   - Performance-Metriken

## Workflow-System

### Approval-Workflow
```php
class ApprovalWorkflow {
    public function processInvoice(VendorInvoice $invoice): void {
        $validationResult = $this->validateAgainstContract($invoice);
        
        if ($validationResult->hasDiscrepancies()) {
            $invoice->markForReview($validationResult->getDiscrepancies());
        } else {
            $invoice->markAsValidated();
        }
    }
}
```

### Rollen & Berechtigungen
- **Administrator**: Vollzugriff, Tenant-Management
- **Sachbearbeiter**: Vertrags-/Kundendaten, Abrechnungen
- **Prüfer**: Rechnungsprüfung, Freigaben
- **Viewer**: Nur Leserechte

## Nächste Schritte

### Sofortmaßnahmen (Wochen 1-2)
1. **Laravel-Projekt Setup**
   - Laravel 11 + tenancy/tenancy
   - MySQL Multi-Tenant-Konfiguration
   - Minia Template Integration
   - Basis-Authentifizierung

2. **Datenmodell Implementation**
   - Migrations für alle Entitäten
   - Eloquent Models mit Relationships
   - Tenant-Isolation

3. **Import-Framework**
   - Abstract ImportAdapter
   - Queue-System Setup
   - File-Processing Pipeline

### Prioritäten Datenquellen
1. **Sofort**: Starface, ALSO, Acronis (CSV/XLSX - einfach)
2. **Phase 2**: TrendMicro, Altaro, WASABI (XLS/spezielle CSV)
3. **Phase 3**: TANSS (XML), Starface PDF
4. **Phase 4**: REST-APIs (ALSO, N-Sigth, Altaro JSON)

---

**Status**: Planung abgeschlossen, bereit für Development-Setup
**Letzte Aktualisierung**: 2025-01-16