# Limitation des ressources utilisateurs

Cette page explique comment utiliser systemd-logind pour limiter automatiquement les ressources (CPU, RAM, processus) allouées aux utilisateurs lors de leurs connexions SSH ou console.

## Principe

systemd-logind crée automatiquement des slices pour chaque utilisateur connecté :

```
user.slice
  ├── user-1000.slice (utilisateur alice)
  │   └── session-1.scope (session SSH)
  ├── user-1001.slice (utilisateur bob)
  │   └── session-2.scope (session SSH)
  └── user-1002.slice (utilisateur charlie)
      └── session-3.scope (session console)
```

Chaque `user-UID.slice` peut avoir des limites de ressources.

## Configuration globale pour tous les utilisateurs

### Méthode 1 : Configuration logind

Fichier `/etc/systemd/logind.conf` :

```ini
[Login]
# Limites par défaut pour tous les utilisateurs
UserTasksMax=500
```

**Version minimum** : systemd 230+

Appliquer :

```bash
sudo systemctl restart systemd-logind
```

!!! warning "Attention"
    Redémarrer logind déconnecte tous les utilisateurs. Planifier pendant une maintenance.

### Méthode 2 : Drop-in pour user.slice

Configuration `/etc/systemd/system/user.slice.d/limits.conf` :

```ini
[Slice]
# Limites pour tous les utilisateurs
CPUQuota=100%              # 1 core total par utilisateur
MemoryMax=2G               # 2 Go RAM max par utilisateur
MemoryHigh=1.5G            # Throttling à 1.5 Go
TasksMax=500               # Max 500 processus/threads
IOWeight=100               # Priorité I/O basse
```

**Versions minimums** :

- `CPUQuota` : systemd 213+
- `MemoryMax`, `MemoryHigh` : systemd 231+
- `TasksMax` : systemd 227+
- `IOWeight` : systemd 232+

Appliquer :

```bash
sudo systemctl daemon-reload

# Pas besoin de redémarrer, s'applique aux nouvelles sessions
```

## Limites par utilisateur spécifique

### Pour un utilisateur donné

Configuration `/etc/systemd/system/user-1000.slice.d/limits.conf` :

```ini
[Slice]
CPUQuota=200%         # 2 cores pour alice (UID 1000)
MemoryMax=4G          # 4 Go RAM
TasksMax=1000         # 1000 processus
```

Appliquer :

```bash
sudo systemctl daemon-reload
```

Pour trouver l'UID d'un utilisateur :

```bash
id -u alice
```

### Configuration dynamique

