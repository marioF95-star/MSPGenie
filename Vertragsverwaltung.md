MSP Genie – Pflichtenheft „Vertragsverwaltung“ (Eigenes Modul)
Stand: 12.08.2025 – Vorabversion v0.1 für die Laravel‑Umsetzung

1. Zweck und Geltungsbereich
Die Vertragsverwaltung bildet alle vertraglichen Beziehungen zu Kunden ab, inklusive Laufzeiten, Verlängerungslogik, Kündigungsfristen, Produkt‑/Modulpositionen, Kontingenten, Preisregeln, Partner‑Laufzeiten sowie Versionierung und rückwirkender Änderungen (Differenzabrechnung). Sie ist Kernbasis der Abrechnung und der Eingangsrechnungs‑Prüfung.

Im Fokus steht die IM+ Produktwelt mit Säulen (Workplace, Network, Cloud, Secure, DataProtect, Assist, Awareness & Cover) und deren typischen Laufzeit‑ und Abrechnungsbesonderheiten.

2. Fachliche Ziele
Eindeutige, versionierte Vertragsabbildung je Kunde mit Mastervertrag + Unterpositionen je Säule/Produktgruppe.

Keine Mischlaufzeiten innerhalb einer Produktgruppe (Säule). Unterschiedliche Laufzeiten werden als getrennte Unterverträge/Segmente geführt.

Automatisierte Verlängerung nach Regeln pro Produktgruppe inkl. Preisänderungsoption.

Happiness‑Exit / Frühkündigung: regelbasierte Rückberechnung (Setup‑Anteil, Hardware‑Restwert) inkl. Nachweise.

Produkt-/User‑Zuwächse während der Laufzeit: Angleich an Vertragsende des Hauptprodukts; voller Monat bei Start im laufenden Monat.

Upgrades/Produktwechsel: ggf. neu startende Mindestlaufzeit für das gesamte Paket (konfigurierbar).

Kopplung an Partner‑Laufzeiten (z. B. STARFACE 365 1/12/36/60; M365 NCE 1/12; Versicherungen 12) → Enddaten müssen konsistent sein.

Erinnerungen (90/60/30 Tage vor Kündigungsfrist) und Verlängerungsangebote (Optional: Workflows).

Lückenlose Historie (Versionierung & Audit) und Differenzabrechnung bei rückwirkenden Änderungen.

3. Domänenmodell und Begriffe
3.1 Säulen (Produktgruppen)
IM+ Workplace: Hardware (z. B. Dell + ProSupport), RMM (N‑able N‑sight), AV/EDR (Bitdefender/Trend Micro), Backup (Acronis), Helpdesk.
Laufzeit i. d. R. 36–60 Monate (Hardware‑Refinanzierung). Frühkündigung → Setup-/Hardwareanteile nachberechnen. Hardwaretauschzyklen dokumentieren.

IM+ Network: Managed Switches, Firewalls (Securepoint), WLAN (Aruba/Meraki).
Eigene Laufzeiten möglich (Leasing, Firmware‑Support). Wartung oft jährlich. Bei Bündelung mit Workplace möglichst gleiches Vertragsende.

IM+ Cloud: Microsoft 365, Azure, SaaS‑Management.
NCE meist 1 oder 12 Monate. Add‑ons mit Hauptvertrag synchronisieren.

IM+ Secure: Security‑Audits, Awareness‑Trainings (SoSafe/KnowBe4), MDR, Pen‑Tests.
Awareness oft 12 Monate, automatische Verlängerung.

IM+ DataProtect: Backup (Endpoints/Server/M365), Archiv, DRaaS.
Laufzeit oft = Workplace oder 12 Monate. Abrechnung nach Speicher + Devices.

IM+ Assist: Support‑Flatrates, On‑Site‑Optionen, SLA‑Erweiterungen.
Monatlich oder 12 Monate. Wenn Teil von Workplace → Synchronisierung.

IM+ Awareness & Cover: Security‑Awareness + Cyberversicherung (z. B. CyberDirekt/Stoïk/Baobab).
Versicherung 12 Monate (auto‑renew). Awareness je nach Anbieter 1/12 Monate. Enddatum = Partnerleistung.

