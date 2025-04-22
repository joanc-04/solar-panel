import json
import serial
import time
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_assets import Environment, Bundle
import numpy as np


# Créer l'application Flask et initialiser WebSocket
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["http://127.0.0.1:5000"])

# Configuration des assets
assets = Environment(app)
scss = Bundle('./styles/styles.scss', output='./styles/styles.css', filters='libsass')

# Enregistrer le bundle
assets.register('scss_all', scss)

# Temps d'attente entre chaque requête WebSocket
sleeping_time = 1  # secondes


arduino = None # Objet global pour la connexion série
port = "COM3"
baudrate = 115200
timeout = 1  # Délai pour lire une ligne via Arduino
log_fileName = "log.txt"

def write_log(message, filename=log_fileName):
    with open(filename, "a") as file:
        # file.write(message + "\n")
        return

# Fonction pour établir la connexion série avec Arduino
def connect_serial():
    global arduino
    if arduino is None or not arduino.is_open:  # Vérifie si la connexion est déjà ouverte
        try:
            arduino = serial.Serial(port, baudrate, timeout=timeout)
            print(f"Connexion à Arduino établie sur {port} à {baudrate} bauds.")
        except serial.SerialException as e:
            print(f"Erreur lors de la connexion à l'Arduino : {e}")


# Fonction pour lire les données Arduino et les envoyer au client via WebSocket
def read_arduino_data():
    global arduino

    connect_serial() # Tente de se connecter à l'Arduino via le port série

    if arduino and arduino.is_open: # Vérifie si la connexion série est ouverte avant de tenter de lire les données
        time.sleep(1)  # Attend que la connexion soit stable

        Yield = []

        try:
            while True:  # Boucle infinie pour lire en continu les données de l'Arduino

                line = arduino.readline().strip()  # Lire une ligne complète du port série et supprimer les espaces ou retours à la ligne
                if line:

                    try:

                        line = line.decode("utf-8")  # Décoder la ligne reçue en UTF-8

                        write_log("\nDonnées reçues par Arduino :")
                        write_log(line)

                        if line.startswith("{"): # Si les données reçue sont un JSON

                            try:
                                data = json.loads(line) # Tente de charger les données JSON dans un dictionnaire Python

                                message_type = data.get("type")  # Récupère le type de message

                                if message_type == "ws": # Si le message est à direction du websocket, on l'envoie au site web
                                    Yield.append(data["data"]["currentYield"])
                                    data["data"]["meanYield"] = np.mean(np.array(Yield))
                                    data["data"]["time"] = time.time()
                                    socketio.emit('new_data', data["data"])

                            except json.JSONDecodeError as e:
                                write_log("Erreur lors du décodage du JSON :")
                                write_log(e)

                    except UnicodeDecodeError as e: # Si une erreur de décodage survient, cela signifie probablement que les données ne sont pas en texte
                        write_log("Erreur lors du décodage unicode :")
                        write_log(e)

        except KeyboardInterrupt: # Si le programme est arrêté manuellement, affiche un message
            write_log("Arrêt du programme.")

        except Exception as e:
            write_log(e)

        finally: # Lorsque la lecture est terminée ou une erreur se produit, on ferme la connexion
            if arduino.is_open:
                arduino.close()
                message = "Connexion série fermée."
                write_log(message)
                print(message)

    else: # Si la connexion série échoue ou est perdue, essaie de se reconnecter après 5 secondes
        write_log("Tentative de reconnexion dans 5 secondes...")
        time.sleep(5)
        read_arduino_data()  # Nouvelle tentative de connexion pour lire les données



# Fonction pour envoyer des commandes depuis le site Web vers Arduino via WebSocket
@socketio.on('from_website')
def handle_from_website(data):
    # global arduino

    if data and isinstance(data, dict) and arduino and arduino.is_open:  # Vérifie que 'data' est bien dans le message et est un dictionnaire

        try:

            if data.get("type") == "ws":

                data_string = json.dumps(data.get("data")) + "\n"  # Converti les données en chaine de caractère en séparant chaque envoie d'un retour à la ligne
                arduino.write(data_string.encode('utf-8'))  # Envoie les données encodées en UTF-8
                write_log("\nDonnées envoyées à Arduino :")
                write_log(data_string[:-1])

        except UnicodeDecodeError as e:  # Spécifique pour les erreurs d'encodage
            write_log("Erreur lors de l'encodage de la chaîne de caractère :")
            write_log(e)

        except json.JSONEncoder as e:  # Spécifique pour les erreurs JSON
            write_log("Erreur lors de l'encodage du JSON :")
            write_log(e)

        except Exception as e:  # Pour toute autre erreur
            write_log("Erreur générale lors de l'envoie de données à Arduino :")
            write_log(e)

    else:
        write_log("Données incorrectes reçues par Python depuis le site web.")
        write_log(repr(data))


# Route pour la page HTML, qui sera servie à partir du serveur Flask
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    open("log.txt", "w").close() # Efface le fichier log
    socketio.start_background_task(read_arduino_data) # Démarre une tâche en arrière-plan qui lira continuellement les données depuis Arduino
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True) # Lance le serveur Flask avec WebSocket, écoutant sur toutes les interfaces réseau (0.0.0.0) et le port 5001




