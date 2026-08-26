# Sapphire Discord Bot

Sapphire est un bot Discord modulaire écrit en **JavaScript avec Node.js et discord.js**. Il fournit la modération, les messages d’accueil et de départ, les niveaux XP, la protection anti-raid, les rôles, le honeypot et les commandes Akinator.

## Démarrage Wispbyte

Le fichier principal à sélectionner dans Wispbyte est :

```text
bot.js
```

La commande de démarrage est :

```bash
node bot.js
```

Le dépôt est public et ne nécessite pas de token GitHub pour le clonage. La commande d’installation est :

```bash
npm install
```

## Variables d’environnement

Configure exactement ces trois variables dans le panneau Wispbyte :

| Variable | Utilisation |
|---|---|
| `DISCORD_TOKEN` | Token privé du bot Discord ; obligatoire pour la connexion |
| `CLIENT_ID` | Identifiant de l’application Discord |
| `CLIENT_SECRET` | Secret OAuth utilisé par l’intégration du dashboard |

Ne publie jamais la valeur de `DISCORD_TOKEN` dans GitHub, le README ou le chat.

## Discord Developer Portal

Active les intents privilégiés **Server Members Intent** et **Message Content Intent**. Le bot doit avoir les permissions nécessaires aux fonctions activées : voir les salons, envoyer des messages, intégrer des liens, gérer les messages, modérer les membres, expulser, bannir et gérer les rôles.

## Structure

```text
bot.js             # point d’entrée Node.js
package.json       # dépendance discord.js et script start
sapphire-data.json # créé automatiquement pour les données locales
```

Les données locales sont enregistrées dans `sapphire-data.json`. Ce fichier est ignoré par Git et doit être conservé sur un stockage persistant si Wispbyte le permet.

## Commandes

Le bot enregistre des commandes slash pour l’aide, les informations serveur et membre, la modération, l’accueil, les niveaux XP, le classement, l’anti-raid, les rôles, les logs, les commandes personnalisées et Akinator.
