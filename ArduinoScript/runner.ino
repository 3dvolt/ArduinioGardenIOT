// library initialization for temperature reading from DHT sensor
#include <dht.h>
dht DHT;
// pin definition for reading
#define SensorPin A0
#define dht_apin A1

enum states {
  INITIALIZE, MEASUREMENTS_DONE, RAIN, WEATHER_OK
};

states currentstate;
states futurestate;
// initial value statement
float soil_humidity = 0;
float temperature = 0;

void setup () {
  Serial.begin (9600);
  // pin setting in OUTPUT mode
  // LED
  pinMode (12, OUTPUT); // status measurements
  pinMode (11, OUTPUT); // weather status
  pinMode (13, OUTPUT); // status people detected

  pinMode (7, OUTPUT); // water pump
  currentstate = INITIALIZE;
  futurestate = INITIALIZE;
}

void loop () {
  // if there is a serial connection
  if (Serial.available ()> 0)
  {
    currentstate = futurestate;
    
    char command = Serial.read (); // read the character received in input

    if (command == 'h' && (currentstate == INITIALIZE || currentstate == MEASUREMENTS_DONE)) {// if the input character is h, part irrigation
      for (int i = 0; i <= 100; i ++) // 100 measurements are sampled and then averaged for accuracy
      {
        soil_humidity = soil_humidity + analogRead (soil_humidity);
        delay (1);
      }
      soil_humidity = soil_humidity / 100.0;
      //Serial.print("Soil Humidity = ");
      if (soil_humidity <= 400) {// if the detected humidity is below the threshold the led lights up, water need status
        digitalWrite (12, HIGH);
      }
      else {
        digitalWrite (12, LOW);
      }
      futurestate = MEASUREMENTS_DONE;
      Serial.println (soil_humidity); // communicates the measurement on a serial port
    }
    if (command == 't' && (currentstate == INITIALIZE || currentstate == MEASUREMENTS_DONE)) {// if the input character is t, the temperature on the
      DHT.read11 (dht_apin);
      //Serial.print("External temperature = ");
      temperature = DHT.temperature;
      if (temperature == -999.00) {// if the read temperature is -999.99 means that the sensor is not connected properly. we return a static value.
        temperature = 20;
      }
      futurestate = MEASUREMENTS_DONE;
      Serial.println (temperature); // communicates the measurement on a serial port
    }
    if (command == 'r' && currentstate == MEASUREMENTS_DONE) {// if the input character is r, it will rain and therefore the led will be off
      futurestate = RAIN;
      digitalWrite (11, LOW);
    }
    if (command == 'w' && currentstate == MEASUREMENTS_DONE) {// if the input character is w, there will be no rain in the weather forecast and the led will light up as water need status.
      futurestate = WEATHER_OK;
      digitalWrite (11, HIGH);
    }

    if (command == 's' && currentstate == WEATHER_OK) {// if the input character is s and the status is correct, part irrigation
      digitalWrite (7, HIGH); // water pump ON
      digitalWrite (13, HIGH); // status LED ON
      Serial.println ("Irrigation Started");
    }
    
    if (command == 'e') {// if the input character is e, irrigation is interrupted due to presence nearby
      digitalWrite (7, LOW); // water pump OFF
      digitalWrite (13, LOW); // status LED OFF
      Serial.println ("Interrupted Irrigation");
    }

    
    if (command == 'f') {// force, turn off all LEDs, pump and reset states
      digitalWrite (7, LOW); // water pump OFF
      digitalWrite (13, LOW);
      digitalWrite (12, LOW);
      digitalWrite (11, LOW);
      futurestate = INITIALIZE;
    }

  }
}