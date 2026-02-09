# Sockets (.socket)

Les unités `.socket` permettent l'activation à la demande des services. systemd peut écouter sur un socket (Unix, TCP, UDP...) et démarrer le service associé uniquement lorsqu'une connexion arrive.

## Principe de l'activation par socket

L'activation par socket offre plusieurs avantages :

- **Démarrage plus rapide** : Le socket est créé immédiatement, le service démarre à la demande
- **Parallélisation** : Plusieurs services peuvent démarrer en parallèle même s'ils ont des dépendances
- **Économie de ressources** : Services inactifs ne consomment pas de mémoire
- **Redémarrage transparent** : Les connexions sont mises en file pendant le redémarrage

## Fonctionnement

1. systemd crée et écoute sur le socket
2. Une connexion arrive
3. systemd démarre le service associé
4. systemd passe le socket au service
5. Le service traite la connexion

## Structure d'un fichier socket

```ini
[Unit]
Description=SSH Socket for Per-Connection Servers

[Socket]
ListenStream=22
Accept=no

[Install]
WantedBy=sockets.target
```

## Section [Socket]

### Types de sockets

**ListenStream**

: Socket TCP ou Unix stream

```ini
# TCP
ListenStream=8080
ListenStream=0.0.0.0:8080
ListenStream=[::]:8080

# Unix socket
ListenStream=/run/myapp.sock
```

**ListenDatagram**

: Socket UDP ou Unix datagram

```ini
# UDP
ListenDatagram=514

# Unix datagram
ListenDatagram=/run/myapp.sock
```

**ListenSequentialPacket**

: Socket Unix sequential packet

```ini
ListenSequentialPacket=/run/myapp.sock
```

**ListenFIFO**

: Named pipe (FIFO)

```ini
ListenFIFO=/run/myapp.fifo
```

**ListenSpecial**

: Fichier spécial (device)

```ini
ListenSpecial=/dev/special
```

**ListenNetlink**

: Socket Netlink

```ini
ListenNetlink=kobject-uevent 1
```

**ListenMessageQueue**

: File de messages POSIX

```ini
ListenMessageQueue=/myqueue
```

### Options de socket

**Accept**

: Crée une instance de service par connexion

```ini
Accept=yes  # Une instance par connexion (inetd-style)
Accept=no   # Service unique gère toutes les connexions (défaut)
```

**SocketUser** / **SocketGroup**

: Propriétaire du socket Unix

```ini
SocketUser=www-data
SocketGroup=www-data
```

**SocketMode**

: Permissions du socket Unix

```ini
SocketMode=0660
```

**Backlog**

: Taille de la file d'attente des connexions

```ini
Backlog=256
```

**BindIPv6Only**

: Écouter uniquement IPv6

```ini
BindIPv6Only=both      # IPv4 et IPv6 (défaut)
BindIPv6Only=ipv6-only # Uniquement IPv6
```

**Broadcast**

: Activer le broadcast UDP

```ini
Broadcast=yes
```

**PassCredentials**

: Passer les credentials via SCM_CREDENTIALS

```ini
PassCredentials=yes
```

**PassSecurity**

: Passer le contexte de sécurité

```ini
PassSecurity=yes
```

**RemoveOnStop**

: Supprimer le socket Unix à l'arrêt

```ini
RemoveOnStop=yes
```

**MaxConnections**

: Nombre maximum de connexions simultanées

```ini
MaxConnections=64
```

**Service**

: Nom du service à activer (par défaut : même nom sans .socket)

```ini
Service=myapp.service
```

## Exemples

### Socket HTTP simple

```ini
# /etc/systemd/system/webapp.socket
[Unit]
Description=Web Application Socket

[Socket]
ListenStream=8080
Accept=no

[Install]
WantedBy=sockets.target
```

```ini
# /etc/systemd/system/webapp.service
[Unit]
Description=Web Application

[Service]
Type=simple
ExecStart=/usr/bin/webapp
StandardInput=socket
```

Activation :

```bash
systemctl enable webapp.socket
systemctl start webapp.socket

# Le service webapp.service démarrera automatiquement à la première connexion
```

### Socket Unix avec permissions

```ini
# /etc/systemd/system/myapp.socket
[Unit]
Description=My Application Socket

[Socket]
ListenStream=/run/myapp.sock
SocketMode=0660
SocketUser=myapp
SocketGroup=www-data
RemoveOnStop=yes

[Install]
WantedBy=sockets.target
```

### Socket SSH par connexion (Accept=yes)

```ini
# /etc/systemd/system/sshd.socket
[Unit]
Description=SSH Socket per Connection

[Socket]
ListenStream=22
Accept=yes

[Install]
WantedBy=sockets.target
```

```ini
# /etc/systemd/system/sshd@.service
[Unit]
Description=SSH Per-Connection Server

[Service]
Type=simple
ExecStart=-/usr/sbin/sshd -i
StandardInput=socket
StandardError=journal
```

### Socket UDP syslog

```ini
# /etc/systemd/system/syslog.socket
[Unit]
Description=Syslog Socket

[Socket]
ListenDatagram=514
Broadcast=yes

[Install]
WantedBy=sockets.target
```

### Socket Docker

Exemple réel de Docker :

