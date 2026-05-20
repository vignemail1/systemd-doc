# Journal centralisé

Systemd fournit trois composants pour centraliser les logs entre machines : `systemd-journal-remote` (réception), `systemd-journal-upload` (envoi) et `systemd-journal-gatewayd` (lecture via HTTP). Cette page détaille leur configuration et leur utilisation.

Pour la configuration locale de journald, voir [Configuration avancée de journald](journald-config.md).

## Architecture de centralisation

```
  Machine A (source)              Machine B (collecteur)
  ┌───────────────────┐         ┌───────────────────┐
  │ systemd-journald    │         │ systemd-journald    │
  │ systemd-journal-   │  HTTPS  │ systemd-journal-   │
  │   upload           │ ──────→ │   remote           │
  └───────────────────┘         └───────────────────┘

  Machine C (source)               Machine B (collecteur)
  ┌───────────────────┐         ┌───────────────────┐
  │ systemd-journald   │  HTTP   │ systemd-journal-   │
  │ systemd-journal-   │ ──────→ │   gatewayd         │
  │   gatewayd (pull)  │         │ (lecture SSE/JSON) │
  └───────────────────┘         └───────────────────┘
```

Le flux principal utilisé en production est **upload → remote** (push actif depuis chaque source vers le collecteur). `gatewayd` est utile pour la lecture à la demande via un navigateur ou des outils HTTP.

## Prérequis et paquets

```bash
# Debian / Ubuntu
sudo apt install systemd-journal-remote

# RHEL / Fedora / Rocky
sudo dnf install systemd-journal-remote

# Les trois unités sont dans ce paquet :
# - systemd-journal-remote.service / .socket
# - systemd-journal-upload.service
# - systemd-journal-gatewayd.service / .socket
```

## Mise en place TLS (recommandé)

Les communications entre `upload` et `remote` transitent en HTTPS. En production, utiliser des certificats signés par une CA interne ou Let’s Encrypt. Pour un lab, un PKI minimal avec `openssl` suffit.

```bash
# --- Sur le collecteur ET sur chaque source ---
# Générer une CA auto-signée
openssl req -newkey rsa:4096 -nodes -keyout ca.key -x509 -days 3650 \
  -out ca.crt -subj "/CN=JournalCA"

# Générer la clé et le certificat du collecteur
openssl req -newkey rsa:4096 -nodes -keyout remote.key \
  -out remote.csr -subj "/CN=log-collector.example.com"
openssl x509 -req -in remote.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out remote.crt -days 730

# Générer la clé et le certificat d’une source
openssl req -newkey rsa:4096 -nodes -keyout upload.key \
  -out upload.csr -subj "/CN=server-a.example.com"
openssl x509 -req -in upload.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out upload.crt -days 730

# Installer sur le collecteur
sudo install -m 640 -o root -g systemd-journal-remote \
  remote.key /etc/ssl/private/journal-remote.key
sudo install -m 644 remote.crt /etc/ssl/certs/journal-remote.crt
sudo install -m 644 ca.crt /etc/ssl/certs/journal-ca.crt

# Installer sur chaque source
sudo install -m 640 -o root -g systemd-journal-upload \
  upload.key /etc/ssl/private/journal-upload.key
sudo install -m 644 upload.crt /etc/ssl/certs/journal-upload.crt
sudo install -m 644 ca.crt /etc/ssl/certs/journal-ca.crt
```

## Configurer le collecteur : `systemd-journal-remote`

### Fichier de configuration

`/etc/systemd/journal-remote.conf` :

```ini
[Remote]
# Certificat et clé du collecteur
ServerKeyFile=/etc/ssl/private/journal-remote.key
ServerCertificateFile=/etc/ssl/certs/journal-remote.crt

# CA pour valider les certificats clients
TrustedCertificateFile=/etc/ssl/certs/journal-ca.crt

# Mode de séparation des fichiers reçus
# host  = un fichier par machine source (recommandé)
# none  = tout dans un seul fichier
SplitMode=host

# Répertoire de destination des journaux reçus
# (le répertoire doit appartenir à systemd-journal-remote)
OutputDirectory=/var/log/journal/remote

# Scellement cryptographique des fichiers reçus
Seal=yes
```