3.2 Vertragsstruktur
Mastervertrag (Kunde, übergreifende Bedingungen).

Vertragssegmente (= Unterverträge) je Säule/Produktgruppe mit eigenständiger Laufzeit/Regeln.

Vertragsversionen (SCD‑ähnlich): jede Änderung → neue Version mit valid_from/valid_to.

Vertragspositionen: Produkte/Leistungen (z. B. M365 E3, Firewall‑Wartung, Arbeitsplatz‑Bundle).

Kontingente: definierte Einheiten (Stunden, Tickets, GB). Verbrauch wird periodisch gegengerechnet.

4. Geschäftsregeln
4.1 Laufzeiten & Verlängerungen
Standardlaufzeiten: 1, 12, 36, 60 (ggf. 24) Monate; je Segment einheitlich.

Auto‑Renew:

Workplace/Hardware: Verlängerung identisch zur Ursprungslaufzeit oder in 12‑Monats‑Schritten (konfigurierbar).

M365 NCE: 1 oder 12 Monate.

Awareness/Versicherungen: i. d. R. 12 Monate.

Preisänderung bei Verlängerung: zulässig; Prozentsatz/Fixpreis hinterlegbar; Gültig ab renewal_from.

Teilverlängerung: einzelne Module/Add‑ons eines Segments können verlängert werden, wenn Regel dies vorsieht.

4.2 Kündigungsfristen & Erinnerungen
Kündigungsfrist je Segment (z. B. 30/60/90 Tage).

Automatische Erinnerungen 90/60/30 Tage vor Frist per E‑Mail/Task.

Workflow: Angebot erstellen → Kunde bestätigt/ablehnt → Status aktualisieren.

4.3 Produkt‑/User‑Erweiterungen (während der Laufzeit)
Alignment: Neue User/Lizenzen/Module laufen bis Ende des Segments.

Abrechnung: Voller Monat auch bei Start am 20. Tag (regelgesteuert).

Preisregeln: Staffelpreise, Mindestmengen, Sonderpreise pro Kunde/Segment.

4.4 Upgrades/Produktwechsel
Basic → Plus/Premium: optional neue Mindestlaufzeit für das gesamte Segment.

Preisänderung dokumentieren; alte Version endet valid_to = Upgrade‑Start − 1 Tag, neue Version ab valid_from.

4.5 Frühkündigung / Happiness‑Exit
Setup‑Kostenanteil (linear über Ursprungslaufzeit):
Exit_Setup = Setup_gesamt × Restlaufzeit / Ursprungslaufzeit

Hardware‑Restwert (lineare Abschreibung über Refinanzierungsmonate):
Restwert = max(0, Anschaffung − (Anschaffung / RefinanzMonate × bereits vergangene Monate))

Rückgabe-/Löschpflichten als Checkliste (Assets, Daten, Lizenzen).

Beispielrechnung:
Anschaffung = 1 800 €, Refinanz = 36 Mon., vergangen = 20 Mon. → Abschr./Monat = 1 800/36 = 50,00 €;
bereits abgeschrieben = 20 × 50 = 1 000,00 €; Restwert = 800,00 €.
Setup = 600 €, Ursprung = 36 Mon., Restlauf = 16 Mon.: 600 × 16 / 36 = 266,67 € (auf 2 Stellen gerundet).
Exit‑Gesamt vor USt = 1 066,67 € (zzgl. evtl. weitere Gebühren, konfigurierbar).

4.6 Partner‑Laufzeiten
Je Position kann eine Partnerreferenz (z. B. M365‑Abo, STARFACE‑Lizenz, Versicherungspolice) mit Start/Ende gepflegt werden.

Constraint: Enddatum der eigenen Leistung = Enddatum der Partnerleistung (Warnung/Block bei Abweichung).

4.7 Differenzabrechnung (rückwirkend)
Bei nachträglichen Mengen‑/Preis‑/Laufzeitänderungen erzeugt das System Gutschriften/Nachbelastungen mit Bezug auf Ursprungsrechnung/Zeitraum.

Runden/Schwellen (konfigurierbar), Protokoll im Änderungslog.

