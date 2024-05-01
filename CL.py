#include <Wire.h>
#include <EEPROM.h>
//#include "ESP8266WiFi.h"
#include <RTClib.h>
#include <Adafruit_GFX.h> 
#include <Adafruit_SSD1306.h>
#include <Fonts/FreeMonoBold12pt7b.h> 
#include <Fonts/FreeMono9pt7b.h> 
#define OLED_ADDRESS 0x3C
Adafruit_SSD1306 display(128, 64, &Wire, -1); 
#define menuSelectButtonPin 15
#define button1Pin 16
#define button2Pin 17

#define EEPROM_ALARM_0_ADDRESS 0
#define EEPROM_ALARM_1_ADDRESS (EEPROM_ALARM_0_ADDRESS + sizeof(Alarm))
#define EEPROM_ALARM_2_ADDRESS (EEPROM_ALARM_1_ADDRESS + sizeof(Alarm))

#define buzzerPin 12
bool buzzerOn = false;
RTC_DS1307 rtc; 

unsigned long lastMenuPressTime = 0;
unsigned long debounceDelay = 50;
unsigned long lastDebounceTime = 0;
unsigned long lastBuzzTime = 0;
int lastButtonState = HIGH;

int menu = 0;
int order = 0;
int cabinet = 1;
int pills = 0;
bool settingMode0 = false;
bool settingMode1 = false;
bool settingMode2 = false;
bool isPaused = false;
bool isPaused5m = false;
bool isPaused30m = false;
bool isStopped = false;
DateTime now;
DateTime alarmTime0;
DateTime alarmTime1;
DateTime alarmTime2;
/*const char *ssid = "Chưa có"; 
const char *password = "Chưa có";
const char *serverIp = "192.168.1.1 - 192.168.1.255, tùy"; 
const int serverPort = 80;*/
struct Alarm {
  int day;
  int hour;
  int minute;
  int pills;
};
Alarm alarmEEPROM0;
Alarm alarmEEPROM1;
Alarm alarmEEPROM2;
void readAlarmsFromEEPROM() {
  EEPROM.get(EEPROM_ALARM_0_ADDRESS, alarmEEPROM0);
  EEPROM.get(EEPROM_ALARM_1_ADDRESS, alarmEEPROM1);
  EEPROM.get(EEPROM_ALARM_2_ADDRESS, alarmEEPROM2);
}
void writeAlarmToEEPROM(const Alarm& alarm, uint16_t address) {
  EEPROM.put(address, alarm);
}
void setup() {   
  pinMode(menuSelectButtonPin, INPUT_PULLUP);
  pinMode(button1Pin, INPUT_PULLUP);
  pinMode(button2Pin, INPUT_PULLUP);  
  pinMode(buzzerPin, OUTPUT); 
  Serial.begin(9600);
  Wire.begin();
  rtc.begin(); 
  //WiFi.begin(ssid, password);         
  delay(100);  
  display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS); 
  display.clearDisplay(); 
  display.setTextColor(WHITE); 
  display.setRotation(0); 
  display.setTextWrap(false); 
  display.dim(0); 
  display.setCursor(0, 0);
  display.println(F("Hello <333"));
  display.display();

  if (!rtc.begin()) {
    Serial.println("Không thấy RTC!");
    display.setCursor(0, 50);
    display.println(F("not rtc"));
    display.display();
    while(1);
  }

  if (!rtc.isrunning()) {
    Serial.println("RTC không chạy!");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
  Serial.println("RTC Ok!");
  /*while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Đang kết nối vào mạng WiFi...");
  }

  Serial.println("Kết nối thành công!");
  Serial.println("Kết nối đến server...");
  WiFiClient client;
  if (client.connect(serverIp, serverPort)) {
    Serial.println("Kết nối thành công đến server!");
  } else {
    Serial.println("Kết nối thất bại đến server!");
  }*/
  readAlarmsFromEEPROM();
  alarmTime0 = DateTime(0, 0, alarmEEPROM0.day, alarmEEPROM0.hour, alarmEEPROM0.minute, 0);
  alarmTime1 = DateTime(0, 0, alarmEEPROM1.day, alarmEEPROM1.hour, alarmEEPROM1.minute, 0);
  alarmTime2 = DateTime(0, 0, alarmEEPROM2.day, alarmEEPROM2.hour, alarmEEPROM2.minute, 0);
}

