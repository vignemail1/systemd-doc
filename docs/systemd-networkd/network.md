# Fichiers `.network`

Un fichier `.network` décrit la configuration d'une interface déjà existante. Il est associé à une interface par la section `[Match]`, puis configure cette interface avec `[Network]`, `[Address]`, `[Route]` et d'autres sections.

## Exemple DHCP

```ini
# /etc/systemd/network/20-wired.network
[Match]
Name=en*

[Network]
DHCP=yes
IPv6AcceptRA=yes
```

## Exemple adresse statique

```ini
[Match]
Name=eth0

[Network]
Address=192.0.2.10/24
Gateway=192.0.2.1
DNS=192.0.2.1
DNS=2001:db8::53

[Route]
Destination=198.51.100.0/24
Gateway=192.0.2.254
```

`Gateway=` reste pratique pour une route par défaut. `[Route]` permet de décrire précisément destination, passerelle, métrique et table de routage.

## Sections courantes

- `[Match]` : `Name=`, `MACAddress=`, `Type=`, `Driver=` ;
- `[Link]` : `RequiredForOnline=`, `MACAddressPolicy=` ;
- `[Network]` : `Address=`, `DHCP=`, `IPv6AcceptRA=`, `DNS=`, `Domains=`, `Bridge=`, `Bond=`, `VLAN=` ;
- `[Address]` : adresse, `Peer=`, `PreferredLifetime=` ;
- `[Route]` : `Destination=`, `Gateway=`, `Metric=`, `Table=` ;
- `[DHCPv4]` et `[DHCPv6]` : options propres au client DHCP.

## VLAN et bridge

```ini
# 10-bridge.netdev
[NetDev]
Name=br0
Kind=bridge

# 20-bridge.network
[Match]
Name=br0

[Network]
Address=192.0.2.20/24

# 30-port.network
[Match]
Name=eth0

[Network]
Bridge=br0
```

!!! tip
    Préfixer les fichiers par des numéros (`10-`, `20-`, `30-`) rend l'ordre de sélection explicite.
