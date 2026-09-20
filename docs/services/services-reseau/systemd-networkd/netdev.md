# Fichiers `.netdev`

Un fichier `.netdev` crée une interface virtuelle. La section `[NetDev]` définit son nom et son type ; des sections supplémentaires configurent ce type.

## Bridge

```ini
[NetDev]
Name=br0
Kind=bridge
```

## VLAN

```ini
[NetDev]
Name= vlan100
Kind=vlan

[VLAN]
Id=100
```

Le nom ne doit normalement pas contenir d'espace :

```ini
[NetDev]
Name=vlan100
Kind=vlan

[VLAN]
Id=100
```

Puis rattacher le VLAN à une interface dans un fichier `.network` :

```ini
[Match]
Name=eth0

[Network]
VLAN=vlan100
```

## Bond

```ini
[NetDev]
Name=bond0
Kind=bond

[Bond]
Mode=active-backup
```

```ini
[Match]
Name=eno1 eno2

[Network]
Bond=bond0
```

## Types fréquents

`bridge`, `bond`, `vlan`, `macvlan`, `ipvlan`, `vxlan`, `vrf`, `dummy`, `veth`, `wireguard` et des tunnels IP selon la version de systemd et du noyau.

!!! warning
    Vérifier les types disponibles avec la documentation de la version installée (`man systemd.netdev`). Les options évoluent entre versions.
