# Timers (.timer)

Les unités `.timer` permettent de planifier l'exécution de services à des moments spécifiques. Elles constituent une alternative moderne et puissante à cron.

## Avantages par rapport à cron

- **Intégration systemd** : Logs dans journald, gestion unifiée
- **Dépendances** : Peut dépendre d'autres unités
- **Flexibilité** : Planification relative (après boot, après activation...)
- **Précision** : Gestion des timers manqués (Persistent=)
- **Calendar expressions** : Syntaxe riche et lisible
- **Monitoring** : État visible avec systemctl

## Structure d'un timer

```ini
[Unit]
Description=Daily Backup Timer

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

## Section [Timer]

### Types de déclenchement

Il existe deux catégories de timers :

#### Timers monotoniques (relatifs)

Déclenchés relativement à un événement :

**OnActiveSec**

: Après l'activation du timer

```ini
OnActiveSec=5min
```

**OnBootSec**

: Après le démarrage du système

```ini
OnBootSec=10min
```

**OnStartupSec**

: Après le démarrage de systemd (user mode)

```ini
OnStartupSec=1h
```

**OnUnitActiveSec**

: Après la dernière activation du service

```ini
OnUnitActiveSec=1h  # Toutes les heures après la dernière exécution
```

**OnUnitInactiveSec**

: Après la dernière désactivation du service

```ini
OnUnitInactiveSec=30min
```

#### Timers en temps réel (absolus)

Déclenchés à des moments précis :

**OnCalendar**

: Selon un calendrier (jours, heures...)

```ini
OnCalendar=Mon *-*-* 02:00:00  # Tous les lundis à 2h
OnCalendar=daily                # Chaque jour à 00:00
OnCalendar=weekly               # Chaque lundi à 00:00
OnCalendar=monthly              # Le 1er de chaque mois à 00:00
OnCalendar=*-*-* 04:00:00       # Chaque jour à 4h
OnCalendar=*:0/15               # Toutes les 15 minutes
```

### Format OnCalendar

La syntaxe `OnCalendar` est très flexible :

```text
Jour Mois Année Heure:Minute:Seconde
```

#### Exemples

```ini
# Raccourcis
OnCalendar=minutely        # Chaque minute
OnCalendar=hourly          # Chaque heure
OnCalendar=daily           # Chaque jour à 00:00
OnCalendar=weekly          # Chaque lundi à 00:00
OnCalendar=monthly         # Le 1er du mois à 00:00
OnCalendar=quarterly       # Le 1er du trimestre
OnCalendar=yearly          # Le 1er janvier

# Heures spécifiques
OnCalendar=*-*-* 04:00:00       # Chaque jour à 4h
OnCalendar=*-*-* 09:30:00       # Chaque jour à 9h30
OnCalendar=*-*-* 12,18:00:00    # Midi et 18h

# Jours de la semaine
OnCalendar=Mon *-*-* 00:00:00   # Chaque lundi
OnCalendar=Mon,Fri *-*-* 08:00  # Lundi et vendredi à 8h
OnCalendar=Mon..Fri *-*-* 09:00 # Du lundi au vendredi à 9h

# Jours du mois
OnCalendar=*-*-01 00:00:00      # Le 1er de chaque mois
OnCalendar=*-01,07-01 00:00:00  # 1er janvier et 1er juillet
OnCalendar=*-*-01..07 00:00:00  # Les 7 premiers jours du mois

# Intervalles
OnCalendar=*:0/10               # Toutes les 10 minutes
OnCalendar=*:*/5                # Toutes les 5 minutes
OnCalendar=*-*-* *:00,30:00     # Toutes les 30 minutes

# Plusieurs horaires
OnCalendar=Mon,Wed,Fri 08:00:00
OnCalendar=Tue,Thu 10:00:00
```

#### Tester une expression calendar

```bash
# Vérifier quand une expression sera déclenchée
systemd-analyze calendar "Mon,Fri *-*-* 09:00:00"

