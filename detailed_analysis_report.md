# ALSO November 2024 Vergleichsanalyse

## Zusammenfassung
- **Excel Total**: 566 Quantity (SOLL)
- **Access Total**: 581 Usage (IST)
- **Differenz**: -15 (-2.7%)
- **Probleme gefunden**: 36 Einzelfehler

## 1. Hauptproblem: Kundennamen-Mapping

### Fehlende Kunden (18):
```
Excel Name                          → Access Name (erwartet)
─────────────────────────────────────────────────────────
Adler Apotheke Stefanie Heckhoff    → Adler Apotheke
Baugewerbe-Innung-Düsseldorf        → Baugewerbe- Innung- Düsseldorf
Berg Communication - Volker Berg    → Berg Communication
Endler Bauunternehmung GmbH         → EBG Endler Bauunternehmung GmbH
Vetten Krane & Service GmbH         → Vetten Krane GmbH
HKP Wagschal GmbH                   → Wagschal GmbH
```

**Ursache**: `tblKunden.IDAlso` Feld enthält andere Namen als in Excel

## 2. Mengenabweichungen (6 Kunden)

### Kritische Abweichungen:
1. **Tefert & Anvari GbR**: 22 → 29 (+7)
   - Microsoft 365 Business Standard: 20 → 27 (+7)
   
2. **Dachfenstertechnik Theo May**: 8 → 10 (+2)
   - Exchange Online (Plan 1): 1 → 2 (+1)
   - Microsoft 365 Business Standard: 2 → 3 (+1)

**Ursache**: Vermutlich **Doppelzählung** in der VBA-Aggregierung

## 3. Lösungsansätze für MSPGenie

### Sofortmaßnahmen:
1. **IDAlso-Feld korrigieren** in tblKunden
2. **VBA-Aggregierungslogik prüfen** - Warum werden manche Mengen verdoppelt?

### Für MSPGenie-Entwicklung:
1. **Fuzzy Name Matching** implementieren
2. **Validierung gegen Excel-Rohdaten** 
3. **Multi-Intervall-Support** (Monthly/Annual/Prepaid)

## 4. Technische Details

### Excel Struktur (korrekt):
- 131 Raw Charges Einträge
- 113 Einträge nach Aggregierung (MAX per Kunde+Produkt)
- 55 Kunden
- Attribute-Parsing funktioniert

### Access Probleme:
- Kundennamen-Mapping versagt
- Einzelne Produkte werden überzählt
- Aggregierungslogik fehlerhaft

## 5. Nächste Schritte

1. **tblKunden.IDAlso Feld analysieren**
2. **VBA-Query qry_PRG_tblImport_ALSO_Basis_Summe überprüfen** 
3. **Python-Prototyp für korrekten Import erstellen**