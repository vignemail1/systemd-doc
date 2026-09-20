# Les unités systemd

Une unité est une ressource gérée par systemd. Chaque type d'unité possède une extension et un rôle propres.

## Types d'unités

- [Services (`.service`)](services.md)
- [Cibles (`.target`)](targets.md)
- [Sockets (`.socket`)](sockets.md)
- [Périphériques (`.device`)](device.md)
- [Points de montage et montages automatiques (`.mount`, `.automount`)](mount-automount.md)
- [Partitions d'échange (`.swap`)](swap.md)
- [Chemins (`.path`)](path.md)
- [Minuteurs (`.timer`)](timers.md)
- [Tranches et étendues (`.slice`, `.scope`)](slices-scopes.md)

## Unités liées au réseau

Les fichiers `.network`, `.netdev` et `.link` ne sont pas des types d'unités systemd. Ils sont lus par `systemd-networkd` et sont documentés dans la section [systemd-networkd](../services/systemd-networkd/index.md) :

- [Fichiers `.network`](../services/systemd-networkd/network.md)
- [Fichiers `.netdev`](../services/systemd-networkd/netdev.md)
- [Fichiers `.link`](../services/systemd-networkd/link.md)
