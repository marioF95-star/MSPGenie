# MSPGenie - Managed Service Provider Management Platform

## Überblick
MSPGenie ist eine umfassende Plattform zur Verwaltung von MSP (Managed Service Provider) Operationen, einschließlich Kundenverwaltung, Vertragsverwaltung und Abrechnungsimport.

## Aktuelle Entwicklung
- **ALSO Abrechnungsimport**: Multi-Vendor Support für Microsoft und Adobe Produkte
- **Vertragsverwaltung**: Comprehensive contract management system
- **Laravel Backend**: Modern PHP framework implementation

## Dokumentation

### Import-Systeme
- [`ALSO_Import_Pflichtenheft.md`](ALSO_Import_Pflichtenheft.md) - Komplette Spezifikation für ALSO-Abrechnungsdaten Import mit Multi-Vendor Support

### Projektmanagement
- [`PROJEKTPLAN.md`](PROJEKTPLAN.md) - Übergeordneter Projektplan
- [`Vertragsverwaltung.md`](Vertragsverwaltung.md) - Vertragsverwaltungs-Spezifikation

### Setup-Anleitungen
- [`DEVELOPMENT-SETUP.md`](DEVELOPMENT-SETUP.md) - Development Environment Setup
- [`WINDOWS-SETUP.md`](WINDOWS-SETUP.md) - Windows-spezifische Setup-Anweisungen

## Features (In Entwicklung)

### ALSO Import System
- **Multi-Vendor Support**: Microsoft, Adobe, erweiterbar für weitere Anbieter
- **Konfigurierbare Parser**: Vendor-spezifische Attribute-Parsing
- **Access Database Integration**: Kompatibilität mit bestehenden Access 2016 Systemen
- **Raw Charges Import**: Detaillierte Rohdatenverarbeitung

### Key Capabilities
- Monatliche vs. jährliche Produkterkennung
- Vorausbezahlungs-Support (P1Y Prepaid)
- Endkunden-Mapping
- Microsoft Artikel-GUID Referenzierung
- Negative Quantity Handling (Stornierungen)

## Technischer Stack
- **Backend**: Laravel PHP Framework
- **Database**: MySQL/MariaDB + Access 2016 Integration
- **Import Engine**: Python mit pandas/openpyxl
- **Frontend**: Tailwind CSS

## Entwicklungsstand
- ✅ ALSO Import Spezifikation komplett
- ✅ Multi-Vendor Architecture definiert
- ⏳ Implementation in Progress
- ⏳ Access Database Integration
- ⏳ Laravel Backend Implementation

## Nächste Schritte
1. ODBC/pyodbc Installation für Access-Anbindung
2. Python Import-Engine Implementierung
3. Laravel Backend Integration
4. Frontend Development

## Datenanalyse
Basierend auf 66 Excel-Dateien (2020-2025):
- **2 Vendors**: Microsoft (99%+), Adobe (1%)
- **324 Detaileinträge** in Dezember 2024
- **55 Endkunden**, **218 Subscriptions**
- **75 Vorausbezahlungen** (32.6% in Dez. 2024)

---

*Stand: September 2025 - Work in Progress*