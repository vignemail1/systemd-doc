# Comparaison avec SysVinit

Pour comprendre les avantages de systemd, il est utile de le comparer avec son prédécesseur SysVinit. Cette comparaison met en lumière les améliorations apportées par systemd et les raisons de son adoption massive.

## Vue d'ensemble

| Aspect | SysVinit | systemd |
| -------- | ---------- | ---------- |
| **Année de création** | 1983 | 2010 |
| **Langage principal** | Scripts Shell | C |
| **Type de démarrage** | Séquentiel | Parallèle |
| **Configuration** | Scripts complexes | Fichiers déclaratifs |
| **Gestion des logs** | Syslog externe | Journal intégré |
| **Supervision** | Aucune native | Intégrée |
| **Temps de boot** | 30-60s typique | 5-15s typique |
| **Activation à la demande** | Non | Oui |

## Démarrage des services

### SysVinit : approche séquentielle

Avec SysVinit, les services démarrent l'un après l'autre selon un ordre défini par des nombres :

```bash
# Répertoire /etc/rc3.d/
S01networking
S02syslog
S03sshd
S04apache2
S05postgresql
```

**Problèmes** :

- Aucune parallélisation possible
- Un service lent bloque tous les suivants
- Difficulté à gérer les dépendances réelles
- Ordre rigide peu flexible

**Exemple** : Si le réseau met 10 secondes à démarrer, tous les services suivants doivent attendre.

### systemd : parallélisation intelligente

systemd analyse les dépendances et démarre les services en parallèle quand c'est possible :

```ini
[Unit]
Description=Apache Web Server
After=network.target
Requires=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/httpd
```

**Avantages** :

- Démarrage simultané des services indépendants
- Exploitation des processeurs multi-cœurs
- Dépendances explicites et vérifiées
- Activation progressive selon les besoins

**Résultat** : Réduction typique du temps de boot de 60-80%.

## Scripts vs fichiers d'unités

### SysVinit : scripts shell complexes

Exemple de script init SysVinit pour un service web :

```bash
#!/bin/bash
# /etc/init.d/mywebapp

case "$1" in
  start)
    echo "Starting mywebapp..."
    /usr/bin/mywebapp --daemon --pid-file=/var/run/mywebapp.pid
    ;;
  stop)
    echo "Stopping mywebapp..."
    kill $(cat /var/run/mywebapp.pid)
    ;;
  restart)
    $0 stop
    sleep 2
    $0 start
    ;;
  status)
    if [ -f /var/run/mywebapp.pid ]; then
      echo "mywebapp is running"
    else
      echo "mywebapp is stopped"
    fi
    ;;
esac
```

**Problèmes** :

- Nécessite des compétences en scripting bash
- Gestion manuelle des PID files
- Pas de supervision intégrée
- Code répétitif entre services
- Erreurs de syntaxe possibles

### systemd : configuration déclarative

Équivalent systemd :

```ini
[Unit]
Description=My Web Application
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/mywebapp
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Avantages** :

- Configuration simple et lisible
- Pas de code procédural
- Supervision automatique (Restart=)
- Pas de gestion manuelle des PIDs
- Syntaxe vérifiable

## Gestion des dépendances

### SysVinit : ordre numérique

```bash
# /etc/rc3.d/
S10networking   # Démarre en premier
S20sshd        # Démarre après networking
S30apache      # Démarre après sshd
```

**Limitations** :

- Pas de vérification des dépendances réelles
- Ordre fixe même si un service n'est pas nécessaire
- Difficile de comprendre pourquoi un ordre est choisi
- Conflits de numérotation entre packages

### systemd : dépendances explicites

```ini
[Unit]
Description=Apache Web Server
After=network.target postgresql.service
Requires=network.target
Wants=postgresql.service
```

**Avantages** :

- Relations claires et documentées
- Vérification automatique
- Optimisation possible du graphe de dépendances
- Flexibilité (Requires vs Wants)

## Gestion des logs

### SysVinit : syslog externe

```bash
# Les services loggent via syslog
logger -t myapp "Application started"

# Consultation
tail -f /var/log/syslog
grep myapp /var/log/syslog
```

**Problèmes** :

- Logs texte non structurés
- Rotation manuelle nécessaire
- Pas de métadonnées (PID, timestamp précis)
- Recherche basique (grep)
- Perte possible de logs au boot

### systemd : journal intégré

```bash
# Les services loggent automatiquement
# Consultation avec journalctl
journalctl -u myapp
journalctl -u myapp --since "1 hour ago"
journalctl -u myapp -p err
journalctl -f  # Suivi temps réel
```

**Avantages** :

- Logs structurés avec métadonnées
- Indexation pour recherche rapide
- Filtrage puissant
- Rotation automatique
- Capture précoce des logs de boot
- Corrélation entre services

## Supervision des services

### SysVinit : aucune supervision native

Avec SysVinit, la supervision nécessite des outils externes :

- **monit** : Surveillance et redémarrage
- **supervisor** : Gestion de processus
- **daemontools** : Supervision de daemons

```bash
# Script cron pour vérifier qu'un service tourne