void loop() {
  int menuSelectButtonState = digitalRead(menuSelectButtonPin);
  int button1State = digitalRead(button1Pin);
  int button2State = digitalRead(button2Pin);
  now = rtc.now();
  pressDetectMenu();
  menuSelect();
  if (settingMode0) {
    pillsTakingSetting(alarmEEPROM0, alarmTime0, settingMode0);
  }
  if (settingMode1) {
    pillsTakingSetting(alarmEEPROM1, alarmTime1, settingMode1);
  }
  if (settingMode2) {
    pillsTakingSetting(alarmEEPROM2, alarmTime2, settingMode2);
  }
  alarmCheck(alarmTime0);
  alarmCheck(alarmTime1);
  alarmCheck(alarmTime2);
  if(buzzerOn)
  {
    while(!isPaused && !isStopped)
    {
    buzzer();
    }
      
      buzzerOn = false;
      noTone(buzzerPin);
      
      Serial.println("Buzzer Off");
  }
  Serial.println(alarmEEPROM0.day);
  if(isPaused)
  {
    if (isPaused5m && millis() - lastMenuPressTime >= 5 * 60 * 1000) { 
      isPaused = false;
      buzzerOn = true;
      
  }
  if (isPaused30m && millis() - lastMenuPressTime >= 30 * 60 * 1000) { 
      isPaused = false;
      buzzerOn = true;
      
  }
  
}
goToSleep();
}
bool pressDetectMenu() {
  int menuButtonState = digitalRead(menuSelectButtonPin);
  
  if (pressDetect(menuButtonState)) {
    delay(50);
    menu = (menu + 1) % 4;
    settingMode0 = (menu == 1);
    settingMode1 = (menu == 2);
    settingMode2 = (menu == 3);
    Serial.println("Menu pressed");
    
    return true;
  }
  return false;
}
void menuSelect() {
  switch(menu) {
    case 0:
      timeDisplay();
      break;
    case 1:   
      
    display.clearDisplay();
    
    display.setCursor(0, 20);
    display.println("Dose: " + String(menu));
    pillsTakingSetting(alarmEEPROM0, alarmTime0, settingMode0);
    writeAlarmToEEPROM(alarmEEPROM0, EEPROM_ALARM_0_ADDRESS);
    EEPROM.commit();
      break;
    case 2:   
      display.clearDisplay();
    
    display.setCursor(0, 20);
    display.println("Dose: " + String(menu));
    pillsTakingSetting(alarmEEPROM1, alarmTime1, settingMode1);
    writeAlarmToEEPROM(alarmEEPROM1, EEPROM_ALARM_1_ADDRESS);
      break;
    case 3:   
      display.clearDisplay();
    
    display.setCursor(0, 20);
    display.println("Dose: " + String(menu));
    pillsTakingSetting(alarmEEPROM2, alarmTime2, settingMode2);
    writeAlarmToEEPROM(alarmEEPROM2, EEPROM_ALARM_2_ADDRESS);
      break;
  }
}

void timeDisplay() {
  display.clearDisplay();
  printDateTime(now);
}
void alarmCheck(DateTime &alarmTime)
{
  int hourDiff = alarmTime.hour() - now.hour();
  int minuteDiff = 60 - now.minute();
  int secondDiff = 60 - now.second();
  if (now.hour() >= alarmTime.hour()) {
    hourDiff += 24;
  }
  if (alarmTime.dayOfTheWeek() == now.dayOfTheWeek() && hourDiff < 4 && minuteDiff < 60 && !isStopped ) {
    
    buzzerOn = true;
    
  }
}
void alarmChoice()
{
  int menuSelectButtonState = digitalRead(menuSelectButtonPin);
  int button1State = digitalRead(button1Pin);
  int button2State = digitalRead(button2Pin);
  if(pressDetect(button1State))
  {
    isPaused = true;
    isPaused5m = true;
    buzzerOn = false;
    lastMenuPressTime = millis();
    Serial.println("is Paused 5m");
  }
  if(pressDetect(button2State))
  {
    isPaused = true;
    isPaused30m = true;
    buzzerOn = false;
    Serial.println("is Paused 30m");
  }
  if(pressDetect(menuSelectButtonState))
  {
    isStopped = true;
    buzzerOn = false;
    Serial.println("is Stopped");
  }
}
void buzzer()
{
    
    if (millis() - lastBuzzTime >= 1000)
    {
    tone(buzzerPin, 500); 
    delay(10);
    
    lastBuzzTime = millis();
    }
    noTone(buzzerPin); 
    display.clearDisplay();
    display.setCursor(15, 10);
    display.println("Take pills");
    display.setCursor(5, 30);
    display.println("1.Stop");
    display.setCursor(5, 45);
    display.println("2.Pause 5m");
    display.setCursor(5, 60);
    display.println("3.Pause 30m");
    alarmChoice();

    display.display();

    
}


