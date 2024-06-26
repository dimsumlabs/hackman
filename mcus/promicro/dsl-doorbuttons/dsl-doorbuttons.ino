/*
 DSL door buttons
*/
#include <Adafruit_NeoPixel.h>
#include <Keyboard.h>

enum led_mode {
  LED_MODE_NORMAL = 0,
  LED_MODE_RED = 1,
  LED_MODE_GREEN = 2,
  LED_MODE_BLUE = 3,
  LED_MODE_RAINBOW = 10
};

// Constants
const unsigned long debounceDelay = 10;     // the debounce time; increase if the output flickers
const int ledBrightness = 100;              // the full brightness of the LED
const unsigned long ledLeaveOnTime = 1000;  // the length of time in millis to decay the light
const unsigned long decayNumer = 800;       // brightness decay numerator (gamma)
const unsigned long decayDenom = 1000;      // brightness decay denominator (gamma)

class ChonkerButton {
private:
  // Setup devices
  int buttonPin;
  Adafruit_NeoPixel* strip;
  int ledPin;    // the number of the LED pin
  int ledCount;  // the number of LEDs

  // Variables
  int buttonState;                     // the current reading from the input pin
  int lastButtonState = HIGH;          // the previous reading from the input pin
  int buttonPressed = LOW;             // the state when the button is pressed
  unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
  unsigned long lastLitTime = 0;       // the last time the LEDs are lit
  led_mode ledMode = LED_MODE_NORMAL;

public:
  ChonkerButton(int button_pin, int led_pin, int led_count) {
    buttonPin = button_pin;
    ledPin = led_pin;
    ledCount = led_count;
    strip = new Adafruit_NeoPixel(led_count, led_pin, NEO_GRB + NEO_KHZ800);
  }

  void setup() {
    pinMode(buttonPin, INPUT);
    digitalWrite(buttonPin, lastButtonState);
    strip->begin();
    strip->show();
  }

  /** returns true if button is just pushed (pressed and released) */
  uint8_t checkButtonPush() {
    // read the state of the switch into a local variable:
    int reading = digitalRead(buttonPin);
    uint8_t pushed = 0;

    // If the switch changed, due to noise or pressing:
    if (reading != lastButtonState) {
      // reset the debouncing timer
      lastDebounceTime = millis();
    }

    if ((millis() - lastDebounceTime) > debounceDelay) {
      // whatever the reading is at, it's been there for longer than the debounce
      // delay, so take it as the actual current state:

      // if the button state has changed:
      if (reading != buttonState) {
        buttonState = reading;

        // only send command if the new button state is triggered
        if (buttonState == buttonPressed) {
          // light up the key
          if (ledMode == LED_MODE_NORMAL) {
            strip->setBrightness(ledBrightness);
            colorAll(strip->Color(255, 255, 255), 10);
            lastLitTime = millis();
          }
        } else {
          pushed = 1;
        }
      }
    }

    // fade lit LEDs due to button press
    unsigned long sinceLastLit = millis() - lastLitTime;
    if (ledMode == LED_MODE_NORMAL && buttonState != buttonPressed && sinceLastLit <= ledLeaveOnTime) {
      uint8_t brightness = (ledLeaveOnTime - sinceLastLit) * ledBrightness / ledLeaveOnTime * decayNumer / decayDenom;
      strip->setBrightness(brightness);
      strip->show();
    }

    // save the reading. Next time through the loop, it'll be the lastButtonState:
    lastButtonState = reading;
    return pushed;
  }

  void setLEDMode(led_mode m) {
    ledMode = m;

    strip->setBrightness(ledBrightness);
    switch (m) {
      case LED_MODE_RED:
        colorBase(strip->Color(255, 0, 0), 0);
        break;

      case LED_MODE_GREEN:
        colorBase(strip->Color(0, 255, 0), 0);
        break;

      case LED_MODE_BLUE:
        colorBase(strip->Color(0, 0, 255), 0);
        break;

      case LED_MODE_RAINBOW:
        colorBaseRainbow(0, 1, 255, 255);
        break;

      default:
        colorAll(strip->Color(0, 0, 0), 0);
        break;
    }
  }

