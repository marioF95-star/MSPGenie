# MSPGenie - Vendor Integration Matrix

## Vollständige Vendor-Übersicht

### Vendor Coverage Statistics
| Vendor | Customers | Coverage | Files | Data Period | Complexity |
|--------|-----------|----------|-------|-------------|------------|
| **Starface** | 85 | 53.8% | 67 CSV | 2020-2025 | 🥉 Dual-System |
| **ALSO** | 69 | 43.7% | 66 Excel | 2020-2025 | 🥈 Multi-Commitment |
| **TrendMicro** | 38 | 24.1% | 67 XLS | 2020-2024 | ⭐ Standard |
| **Altaro** | 33 | 20.9% | 69 CSV/Excel | 2020-2025 | ⭐ Matrix-Based |
| **Acronis** | 17 | 10.8% | 68 CSV | 2020-2025 | ⭐ Standard |
| **N-Sight** | ? | ? | 10 CSV/Excel | 2020-2025 | 🏆 Bundle-System |
| **Securepoint** | 7 | 4.4% | 6 Excel | License-based | ⭐ License-Model |
| **Wasabi** | ? | ? | 13 CSV/Excel | 2024 | ⭐ Storage-Based |

## Detailed Vendor Analysis

### 1. ALSO (Microsoft 365) - 43.7% Coverage
```
File Format: Excel (.xlsx)
Key Sheet: "Raw Charges" (14 columns)
Billing Complexity: HIGH

Critical Business Logic:
✅ P1M (Monthly commitment) → Separate pool
✅ P1Y (Yearly commitment) → Separate pool  
🚨 P1Y PREPAID → Revenue recognition over 12 months
❌ Current: Lost ~300€/year revenue

Data Quality: EXCELLENT
- 100% customer mapping success
- Rich product metadata (VendorReference GUID)
- Complete commitment type information

Implementation Priority: #1 (Revenue Impact)
```

### 2. Starface (Telephony) - 53.8% Coverage
```
File Format: Dual-source complexity
Source 1: CSV Cloud data (28 domains)
Source 2: PDF→Excel Private Cloud (10+ customers)

Billing Complexity: HIGH (Dual System)

Business Logic:
✅ Cloud: Usage-based (MAX monthly users)
✅ Private: License-based (Fixed monthly fees)
❌ Current: 0% Cloud customer mapping success
✅ Current: 40% Private customer mapping success

Data Quality: MIXED
- Cloud: Perfect CSV structure, failed mapping
- Private: Complex PDF extraction, partial mapping

Implementation Priority: #2 (Coverage Impact)
```

### 3. Altaro (Office 365 Backup) - 20.9% Coverage
```
File Format: CSV
Billing Logic: Product + Object Type Matrix

Key Insight: "Invoice" field critical
- "Billable" vs "Free" usage distinction
- Product types: 365 Total Backup, VM Backup
- Object types: M365 User, M365 Group, Shared Mailbox, VM

VBA Implementation: Dual product classes
- IDProductclass 3: Altaro Office 365 Backup
- IDProductclass 6: Altaro VM Backup

Implementation Priority: #3 (Matrix complexity)
```

### 4. TrendMicro (Security) - 24.1% Coverage  
```
File Format: XLS (Excel legacy)
Billing Logic: Standard usage-based

Structure: CustomerSummary(Month Year).xls
Key Fields:
- Kunde (Customer name)
- Genutzt (Used quantity)  
- Service/Produkt (Product name)

VBA Logic: Simple MAX usage
Data Quality: GOOD (consistent customer mapping)

Implementation Priority: #4 (Stable, standard logic)
```

