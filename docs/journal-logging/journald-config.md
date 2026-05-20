# Configuration avancée de journald

La page [Journal et logging](index.md) présente les commandes `journalctl` et les paramètres de base. Cette page couvre la configuration fine de `/etc/systemd/journald.conf` : stratégies de stockage, limites de taille, rate-limiting, forwarding, compression et scellement cryptographique.

Le fichier de référence est `/etc/systemd/journald.conf`. Des surcharges peuvent être placées dans `/etc/systemd/journald.conf.d/*.conf` pour une gestion modulaire (recommandé en production).

```bash
# Voir la configuration effective (valeurs réelles après fusion des surcharges)
systemd-analyze cat-config systemd/journald.conf
```

## Stratégie de stockage (`Storage=`)

```ini
[Journal]
Storage=auto
```

| Valeur | Comportement |
| ------ | ------------ |
| `auto` | Persistant si `/var/log/journal/` existe, volatile sinon (défaut) |
| `persistent` | Toujours dans `/var/log/journal/`, crée le dossier si nécessaire |
| `volatile` | Uniquement dans `/run/log/journal/` (RAM, perdu au reboot) |
| `none` | Aucun stockage ; les messages sont quand même transmis aux sockets |

### Activer la persistance de façon propre

```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
```

!!! tip "Surcharge minimale recommandée"
    Plutôt que de modifier le fichier principal, créer :

    ```bash
    sudo mkdir -p /etc/systemd/journald.conf.d
    sudo tee /etc/systemd/journald.conf.d/persistence.conf <<'EOF'
    [Journal]
    Storage=persistent
    EOF
    sudo systemctl restart systemd-journald
    ```

## Limites de taille

Deux ensembles de limites coexistent : l'un pour le stockage persistant (`/var/log/journal/`), l'autre pour le stockage volatile (`/run/log/journal/`).

```ini
[Journal]
# --- Stockage persistant ---
# Taille totale maximale des fichiers journal sur disque
SystemMaxUse=2G

# Espace libre minimum à conserver sur la partition
SystemKeepFree=1G

# Taille maximale d'un seul fichier journal
SystemMaxFileSize=128M

# Nombre maximal de fichiers journal archivés
SystemMaxFiles=100

# --- Stockage volatile ---
RuntimeMaxUse=256M
RuntimeKeepFree=512M
RuntimeMaxFileSize=32M
RuntimeMaxFiles=10
```

!!! warning "Priorité des limites"
    systemd-journald applique **la plus restrictive** entre `SystemMaxUse` et la taille laissée libre par `SystemKeepFree`. Si la partition est déjà bien remplie, le journal peut occuper moins que `SystemMaxUse`.

### Calibrer les limites selon le contexte

| Contexte | `SystemMaxUse` | `MaxRetentionSec` | Remarques |
| -------- | -------------- | ----------------- | --------- |
| Serveur de production | 4-8 G | 3 mois | Garder suffisamment pour les audits |
| Container / VM légère | 128-256 M | 1 semaine | Espace disque limité |
| Poste de travail | 1-2 G | 1 mois | Valeurs raisonnables par défaut |
| Serveur de logs centralisé | 50-200 G | 1 an | Adapter à la rétention réglementaire |

## Rotation et rétention

```ini
[Journal]
# Durée maximale de rétention des entrées
MaxRetentionSec=1month

# Intervalle de rotation des fichiers
MaxFileSec=1week

# Rotation manuelle (signal ou commande)
# journalctl --rotate
```

Les valeurs acceptées pour les durées : `s` (secondes), `min`, `h`, `days`, `weeks`, `months`, `years`.

```bash
# Forcer une rotation immédiate sans redémarrer journald
sudo journalctl --rotate

# Puis nettoyer les anciens fichiers
sudo journalctl --vacuum-time=30d
```

## Rate-limiting

Le rate-limiting protège journald contre les services qui génèrent un volume excessif de messages en rafale. Il fonctionne par service (par cgroup).

```ini
[Journal]
# Fenêtre de temps pour le calcul du débit
RateLimitIntervalSec=30s

# Nombre maximum de messages par fenêtre et par service
RateLimitBurst=10000
```

Quand un service dépasse la limite, journald émet un message de synthèse indiquant combien de messages ont été supprimés, puis reprend la collecte.

### Adapter selon le type de service

```ini
# Pour un serveur très verbeux (ex. base de données, proxy)
RateLimitIntervalSec=30s
RateLimitBurst=50000

# Pour désactiver le rate-limiting (déconseillé en production)
RateLimitIntervalSec=0
```

!!! note "Rate-limiting par service"
    Il est possible de surcharger le rate-limiting pour un service spécifique directement dans l'unité systemd :

    ```ini
    [Service]
    LogRateLimitIntervalSec=0
    LogRateLimitBurst=0
    ```

## Compression et scellement

```ini
[Journal]
# Compresser les entrées volumineuses (> quelques Ko)
Compress=yes

# Scellement cryptographique Forward Secure Sealing (FSS)
# Permet de détecter toute altération des fichiers journaux
Seal=yes
```

