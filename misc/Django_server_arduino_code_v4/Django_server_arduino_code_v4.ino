

#include <HttpClient.h>
#include <WiFiNINA.h>

#include "arduino_secrets.h"

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
/////// Wifi Settings ///////
char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

char serverAddress[] = "192.168.1.82";  // server address
int port = 8000;

float data ;
WiFiClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, port);
int status = WL_IDLE_STATUS;


/////////////////////////////////////////Slot in Include/////////////////////////////

#include <Wire.h>
#include "DFRobot_EC.h"
#include <EEPROM.h>

//EC sensor configuration
#define EC_PIN A1
float voltage, ecValue, temperature;
DFRobot_EC ec;

//Stainless Steel Waterproof Temperature Sensor DS18B20 configuration
#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2                // DS18B20 data wire is connected to input 2
DeviceAddress thermometerAddress;     // custom array type to hold 64 bit device address
OneWire oneWire(ONE_WIRE_BUS);        // create a oneWire instance to communicate with temperature IC
DallasTemperature tempSensor(&oneWire);  // pass the oneWire reference to Dallas Temperature

float Celsius = 0;
float Fahrenheit = 0;


/////////////////////////////////////////////////////////////////////////////////////



//
unsigned long nextUpdate = 0;
unsigned long timeoutAmount = 300000 ;

// defines variables
long duration;
float count = 0.00;
int track_state = 1;
unsigned int distance_sum ;
int person = 0 ;
int server_status ;

void setup()
{

  ///////////////////////Slot in void setup////////////////////////////


  Serial.begin(9600);
  ec.begin();
  //setup for Stainless Steel Waterproof Temperature Sensor DS18B20
  Serial.println("DS18B20 Temperature IC Test");
  Serial.println("Locating devices...");
  tempSensor.begin();                         // initialize the temp sensor
  if (!tempSensor.getAddress(thermometerAddress, 0))
    Serial.println("Unable to find Device.");
  else {
    Serial.print("Device 0 Address: ");
    Serial.println();
  }
  tempSensor.setResolution(thermometerAddress, 9);      // set the temperature resolution (9-12)

  /////////////////////////////////////////////////////////////////////

  Serial.begin(9600); // Starts the serial communication
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to Network named: ");
    Serial.println(ssid);                   // print the network name (SSID);

    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);
  }

  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
}


void loop()
{
  if (millis() >= nextUpdate) {
    int gg = WiFi.ping(serverAddress);
    if (gg  >= 0) {
      server_status = 1;
    }
    if (gg < 0) {
      server_status = 0 ;
    }
    nextUpdate = millis() + timeoutAmount;
  }

  ///////////////////////Slot in void setup////////////////////////////


  //Stainless Steel Waterproof Temperature Sensor DS18B20 read temperature
  tempSensor.requestTemperatures();                      // request temperature sample from sensor on the one wire bus
  temperature = tempSensor.getTempC(thermometerAddress);

  //EC Start taking measurements here

  static unsigned long printTimepoint = millis();
  if (millis() - printTimepoint > 1000U) //after 1sec
  {
    printTimepoint = millis();
    voltage = analogRead(EC_PIN) / 1024.0 * 5000; // read the voltage
    ecValue =  ec.readEC(voltage, temperature); // convert voltage to EC with temperature compensation
    Serial.print("temperature:");
    Serial.print(temperature, 1);
    Serial.print("^C  EC:");
    Serial.print(ecValue, 2);
    Serial.println("ms/cm");
  }
  ec.calibration(voltage, temperature);         // calibration process by Serail CMD
  static unsigned long readingTimepoint = millis();
  if (millis() - readingTimepoint > 60000U) //every 1 minute
  {
    Serial.println((String)"DATA,TIME," + temperature + (String)"," + ecValue);
    readingTimepoint = millis();
  }

  /////////////////////////////////////////////////////////////////////

  Serial.println("making GET request");
      client.get("/new?sensor_id=1&ec=" + String(ecValue,2) + "&temp=" + String (temperature,1));
      count = 0;
      ecValue = 0;
      temperature =0; 
      Serial.println("boom");
      int statusCode = client.responseStatusCode();
      if (statusCode != 200) {
      server_status = 0 ;
      nextUpdate = millis() + timeoutAmount;
      }
      Serial.print("Status code: ");
      Serial.println(statusCode);
      String response = client.responseBody();
}


void displayTemp(float temperatureReading) {             // temperature comes in as a float with 2 decimal places

  // show temperature °C
  Serial.print(temperatureReading);      // serial debug output
  Serial.print("°");
  Serial.print("C  ");

  // show temperature °F
  Serial.print(DallasTemperature::toFahrenheit(temperatureReading));     // serial debug output
  Serial.print("°");
  Serial.println("F");
}