5. Datenmodell (Vorschlag für Laravel/Eloquent)
customers (id, name, …)
contracts (id, customer_id, title, status[DRAFT|ACTIVE|TERMINATION_REQ|TERMINATED|EXPIRED], master_flag, start_date, end_date, notice_period_days, billing_cycle[monthly/quarterly/yearly], currency, payment_terms, created_by, …)

contract_segments (id, contract_id, pillar[workplace|network|…], start_date, end_date, term_months, renewal_rule[none|same_term|12m], renewal_price_change_pct, notice_period_days, align_addons_full_month[bool], new_tier_resets_term[bool], partner_binding_required[bool], status, …)

contract_versions (id, segment_id, version_no, valid_from, valid_to, reason[upgrade|price_change|correction|…], snapshot_json, created_by, created_at)

contract_items (id, version_id, product_id, description, unit[licence|device|GB|hour|…], qty, unit_price_net, tax_rate, price_rule[flat|tiered|contingent], contingent_total, contingent_period[monthly|quarterly|yearly], partner_ref_id, partner_start, partner_end, requires_alignment[bool], …)

price_overrides (id, customer_id/null, product_id/null, pillar/null, valid_from, valid_to, rule_json)

adjustments (id, segment_id, type[credit|debit], reason[retro_change|exit|correction], base_period_from, base_period_to, amount_net, reference_invoice_id, note, created_by)

audit_logs (id, actor_id, entity_type, entity_id, action, old_values_json, new_values_json, created_at)

reminders (id, segment_id, type[notice|renewal_offer], due_at, sent_at, channel[email|task], status)

partner_links (id, item_id, partner_type[m365|starface|insurance|…], partner_identifier, start_date, end_date, sync_state)

assets (id, segment_id, serial_no, model, purchase_value, refinance_months, start_date) – für Hardware/Refinanzierung.

Hinweis: contract_segments realisieren das „keine Mischlaufzeiten pro Produktgruppe“. contract_versions erfüllen die Versionierung mit vollständigem Snapshot.

6. Benutzerrollen & Rechte
Admin: alle Rechte, Konfiguration, Preislisten, Regeln, Nummernkreise.

Vertrieb/Abrechnung: Anlage/Bearbeitung von Verträgen/Segmenten/Angeboten, Verlängerungen, Upgrades.

Prüfer: Freigabe von Änderungen, Exit‑Berechnungen, Partner‑Laufzeiten‑Kontrolle.

Leser: Nur Ansicht (z. B. Wirtschaftsprüfer).
Feingranular: Änderungen an Preisregeln, Exit‑Fees und Rückrechnungen nur mit Berechtigung.

7. Workflows (End‑to‑End)
7.1 Neuer Vertrag
Kunde wählen → Mastervertrag anlegen.

Segment(e) je Säule anlegen: Laufzeit, Verlängerungsregel, Kündigungsfrist.

Vertragspositionen (Produkte/Add‑ons) mit Preisen/Einheiten/Partnerlink.

Freigabe → Status ACTIVE.

7.2 Erweiterung (neue User/Lizenzen)
Segment auswählen → „Erweitern“ → Menge/Start (im Monat).

Regelprüfung: voller Monat, Alignment an Segmentende.

Neue contract_version erzeugen; Preisauswirkung anzeigen → speichern.

Wirkt in nächster Abrechnung.

7.3 Upgrade/Produktwechsel
Segment → „Upgrade“ (z. B. Basic → Premium).

Option: new_tier_resets_term → neue Mindestlaufzeit ab Upgrade‑Datum.

Versionierung, Altversion schließen, neue Version aktivieren.

7.4 Verlängerung
Reminder 90/60/30 Tage.

Angebot mit optionaler Preisänderung; Annahme → Segment end_date + term_months; Versionierung mit neuen Preisen.

7.5 Frühkündigung / Happiness‑Exit
Antrag → Exit‑Assistent berechnet Setup‑Anteil + Restwert Hardware (Formeln s. 4.5).

Checkliste Rückgabe/Löschung.

Gutschrift/Nachbelastung erzeugen (adjustments), Dokumentation im Audit.

Segment schließen.

7.6 Partner‑Synchronisation
Import der Partnerlaufzeiten oder manuelle Pflege.