```ini
# /lib/systemd/system/docker.socket
[Unit]
Description=Docker Socket for the API

[Socket]
ListenStream=/var/run/docker.sock
SocketMode=0660
SocketUser=root
SocketGroup=docker

[Install]
WantedBy=sockets.target
```

### Socket avec plusieurs ports

```ini
# /etc/systemd/system/multiport.socket
[Unit]
Description=Multi-Port Socket

[Socket]
ListenStream=8080
ListenStream=8443
ListenStream=/run/myapp.sock
Accept=no

[Install]
WantedBy=sockets.target
```

## Intégration avec les services

### Recevoir le socket dans le service

Pour qu'un service reçoive le socket, utilisez :

```ini
[Service]
StandardInput=socket
```

Ou l'API systemd pour récupérer les file descriptors :

**En C** :

```c
#include <systemd/sd-daemon.h>

int n = sd_listen_fds(0);
if (n > 0) {
    int fd = SD_LISTEN_FDS_START + 0;  // Premier socket
    // Utiliser fd...
}
```

**En Python** :

```python
import systemd.daemon

fds = systemd.daemon.listen_fds()
if fds:
    sock = socket.fromfd(fds[0], socket.AF_INET, socket.SOCK_STREAM)
```

**En Go** :

```go
import "github.com/coreos/go-systemd/activation"

listeners, _ := activation.Listeners()
if len(listeners) > 0 {
    ln := listeners[0]
    // Utiliser ln...
}
```

## Gestion des sockets

### Commandes de base

```bash
# Lister les sockets actifs
systemctl list-sockets

# Démarrer un socket
systemctl start myapp.socket

# Arrêter (arrête aussi le service associé)
systemctl stop myapp.socket

# Activer au boot
systemctl enable myapp.socket

# Voir l'état
systemctl status myapp.socket

# Voir les connexions actives
systemctl show myapp.socket -p NAccepted,NConnections
```

### Dépendances

Quand un socket est démarré, systemd crée automatiquement des dépendances :

- `Requires=myapp.service` : Le service est requis
- `Before=myapp.service` : Le socket démarre avant
- `Triggers=myapp.service` : Le socket déclenche le service

## Cas d'usage avancés

### Redémarrage sans coupure

L'activation par socket permet de redémarrer un service sans perdre de connexions :

```bash
# Les nouvelles connexions sont mises en file
systemctl restart myapp.service

# Le socket reste actif et buffer les connexions
```

### Dépendances parallélisées

Sans socket :

```text
service-a.service (démarre) 
  → attend que service-b.service soit prêt
```

Avec socket :

```text
service-a.socket (instantané)
service-b.socket (instantané)
  → Les deux services peuvent démarrer en parallèle
```

### Socket pour services gourmands

Pour des services qui consomment beaucoup de ressources mais rarement utilisés :

```ini
# Le service ne se lance que quand nécessaire
[Socket]
ListenStream=/run/heavy-service.sock
```

## Surveillance et métriques

### Voir les statistiques

```bash
systemctl show myapp.socket
```

Propriétés intéressantes :

- `NAccepted` : Nombre total de connexions acceptées
- `NConnections` : Nombre de connexions actuelles
- `NRefused` : Nombre de connexions refusées

### Logs

```bash
journalctl -u myapp.socket
journalctl -u myapp.socket -u myapp.service  # Socket + service
```

## Limitations et considérations

### Quand utiliser l'activation par socket ?

**Bon pour** :

- Services utilisés occasionnellement
- Optimisation du temps de boot
- Services avec dépendances complexes
- Redémarrages sans interruption

**Moins bon pour** :

- Services à haute fréquence (overhead de démarrage)
- Services qui doivent être toujours actifs
- Services avec initialisation longue

### Latence de démarrage

La première connexion peut être plus lente (temps de démarrage du service). Pour éviter cela :

```ini
[Service]
# Força le démarrage immédiat si nécessaire
ExecStartPre=/usr/bin/warmup.sh
```

## Sécurité

### Limiter les connexions

```ini
[Socket]
MaxConnections=100
MaxConnectionsPerSource=10
```

### Filtrage par IP

Utiliser `IPAddressAllow` / `IPAddressDeny` :

```ini
[Socket]
IPAddressAllow=192.168.1.0/24
IPAddressDeny=any
```

### Permissions Unix socket

```ini
[Socket]
SocketMode=0660        # Permissions
SocketUser=myapp       # Propriétaire
SocketGroup=www-data   # Groupe
```

## Débogage

### Problème : le service ne démarre pas

Vérifier :

```bash
# Le socket est-il actif ?
systemctl status myapp.socket

# Le service peut-il se lancer manuellement ?
systemctl start myapp.service

# Erreurs dans les logs
journalctl -u myapp.socket -u myapp.service
```

### Problème : permission denied

Vérifier les permissions du socket :

```bash
ls -l /run/myapp.sock

# Ajuster dans le fichier socket
SocketMode=0666
```

### Tester manuellement

Tester la connexion au socket :

```bash
# TCP
telnet localhost 8080

# Unix socket
socat - UNIX-CONNECT:/run/myapp.sock
```

L'activation par socket est une fonctionnalité puissante de systemd qui permet d'optimiser les performances et la gestion des services. Elle est particulièrement utile pour les services occasionnellement utilisés ou avec des dépendances complexes.