  void colorAll(uint32_t color, int wait) {
    for (int i = 0; i < strip->numPixels(); i++) {  // For each pixel in strip...
      strip->setPixelColor(i, color);               //  Set pixel's color (in RAM)
      strip->show();                                //  Update strip to match
      if (wait > 0) {
        delay(wait);  //  Pause for a moment
      }
    }
  }

  void colorBase(uint32_t color, int wait) {
    strip->setPixelColor(0, strip->Color(0, 0, 0));
    for (int i = 1; i < strip->numPixels(); i++) {  // For each pixel in strip...
      strip->setPixelColor(i, color);               //  Set pixel's color (in RAM)
      strip->show();                                //  Update strip to match
      if (wait > 0) {
        delay(wait);  //  Pause for a moment
      }
    }
  }

  void colorBaseRainbow(uint16_t first_hue, int8_t reps,
                        uint8_t saturation, uint8_t brightness) {
    for (uint16_t i = 0; i < strip->numPixels() - 1; i++) {
      uint16_t hue = first_hue + (i * reps * 65536) / (strip->numPixels() - 1);
      uint32_t color = strip->ColorHSV(hue, saturation, brightness);
      strip->setPixelColor(i + 1, color);
    }
    strip->show();
  }
};

ChonkerButton openButton(2, 21, 7);
ChonkerButton unlockButton(3, 20, 4);
ChonkerButton bellButton(4, 19, 4);

void setup() {
  Serial.begin(9600);
  Keyboard.begin();
  openButton.setup();
  unlockButton.setup();
  bellButton.setup();
}

void loop() {
  if (openButton.checkButtonPush()) {
    // open
    Keyboard.press(KEY_LEFT_CTRL);
    Keyboard.press(KEY_LEFT_SHIFT);
    Keyboard.press(';');
    Keyboard.releaseAll();
  }
  if (unlockButton.checkButtonPush()) {
    // unlock
    Keyboard.press(KEY_LEFT_CTRL);
    Keyboard.press(KEY_LEFT_SHIFT);
    Keyboard.press('|');
    Keyboard.releaseAll();
  }
  if (bellButton.checkButtonPush()) {
    // bell
    Keyboard.press(KEY_LEFT_CTRL);
    Keyboard.press(KEY_LEFT_SHIFT);
    Keyboard.press(',');
    Keyboard.releaseAll();
  }

  if (Serial.available() > 0) {
    uint8_t in = Serial.read();
    switch (in) {
      case 'R':
        openButton.setLEDMode(LED_MODE_RED);
        unlockButton.setLEDMode(LED_MODE_RED);
        bellButton.setLEDMode(LED_MODE_NORMAL);
        break;

      case 'G':
        openButton.setLEDMode(LED_MODE_GREEN);
        unlockButton.setLEDMode(LED_MODE_GREEN);
        bellButton.setLEDMode(LED_MODE_GREEN);
        break;

      case 'B':
        openButton.setLEDMode(LED_MODE_BLUE);
        unlockButton.setLEDMode(LED_MODE_NORMAL);
        bellButton.setLEDMode(LED_MODE_NORMAL);
        break;

      case 'N':
        openButton.setLEDMode(LED_MODE_RAINBOW);
        unlockButton.setLEDMode(LED_MODE_NORMAL);
        bellButton.setLEDMode(LED_MODE_NORMAL);
        break;

      default:
        openButton.setLEDMode(LED_MODE_NORMAL);
        unlockButton.setLEDMode(LED_MODE_NORMAL);
        bellButton.setLEDMode(LED_MODE_NORMAL);
        break;
    }
  }
}