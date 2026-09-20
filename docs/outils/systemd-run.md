# systemd-run

`systemd-run` crée et démarre une unité transitoire. Il permet d'exécuter une commande avec les limites, la journalisation et l'isolation de systemd, sans écrire immédiatement un fichier d'unité.

## Exécuter une commande

```bash
systemd-run --unit=maintenance --property=CPUQuota=50% /usr/local/bin/maintenance
```

Voir son état :

```bash
systemctl status maintenance.service
journalctl -u maintenance.service
```

## Tâche ponctuelle

```bash
systemd-run --on-active=10min --unit=rapport.service /usr/local/bin/rapport
```

Pour une commande utilisateur :

```bash
systemd-run --user --scope --quiet make test
```

Options utiles : `--description=`, `--remain-after-exit`, `--service-type=oneshot`, `--working-directory=`, `--setenv=` et `--property=`. Les propriétés disponibles dépendent de la version de systemd.
