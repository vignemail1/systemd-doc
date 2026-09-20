# systemd-cat

`systemd-cat` relie la sortie standard et la sortie d'erreur d'une commande au journal systemd. C'est utile pour intégrer rapidement la sortie d'un script ou d'un programme à `journald`.

## Utilisation

```bash
systemd-cat --identifier=mon-script ./script.sh
```

Lire ensuite les messages :

```bash
journalctl -t mon-script
```

Le niveau peut être indiqué dans le flux avec le préfixe syslog approprié, ou configuré avec les options disponibles dans la version installée. Pour journaliser une commande sans la modifier :

```bash
systemd-cat -t sauvegarde --level-prefix /usr/local/bin/sauvegarde
```

## Avec un service

Pour une unité systemd, préférer généralement les directives natives :

```ini
[Service]
ExecStart=/usr/local/bin/mon-programme
SyslogIdentifier=mon-programme
StandardOutput=journal
StandardError=journal
```

`systemd-cat` est surtout pratique pour les commandes lancées manuellement, les tests et les scripts externes.
