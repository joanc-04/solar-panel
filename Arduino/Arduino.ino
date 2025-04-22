// Importation des librairies
#include <Servo.h>
#include <ArduinoJson.h>

// Déclaration des variables de configuration
int DELAY_TIME_UPDATE = 50;
int DELAY_TIME_SEND_DATA = 50;
int DELAY_TIME_BUTTON = 20;
int buttonPin = 1;
int angleRotation = 3;
int servo1Pin = 6;
int servo2Pin = 7;
int sensor1Pin = A1;
int sensor2Pin = A2;
int sensor3Pin = A3;
int sensor4Pin = A4;
float sensor1Resistance = 9700;
float sensor2Resistance = 9660;
float sensor3Resistance = 9700;
float sensor4Resistance = 9770;
int SEUIL_SENSIBILITY = 5;
int DEFAULT_MANUAL_MOD = 0;

int RESISTOR_CELL = 9710;
int RESISTOR_CELL_PIN_1 = A0;
int RESISTOR_CELL_PIN_2 = A5;





class Cooldown {
    private:
        long previousTime;      // Moment d'activation
        long delayCooldown;     // Durée

    public:
        Cooldown(long delayCooldown, long previousTime = millis()):
        delayCooldown(delayCooldown),
        previousTime(previousTime) {}

    bool check() {
        long time = millis();
        if (time - previousTime < delayCooldown) return false;
        previousTime = time;
        return true;
    }

    void set_delay(int newDelay) {
        delayCooldown = newDelay;
        previousTime = millis();
    }

    int get_delay() {
      return delayCooldown;
    }
};




class ServoControl {
    private:
        Servo servo;        // Servomoteur
        int pin;            // Numéro de l'entrée
        int angle;          // Angle actuel
        int angleStep;      // Angle de rotation
        int minAngle;       // Angle minimal
        int maxAngle;       // Angle maximal

    public:
        ServoControl(int pin, int angleStep, int minAngle = 0, int maxAngle = 180):
        pin(pin),
        angle(0),          // Par défaut l'angle est à 90°
        angleStep(angleStep),
        minAngle(minAngle),
        maxAngle(maxAngle) {}

    void init() {
        servo.attach(pin);
        servo.write(angle);
    }

    int get_angle() {
        return angle;
    }
    
    void set_angle(int newAngle) {
        angle = newAngle;
        servo.write(angle);
    }

    int get_angleStep() {
        return angleStep;
    }

    int set_angleStep(int newAngleStep) {
        angleStep = newAngleStep;
        return newAngleStep;
    }

    int angleLimit = 40;

    bool increase(ServoControl* servo1=nullptr) {
        bool limitReached = false;
        if (angle + angleStep <= maxAngle) angle += angleStep;
        else if (angle < maxAngle) {
            angle = maxAngle;
        }
//         else if (angle == maxAngle && pin == servo2Pin && servo1 && (servo1->get_angle() < 30 || servo1->get_angle() > 150)) {
//             limitReached = true;
//             servo1->set_angle(180 - servo1->get_angle());
//             angle = 0;
//         }
        servo.write(angle);
        return limitReached;
    }

    bool decrease(ServoControl* servo1=nullptr) {
        bool limitReached = false;
        if (angle - angleStep >= minAngle) angle -= angleStep;
        else if (angle > minAngle) {
            angle = minAngle;
        }
//         else if (angle == minAngle && pin == servo2Pin && servo1 && (servo1->get_angle() < 30 || servo1->get_angle() > 150)) {
//             limitReached = true;
//             servo1->set_angle(180 - servo1->get_angle());
//             angle = 180;
//         }
        servo.write(angle);
        return limitReached;
    }
};







class LightSensor {
    private:
        int pin;            // Numéro du capteur
        int resistance;     // Valeur de la résistance du capteur

    public:
        LightSensor(int pin, int resistance):
        pin(pin),
        resistance(resistance) {}

    int get_value() {
        return ((long)analogRead(pin) * 10000) / resistance;
    }
};




