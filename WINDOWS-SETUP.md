# MSP Genie - Windows Development Setup

## Schritt 1: Docker Desktop installieren

### 1.1 Docker Desktop herunterladen
1. Öffnen Sie https://www.docker.com/products/docker-desktop
2. Klicken Sie auf "Download for Windows"
3. Laden Sie die .exe-Datei herunter

### 1.2 Docker Desktop installieren
1. Führen Sie die heruntergeladene .exe-Datei aus
2. Folgen Sie dem Installations-Assistenten
3. **Wichtig**: Aktivieren Sie "Use WSL 2 instead of Hyper-V"
4. Neustart nach der Installation

### 1.3 Docker Desktop starten
1. Starten Sie Docker Desktop über das Startmenü
2. Warten Sie, bis Docker vollständig gestartet ist (grünes Icon in der Taskleiste)
3. Öffnen Sie PowerShell/CMD und testen Sie:
```bash
docker --version
docker-compose --version
```

## Schritt 2: WSL2-Integration einrichten

### 2.1 WSL2 Distribution installieren (falls noch nicht vorhanden)
```powershell
# PowerShell als Administrator öffnen
wsl --install -d Ubuntu
```

### 2.2 Docker Desktop WSL2-Integration aktivieren
1. Öffnen Sie Docker Desktop
2. Gehen Sie zu Settings (Zahnrad-Icon)
3. Wählen Sie "Resources" → "WSL Integration"
4. Aktivieren Sie "Enable integration with my default WSL distro"
5. Aktivieren Sie Ihre Ubuntu-Distribution
6. Klicken Sie "Apply & Restart"

### 2.3 WSL2 testen
```bash
# Windows Terminal/PowerShell öffnen
wsl
# Sie sollten jetzt in Ubuntu sein

# Docker in WSL2 testen
docker --version
docker-compose --version
```

## Schritt 3: Entwicklungstools installieren

### 3.1 IDE-Auswahl

#### Option A: PHPStorm (Empfohlen für Laravel)
1. Installieren Sie PHPStorm: https://www.jetbrains.com/phpstorm/
2. PHPStorm WSL2-Integration:
   - File → Settings → Build, Execution, Deployment → Deployment
   - "+" → "SFTP" → Name: "WSL2"
   - Connection: Type: "Local or mounted folder"
   - Folder: `/mnt/c/Projekte/MSPGenie/msp-genie`
3. Docker-Integration aktivieren:
   - File → Settings → Build, Execution, Deployment → Docker
   - "+" → "Docker for Windows"
   - Engine API URL: `tcp://localhost:2375`
4. Laravel Plugin installieren:
   - File → Settings → Plugins
   - "Laravel" Plugin von Barryvdh installieren

#### Option B: VS Code (Leichtere Alternative)
1. Installieren Sie VS Code: https://code.visualstudio.com/
2. Installieren Sie die WSL Extension:
   - VS Code öffnen
   - Extensions (Strg+Shift+X)
   - Suchen Sie nach "WSL"
   - Installieren Sie "WSL" von Microsoft

### 3.2 Git in WSL2 konfigurieren
```bash
# In WSL2 (Ubuntu)
sudo apt update
sudo apt install git

# Git konfigurieren
git config --global user.name "Ihr Name"
git config --global user.email "ihre.email@example.com"
```

## Schritt 4: Laravel Sail Projekt erstellen

### 4.1 Projektverzeichnis erstellen
```bash
# In WSL2
cd /mnt/c/Projekte/MSPGenie

# Oder falls das Verzeichnis nicht existiert:
mkdir -p /mnt/c/Projekte/MSPGenie
cd /mnt/c/Projekte/MSPGenie
```

### 4.2 Laravel Sail Projekt erstellen
```bash
# Laravel mit Sail installieren
curl -s "https://laravel.build/msp-genie?with=mysql,redis,mailhog" | bash

# Ins Projektverzeichnis wechseln
cd msp-genie

# Berechtigungen für Sail setzen
chmod +x vendor/bin/sail
```

