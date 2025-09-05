# MSP Genie - Development Setup Guide

## Lokale Entwicklungsumgebung (Windows)

### Empfohlener Stack
```
Windows 11 mit WSL2 (Ubuntu)
Docker Desktop
Visual Studio Code mit WSL Extension
```

### Option 1: Docker + Laravel Sail (Empfohlen)
```bash
# 1. Laravel Projekt erstellen
curl -s "https://laravel.build/msp-genie?with=mysql,redis,mailhog" | bash

# 2. Ins Projekt-Verzeichnis
cd msp-genie

# 3. Sail starten
./vendor/bin/sail up -d

# 4. Anwendung erreichbar unter:
http://localhost
```

**Dienste:**
- **Laravel App**: http://localhost
- **MySQL**: localhost:3306
- **Redis**: localhost:6379
- **Mailhog**: http://localhost:8025

### Option 2: Lokale Installation
```bash
# Windows-spezifische Tools
choco install php composer nodejs git

# Laravel-spezifische Tools
composer global require laravel/installer

# MySQL/Redis über Docker
docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql:8.0
docker run --name redis -p 6379:6379 -d redis:alpine
```

### Entwicklungstools
```bash
# VS Code Extensions
- Laravel Extension Pack
- PHP Intelephense
- Docker
- WSL

# Composer-Pakete für Development
composer require --dev laravel/telescope
composer require --dev barryvdh/laravel-debugbar
composer require --dev nunomaduro/collision
```

## Live-Umgebung (Ubuntu Server)

### Server-Spezifikationen
```
OS: Ubuntu 22.04 LTS
RAM: 8GB+ (für Multi-Tenant)
CPU: 4 Cores+
Storage: 100GB+ SSD
```

### Server-Setup (Ubuntu 22.04)
```bash
# 1. System-Update
sudo apt update && sudo apt upgrade -y

# 2. Basis-Pakete
sudo apt install -y curl wget git unzip software-properties-common

# 3. Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 4. Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. Nginx als Reverse Proxy
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Production Docker Setup
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: msp-genie-app
    restart: unless-stopped
    working_dir: /var/www
    volumes:
      - ./:/var/www
      - ./storage/app/public:/var/www/public/storage
    depends_on:
      - mysql
      - redis
    environment:
      - APP_ENV=production
      - APP_DEBUG=false
    networks:
      - msp-network

  mysql:
    image: mysql:8.0
    container_name: msp-genie-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_DATABASE}
      MYSQL_USER: ${DB_USERNAME}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - msp-network

  redis:
    image: redis:alpine
    container_name: msp-genie-redis
    restart: unless-stopped
    networks:
      - msp-network

  nginx:
    image: nginx:alpine
    container_name: msp-genie-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - msp-network

volumes:
  mysql_data:

networks:
  msp-network:
    driver: bridge
```

### Production Dockerfile
```dockerfile
# Dockerfile.prod
FROM php:8.2-fpm

# Arbeitsverzeichnis
WORKDIR /var/www

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    libzip-dev \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip

# Composer installieren
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Node.js installieren
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Anwendung kopieren
COPY . .

# Abhängigkeiten installieren
RUN composer install --optimize-autoloader --no-dev
RUN npm install && npm run build

# Berechtigungen setzen
RUN chown -R www-data:www-data /var/www
RUN chmod -R 755 /var/www/storage

# Port exposieren
EXPOSE 9000

CMD ["php-fpm"]
```

### Nginx-Konfiguration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:9000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        root /var/www/public;
        index index.php;

        location / {
            try_files $uri $uri/ /index.php?$query_string;
        }

        location ~ \.php$ {
            fastcgi_pass app;
            fastcgi_index index.php;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            include fastcgi_params;
        }

        location ~ /\.ht {
            deny all;
        }
    }
}
```

## Multi-Tenant-Setup

### Database-Konfiguration
```php
// config/database.php
'connections' => [
    'mysql' => [
        'driver' => 'mysql',
        'host' => env('DB_HOST', '127.0.0.1'),
        'port' => env('DB_PORT', '3306'),
        'database' => env('DB_DATABASE', 'msp_genie'),
        'username' => env('DB_USERNAME', 'root'),
        'password' => env('DB_PASSWORD', ''),
        'charset' => 'utf8mb4',
        'collation' => 'utf8mb4_unicode_ci',
        'prefix' => '',
        'strict' => true,
        'engine' => null,
    ],
    
    'tenant' => [
        'driver' => 'mysql',
        'host' => env('DB_HOST', '127.0.0.1'),
        'port' => env('DB_PORT', '3306'),
        'database' => null, // Wird dynamisch gesetzt
        'username' => env('DB_USERNAME', 'root'),
        'password' => env('DB_PASSWORD', ''),
        'charset' => 'utf8mb4',
        'collation' => 'utf8mb4_unicode_ci',
        'prefix' => '',
        'strict' => true,
        'engine' => null,
    ],
],
```

### Tenancy-Konfiguration
```php
// config/tenancy.php
<?php