// Nécessaire pour éviter le référencement circulaire entre Tracker et Communication
class Tracker;
class Communication {
    private:
        Tracker* tracker;       // Tracker associé
        Cooldown* cooldown;      // Durée du cooldown pour l'échange de données avec Python

    public:
        Communication(Tracker* tracker, Cooldown* cooldown, long previousTime = 0):
        tracker(tracker),
        cooldown(cooldown) {}

    void send_data(int manualMod, int sensor1, int sensor2, int sensor3, int sensor4, int angle1, int angle2, String direction1, String direction2, int angleStep, int delayUpdate, int sensibility, float powerGenerated, float powerRequired, float currentYield);
    void receive_data();
};





class Tracker {
    private:
        ServoControl servo1, servo2;                                // Servomoteurs
        LightSensor sensor1, sensor2, sensor3, sensor4;             // Capteurs
        int sensibility;                                            // Seuil de sensibilité
        int lastSensibility;
        int manualMod;                                              // Status du mode manuel
        int buttonPin;                                              // Numéro du bouton
        Cooldown cooldownUpdate, cooldownSendData, cooldownButton;  // Durée des cooldowns
        Communication communication;                                // Communication
        String direction1, direction2;                              // Directions d'orientation

    public:
        Tracker(int manualMod, int servo1Pin, int servo2Pin, int sensor1Pin, int sensor2Pin, int sensor3Pin, int sensor4Pin, int buttonPin):
        servo1(servo1Pin, angleRotation),
        servo2(servo2Pin, angleRotation),

        sensor1(sensor1Pin, sensor1Resistance),
        sensor2(sensor2Pin, sensor2Resistance),
        sensor3(sensor3Pin, sensor3Resistance),
        sensor4(sensor4Pin, sensor4Resistance),

        sensibility(SEUIL_SENSIBILITY),
        lastSensibility(SEUIL_SENSIBILITY),
        manualMod(manualMod),
        buttonPin(buttonPin),

        cooldownUpdate(DELAY_TIME_UPDATE),
        cooldownSendData(DELAY_TIME_SEND_DATA),
        cooldownButton(DELAY_TIME_BUTTON),

        communication(this, &cooldownSendData),

        direction1(""),
        direction2("") {}


    void init() {
        servo1.init();
        servo2.init();
        pinMode(buttonPin, INPUT_PULLUP); // Si on appuie pas sur le bouton, il est par défaut HIGH.
    }


    void check_button() {

        if (!cooldownUpdate.check()) return;

        bool buttonState = digitalRead(buttonPin);
        if (buttonState == LOW) {
            switch_manualMod();
            Serial.println("Mode manuel : " + String(manualMod ? "Activé" : "Désactivé"));
        }
    }


    void update() {

//         check_button();

        if (manualMod == 1) return; // La suite du code s'exécute seulement si le modeManuel est désactivé.

        if (!cooldownUpdate.check()) return; // La suite du code s'exécute tous les X temps.

        int sensor1Value = sensor1.get_value();
        int sensor2Value = sensor2.get_value();
        int sensor3Value = sensor3.get_value();
        int sensor4Value = sensor4.get_value();


        // Contrôle l'inclinaison du panneau solaire
        if (abs(sensor1Value - sensor2Value) > sensibility) {
            if (sensor1Value > sensor2Value) {
                servo1.decrease();
                direction1 = "up";
            } else {
                servo1.increase();
                direction1 = "down";
            }
        } else direction1 = "";


        // Contrôle l'orientation du panneau solaire
        if (abs(sensor3Value - sensor4Value) > sensibility) {

            // Si l'angle du servomoteur 1 dépasse 90°, alors on inverse les capteurs 3 et 4
            if (servo1.get_angle() >= 90) {
                int temp = sensor4Value;
                sensor4Value = sensor3Value;
                sensor3Value = temp;
            }

            bool limitReached;
            if (sensor3Value > sensor4Value) {
                limitReached = servo2.increase(&servo1);
                direction2 = "left";
            } else {
                limitReached = servo2.decrease(&servo1);
                direction2 = "right";
            }

//             if (limitReached) {
//                 lastSensibility = sensibility;
//                 sensibility = 300;
//             } else {
//                 sensibility = lastSensibility;
//             }

        } else direction2 = "";

    }


