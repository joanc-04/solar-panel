```
██████╗ ██████╗  ██████╗      ██╗███████╗████████╗
██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝╚══██╔══╝
██████╔╝██████╔╝██║   ██║     ██║█████╗     ██║   
██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝     ██║   
██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗   ██║   
╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝   ╚═╝   
                                                  


████████╗ ██████╗ ██╗   ██╗██████╗ ███╗   ██╗███████╗███████╗ ██████╗ ██╗     
╚══██╔══╝██╔═══██╗██║   ██║██╔══██╗████╗  ██║██╔════╝██╔════╝██╔═══██╗██║     
   ██║   ██║   ██║██║   ██║██████╔╝██╔██╗ ██║█████╗  ███████╗██║   ██║██║     
   ██║   ██║   ██║██║   ██║██╔══██╗██║╚██╗██║██╔══╝  ╚════██║██║   ██║██║     
   ██║   ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║███████╗███████║╚██████╔╝███████╗
   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝

```

## Fichiers

Dans le dossier `website`, vous trouverez tous les fichiers nécessaires à l'interface graphique.
- `app.py` est le fichier Python faisant la connexion port série avec l'Arduino. Il envoie ensuite les données au WebSocket en `localhost:5000`.
- Le dossier `templates` contient le code HTML contenant le corps du site web.
- Le dossier `static` contient :
  - Le dossier `styles`, qui contient le code SCSS pour la mise en page du site web.
  - Le dossier `scripts`, qui contient le code JavaScript pour la partie dynamique du site web (il gère notamment les données du WebSocket).

Dans le dossier `Arduino`, vous trouverez le code faisant fonctionner l'Arduino.

Dans le dossier `yield`, vous trouverez les données mesurées pour la caractéristique courant tension, ainsi que le code Python permettant de tracer ces courbes. Il y a également le code utilisé pour le réseau de neurones.

Dans le dosser `Compte rendu`, vous trouverez le compte rendu de notre projet.

# Fonctionnement

1. Lancer le code Arduino depuis un éditeur spécifique à Arduino.
2. Fermer cet éditeur pour libérer le port série.
3. Lancer le fichier `/templates/app.py` pour héberger le site web en local.
4. Rendez-vous sur l'adresse : `localhost:5000`