# systemd-logind

`systemd-logind` gère les sessions utilisateur, les sièges, les périphériques associés et les actions d'alimentation. Il expose ces informations via D-Bus et `loginctl`.

## Concepts

- **Session** : connexion d'un utilisateur.
- **Utilisateur** : état global d'un compte connecté.
- **Siège** : ensemble de périphériques utilisables localement.
- **Inhibiteur** : verrou empêchant temporairement veille, extinction ou changement de session.

## Commandes de base

```bash
loginctl list-sessions
loginctl session-status SESSION
loginctl list-users
loginctl seat-status seat0
loginctl list-inhibitors
```

## Cycle de vie

PAM crée et ferme les sessions via `pam_systemd`. Pour un service utilisateur persistant après déconnexion :

```bash
loginctl enable-linger alice
loginctl disable-linger alice
```

!!! warning
    Le linger permet à des services utilisateur de fonctionner sans session interactive ; il doit être activé seulement pour les comptes concernés.

## Actions d'alimentation

`logind` reçoit les demandes d'arrêt, redémarrage, veille et fermeture du capot. Les politiques peuvent être ajustées dans `logind.conf`.