    int switch_manualMod() {
        manualMod = manualMod ? 0 : 1;
        return manualMod;
    }

    int get_manualMod() {
        return manualMod;
    }


    void send_data() {

        if (!cooldownSendData.check()) return; // Le code suivant est exécuté tout les X temps.

        int sensor1Value = sensor1.get_value();
        int sensor2Value = sensor2.get_value();
        int sensor3Value = sensor3.get_value();
        int sensor4Value = sensor4.get_value();

        float* yield = get_yield();  // Récupère le tableau retourné

        float r = yield[0];
        float Pp = yield[1];
        float Pa = yield[2];

        delete[] yield;

        // Envoie les données à Communication qui les formatent pour les envoyez par port série à Python
        communication.send_data(
            manualMod,
            sensor1Value, sensor2Value, sensor3Value, sensor4Value,
            servo1.get_angle(), servo2.get_angle(),
            direction1, direction2,
            servo1.get_angleStep(),
            cooldownUpdate.get_delay(),
            sensibility,
            Pp,
            Pa,
            r
        );

    }

    // Vérifie que Communication n'a pas reçue des données en provenance de Python par port série.
    void receive_data() {
        communication.receive_data();
    }

    ServoControl* getServo(int number) {
        ServoControl* servos[] = {&servo1, &servo2};
        return servos[number - 1];
    }

    void set_angleStep(int newAngleStep) {
        servo1.set_angleStep(newAngleStep);
        servo2.set_angleStep(newAngleStep);
    }

    void set_delayUpdate(int newDelayUpdate) {
        cooldownUpdate.set_delay(newDelayUpdate);
    }

    void set_sensibility(int newSensibility) {
        sensibility = newSensibility;
    }

    void displaySensors() {
        Serial.println("Sensor 1 : " + String(analogRead(sensor1Pin)));
        Serial.println("Sensor 2 : " + String(analogRead(sensor2Pin)));
        Serial.println("Sensor 3 : " + String(analogRead(sensor3Pin)));
        Serial.println("Sensor 4 : " + String(analogRead(sensor4Pin)));
        Serial.println("");
    }

    float* get_yield() {

        float Up = (analogRead(RESISTOR_CELL_PIN_1) - analogRead(RESISTOR_CELL_PIN_2)) * 5 / 1023.0;
        float Ip = Up / 9710.;
        float Pp = Up * Ip;

        float Ua = 5;
        float I1 = (analogRead(A1) * 5 / 1023.) / sensor1Resistance;
        float I2 = (analogRead(A2) * 5 / 1023.) / sensor2Resistance;
        float I3 = (analogRead(A3) * 5 / 1023.) / sensor3Resistance;
        float I4 = (analogRead(A4) * 5 / 1023.) / sensor4Resistance;
        float Ia = - (I1 + I2 + I3 + I4);
        
        float Pa = abs(Ua * Ia);

        float r = abs(Pp / Pa) * 100;

//         Serial.println("Puissance générée par le panneau solaire : " + String(Pp));
//         Serial.println("Puissance générée par l'ensemble du circuit : " + String(Pa));
//         Serial.println("Rendement du panneau solaire par rapport à l'énergie fournie par le circuit : " + String(r));
//         Serial.println("");

        float* yield = new float[3];  // Alloue dynamiquement un tableau de 3 éléments
        yield[0] = r;  // Initialise r
        yield[1] = Pp;  // Initialise Pp
        yield[2] = Pa;  // Initialise Pa
        return yield;

    }
};





