# SpotifySort - Deployment Guide

Guide pour déployer SpotifySort en production avec un nom de domaine et HTTPS.

## Prérequis

- VPS Linux (Ubuntu/Debian)
- Nom de domaine configuré (ex: spotifysort.nyx-off.dev)
- Nginx installé
- Certbot pour SSL (Let's Encrypt)
- Python 3.10+

## Étape 1 : Configuration Spotify API

1. Allez sur https://developer.spotify.com/dashboard
2. Créez ou sélectionnez votre application
3. Cliquez sur **Settings**
4. Ajoutez votre Redirect URI :
   ```
   https://spotifysort.nyx-off.dev/callback
   ```
   (Remplacez par votre domaine)
5. Notez votre **Client ID** et **Client Secret**

## Étape 2 : Installation sur le serveur

```bash
# Cloner le projet
cd ~
git clone https://github.com/Nyx-Off/SpotifySort.git
cd SpotifySort

# Installer dans un venv
./install.sh
```

## Étape 3 : Configuration

Créez le fichier `.env` :

```bash
nano .env
```

Contenu :
```env
# Spotify API Credentials
SPOTIFY_CLIENT_ID=votre_client_id
SPOTIFY_CLIENT_SECRET=votre_client_secret
SPOTIFY_REDIRECT_URI=https://spotifysort.nyx-off.dev/callback

# Flask Configuration
FLASK_SECRET_KEY=generez_une_cle_aleatoire_ici
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false
```

Pour générer une clé secrète :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Étape 4 : Configuration Nginx

### Installer Nginx (si pas déjà fait)

```bash
sudo apt update
sudo apt install nginx
```

### Créer la configuration

```bash
sudo nano /etc/nginx/sites-available/spotifysort
```

Copiez le contenu de `nginx-config.example` ou utilisez :

```nginx
server {
    listen 80;
    server_name spotifysort.nyx-off.dev;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name spotifysort.nyx-off.dev;

    ssl_certificate /etc/letsencrypt/live/spotifysort.nyx-off.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/spotifysort.nyx-off.dev/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Activer la configuration

```bash
sudo ln -s /etc/nginx/sites-available/spotifysort /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Étape 5 : Certificat SSL (Let's Encrypt)

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat
sudo certbot --nginx -d spotifysort.nyx-off.dev

# Auto-renewal (déjà configuré par défaut)
sudo certbot renew --dry-run
```

## Étape 6 : Service Systemd (démarrage automatique)

Créez le service :

```bash
sudo nano /etc/systemd/system/spotifysort.service
```

Contenu (adaptez le chemin et l'utilisateur) :

```ini
[Unit]
Description=SpotifySort Web Application
After=network.target

[Service]
Type=simple
User=nyx
WorkingDirectory=/home/nyx/SpotifySort
Environment="PATH=/home/nyx/SpotifySort/venv/bin"
ExecStart=/home/nyx/SpotifySort/venv/bin/python -m spotifysort.web.app --host 127.0.0.1 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activez et démarrez :

```bash
sudo systemctl daemon-reload
sudo systemctl enable spotifysort
sudo systemctl start spotifysort
sudo systemctl status spotifysort
```

## Étape 7 : Vérification

1. Vérifiez que le service tourne :
   ```bash
   sudo systemctl status spotifysort
   ```

2. Vérifiez Nginx :
   ```bash
   sudo systemctl status nginx
   ```

3. Testez l'accès :
   ```bash
   curl https://spotifysort.nyx-off.dev
   ```

4. Ouvrez dans le navigateur :
   ```
   https://spotifysort.nyx-off.dev
   ```

## Étape 8 : Utilisation

1. Ouvrez https://spotifysort.nyx-off.dev
2. Cliquez sur "Login with Spotify"
3. Autorisez l'application
4. Commencez à organiser votre bibliothèque !

## Commandes utiles

### Voir les logs

```bash
# Logs de l'application
sudo journalctl -u spotifysort -f

# Logs Nginx
sudo tail -f /var/log/nginx/spotifysort_access.log
sudo tail -f /var/log/nginx/spotifysort_error.log
```

### Redémarrer

```bash
# Redémarrer l'application
sudo systemctl restart spotifysort

# Redémarrer Nginx
sudo systemctl restart nginx
```

### Mettre à jour

```bash
cd ~/SpotifySort
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart spotifysort
```

## Sécurité

### Firewall

```bash
# Autoriser HTTP et HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Bloquer l'accès direct au port 5000
sudo ufw deny 5000/tcp
```

### Sauvegardes

Les sessions Spotify sont stockées dans `/tmp/spotifysort_sessions/`.
Vous pouvez les sauvegarder si nécessaire :

```bash
# Backup
tar -czf spotifysort-backup-$(date +%Y%m%d).tar.gz ~/SpotifySort/.env /tmp/spotifysort_sessions/

# Restore
tar -xzf spotifysort-backup-YYYYMMDD.tar.gz
```

## Troubleshooting

### L'application ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u spotifysort -n 50

# Vérifier manuellement
cd ~/SpotifySort
source venv/bin/activate
python -m spotifysort.web.app
```

### Erreur 502 Bad Gateway

```bash
# L'application n'est pas démarrée
sudo systemctl start spotifysort

# Vérifier qu'elle écoute sur le bon port
sudo netstat -tlnp | grep 5000
```

### Erreur OAuth

- Vérifiez que le Redirect URI dans Spotify Dashboard correspond exactement
- Vérifiez votre `.env`
- Le domaine doit être accessible publiquement
- HTTPS obligatoire en production

## Performance

Pour de meilleures performances :

1. **Activer la compression** dans Nginx :
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **Cache des fichiers statiques** :
   ```nginx
   location /static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

3. **Limiter les requêtes** :
   ```nginx
   limit_req_zone $binary_remote_addr zone=spotifysort:10m rate=10r/s;
   limit_req zone=spotifysort burst=20;
   ```

## Support

- GitHub Issues: https://github.com/Nyx-Off/SpotifySort/issues
- Documentation: https://github.com/Nyx-Off/SpotifySort