# Output:
#   Original form: Mon,Fri *-*-* 09:00:00
#   Normalized form: Mon,Fri *-*-* 09:00:00
#   Next elapse: Mon 2026-02-09 09:00:00 CET
#          From now: 18h left
```

### Options de configuration

**AccuracySec**

: Précision du timer (permet d'optimiser la consommation)

```ini
AccuracySec=1min   # Défaut
AccuracySec=1s     # Précision maximale
AccuracySec=1h     # Moins précis, économise la batterie
```

**RandomizedDelaySec**

: Ajoute un délai aléatoire avant déclenchement

```ini
RandomizedDelaySec=5min  # Délai aléatoire jusqu'à 5min
```

Utile pour :

- Éviter que plusieurs machines se synchronisent exactement
- Étaler la charge sur un serveur

**Persistent**

: Exécute le service si un déclenchement a été manqué (machine éteinte)

```ini
Persistent=true    # Rattrape les exécutions manquées
Persistent=false   # Ignore les exécutions manquées (défaut)
```

**WakeSystem**

: Réveille le système en veille pour exécuter

```ini
WakeSystem=true
```

**RemainAfterElapse**

: Garde le timer actif après déclenchement

```ini
RemainAfterElapse=false  # Défaut: le timer reste actif
```

**Unit**

: Service à activer (par défaut : même nom sans .timer)

```ini
Unit=myservice.service
```

## Exemples complets

### Sauvegarde quotidienne

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily Backup Timer
Requires=backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Backup Service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
User=backup
```

Activation :

```bash
systemctl enable backup.timer
systemctl start backup.timer

# Vérifier
systemctl list-timers
```

### Nettoyage hebdomadaire

```ini
# /etc/systemd/system/cleanup.timer
[Unit]
Description=Weekly Cleanup

[Timer]
OnCalendar=Sun 03:00:00
Persistent=true
RandomizedDelaySec=1h

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/cleanup.service
[Unit]
Description=Cleanup Old Files

[Service]
Type=oneshot
ExecStart=/usr/bin/find /tmp -mtime +7 -delete
ExecStart=/usr/bin/find /var/log -name '*.old' -delete
```

### Monitoring toutes les 5 minutes

```ini
# /etc/systemd/system/monitor.timer
[Unit]
Description=Monitor System Every 5 Minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
AccuracySec=1s

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/monitor.service
[Unit]
Description=System Monitoring

[Service]
Type=oneshot
ExecStart=/usr/local/bin/check-system.sh
```

### Synchronisation horaire

```ini
# /etc/systemd/system/sync-time.timer
[Unit]
Description=Hourly Time Synchronization

[Timer]
OnCalendar=hourly
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
```

### Tâche en semaine

```ini
# /etc/systemd/system/workday-task.timer
[Unit]
Description=Workday Task Timer

[Timer]
OnCalendar=Mon..Fri 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Multiple schedules

```ini
# /etc/systemd/system/multi-schedule.timer
[Unit]
Description=Multiple Schedule Timer

[Timer]
# Tous les jours à 6h
OnCalendar=*-*-* 06:00:00
# Et tous les jours à 18h
OnCalendar=*-*-* 18:00:00
# Et toutes les heures en journée
OnCalendar=Mon..Fri 09..17:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

## Gestion des timers

### Commandes de base

```bash
# Lister tous les timers
systemctl list-timers
systemctl list-timers --all  # Inclut les inactifs

# Démarrer un timer
systemctl start backup.timer

# Activer au boot
systemctl enable backup.timer

# Voir l'état
systemctl status backup.timer

# Voir quand il va se déclencher
systemctl list-timers backup.timer

# Forcer l'exécution immédiate du service
systemctl start backup.service
```

### Informations détaillées

```bash
# Configuration complète
systemctl show backup.timer

# Propriétés importantes
systemctl show backup.timer -p NextElapseUSecRealtime
systemctl show backup.timer -p LastTriggerUSec
```

### Output de list-timers

```bash
$ systemctl list-timers

NEXT                         LEFT     LAST                         PASSED  UNIT              ACTIVATES
Mon 2026-02-09 03:00:00 CET  8h left  Sun 2026-02-08 03:00:00 CET  16h ago cleanup.timer     cleanup.service
Mon 2026-02-09 00:00:00 CET  5h left  Sun 2026-02-08 00:00:00 CET  19h ago backup.timer      backup.service
```