void Communication::send_data(int manualMod, int sensor1, int sensor2, int sensor3, int sensor4, int angle1, int angle2, String direction1, String direction2, int angleStep, int delayUpdate, int sensibility, float powerGenerated, float powerRequired, float currentYield) {

    String jsonString = "{";
    jsonString += "\"type\":\"ws\",";
    jsonString += "\"data\":{";
    jsonString += "\"system\":{";
    jsonString += "\"manual\":" + String(manualMod) + ",";
    jsonString += "\"angleRotation\":" + String(angleStep) + ",";
    jsonString += "\"delayUpdate\":" + String(delayUpdate) + ",";
    jsonString += "\"sensibility\":" + String(sensibility);
    jsonString += "},";

    jsonString += "\"phototransistors\":{";
    jsonString += "\"sensor_1\":" + String(sensor1) + ",";
    jsonString += "\"sensor_2\":" + String(sensor2) + ",";
    jsonString += "\"sensor_3\":" + String(sensor3) + ",";
    jsonString += "\"sensor_4\":" + String(sensor4);
    jsonString += "},";

    jsonString += "\"servomotors\":{";
    jsonString += "\"servo_1\":{\"angle\":" + String(angle1) + ",\"direction\":\"" + (direction1 == "" ? "null" : direction1) + "\"},";
    jsonString += "\"servo_2\":{\"angle\":" + String(angle2) + ",\"direction\":\"" + (direction2 == "" ? "null" : direction2) + "\"}";
    jsonString += "},";

    jsonString += "\"powerGenerated\":" + String(powerGenerated * pow(10, 3), 3) + ",";
    jsonString += "\"powerRequired\":" + String(powerRequired * pow(10, 3), 3) + ",";
    jsonString += "\"currentYield\":" + String(currentYield, 3);
    jsonString += "}}";

    Serial.println(jsonString); // Envoie la chaine de caractère formée à Python par port série

}


void Communication::receive_data() {

    if (Serial.available() > 0) {
        String line = Serial.readStringUntil('\n'); // Lire la ligne jusqu'à un saut de ligne
        line.trim();

        Serial.println(line);  // Affiche la ligne lue pour débogage

        if (line.startsWith("{") && line.endsWith("}")) {  // Filtrer les bonnes données JSON
            StaticJsonDocument<512> data;
            DeserializationError error = deserializeJson(data, line);

            if (!error) {
                String editName = data["edit"];
                int editValue = data["value"];

//                 String message = ""; // Déclarée ici pour être accessible partout

                // Vérifier et appliquer les modifications selon les clés du JSON
                if (editName == "manualMod") {
                    int newStatus_manualMod = tracker->switch_manualMod(); // Modifie le mode manuel (sur 1 s'il était sur 0 et inversement)
//                     String message = "Le mode manuel est désormais : " + String(newStatus_manualMod ? "allumé" : "éteint");
                }

                if (editName.startsWith("servo-")) {
                    int servoNumber = String(editName.charAt(editName.length() - 1)).toInt();
                    ServoControl* servo = tracker->getServo(servoNumber);
                    servo->set_angle(editValue);
//                     message = "Angle du servomoteur 1 : " + String(angle);
                }

                 if (editName == "angleRotation") {
                    int angleStep = editValue;
                    tracker->set_angleStep(angleStep);
//                     message = "L'angle de rotation est désormais : " + String(angleStep);
                }

                if (editName == "sensibility") {
                    int sensibility = editValue;
                    tracker->set_sensibility(sensibility);
//                     message = "La sensibilité est désormais : " + String(sensibility);
                }

                if (editName == "delayUpdate") {
                    int delayUpdate = editValue;
                    tracker->set_delayUpdate(delayUpdate);
//                     message = "Le délai d'actualisation est désormais : " + String(delayUpdate);
                }

            }
        }
    }

}





// Création d'une instance Tracker qui contrôlera le panneau solaire
Tracker tracker(DEFAULT_MANUAL_MOD, servo1Pin, servo2Pin, sensor1Pin, sensor2Pin, sensor3Pin, sensor4Pin, buttonPin);

// Fonction qui s'exécute au lancement du programme.
void setup() {
    Serial.begin(115200);
    tracker.init();
}

// Fonction qui s'exécute en boucle
void loop() {

    tracker.update();
    tracker.send_data();
    tracker.receive_data();

//     tracker.get_yield();
    //tracker.displaySensors();

}