Validierung: Enddatum Segment == Partnerende (Warnung/Block).

Abweichungen → Task/Workflow.

8. Abrechnungsrelevanz
Vertragsverwaltung liefert periodenfähige, versionierte Daten an Abrechnungs‑Engine.

Kontingente: Verbrauch wird pro Periode abgebucht (Über-/Unterlauf → Regeln).

Differenzabrechnung bei rückwirkenden Änderungen (automatisch erzeugte adjustments).

9. UI/UX‑Anforderungen (Auszug)
Kunden‑Cockpit: Säulen‑Übersicht (Kacheln Workplace/Network/… mit Status, Enddatum, Frist).

Zeitstrahl pro Segment: Versionen mit valid_from/valid_to, Preis/Mengen‑Änderungen, Partnerlink.

Assistenten:

Erweiterung (Mengen/Add‑ons)

Upgrade/Wechsel (inkl. Option „Laufzeit neu starten“)

Verlängerung (mit Preisänderung)

Exit (inkl. Kalkulation, Checkliste)

Validierungsbanner: Partner‑Laufzeiten, Kündigungsfristen, Mischlaufzeiten‑Verbot, Pflichtfelder.

Änderungslog pro Segment/Version (diff‑Ansicht).

10. Nicht‑funktionale Anforderungen
Nachvollziehbarkeit: Jede Änderung auditierbar (wer/was/wann, alt/neu).

Konsistenzregeln (Blocking/Warnungen) zentral.

Performance: Segment‑Listenfilter performant (Indexierung auf Kunde, Status, Enddatum).

Internationalisierung: Währung/Steuer je Kunde (v1: DE‑Fokus).

Sicherheit: Rollen/Rechte (spatie/permission), 2FA optional, TLS, getrennte Nummernkreise.

11. Akzeptanzkriterien (Beispiele)
Versionierung: Jede Mengen‑/Preis‑/Regeländerung erzeugt neue Version mit korrekter Gültigkeit, UI zeigt Historie.

Regeln „keine Mischlaufzeiten“: System verhindert Anlage widersprüchlicher Positionen in einem Segment.

Erinnerungen: Für Segmente mit end_date in 90/60/30 Tagen werden automatisch Tasks/E‑Mails generiert.

Exit‑Assistent: Rechnet Setup‑Anteil und Hardware‑Restwert korrekt (Beispiel aus 4.5 reproduzierbar), erzeugt Beleg (Adjustment).

Partner‑Bindung: Abweichung der Enddaten wird angezeigt und kann nicht freigegeben werden ohne Override‑Recht.

Differenzabrechnung: Rückwirkende Mengenänderung erzeugt Gutschrift/Nachbelastung mit Bezug auf Ursprung.

12. Offene Punkte / Nächste Schritte
Detaillierte Feldlisten je Tabelle (Datentypen, Constraints, Defaults).

Preislogiken (Staffeln, Mindestabnahmen, Rundungsregeln) formal festlegen.

Vorlagen (Angebot/Verlängerung/Exit‑Beleg) – Layout, Nummernkreise, Textbausteine.

Partner‑Datenfluss: Wie werden Partner‑Laufzeiten geliefert (API/File)? Mapping definieren.

Kontingent‑Regeln: Übertrag Restkontingent ja/nein; Mehrverbrauchslogik (Satz/Block).

Rechte‑Matrix (Wer darf Exit, Preisänderungen, Partner‑Overrides, Stornos?).

13. Technische Umsetzung (Laravel – Kurzleitplanken)
Migrations/Modelle gemäß Datenmodell; Beziehungen:
Customer hasMany Contract, Contract hasMany Segment, Segment hasMany Version, Version hasMany Items.

Policies für Schreibrechte (Segment‑Änderung, Exit, Preisänderung).

Jobs/Commands: Reminder‑Scheduler, Vertragsläufe, Exit‑Berechnung (Idempotenz).

Services: VersioningService, ExitCalculationService, PartnerSyncService, RenewalService.

Events: SegmentExtended, SegmentUpgraded, SegmentRenewed, SegmentTerminated, PartnerMismatchDetected.

Auditing: activitylog auf Contract/Segment/Version/Item/Adjustment.