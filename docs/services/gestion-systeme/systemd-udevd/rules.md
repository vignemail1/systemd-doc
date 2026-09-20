# Règles udev

Une règle est composée de correspondances et d'affectations séparées par des virgules.

```udev
# /etc/udev/rules.d/70-local-net.rules
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="02:00:00:12:34:56", NAME="lan0"
```

## Correspondances courantes

- `ACTION==` : `add`, `remove`, `change`.
- `SUBSYSTEM==` : sous-système, par exemple `block`, `net`, `usb`.
- `KERNEL==` : nom noyau avec motifs.
- `ATTR{...}==` : attribut sysfs.
- `ENV{...}==` : variable d'environnement udev.
- `DRIVERS==` : pilote attaché.
- `TAG==` : étiquette existante.

## Affectations courantes

- `NAME=` : nom du périphérique réseau ou fichier de périphérique selon le contexte.
- `SYMLINK+=` : lien symbolique sous `/dev`.
- `OWNER=`, `GROUP=`, `MODE=` : propriété et permissions.
- `TAG+=` : ajouter une étiquette.
- `ENV{clé}=` : définir une variable.
- `RUN+=` : action courte après traitement.

Exemple pour un périphérique USB stable :

```udev
SUBSYSTEM=="usb", ATTR{idVendor}=="1d6b", ATTR{idProduct}=="0002", SYMLINK+="usb-root-hub", TAG+="systemd"
```

Préférer les attributs stables (`serial`, identifiant matériel) aux chemins physiques susceptibles de changer.

## Services systemd

Pour déclencher un service, utiliser de préférence les propriétés `TAG+="systemd"` et `ENV{SYSTEMD_WANTS}="mon-service.service"`, avec prudence pour éviter les boucles et démarrages répétés.

```udev
ACTION=="add", SUBSYSTEM=="block", ENV{ID_FS_UUID}=="...", ENV{SYSTEMD_WANTS}="backup-disk.service"
```