### 5. N-Sight (Bundle System) - Unknown Coverage
```
File Format: CSV/Excel  
Billing Complexity: EXTREME (Bundle + Validation)

Revolutionary Bundle Pattern:
Customer sees: "IM+ Endpoint Basic" (15€/endpoint)
System validates: 3x N-Sight SKUs per endpoint
- MAXWMXXWXXE (Windows)
- MAXMAVXWXXE (Mac)  
- MAXDEMAWXXE (Defense)

Business Impact: New paradigm for MSP billing
- Customer simplicity
- Vendor validation completeness
- Contract transparency

Implementation Priority: #5 (Future model)
```

### 6. Acronis (Backup) - 10.8% Coverage
```
File Format: CSV
Billing Logic: Standard usage-based

Similar to TrendMicro:
- Customer name based mapping
- Usage quantity extraction
- Simple aggregation (MAX)

Data Challenges: CSV format inconsistency
Implementation Priority: #6 (Lower coverage)
```

### 7. Securepoint (UTM/Firewall) - 4.4% Coverage
```
File Format: Excel
Billing Logic: License-based with free allowances

Unique Features:
- "Anzahl kostenpflichtige Einheiten" vs "Anzahl kostenlose Einheiten"
- License expiration tracking
- Hardware serial number tracking

Implementation Priority: #7 (Specialized use case)
```

### 8. Wasabi (Cloud Storage) - Unknown Coverage
```
File Format: Excel/CSV
Billing Logic: Storage consumption-based

Metrics:
- Active Storage (TB)
- Bucket-based organization  
- Monthly consumption tracking

Implementation Priority: #8 (Storage-specific)
```

## Multi-Vendor Customer Complexity

### Tier 1: Maximum Complexity (5+ vendors)
**8 customers with 5 vendors each:**
- Hinkel & Cie. Vermögensverwaltung AG
- Cebra GmbH  
- Zahnarztpraxis Dr. Horenburg-Rennert
- Rahpro GmbH
- King Car Germany GmbH
- BOS Projektmanagement GmbH
- Michels, Jörn
- Vetten Krane GmbH

**Contract Requirements:**
- Multi-vendor bundle contracts
- Complex commitment type handling
- Cross-vendor usage validation
- Unified customer billing

### Tier 2: High Complexity (3-4 vendors)
**22 customers with 3-4 vendors**

**Contract Requirements:**
- Standard MSP contract templates
- Multi-vendor coordination
- Simplified customer view

### Tier 3: Standard Complexity (1-2 vendors)
**94+ customers with single vendor or simple combinations**

**Contract Requirements:**
- Standard templates
- Single vendor validation
- Straightforward billing

## Implementation Strategy

### Phase 1: Core Vendors (Revenue Impact)
1. **ALSO** (Revenue Loss Fix)
2. **Starface** (Coverage Impact)  
3. **Altaro** (Matrix Logic)

### Phase 2: Standard Vendors (Completeness)
4. **TrendMicro** (Stable baseline)
5. **Acronis** (Similar pattern)

### Phase 3: Advanced Features (Innovation)
6. **N-Sight** (Bundle paradigm)
7. **Securepoint** (License model)
8. **Wasabi** (Storage billing)

## Contract Template Requirements

### Template 1: Single Vendor Contract
**For:** 94+ simple customers
**Features:** Standard billing, single vendor validation

### Template 2: Multi-Vendor MSP Contract  
**For:** 22 customers with 3-4 vendors
**Features:** Vendor coordination, unified billing

### Template 3: Enterprise Bundle Contract
**For:** 8 maximum complexity customers  
**Features:** Bundle management, cross-vendor validation, complex commitment handling

### Template 4: Bundle Service Contract
**For:** N-Sight customers
**Features:** Customer bundle products, internal vendor validation, transparent explanations

---

**Critical Success Factors:**
1. **Revenue Recognition** (P1Y Prepaid fix)
2. **Customer Transparency** (Bundle explanations)
3. **Vendor Coordination** (Multi-vendor contracts)
4. **Scalability** (Template-based system)

This matrix provides the foundation for implementing a contract-based system that handles the full complexity of real MSP operations while maintaining customer simplicity.