# # # # Données initiales de l'application, utilisées pour envoyer des informations au client via WebSocket
# import random
# import time
#
# Yields = []
#
# # Fonction pour générer un objet "data" avec des valeurs aléatoires
# def generate_data():
#     # Génération aléatoire des valeurs des phototransistors entre 1 et 1023
#     captor_1 = random.randint(1, 1023)
#     captor_2 = random.randint(1, 1023)
#     captor_3 = random.randint(1, 1023)
#     captor_4 = random.randint(1, 1023)
#
#     # Génération aléatoire de l'angle des servos (de 0 à 180° avec des pas de 10)
#     servo_1_angle = random.choice(range(0, 181, 10))
#     servo_2_angle = random.choice(range(0, 181, 10))
#
#     # Génération aléatoire des directions des servos (left, right, ou None)
#     servo_1_turning = random.choice(["null", "up", "down"])
#     servo_2_turning = random.choice(["null", "left", "right"])
#
#     currentYield = np.round(random.random() * 100)
#
#     Yields.append(currentYield)
#
#     print(np.mean(Yields))
#
#     # Création de l'objet data
#     data = {
#         "type": "ws",
#         "data": {
#             "system": {
#                 "manual": 1,  # Mode manuel activé par défaut
#                 "angleRotation": 5,
#                 "sensibility": 15,
#                 "delayUpdate": 30
#             },
#             "phototransistors": {
#                 "sensor_1": captor_1,
#                 "sensor_2": captor_2,
#                 "sensor_3": captor_3,
#                 "sensor_4": captor_4
#             },
#             "servomotors": {
#                 "servo_1": {
#                     "angle": servo_1_angle,  # Angle du servo_1
#                     "direction": servo_1_turning  # Direction du servo_1
#                 },
#                 "servo_2": {
#                     "angle": servo_2_angle,  # Angle du servo_2
#                     "direction": servo_2_turning  # Direction du servo_2
#                 }
#             },
#             "powerGenerated": (time.time(), random.uniform(1, 5)),
#             "powerRequired": (time.time(), random.uniform(1, 5)),
#             "meanYield": (time.time(), np.mean(Yields)),
#             "currentYield": (time.time(), currentYield)
#         }
#     }
#
#     return data
#
#
#
#
#
# # Fonction pour envoyer en continu les données au WebSocket
# def update():
#
#     while True:
#         data = generate_data()
#         print(data)
#         socketio.emit('new_data', data["data"])  # Envoie les données à tous les clients connectés
#         # Affichage de l'angle du servomoteur 1 dans la console pour débogage
#         # print(data['data']['servomotors']['servo_1']['angle'])
#         time.sleep(1)  # Pause avant de renvoyer les données
#
#
# # Route principale pour servir la page HTML
# @app.route('/')
# def index():
#     return render_template('index.html')  # Rend le fichier index.html à l'utilisateur
#
#
#
# @socketio.on('from_website')
# def handle_from_website(data):
#     # global arduino
#
#     if data and isinstance(data, dict): # and arduino and arduino.is_open:  # Vérifie que 'data' est bien dans le message et est un dictionnaire
#
#         try:
#
#             if data.get("type") == "ws":
#
#                 data_string = json.dumps(data.get("data")) + "\n"  # Assure que les données JSON sont bien séparées par une nouvelle ligne
#
#                 # arduino.write(data_string.encode('utf-8'))  # Envoie les données encodées en UTF-8
#                 print(f"\n Données envoyées à Arduino : {data_string}")
#
#                 socketio.emit('status', {'message': 'Commande envoyée à Arduino avec succès.'}) # Retour de succès à l'utilisateur (facultatif)
#
#         except UnicodeDecodeError as e:  # Spécifique pour les erreurs d'encodage
#             print(f"Erreur d'encodage lors de l'envoi à Arduino : {e}")
#             socketio.emit('e', {'message': f"Erreur d'encodage des données : {e}"})
#
#         except json.JSONDecodeError as e:  # Spécifique pour les erreurs JSON
#             print(f"Erreur lors du décodage JSON : {e}")
#             socketio.emit('e', {'message': f"Erreur lors du décodage JSON : {e}"})
#
#         except Exception as e:  # Pour toute autre erreur
#             print(f"Erreur générale lors de l'envoi de la commande à Arduino : {e}")
#             socketio.emit('e', {'message': "Erreur générale lors de l'envoi à Arduino."})
#
#     else:
#         # Si les données reçues sont invalides, on renvoie un message d'erreur au client
#         print("Données invalides ou manquantes")
#         socketio.emit('e', {'message': "Données invalides ou manquantes reçues."})
#
#
# if __name__ == '__main__':
#     scss.build()  # Compiler SCSS au démarrage
#
#     # Démarre la tâche en arrière-plan pour envoyer les données Arduino de façon continue
#     socketio.start_background_task(update)
#
#     # Lance le serveur Flask avec WebSocket, écoute sur toutes les interfaces réseau et le port 5001
#     socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)