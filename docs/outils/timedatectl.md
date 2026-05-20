# timedatectl

`timedatectl` est l'outil de configuration de la date, de l'heure, du fuseau horaire et de la synchronisation NTP sous systemd. Il pilote `systemd-timesyncd` (client SNTP intégré) et interagit avec l'horloge matérielle (RTC).

## Syntaxe générale

```bash
timedatectl [OPTIONS] COMMANDE
```

## État et informations

```bash
# État complet : heure locale, UTC, RTC, fuseau, NTP
timedatectl status

# Vue condensée (systemd 239+)
timedatectl show

# Propriété spécifique
timedatectl show -p NTP
timedatectl show -p Timezone
timedatectl show -p LocalRTC
```

Exemple de sortie de `timedatectl status` :

```text
               Local time: Wed 2026-05-20 09:00:00 CEST
           Universal time: Wed 2026-05-20 07:00:00 UTC
                 RTC time: Wed 2026-05-20 07:00:00
                Time zone: Europe/Paris (CEST, +0200)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

## Fuseau horaire

```bash
# Lister tous les fuseaux disponibles
timedatectl list-timezones

# Filtrer
timedatectl list-timezones | grep Europe
timedatectl list-timezones | grep Paris

# Définir le fuseau horaire
sudo timedatectl set-timezone Europe/Paris
sudo timedatectl set-timezone UTC
sudo timedatectl set-timezone America/New_York
```

!!! tip "Serveurs sans interface graphique"
    Il est recommandé de configurer les serveurs en `UTC` et de gérer le fuseau horaire au niveau de l'application ou des logs. Cela évite les ambiguïtés lors des changements d'heure (heure d'été/hiver).

## Synchronisation NTP

```bash
# Activer la synchronisation NTP (via systemd-timesyncd ou chrony/ntpd)
sudo timedatectl set-ntp true

# Désactiver
sudo timedatectl set-ntp false

# Vérifier l'état de synchronisation
timedatectl status
# Chercher "System clock synchronized" et "NTP service"
```

### État détaillé de timesyncd

```bash
# État du client NTP systemd-timesyncd
timedatectl timesync-status

# Affichage exemple :
#        Server: 185.125.190.57 (ntp.ubuntu.com)
# Poll interval: 1min 4s (min: 32s; max 34min 8s)
#          Leap: normal
#       Version: 4
#       Stratum: 2
#     Reference: 11FABA17
#     Precision: 1us (-20)
#Root distance: 10.376ms (max: 5s)
#       Offset: +1.209ms
#        Delay: 20.662ms
#       Jitter: 1.533ms
#  Packet count: 5
```

```bash
# Propriétés brutes de timesyncd
timedatectl show-timesync
timedatectl show-timesync -p ServerName
timedatectl show-timesync -p NTPMessage
```

## Réglage manuel de l'heure

!!! warning "Désactiver NTP avant réglage manuel"
    Il faut désactiver `set-ntp` avant de modifier l'heure manuellement, sinon `timesyncd` écrase le changement.

```bash
# Désactiver NTP
sudo timedatectl set-ntp false

# Définir date et heure (format : "YYYY-MM-DD HH:MM:SS")
sudo timedatectl set-time "2026-05-20 09:30:00"

# Définir la date uniquement
sudo timedatectl set-time "2026-05-20"

# Réactiver NTP
sudo timedatectl set-ntp true
```

## Horloge matérielle (RTC)

```bash
# Afficher l'heure RTC actuelle
timedatectl status
# Ligne "RTC time"

# Indiquer que la RTC est en heure locale (déconseillé, compatibilité Windows)
sudo timedatectl set-local-rtc true

# Revenir en UTC (recommandé)
sudo timedatectl set-local-rtc false
```

!!! warning "RTC en heure locale"
    `set-local-rtc true` est utile sur des machines dual-boot avec Windows (qui stocke l'heure locale dans la RTC). Sur un serveur Linux pur, toujours laisser la RTC en UTC.

## Configuration de timesyncd

Le fichier de configuration de `systemd-timesyncd` est `/etc/systemd/timesyncd.conf` (ou un fichier dans `/etc/systemd/timesyncd.conf.d/`).

```ini
[Time]
# Serveurs NTP principaux
NTP=0.fr.pool.ntp.org 1.fr.pool.ntp.org 2.fr.pool.ntp.org 3.fr.pool.ntp.org

# Serveurs de secours
FallbackNTP=time.cloudflare.com ntp.ubuntu.com

# Décalage RTC minimal pour mise à jour (défaut : 11min)
#RootDistanceMaxSec=5
#PollIntervalMinSec=32
#PollIntervalMaxSec=2048
```

```bash
# Appliquer la configuration
sudo systemctl restart systemd-timesyncd

# Vérifier le serveur utilisé après redémarrage
timedatectl timesync-status
```

## Diagnostics courants

### NTP actif mais horloge non synchronisée

```bash
# Vérifier l'état détaillé
timedatectl timesync-status

# Vérifier les logs de timesyncd
journalctl -u systemd-timesyncd -f

# Vérifier la connectivité vers les serveurs NTP (port 123/UDP)
ss -unp | grep 123
```

### Conflit avec chrony ou ntpd

```bash
# Si chrony ou ntpd est installé, timesyncd doit être désactivé
systemctl status chronyd ntpd systemd-timesyncd

# Désactiver timesyncd si chrony prend la main
sudo systemctl disable --now systemd-timesyncd
```

### Décalage important après hibernation

```bash
# Forcer une synchronisation immédiate
sudo systemctl restart systemd-timesyncd
timedatectl timesync-status
# Vérifier "Offset" : doit revenir proche de 0
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--no-pager` | Désactiver le paginateur |
| `--no-ask-password` | Ne pas demander le mot de passe polkit |
| `-H <hôte>` | Hôte distant (via SSH) |
| `-M <machine>` | Machine / conteneur systemd-nspawn |
| `-p <prop>` | Filtrer sur une propriété (`show`) |

## Voir aussi

- `man timedatectl`
- `man systemd-timesyncd.service`
- `man timesyncd.conf`