void pillsTakingSetting(Alarm &alarmEEPROM, DateTime &alarm, bool &settingMode) {
  int menuSelectButtonState = digitalRead(menuSelectButtonPin);
  int button1State = digitalRead(button1Pin);
  int button2State = digitalRead(button2Pin);
  if (pressDetect(button1State)) 
  {
    order = (order + 1) % 4;
    delay(50);
    Serial.println("button1 pressed");
  }
  switch(order) {
    case 0:
      if (pressDetect(button2State)) 
      {
        delay(50);
        Serial.println("button2 pressed");
        alarm = DateTime(alarm.year(), alarm.month(), alarm.day() + 1, alarm.hour(), alarm.minute(), alarm.second());
        alarmEEPROM.day = alarm.day();
        
      }
      break;
    case 1:
      if (pressDetect(button2State)) 
      {
        delay(50);
        Serial.println("button2 pressed");
        alarm = DateTime(alarm.year(), alarm.month(), alarm.day(), (alarm.hour() + 1) % 24, alarm.minute(), alarm.second());
        alarmEEPROM.hour = alarm.hour();
      }
      break;
    case 2:
      if (pressDetect(button2State)) 
      {
        delay(50);
        alarm = DateTime(alarm.year(), alarm.month(), alarm.day(), alarm.hour(), (alarm.minute() + 1) % 60, alarm.second());
        alarmEEPROM.minute = alarm.minute();
      }
      break;
    case 3:
      
      if (pressDetect(button2State)) 
      {
        alarmEEPROM.pills =(alarmEEPROM.pills + 1) % 10;
      }
      break;
    
  }
  
  
  display.setCursor(0, 60);
  display.println("Pills: " + String(alarmEEPROM.pills));
  printDateAlarm(alarm);
  
  if (pressDetect(menuSelectButtonState)) {
    settingMode = false;
  }
}

void printDateAlarm(DateTime dt) {
    
  display.setFont(&FreeMono9pt7b); 
  display.setTextSize(0);
  display.setCursor(0, 40);
  display.print(dt.hour());
  display.print(':');
  display.setCursor(30, 40);
  display.print(dt.minute());
  display.print(':');
  display.setCursor(60, 40);
  display.print(dt.second());
  display.setCursor(90, 40);
  
  switch (dt.dayOfTheWeek()) {
    case 0:
      display.println("C");
      break;
    case 1:
      display.println("L");
      break;
    case 2:
      display.println("F");
      break;
    case 3:
      display.println("T");
      break;
    case 4:
      display.println("C");
      break;
    case 5:
      display.println("L");
      break;
    case 6:
      display.println("F");
      break;
  }
  display.println();
  display.display();
}

void printDateTime(DateTime dt) {
    
  display.setFont(&FreeMono9pt7b); 
  display.setTextSize(0);
  display.setCursor(0, 40);
  display.print(dt.hour());
  display.print(':');
  display.setCursor(30, 40);
  display.print(dt.minute());
  display.print(':');
  display.setCursor(60, 40);
  display.print(dt.second());
  display.setCursor(90, 40);
  
  switch (dt.dayOfTheWeek()) {
    case 0:
      display.println("CN");
      break;
    case 1:
      display.println("T2");
      break;
    case 2:
      display.println("T3");
      break;
    case 3:
      display.println("T4");
      break;
    case 4:
      display.println("T5");
      break;
    case 5:
      display.println("T6");
      break;
    case 6:
      display.println("T7");
      break;
  }

  display.println();
  display.display();
}

bool pressDetect(int button) {
  if (button != lastButtonState && millis() - lastDebounceTime > debounceDelay) {
    lastDebounceTime = millis();
    lastButtonState = button; 
    if (button == LOW) {
    Serial.println("pressed");
    return true; 
    }
  }
  return false;
}
void goToSleep()
{
  int menuSelectButtonState = digitalRead(menuSelectButtonPin);
  int button1State = digitalRead(button1Pin);
  int button2State = digitalRead(button2Pin);
  static unsigned long startSleep;
  static bool anyButtonPressed = false; 


  if (button1State == LOW || button2State == LOW || menuSelectButtonState == LOW)
  {
    Serial.println(startSleep);
    startSleep = millis();
    anyButtonPressed = true;
  }
  else
  {
    
    anyButtonPressed = false;
    
  }


  if (!anyButtonPressed && !buzzerOn && millis() - startSleep > 10000)
  {
    Serial.println("Get a nap");
    display.ssd1306_command(SSD1306_DISPLAYOFF);
    delay(100);
    ESP.deepSleep(0);
  }

}
