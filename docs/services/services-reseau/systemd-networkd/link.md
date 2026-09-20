# Fichiers `.link`

Un fichier `.link` applique des propriétés très tôt, lorsqu'une interface est découverte par systemd-udevd. Il sert notamment à définir un nom stable, une adresse MAC ou une politique de nommage.

## Renommer une interface par son adresse MAC

```ini
# /etc/systemd/network/10-lan.link
[Match]
MACAddress=52:54:00:12:34:56

[Link]
Name=lan0
```

## Désactiver la politique de nommage MAC

```ini
[Match]
OriginalName=*

[Link]
MACAddressPolicy=persistent
```

Les fichiers `.link` sont évalués lexicalement ; le premier fichier correspondant est utilisé. Éviter de choisir un nom déjà occupé et tester depuis la console lorsque le changement concerne l'interface distante.

## Différence entre `.link` et `.network`

- `.link` configure l'identité et les propriétés bas niveau de l'interface ;
- `.network` configure l'adressage, le routage et les relations réseau ;
- `.netdev` crée une interface virtuelle.

Après modification, un redémarrage de l'interface ou du système peut être nécessaire, car les fichiers `.link` s'appliquent lors de l'apparition de l'interface.