### Créer le répertoire de destination

```bash
sudo mkdir -p /var/log/journal/remote
sudo chown systemd-journal-remote:systemd-journal-remote /var/log/journal/remote
```

### Activer et démarrer

```bash
# Utiliser le socket (activation à la demande, port 19532)
sudo systemctl enable --now systemd-journal-remote.socket

# Vérifier
sudo systemctl status systemd-journal-remote.socket
sudo systemctl status systemd-journal-remote.service
```

### Ouvrir le pare-feu

```bash
# firewalld
sudo firewall-cmd --permanent --add-port=19532/tcp
sudo firewall-cmd --reload

# nftables / iptables
sudo nft add rule inet filter input tcp dport 19532 accept
```

## Configurer les sources : `systemd-journal-upload`

### Fichier de configuration

`/etc/systemd/journal-upload.conf` :

```ini
[Upload]
# URL du collecteur (HTTPS obligatoire en production)
URL=https://log-collector.example.com:19532

# Certificat et clé de la machine source
ServerKeyFile=/etc/ssl/private/journal-upload.key
ServerCertificateFile=/etc/ssl/certs/journal-upload.crt

# CA pour valider le certificat du collecteur
TrustedCertificateFile=/etc/ssl/certs/journal-ca.crt
```

### Activer et démarrer

```bash
sudo systemctl enable --now systemd-journal-upload.service

# Vérifier l’état et les erreurs
sudo systemctl status systemd-journal-upload.service
sudo journalctl -u systemd-journal-upload -f
```

### Reprise après interruption

`systemd-journal-upload` mémorise le curseur de la dernière entrée transmise dans un fichier d’état (`/var/lib/systemd/journal-upload/state`). En cas d’interruption réseau, la reprise est automatique à partir du dernier curseur connu : aucun message n’est perdu ni dupliqué.

```bash
# Consulter l’état de reprise
cat /var/lib/systemd/journal-upload/state

# Réinitialiser (forcer un réenvoi depuis le début)
sudo systemctl stop systemd-journal-upload
sudo rm /var/lib/systemd/journal-upload/state
sudo systemctl start systemd-journal-upload
```

!!! warning "Réinitialiser l’état avec précaution"
    Supprimer le fichier `state` provoque un réenvoi de l’intégralité du journal local vers le collecteur. Sur un journal volumineux, cela peut générer un pic de trafic significatif.

## Mode HTTP sans TLS (lab uniquement)

```ini
# journal-remote.conf — collecteur
[Remote]
SplitMode=host
OutputDirectory=/var/log/journal/remote
# Pas de certificats = HTTP en clair
```

```ini
# journal-upload.conf — source
[Upload]
URL=http://log-collector.example.com:19532
# Pas de certificats
```

!!! danger "HTTP en clair"
    Ne jamais utiliser cette configuration sur un réseau non de confiance. Les logs peuvent contenir des données sensibles (tokens, mots de passe en variable d’environnement, etc.).

## Lire les journaux centralisés sur le collecteur

```bash
# Lister les fichiers reçus
ls /var/log/journal/remote/

# Lire les logs d’un hôte spécifique
journalctl --file=/var/log/journal/remote/remote-server-a.example.com.journal

# Lire tous les journaux distants en même temps
journalctl -D /var/log/journal/remote/

# Fusionner journaux locaux et distants
journalctl --merge -D /var/log/journal/remote/

# Filtrer sur un service d’un hôte distant spécifique
journalctl --file=/var/log/journal/remote/remote-server-a.example.com.journal \
  -u nginx.service -p err --since "1 hour ago"
```

## `systemd-journal-gatewayd` — accès HTTP

`systemd-journal-gatewayd` expose le journal local (ou distant) via une API HTTP, accessible depuis un navigateur ou un outil comme `curl`. Utile pour intégrer des systèmes de monitoring tiers.

### Configuration

`/etc/systemd/journal-gatewayd.conf` (si présent, selon la version de systemd) :

```ini
[Gateway]
# Certificat pour HTTPS (optionnel mais recommandé)
KeyFile=/etc/ssl/private/journal-gatewayd.key
CertificateFile=/etc/ssl/certs/journal-gatewayd.crt
```

### Démarrage

