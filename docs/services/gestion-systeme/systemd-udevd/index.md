# systemd-udevd

`systemd-udevd` reçoit les événements du noyau et applique les règles udev pour nommer les périphériques, créer des liens symboliques, définir des permissions et déclencher des actions.

Le démon est généralement lancé par `systemd-udev-trigger.service` et fonctionne avec `systemd-udev-settle.service` dans les cas qui l'exigent.

## Outils

```bash
udevadm monitor --kernel --udev
udevadm info --query=all --name=/dev/sda
udevadm test /sys/class/net/eth0
udevadm trigger
```

!!! warning
    Les règles doivent rester rapides et déterministes. Ne pas lancer de traitements longs directement depuis une règle udev.

## Emplacements

- `/usr/lib/udev/rules.d/` : règles fournies par les paquets.
- `/run/udev/rules.d/` : règles générées à l'exécution.
- `/etc/udev/rules.d/` : règles administrateur, prioritaires.

Les fichiers sont évalués dans l'ordre lexicographique ; un fichier `/etc/udev/rules.d/` portant le même nom peut masquer une règle fournisseur.