### Forward Secure Sealing (FSS)

Le scellement FSS utilise une clé de vérification publique/privée pour garantir l'intégrité des entrées passées. Une fois une entrée scellée, la supprimer ou la modifier est détectable.

```bash
# Générer une paire de clés FSS
sudo journalctl --setup-keys

# Vérifier l'intégrité d'un journal scellé
sudo journalctl --verify
```

La clé de vérification (publique) peut être stockée hors du système pour les audits de conformité.

## Forwarding — envoi vers d'autres destinations

```ini
[Journal]
# Transmettre à syslog (rsyslog, syslog-ng…)
ForwardToSyslog=no

# Transmettre au buffer noyau kmsg (/dev/kmsg)
ForwardToKMsg=no

# Afficher sur la console (utile pour le debug boot)
ForwardToConsole=no
# TTY cible si ForwardToConsole=yes
TTYPath=/dev/console

# Afficher les messages critiques sur tous les terminaux connectés (wall)
ForwardToWall=yes
```

### Cohabitation avec rsyslog ou syslog-ng

Si `rsyslog` ou `syslog-ng` est présent sur la machine, deux configurations sont possibles :

**Option A — journald collecte tout, syslog lit depuis le journal (recommandé)**

```ini
# journald.conf
ForwardToSyslog=no
```

rsyslog utilise son module `imjournal` pour lire directement depuis le journal sans duplication.

**Option B — double pipeline (compatibilité maximale)**

```ini
# journald.conf
ForwardToSyslog=yes
```

journald retransmet chaque message sur le socket `/run/systemd/journal/syslog`. Attention à la duplication potentielle dans les fichiers syslog.

## Niveaux de log maximaux par destination

```ini
[Journal]
# Niveau maximum stocké dans le journal
MaxLevelStore=debug

# Niveau maximum retransmis à syslog
MaxLevelSyslog=warning

# Niveau maximum retransmis à kmsg
MaxLevelKMsg=notice

# Niveau maximum retransmis à la console
MaxLevelConsole=info

# Niveau maximum diffusé via wall
MaxLevelWall=emerg
```

Cela permet par exemple de stocker tous les niveaux dans le journal persistant tout en n'envoyant que les erreurs vers syslog.

## Paramètres réseau (journal distant entrant)

Ces paramètres concernent `systemd-journald` lorsqu'il est configuré pour recevoir des logs depuis le réseau (mode journal distant). La configuration détaillée de `systemd-journal-remote` et `systemd-journal-upload` est documentée dans [Journal centralisé](journald-remote.md).

## Recettes de configuration par profil

### Serveur de production minimal

```ini
# /etc/systemd/journald.conf.d/production.conf
[Journal]
Storage=persistent
Compress=yes
Seal=yes
SystemMaxUse=4G
SystemKeepFree=2G
SystemMaxFileSize=256M
SystemMaxFiles=50
MaxRetentionSec=3months
RateLimitIntervalSec=30s
RateLimitBurst=20000
ForwardToSyslog=no
ForwardToWall=yes
```

### Container ou VM légère

```ini
# /etc/systemd/journald.conf.d/container.conf
[Journal]
Storage=volatile
Compress=yes
RuntimeMaxUse=64M
RuntimeKeepFree=32M
MaxRetentionSec=1week
RateLimitIntervalSec=30s
RateLimitBurst=1000
ForwardToSyslog=no
ForwardToWall=no
```

### Debug temporaire (à ne pas laisser en production)

```ini
# /etc/systemd/journald.conf.d/debug.conf
[Journal]
MaxLevelStore=debug
RateLimitIntervalSec=0
ForwardToConsole=yes
TTYPath=/dev/tty12
```

```bash
# Activer temporairement, puis supprimer après diagnostic
sudo systemctl restart systemd-journald
# ... investigation ...
sudo rm /etc/systemd/journald.conf.d/debug.conf
sudo systemctl restart systemd-journald
```

## Vérifier la configuration effective

```bash
# Valeurs finales après fusion de tous les fichiers .conf.d
systemd-analyze cat-config systemd/journald.conf

# Afficher les paramètres du journal en cours d'exécution
journalctl --header

# Espace occupé
journalctl --disk-usage

# Statut du démon
systemctl status systemd-journald
```

## Appliquer un changement sans reboot

```bash
# Redémarrage propre de journald (peut provoquer une courte interruption de collecte)
sudo systemctl restart systemd-journald

# Rechargement de configuration (sans interruption, pour certains paramètres)
sudo systemctl reload systemd-journald
```

!!! warning "Changement de `Storage=`"
    Passer de `volatile` à `persistent` (ou l'inverse) nécessite de créer ou supprimer `/var/log/journal/` et de redémarrer `systemd-journald`. Un simple `reload` ne suffit pas.

## Voir aussi

- [Journal et logging](index.md) — vue d'ensemble et commandes `journalctl`
- [Journal centralisé](journald-remote.md) — `systemd-journal-remote` et `systemd-journal-upload`
- `man journald.conf` — référence complète de toutes les options
- `man systemd-journald.service` — documentation du démon