Modifier temporairement (jusqu'à la prochaine connexion) :

```bash
# Pour l'utilisateur UID 1000
sudo systemctl set-property user-1000.slice CPUQuota=50%
sudo systemctl set-property user-1000.slice MemoryMax=1G
sudo systemctl set-property user-1000.slice TasksMax=200
```

Pour rendre permanent :

```bash
sudo systemctl set-property --runtime=false user-1000.slice CPUQuota=50%
```

## Limites par groupe d'utilisateurs

### Créer un groupe

```bash
sudo groupadd limited-users
sudo usermod -aG limited-users alice
sudo usermod -aG limited-users bob
```

### Configuration avec pam_systemd

Fichier `/etc/security/limits.d/limited-users.conf` :

```
@limited-users  hard    nproc       200
@limited-users  hard    memlock     1048576
@limited-users  hard    nofile      1024
```

Fichier `/etc/systemd/system/user-.slice.d/limited-users.conf` :

```ini
[Slice]
CPUQuota=100%
MemoryMax=2G
TasksMax=300
```

### Script pour appliquer selon groupe

Créer `/usr/local/bin/apply-user-limits.sh` :

```bash
#!/bin/bash
# Script exécuté à la connexion via pam_exec

USER="$PAM_USER"
UID=$(id -u "$USER")

if groups "$USER" | grep -q "limited-users"; then
    systemctl set-property "user-${UID}.slice" CPUQuota=50%
    systemctl set-property "user-${UID}.slice" MemoryMax=1G
    systemctl set-property "user-${UID}.slice" TasksMax=200
fi
```

Configuration PAM `/etc/pam.d/sshd` :

```
session optional pam_exec.so /usr/local/bin/apply-user-limits.sh
```

## Exemples pratiques

### Serveur de développement partagé

```ini
# /etc/systemd/system/user.slice.d/dev-limits.conf
[Slice]
# Limiter chaque développeur
CPUQuota=400%              # 4 cores max
MemoryMax=16G              # 16 Go RAM max
MemoryHigh=12G             # Throttling à 12 Go
TasksMax=2000              # Beaucoup de processus (IDE, build...)
IOWeight=500               # Priorité I/O moyenne
```

### Serveur d'accès limité

```ini
# /etc/systemd/system/user.slice.d/restricted.conf
[Slice]
# Utilisateurs avec accès minimal
CPUQuota=50%               # 0.5 core
MemoryMax=512M             # 512 Mo RAM
MemorySwapMax=256M         # 256 Mo swap
TasksMax=100               # 100 processus max
IOWeight=50                # Priorité I/O très basse
```

**Version minimum** : `MemorySwapMax` requiert systemd 232+

### Utilisateurs administrateurs

```ini
# /etc/systemd/system/user-0.slice.d/root-unlimited.conf
[Slice]
# Root sans limites
CPUQuota=infinity
MemoryMax=infinity
TasksMax=infinity
```

### Utilisateurs de service

```ini
# /etc/systemd/system/user-1050.slice.d/service-user.conf
[Slice]
# Utilisateur de monitoring (ex: Prometheus)
CPUQuota=100%
MemoryMax=2G
TasksMax=500
IOWeight=800               # Haute priorité I/O
```

## Monitoring et vérification

### Voir les limites actives

```bash
# Pour un utilisateur spécifique
systemctl show user-1000.slice | grep -E '(CPU|Memory|Tasks)'

# Toutes les propriétés
systemctl show user-1000.slice

# Limites de tous les utilisateurs
for slice in /sys/fs/cgroup/user.slice/user-*.slice; do
    uid=$(basename "$slice" | sed 's/user-\([0-9]*\).slice/\1/')
    user=$(getent passwd "$uid" | cut -d: -f1)
    echo "=== $user (UID $uid) ==="
    systemctl show "user-${uid}.slice" | grep -E '(CPUQuota|MemoryMax|TasksMax)'
    echo
done
```

### Surveiller l'utilisation

```bash
# Vue en temps réel des utilisateurs
systemd-cgtop

# Filtrer sur user.slice
systemd-cgtop | grep user-

# Utilisation détaillée
systemd-cgls user.slice
```

### Vérifier si limites atteintes

```bash
# Pour un utilisateur
journalctl -u user-1000.slice | grep -i "limit\|oom\|throttl"

# Tous les utilisateurs
journalctl | grep -i "user.*limit"

# OOM kills
journalctl -k | grep -i "oom"
```

### Statistiques d'utilisation

```bash
# CPU usage (nanosecondes)
systemctl show user-1000.slice -p CPUUsageNSec

# Mémoire actuelle
systemctl show user-1000.slice -p MemoryCurrent

# Nombre de tâches
systemctl show user-1000.slice -p TasksCurrent

# I/O
systemctl show user-1000.slice -p IOReadBytes -p IOWriteBytes
```

## Débogage

### Utilisateur ne peut pas se connecter

Causes possibles :

1. **TasksMax trop bas** : Shell, sshd, pam nécessitent des processus

   ```bash
   # Augmenter temporairement
   sudo systemctl set-property user-1000.slice TasksMax=200
   ```

2. **MemoryMax trop bas** : Pas assez de RAM pour le shell

   ```bash
   # Vérifier les logs
   sudo journalctl -u user-1000.slice | tail -20
   ```

3. **Limites PAM conflictuelles**

   ```bash
   # Vérifier
   cat /etc/security/limits.conf
   cat /etc/security/limits.d/*
   ```

### Processus tués par OOM

```bash
# Voir les OOM kills
sudo journalctl -k | grep -i "killed process"

# Augmenter la limite
sudo systemctl set-property user-1000.slice MemoryMax=4G
```

### Performances dégradées

```bash
# Vérifier le throttling CPU
systemctl show user-1000.slice -p CPUUsageNSec

# Vérifier le throttling mémoire
systemctl show user-1000.slice -p MemoryCurrent -p MemoryHigh

# Voir les warnings
journalctl -u user-1000.slice | grep -i "throttl"
```

## Configuration avancée

### Limites par heure de connexion

Script `/usr/local/bin/time-based-limits.sh` :

```bash
#!/bin/bash
USER="$PAM_USER"
UID=$(id -u "$USER")
HOUR=$(date +%H)

# Heures de travail (9h-18h) : limites normales
if [ $HOUR -ge 9 ] && [ $HOUR -lt 18 ]; then
    systemctl set-property "user-${UID}.slice" CPUQuota=200%
    systemctl set-property "user-${UID}.slice" MemoryMax=4G
else
    # Hors heures : limites réduites
    systemctl set-property "user-${UID}.slice" CPUQuota=50%
    systemctl set-property "user-${UID}.slice" MemoryMax=1G
fi
```

### Limites selon charge système

Script `/usr/local/bin/adaptive-limits.sh` :

```bash
#!/bin/bash
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | cut -d. -f1)

if [ $LOAD -gt 10 ]; then
    # Charge élevée : limiter davantage
    systemctl set-property user.slice CPUQuota=50%
    systemctl set-property user.slice MemoryMax=1G
else
    # Charge normale
    systemctl set-property user.slice CPUQuota=200%
    systemctl set-property user.slice MemoryMax=4G
fi
```

Exécuter via cron toutes les 5 minutes :

```cron
*/5 * * * * /usr/local/bin/adaptive-limits.sh
```

### Quotas réseau par utilisateur

**Version minimum** : systemd 239+ (pour IPAddressAllow/Deny)

```ini
# /etc/systemd/system/user-1000.slice.d/network.conf
[Slice]
# Limiter la bande passante (nécessite cgroups v2 et tc)
IPAccounting=yes
IPAddressAllow=10.0.0.0/8 192.168.0.0/16
IPAddressDeny=any
```

## Bonnes pratiques

1. **Commencer large**

   ```ini
   CPUQuota=400%
   MemoryMax=8G
   TasksMax=1000
   ```

   Puis ajuster selon le monitoring.

2. **Toujours permettre le shell**

   ```ini
   TasksMax=100  # Minimum absolu
   MemoryMax=256M  # Minimum pour shell basique
   ```

3. **Utiliser MemoryHigh pour soft limit**

   ```ini
   MemoryHigh=3G   # Throttling
   MemoryMax=4G    # Hard limit
   ```

4. **Documenter les limites**

   ```ini
   # Limites pour développeurs (build intensifs)
   CPUQuota=400%
   ```

5. **Monitorer régulièrement**

   ```bash
   systemd-cgtop
   journalctl | grep -i "limit\|oom"
   ```

6. **Tester avant production**

   ```bash
   # Connexion test
   ssh testuser@localhost
   
   # Vérifier les limites
   systemctl show user-$(id -u).slice
   ```

7. **Exclure les admins**

   ```ini
   # /etc/systemd/system/user-0.slice.d/unlimited.conf
   [Slice]
   CPUQuota=infinity
   MemoryMax=infinity
   ```

## Récapitulatif des versions

| Fonctionnalité | Version minimum |
|-----------------|------------------|
| TasksMax | systemd 227+ |
| CPUQuota | systemd 213+ |
| MemoryMax, MemoryHigh | systemd 231+ |
| MemorySwapMax | systemd 232+ |
| IOWeight | systemd 232+ |
| IPAccounting | systemd 235+ |
| IPAddressAllow/Deny | systemd 239+ |
| ProtectProc | systemd 247+ |

Vérifier votre version :

```bash
systemctl --version
```

La limitation des ressources utilisateurs via systemd-logind permet un contrôle granulaire et automatique, essentiel sur les serveurs multi-utilisateurs.
