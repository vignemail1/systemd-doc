# systemd-path

`systemd-path` affiche les chemins importants utilisés par systemd : répertoire des unités système, configuration, données persistantes, fichiers temporaires et chemins utilisateur.

```bash
systemd-path
systemd-path systemd-system-unit
systemd-path systemd-system-conf
```

La commande évite de supposer qu'un chemin est toujours `/lib` ou `/usr/lib`, ce qui est particulièrement utile sur les distributions ayant adopté `/usr` fusionné.
