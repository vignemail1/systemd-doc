# systemd-delta

`systemd-delta` affiche les fichiers d'unités et de configuration qui remplacent ou modifient les fichiers fournis par systemd ou par les paquets.

```bash
systemd-delta
systemd-delta --type=extended
systemd-delta systemd/system
```

C'est un outil utile après une personnalisation, pour repérer les overrides dans `/etc`, les fichiers masqués et les différences avec les valeurs par défaut. Pour inspecter une unité fusionnée, utiliser plutôt :

```bash
systemctl cat nginx.service
systemctl show nginx.service
```