```bash
# Activer via socket (port 19531)
sudo systemctl enable --now systemd-journal-gatewayd.socket
sudo systemctl status systemd-journal-gatewayd.socket
```

### Endpoints disponibles

| Endpoint | Description |
| -------- | ----------- |
| `GET /entries` | Flux d’entrées du journal (JSON, SSE ou export) |
| `GET /entries?UNIT=nginx.service` | Filtrer par unité |
| `GET /entries?PRIORITY=3` | Filtrer par priorité |
| `GET /machine` | Informations sur la machine |
| `GET /fields/FIELD_NAME` | Valeurs connues d’un champ |

```bash
# Lire les 20 dernières entrées en JSON
curl -s http://localhost:19531/entries \
  -H "Accept: application/json" \
  | head -20

# Flux SSE (Server-Sent Events) en temps réel
curl -s http://localhost:19531/entries?follow \
  -H "Accept: text/event-stream"

# Erreurs des 30 dernières minutes
curl -s "http://localhost:19531/entries?PRIORITY=3&since=30+minutes+ago" \
  -H "Accept: application/json"

# Informations machine
curl -s http://localhost:19531/machine | python3 -m json.tool
```

## Cas pratique : infrastructure multi-serveurs

Architecture typique : 3 serveurs web envoient leurs logs vers 1 collecteur central.

### Étape 1 — Préparer le collecteur

```bash
# Sur le collecteur
sudo apt install systemd-journal-remote
sudo mkdir -p /var/log/journal/remote
sudo chown systemd-journal-remote:systemd-journal-remote /var/log/journal/remote

# Déposer les certificats (générés à l’étape TLS ci-dessus)
# puis configurer /etc/systemd/journal-remote.conf

sudo systemctl enable --now systemd-journal-remote.socket
```

### Étape 2 — Configurer chaque source

```bash
# Sur chaque serveur web (web1, web2, web3)
sudo apt install systemd-journal-remote
# Déposer les certificats propres à cette machine
# Configurer /etc/systemd/journal-upload.conf avec l’URL du collecteur
sudo systemctl enable --now systemd-journal-upload.service
```

### Étape 3 — Vérifier la réception

```bash
# Sur le collecteur, vérifier l’arrivée des fichiers
watch -n5 'ls -lh /var/log/journal/remote/'

# Confirmer que les trois hôtes envoient
journalctl -D /var/log/journal/remote/ \
  -F _HOSTNAME

# Surveiller les erreurs de tous les serveurs en temps réel
journalctl -D /var/log/journal/remote/ -f -p err
```

### Étape 4 — Automatiser le vacuum sur le collecteur

```bash
# /etc/systemd/journald.conf.d/remote-collector.conf
[Journal]
Storage=persistent
SystemMaxUse=50G
SystemKeepFree=10G
MaxRetentionSec=1year
```

## Diagnostic courant

### `systemd-journal-upload` ne démarre pas

```bash
journalctl -u systemd-journal-upload -p err
# Causes fréquentes :
# - URL incorrecte ou port fermé
# - Certificat expiré ou mauvaise CA
# - Fichier state corrompu
```

### Le collecteur ne reçoit rien

```bash
# Vérifier que le socket écoute
ss -tlnp | grep 19532

# Vérifier les logs du service remote
journalctl -u systemd-journal-remote -f

# Tester la connectivité TLS depuis la source
curl -v --cacert /etc/ssl/certs/journal-ca.crt \
  --cert /etc/ssl/certs/journal-upload.crt \
  --key /etc/ssl/private/journal-upload.key \
  https://log-collector.example.com:19532/upload
```

### Fichiers journaux corrompus

```bash
# Vérifier l’intégrité des journaux reçus
sudo journalctl --verify --file=/var/log/journal/remote/remote-web1.journal
```

## Voir aussi

- [Journal et logging](index.md) — vue d’ensemble et commandes `journalctl`
- [Configuration avancée de journald](journald-config.md) — `journald.conf` en détail
- `man systemd-journal-remote.service` — documentation du collecteur
- `man systemd-journal-upload.service` — documentation de l’envoi
- `man systemd-journal-gatewayd.service` — documentation de la passerelle HTTP
- `man journal-remote.conf` — référence des options de configuration
