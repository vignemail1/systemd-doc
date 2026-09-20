# systemd-notify

`systemd-notify` permet à un service d'envoyer à systemd des informations d'état, notamment lorsqu'il est prêt ou lorsqu'il signale une progression.

## Service de type notify

```ini
[Service]
Type=notify
ExecStart=/usr/local/bin/mon-daemon
NotifyAccess=main
```

Le programme peut notifier sa disponibilité :

```bash
systemd-notify --ready
```

Autres messages courants :

```bash
systemd-notify STATUS="Initialisation terminée"
systemd-notify WATCHDOG=1
systemd-notify STOPPING=1
```

Pour un script qui ne sait pas parler au protocole, `Type=simple` ou `Type=exec` est souvent plus approprié. Ne pas utiliser `Type=notify` sans notification effective : systemd peut alors considérer le service comme non prêt.