### 4.3 Projekt starten
```bash
# Sail-Alias erstellen (optional aber empfohlen)
echo "alias sail='./vendor/bin/sail'" >> ~/.bashrc
source ~/.bashrc

# Container starten
./vendor/bin/sail up -d
```

### 4.4 Installation testen
```bash
# Anwendung testen
curl http://localhost
# Oder öffnen Sie http://localhost in Ihrem Browser

# Container-Status prüfen
./vendor/bin/sail ps
```

## Schritt 5: IDE mit Projekt verbinden

### 5.1 PHPStorm Projektsetup (Option A)

#### 5.1.1 Projekt öffnen
1. PHPStorm öffnen
2. "Open" → Navigate zu `C:\Projekte\MSPGenie\msp-genie`
3. Als PHP-Projekt öffnen

#### 5.1.2 PHP-Interpreter konfigurieren
1. File → Settings → PHP
2. CLI Interpreter: "..." → "+" → "From Docker, Vagrant, VM, WSL..."
3. "Docker Compose" auswählen
4. Configuration files: `./docker-compose.yml`
5. Service: `laravel.test`

#### 5.1.3 Database-Verbindung
1. Database-Tool öffnen (rechte Seite)
2. "+" → "Data Source" → "MySQL"
3. Host: `localhost`, Port: `3306`
4. User: `sail`, Password: `password`
5. Database: `msp_genie`

#### 5.1.4 Xdebug aktivieren
1. File → Settings → PHP → Debug
2. Port: `9003`
3. In `.env` hinzufügen: `SAIL_XDEBUG_MODE=develop,debug`

### 5.2 VS Code Setup (Option B)

#### 5.2.1 Projekt in VS Code öffnen
```bash
# In WSL2 im Projektverzeichnis
code .
```

#### 5.2.2 Empfohlene VS Code Extensions installieren
- PHP Intelephense
- Laravel Extension Pack
- Docker
- DotENV

#### 5.2.3 VS Code Terminal konfigurieren
1. In VS Code: Strg+Shift+P
2. Suchen Sie nach "Terminal: Select Default Profile"
3. Wählen Sie "WSL"

## Schritt 6: Multi-Tenant Package installieren

### 6.1 Tenancy Package installieren
```bash
# In WSL2 im Projektverzeichnis
./vendor/bin/sail composer require stancl/tenancy
```

### 6.2 Tenancy konfigurieren
```bash
# Service Provider publizieren
./vendor/bin/sail artisan vendor:publish --provider="Stancl\Tenancy\TenancyServiceProvider"

# Migrationen publizieren
./vendor/bin/sail artisan tenancy:install
```

### 6.3 Basis-Konfiguration
```bash
# .env-Datei bearbeiten
code .env
```

Fügen Sie hinzu:
```env
# Tenancy-Konfiguration
TENANCY_DATABASE_AUTO_DELETE=false
TENANCY_DATABASE_AUTO_DELETE_USER=false
```

## Schritt 7: Grundlegende Projektstruktur

### 7.1 Minia Template herunterladen
```bash
# Temporäres Verzeichnis erstellen
mkdir -p /tmp/minia
cd /tmp/minia

# Minia Template herunterladen (falls Sie es haben)
# Oder Bootstrap 5 als Alternative
./vendor/bin/sail npm install bootstrap@5.3.0
```

### 7.2 Basis-Authentifizierung installieren
```bash
# Zurück ins Projektverzeichnis
cd /mnt/c/Projekte/MSPGenie/msp-genie

# Laravel Breeze installieren
./vendor/bin/sail composer require laravel/breeze --dev

# Breeze installieren
./vendor/bin/sail artisan breeze:install

# NPM Dependencies installieren
./vendor/bin/sail npm install
./vendor/bin/sail npm run dev
```

## Schritt 8: Erste Tenant-Konfiguration