return [
    'tenant_model' => \App\Models\Tenant::class,
    'id_generator' => \Stancl\Tenancy\UUIDGenerator::class,
    
    'database' => [
        'prefix' => 'tenant_',
        'suffix' => '',
    ],
    
    'redis' => [
        'prefix_base' => 'tenant_',
    ],
    
    'cache' => [
        'prefix_base' => 'tenant_',
    ],
];
```

## Deployment-Strategie

### Git-Workflow
```bash
# Branches
main        # Production
develop     # Development
feature/*   # Feature-Branches
hotfix/*    # Hotfixes
```

### Deployment-Script
```bash
#!/bin/bash
# deploy.sh

# 1. Code aktualisieren
git pull origin main

# 2. Abhängigkeiten aktualisieren
composer install --optimize-autoloader --no-dev

# 3. Cache leeren
php artisan config:clear
php artisan cache:clear
php artisan route:clear
php artisan view:clear

# 4. Migrationen ausführen
php artisan migrate --force

# 5. Cache aufbauen
php artisan config:cache
php artisan route:cache
php artisan view:cache

# 6. Storage-Links
php artisan storage:link

# 7. Queues neustarten
php artisan queue:restart

# 8. Docker-Container neustarten
docker-compose down
docker-compose up -d
```

### CI/CD mit GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: '8.2'
        
    - name: Install Dependencies
      run: composer install --optimize-autoloader --no-dev
      
    - name: Run Tests
      run: php artisan test
      
    - name: Deploy to Server
      uses: appleboy/ssh-action@v0.1.2
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /var/www/msp-genie
          git pull origin main
          ./deploy.sh
```

## Monitoring & Wartung

### Logging
```php
// config/logging.php
'channels' => [
    'daily' => [
        'driver' => 'daily',
        'path' => storage_path('logs/laravel.log'),
        'level' => 'debug',
        'days' => 14,
    ],
    
    'tenant' => [
        'driver' => 'daily',
        'path' => storage_path('logs/tenant.log'),
        'level' => 'info',
        'days' => 30,
    ],
],
```

### Backup-Strategie
```bash
# Automatisches Backup-Script
#!/bin/bash
# backup.sh

DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="/backups/msp-genie"

# MySQL Backup
docker exec msp-genie-db mysqldump -u root -p${DB_PASSWORD} --all-databases > $BACKUP_DIR/mysql_$DATE.sql

# File Backup
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/msp-genie/storage

# Alte Backups löschen (30 Tage)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## Sicherheit

### SSL/TLS-Zertifikat
```bash
# Let's Encrypt
sudo certbot --nginx -d yourdomain.com

# Automatische Erneuerung
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall
```bash
# UFW konfigurieren
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 3306/tcp
```

### Environment-Variablen
```bash
# .env.production
APP_ENV=production
APP_DEBUG=false
APP_URL=https://yourdomain.com

DB_CONNECTION=mysql
DB_HOST=mysql
DB_PORT=3306
DB_DATABASE=msp_genie
DB_USERNAME=msp_user
DB_PASSWORD=secure_password

REDIS_HOST=redis
REDIS_PASSWORD=null
REDIS_PORT=6379

QUEUE_CONNECTION=redis
CACHE_DRIVER=redis
SESSION_DRIVER=redis
```

## Nächste Schritte

1. **Lokale Entwicklungsumgebung aufsetzen** (Option 1: Docker + Sail)
2. **Ubuntu Server bereitstellen** und grundlegende Konfiguration
3. **Domain & SSL-Zertifikat** einrichten
4. **CI/CD Pipeline** implementieren
5. **Monitoring & Backup** einrichten

---

**Status**: Setup-Guide erstellt, bereit für Implementation
**Letzte Aktualisierung**: 2025-01-16