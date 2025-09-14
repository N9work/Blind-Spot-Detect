#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "Your SSID";
const char* password = "Your Pass";

WiFiUDP udp;
const int localUdpPort = 5005;
char incomingPacket[255];

#define LED_PIN 12  // 

bool carDetected = false;
unsigned long lastEventTime = 0;
const unsigned long TIMEOUT = 500; // 

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  // ตั้ง ESP32 เป็น AP
  WiFi.softAP(ssid, password);
  Serial.println("AP Started");
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  // เริ่ม UDP server
  udp.begin(localUdpPort);
  Serial.printf("Listening at UDP port %d\n", localUdpPort);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(incomingPacket, 255);
    if (len > 0) incomingPacket[len] = 0;

    if (String(incomingPacket) == "CAR_DETECTED") {
      carDetected = true;
      lastEventTime = millis();
      //Serial.println("CAR DETECTED");
    }
  }

  // ตรวจสอบ timeout
  if (carDetected && millis() - lastEventTime > TIMEOUT) {
    carDetected = false;
  }

  // ควบคุม LED
  digitalWrite(LED_PIN, carDetected ? HIGH : LOW);
}
