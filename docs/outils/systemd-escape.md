# systemd-escape

`systemd-escape` convertit un chemin ou une chaîne en nom utilisable par systemd, et effectue l'opération inverse.

```bash
systemd-escape --path /var/lib/containers
systemd-escape --unescape var-lib-containers
```

Un chemin `/var/lib/containers` devient ainsi le nom d'unité `var-lib-containers.mount` lorsqu'il est utilisé pour une unité de montage. Pour obtenir directement un nom d'unité :

```bash
systemd-escape --path --suffix=mount /var/lib/containers
```

Ne pas confondre l'échappement systemd avec un échappement shell : les règles et le contexte sont différents.
