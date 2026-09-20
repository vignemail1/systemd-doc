# Configuration de systemd-udevd

## Paramètres du démon

Les paramètres sont configurés dans `/etc/udev/udev.conf` :

```ini
[udev]
udev_log=info
children_max=128
resolve_names=never
```

Selon la version de systemd, les options et niveaux de journalisation disponibles peuvent différer. Consulter `man udev.conf` sur la machine cible.

## Règles locales

Créer un fichier dont le préfixe est supérieur à celui des règles génériques, par exemple `99-local.rules`, mais choisir le plus petit préfixe possible qui garantit l'ordre voulu. Tester avant de remplacer une règle fournisseur.

```bash
udevadm control --reload
udevadm trigger --subsystem-match=block
```

`udevadm control --reload` recharge les règles pour les nouveaux événements ; il ne rejoue pas automatiquement tous les événements déjà traités.

## Limites et performances

Les règles doivent éviter les commandes externes coûteuses. Pour une opération complexe, déléguer à un service systemd déclenché par udev. Contrôler les limites d'enfants et les événements en attente avant d'augmenter `children_max`.

## Permissions et sécurité

Les permissions udev s'appliquent aux nœuds de périphériques. Elles ne remplacent pas les autorisations polkit, les groupes Unix ni les contrôles d'accès du noyau. Donner l'accès à un périphérique peut permettre des opérations privilégiées.