## Cas d'usage avancés

### Redémarrage périodique d'un service

```ini
# restart-app.timer
[Unit]
Description=Restart Application Every 6 Hours

[Timer]
OnBootSec=6h
OnUnitActiveSec=6h

[Install]
WantedBy=timers.target
```

```ini
# restart-app.service
[Unit]
Description=Restart Application Service

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl restart myapp.service
```

### Healthcheck avec retry

```ini
# healthcheck.timer
[Unit]
Description=Application Health Check

[Timer]
OnBootSec=1min
OnUnitActiveSec=30s
AccuracySec=1s

[Install]
WantedBy=timers.target
```

```ini
# healthcheck.service
[Unit]
Description=Health Check Service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/healthcheck.sh
Restart=on-failure
RestartSec=5s
StartLimitBurst=3
```

### Rotation de logs personnalisée

```ini
# logrotate.timer
[Unit]
Description=Daily Log Rotation

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=12h

[Install]
WantedBy=timers.target
```

## Migration depuis cron

### Conversion cron → systemd

**Crontab** :

```cron
# Tous les jours à 2h30
30 2 * * * /usr/local/bin/backup.sh

# Toutes les 15 minutes

*/15 * * * * /usr/local/bin/check.sh

# Tous les lundis à 8h
0 8 * * 1 /usr/local/bin/weekly.sh
```

**systemd equivalents** :

```ini
# backup.timer
[Timer]
OnCalendar=*-*-* 02:30:00

# check.timer
[Timer]
OnCalendar=*:0/15

# weekly.timer
[Timer]
OnCalendar=Mon *-*-* 08:00:00
```

### Avantages de la migration

- **Logs centralisés** : `journalctl -u backup.service`
- **Gestion d'échecs** : Restart policies, notifications
- **Visibilité** : `systemctl list-timers`
- **Dépendances** : Peut dépendre d'autres services
- **Isolation** : Environnement contrôlé

## Débogage

### Le timer ne se déclenche pas

Vérifications :

```bash
# Le timer est-il actif ?
systemctl status backup.timer

# Quand est le prochain déclenchement ?
systemctl list-timers backup.timer

# Le service peut-il se lancer ?
systemctl start backup.service

# Logs du timer
journalctl -u backup.timer

# Logs du service
journalctl -u backup.service
```

### Tester une expression calendar

```bash
# Valider la syntaxe
systemd-analyze calendar "Mon..Fri 09:00"

# Voir les prochaines occurrences
systemd-analyze calendar "*/15 * * * *" --iterations=10
```

### Vérifier la configuration

```bash
systemd-analyze verify backup.timer
systemd-analyze verify backup.service
```

## Monitoring et alertes

### Surveiller les échecs

```ini
# backup.service avec notification
[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
OnFailure=failure-notification@%n.service
```

```ini
# failure-notification@.service
[Unit]
Description=Send notification for %i

[Service]
Type=oneshot
ExecStart=/usr/local/bin/send-alert.sh "Service %i failed"
```

### Métriques

```bash
# Dernière exécution
systemctl show backup.timer -p LastTriggerUSec

# Prochaine exécution
systemctl show backup.timer -p NextElapseUSecRealtime

# Nombre d'exécutions
journalctl -u backup.service --since "1 month ago" | grep -c "Finished"
```

## Bonnes pratiques

1. **Toujours utiliser Persistent=true** pour les tâches critiques
2. **Ajouter RandomizedDelaySec** pour les tâches réseau
3. **Définir des timeouts** dans le service
4. **Logger correctement** avec StandardOutput=journal
5. **Tester les expressions** avec `systemd-analyze calendar`
6. **Monitorer les échecs** avec OnFailure=
7. **Documenter** : Description claire dans [Unit]

Les timers systemd sont un remplacement puissant et moderne de cron, offrant une meilleure intégration avec le système et des capacités de gestion avancées.