*/5 * * * * /etc/init.d/myapp status || /etc/init.d/myapp start

```

**Problèmes** :

- Configuration supplémentaire requise
- Pas de standard
- Surveillance imparfaite
- Délai de détection

### systemd : supervision intégrée

```ini
[Service]
Type=simple
Restart=on-failure
RestartSec=5s
StartLimitBurst=3
StartLimitIntervalSec=60s
```

**Avantages** :

- Redémarrage automatique configuré
- Protection contre les boucles de restart
- Détection instantanée des crashes
- Logs détaillés des échecs
- Aucun outil externe nécessaire

## Activation à la demande

### SysVinit : démarrage fixe

Tous les services activés démarrent au boot, qu'ils soient utilisés ou non.

```bash
# Activation
update-rc.d myservice defaults

# Le service démarre à chaque boot
```

**Problèmes** :

- Services inutilisés consomment des ressources
- Temps de boot allongé
- Pas de démarrage automatique à la demande

### systemd : activation dynamique

systemd peut démarrer des services uniquement quand ils sont sollicités :

**Socket activation** :

```ini
# sshd.socket
[Socket]
ListenStream=22

# sshd.service démarre automatiquement à la première connexion
```

**Path activation** :

```ini
# Démarre un service quand un fichier est créé
[Path]
PathExists=/tmp/trigger
```

**Avantages** :

- Réduction de la consommation mémoire
- Boot plus rapide
- Services démarrés uniquement si nécessaires

## Performance au démarrage

### Comparaison réelle

Mesure sur un serveur typique (4 cores, SSD) :

```bash
# SysVinit
$ systemd-analyze time
Startup finished in 45.234s (kernel) + 58.721s (userspace) = 103.955s

# systemd
$ systemd-analyze time
Startup finished in 4.521s (kernel) + 8.234s (userspace) = 12.755s
```

**Gain** : ~8x plus rapide avec systemd.

### Analyse détaillée avec systemd

```bash
# Identifier les services lents
$ systemd-analyze blame

5.234s postgresql.service
3.112s nginx.service
1.892s networking.service

```

Cette analyse n'existe pas avec SysVinit.

## Commandes équivalentes

| Action | SysVinit | systemd |
| -------- | ---------- | ---------- |
| Démarrer un service | `service myapp start` | `systemctl start myapp` |
| Arrêter un service | `service myapp stop` | `systemctl stop myapp` |
| Redémarrer | `service myapp restart` | `systemctl restart myapp` |
| Status | `service myapp status` | `systemctl status myapp` |
| Activer au boot | `update-rc.d myapp defaults` | `systemctl enable myapp` |
| Désactiver | `update-rc.d myapp remove` | `systemctl disable myapp` |
| Lister services | `service --status-all` | `systemctl list-units` |
| Voir les logs | `tail /var/log/syslog` | `journalctl -u myapp` |
| Recharger config | N/A | `systemctl daemon-reload` |

## Runlevels vs Targets

### SysVinit : runlevels

```bash
# Runlevels traditionnels
0 - Halt
1 - Single user
2 - Multi-user sans réseau
3 - Multi-user avec réseau
4 - Inutilisé
5 - Multi-user graphique
6 - Reboot

# Changer de runlevel
init 3
```

### systemd : targets

```bash
# Targets équivalents
poweroff.target       # Arrêt
rescue.target         # Mode rescue
multi-user.target     # Multi-utilisateur
graphical.target      # Mode graphique
reboot.target         # Redémarrage

# Changer de target
systemctl isolate multi-user.target
```

**Avantages systemd** :

- Targets plus flexibles et composables
- Possibilité de créer des targets personnalisés
- Dépendances explicites entre targets

## Migration SysVinit vers systemd

### Compatibilité

systemd maintient une compatibilité partielle avec SysVinit :

```bash
# Ces commandes fonctionnent encore
service myapp start      # Redirigé vers systemctl
/etc/init.d/myapp start  # Script appelé si existe
```

### Conversion d'un script init

Principes de conversion :

1. Créer un fichier d'unité `.service`
2. Déclarer les dépendances explicitement
3. Configurer le type de service
4. Définir les commandes exec
5. Configurer le redémarrage automatique

**Outil** : `systemd-analyze verify` vérifie la validité du fichier d'unité.

## Conclusion : pourquoi systemd a gagné

Les avantages décisifs de systemd :

1. **Performance** : Boot 5-10x plus rapide
2. **Fiabilité** : Supervision intégrée et gestion des échecs
3. **Simplicité** : Configuration déclarative vs scripts complexes
4. **Fonctionnalités** : Journal, activation à la demande, isolation
5. **Modernité** : Exploitation des capacités kernel récentes
6. **Standardisation** : Base commune entre distributions

Malgré les controverses initiales, les bénéfices pratiques de systemd ont convaincu la quasi-totalité de l'écosystème Linux.
