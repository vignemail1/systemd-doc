# Diagnostic de systemd-logind

```bash
systemctl status systemd-logind
journalctl -u systemd-logind -b
loginctl list-sessions
loginctl show-session SESSION
```

## Sessions absentes ou incomplètes

Vérifier que `pam_systemd` est présent dans les piles PAM et que la session est créée par un gestionnaire compatible. `loginctl show-user USER` donne l'état du gestionnaire utilisateur.

## Action d'alimentation ignorée

```bash
loginctl list-inhibitors
loginctl show-logind
```

Contrôler `Handle*`, `*IgnoreInhibited` et les règles polkit. Sur un ordinateur portable, la présence d'une station d'accueil modifie l'action via `HandleLidSwitchDocked`.

## Processus persistants

```bash
loginctl user-status alice
loginctl show-user alice -p Linger
```

Linger et `KillUserProcesses` ont des effets différents : le premier démarre un gestionnaire utilisateur sans session ; le second contrôle le nettoyage de processus.