### 8.1 Tenant-Modell erstellen
```bash
# Tenant-Modell und Migration erstellen
./vendor/bin/sail artisan make:model Tenant -m
```

### 8.2 Migrationen ausführen
```bash
# Central-Datenbank migrieren
./vendor/bin/sail artisan migrate

# Tenant-Migrationen installieren
./vendor/bin/sail artisan tenancy:migrate
```

### 8.3 Ersten Tenant erstellen
```bash
# Tinker starten
./vendor/bin/sail artisan tinker

# In Tinker:
$tenant = \App\Models\Tenant::create(['id' => 'test-tenant']);
$tenant->createDomain(['domain' => 'test.localhost']);
```

## Schritt 9: Nützliche Sail-Befehle

### 9.1 Häufige Befehle
```bash
# Container starten
./vendor/bin/sail up -d

# Container stoppen
./vendor/bin/sail down

# Logs anzeigen
./vendor/bin/sail logs

# Artisan-Befehle
./vendor/bin/sail artisan migrate
./vendor/bin/sail artisan tinker

# Composer
./vendor/bin/sail composer install
./vendor/bin/sail composer require package-name

# NPM
./vendor/bin/sail npm install
./vendor/bin/sail npm run dev
./vendor/bin/sail npm run build

# Tests
./vendor/bin/sail test

# Shell-Zugriff
./vendor/bin/sail shell
```

### 9.2 Nützliche Aliases
```bash
# Fügen Sie diese zu ~/.bashrc hinzu
echo "alias sail='./vendor/bin/sail'" >> ~/.bashrc
echo "alias sa='./vendor/bin/sail artisan'" >> ~/.bashrc
echo "alias sc='./vendor/bin/sail composer'" >> ~/.bashrc
echo "alias sn='./vendor/bin/sail npm'" >> ~/.bashrc
source ~/.bashrc
```

## Schritt 10: Entwicklungsumgebung testen

### 10.1 Browser-Test
1. Öffnen Sie http://localhost
2. Sie sollten die Laravel-Willkommensseite sehen

### 10.2 Datenbank-Test
1. Öffnen Sie http://localhost:8080 (phpMyAdmin)
2. Loggen Sie sich ein: User: `sail`, Password: `password`
3. Prüfen Sie, ob die Datenbank `msp_genie` existiert

### 10.3 Redis-Test
```bash
# Redis-CLI testen
./vendor/bin/sail redis redis-cli ping
# Sollte "PONG" zurückgeben
```

### 10.4 Queue-Test
```bash
# Queue-Worker starten
./vendor/bin/sail artisan queue:work

# In einem neuen Terminal:
./vendor/bin/sail artisan queue:failed
```

## Fehlerbehebung

### Problem: Docker startet nicht
```bash
# WSL2 neu starten
wsl --shutdown
# Docker Desktop neu starten
```

### Problem: Port bereits belegt
```bash
# Andere Container stoppen
docker stop $(docker ps -q)

# Oder spezifische Ports in .env ändern
APP_PORT=8080
```

### Problem: Berechtigungen
```bash
# Berechtigungen reparieren
./vendor/bin/sail root-shell
chown -R sail:sail /var/www/html
```

### Problem: Sail-Befehl nicht gefunden
```bash
# Vollständigen Pfad verwenden
./vendor/bin/sail up -d

# Oder Alias setzen
alias sail='./vendor/bin/sail'
```

## Nächste Schritte

1. **Projekt läuft**: ✅ http://localhost erreichbar
2. **Tenancy funktioniert**: ✅ Test-Tenant erstellt
3. **Development-Tools**: ✅ VS Code + Extensions
4. **Git-Repository**: Erstellen und ersten Commit machen

```bash
# Git-Repository initialisieren
git init
git add .
git commit -m "Initial Laravel Sail setup with Tenancy"
```

---

**Status**: Development-Setup bereit
**Nächster Schritt**: Basis-Datenmodell implementieren
**Letzte Aktualisierung**: 2025-01-16