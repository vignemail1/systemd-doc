# Diagnostic de systemd-udevd

## Observer un événement

```bash
udevadm monitor --kernel --udev --property
```

Brancher ou débrancher le périphérique et comparer les propriétés kernel et udev.

## Inspecter un périphérique

```bash
udevadm info --query=property --name=/dev/sda
udevadm info --attribute-walk --name=/dev/sda
```

L'attribut-walk aide à trouver un attribut stable dans l'arbre parent.

## Tester une règle

```bash
udevadm test --action=add /sys/class/block/sda
udevadm test-builtin net_id /sys/class/net/eth0
```

La sortie indique les règles parcourues et les affectations produites ; elle ne doit pas être confondue avec une création réelle du périphérique.

## Recharger et rejouer

```bash
udevadm control --reload
udevadm trigger --name-match=sda
```

Limiter `trigger` avec `--subsystem-match`, `--property-match` ou `--name-match` afin d'éviter des effets de bord.

## Journaux

```bash
journalctl -b -u systemd-udevd
udevadm control --log-priority=debug
```

Rétablir ensuite un niveau normal avec `udevadm control --log-priority=info`.

## Échecs courants

- La règle ne correspond pas : vérifier `SUBSYSTEM`, `ACTION`, le chemin sysfs et les attributs.
- Le nom n'est pas appliqué : une règle ultérieure peut réécrire la propriété.
- Le lien n'apparaît pas : vérifier `SYMLINK+=`, les permissions et les événements `add`.
- Un service est lancé plusieurs fois : rendre le service idempotent et limiter `SYSTEMD_WANTS`.
