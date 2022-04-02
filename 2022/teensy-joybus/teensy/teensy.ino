#include <stdint.h>
#include "common.h"

// True joybus uses only 1 pin for both directions, but the GBA<->GC adapter
// separates the two channels onto the gameboy's SI and SO pins.
//
// This code is assuming that the teensy is connected to the gameboy link port
// through an original gameboy / GBC cable (the one with crossed SI/SO lines).
//
// If connecting to the teensy through a GC<->GBA adapter, will need to modify
// the code to use only a single pin, but the protocol is the same.
//
// A standard multiplay GBA cable will NOT work because the small end's SI pin
// is disconnected.
#define PIN_SO 3 // Gameboy input, arduino output
#define PIN_SI 4 // Gameboy output, arduino input

// State of game (these states basically copied from original python code)
typedef enum {
  LINK_STATE_IDLE = 0,
} link_state_t;

link_state_t link_state = LINK_STATE_IDLE;


// Macros copied from https://github.com/PaulStoffregen/cores/teensy3/pins_arduino.h
// May not work on different teensy models, much less arduino
#define digitalPinToBitMask(pin) (digital_pin_to_info_PGM[(pin)].mask)
#define portOutputRegister(pin) ((digital_pin_to_info_PGM[(pin)].reg + 0))
#define portSetRegister(pin)    ((digital_pin_to_info_PGM[(pin)].reg + 4))
#define portClearRegister(pin)  ((digital_pin_to_info_PGM[(pin)].reg + 8))
#define portInputRegister(pin)  ((digital_pin_to_info_PGM[(pin)].reg + 16))


const unsigned int siPortBitmask = digitalPinToBitMask(PIN_SI);
const unsigned int soPortBitmask = digitalPinToBitMask(PIN_SO);
volatile byte * const siInputRegister = portInputRegister(PIN_SI);
volatile byte * const soSetRegister = portSetRegister(PIN_SO);
volatile byte * const soUnsetRegister = portClearRegister(PIN_SO);



void msg(const char *format, ...) {
  char msg[256];
  va_list argptr;
  va_start(argptr, format);
  vsprintf(msg, format, argptr);
  va_end(argptr);

  Serial.write(CMD_MSG);
  Serial.write(strlen(msg));
  Serial.write(msg);
}
void ledUp() {
  digitalWrite(13, HIGH);
}

void ledDown() {
  digitalWrite(13, LOW);
}

// Assuming the teensy runs a 48MHz. For instruction clock cycles see:
// https://developer.arm.com/documentation/ddi0484/c/Programmers-Model/Instruction-set-summary?lang=en
void sendData(byte *data, unsigned int numBits) {
  unsigned int bi = 0;
  unsigned int b;

  byte tmpBuf[5 * 8];

  for (unsigned int i = 0; i < numBits; i += 8) {
    byte b = data[i / 8];
    for (int j = 0; j < 8; j++) {
      tmpBuf[i + j] = b & 0x80;
      b <<= 1;
    }
  }

  do {
    *soUnsetRegister = soPortBitmask;

    if (tmpBuf[bi++]) {
      // Send bit 1
      asm volatile ( // 48 clocks (1 microsecond) between setting & unsetting
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop;"
          );

      *soSetRegister = soPortBitmask; // strb opcode probably 1 cycle

      asm volatile ( // 144 clocks (3 microseconds) between unsetting here & setting at start of loop
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop;"
          );
    } else {
      // Send bit 0
      asm volatile ( // 144 clocks (3 microsecond) between setting & unsetting
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop;"
          );

      *soSetRegister = soPortBitmask; // strb opcode probably 1 cycle

      asm volatile ( // 48 clocks (1 microsecond) between unsetting here & setting at start of loop
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
          "nop; nop; nop;"
          );
    }
  }
  while (--numBits > 0);

  // Stop bit
  asm volatile ( "nop; nop; nop" );
  *soUnsetRegister = soPortBitmask;
  asm volatile ( // 48 clocks (1 microsecond)
      "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
      "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
      "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
      "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
      );
  *soSetRegister = soPortBitmask;
    asm volatile ( // 96 clocks (2 microsecond)
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        );

  // This line seems necessary to make the GBA's native joybus mode work
  // properly, but this line also prevents "gba-as-controller" from working??
  // Possibly it is misinterpreting this as another bit?
  *soUnsetRegister = soPortBitmask;
}

// Timing here is not as precise as in "sendData" since we can be flexible with
// how fast the gameboy sends data
int recvData(byte *data, unsigned int numBits) {
  unsigned int bt = 0;
  byte tmpBuf[numBits * 8];

  while (bt < numBits) {
    SYST_CVR = F_CPU * 100 / 1000000; // Counts to 0 in 100 microseconds

    while (*siInputRegister & siPortBitmask) {
      if (SYST_CVR < F_CPU / 1000000) // Wait for timeout
        goto loopEnd;
    }

    asm volatile ( // 1 microsecond
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        );

    int up1 = ((*siInputRegister) & siPortBitmask);

    asm volatile ( // 1 microsecond
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        );
    int up2 = ((*siInputRegister) & siPortBitmask);

    if (!up1 && up2) // Controller stop bit
      break;

    tmpBuf[bt++] = up2;

    asm volatile (
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        "nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;"
        );
  }

loopEnd:
  *soSetRegister = soPortBitmask;

  for (int i = 0; i < numBits; i+=8) {
    data[i / 8] = 0;
    for (int j = 0; j < 8; j++) {
      data[i / 8] <<= 1;
      data[i / 8] |= !!tmpBuf[i + j];
    }
  }

  return bt;
}


void setup() {
  Serial.begin(115200);
  pinMode(13, OUTPUT); // LED
  pinMode(PIN_SI, INPUT_PULLUP);
  pinMode(PIN_SO, OUTPUT);

  digitalWrite(PIN_SO, HIGH);

  // Important to let the gameboy see PIN_SO in high state before we begin.
  delay(100);
}

// We can generally get away without actually knowing the response length,
// except for gba-as-controller. I'm not sure if it's actually sending the
// controller stop bit properly.
int getOpcodeResponseLen(int opcode) {
  switch (opcode) {
  case 0xff: // RESET
  case 0x00: // ID
    return 8 * 4;
  case 0x14: // READ from GBA
    return 8 * 5;
  case 0x15: // WRITE to GBA
    return 8;
  case 0x40: // STATUS
    return 8 * 6;
  case 0x41: // ORIGIN
    return 8 * 10;
  default:
    msg("UNKNOWN OPCODE LEN");
    return 8 * 10;
  }
}

void loop() {
  byte data[0x100];
  int avail;

  while ((avail = Serial.available()) == 0);
  Serial.readBytes((char*)data, avail);
  //msg("GOT %.2x BYTES DATA", avail);
  __disable_irq();
  sendData(data, avail * 8);
  int bitsDesired = getOpcodeResponseLen(data[0]);
  int bitsReceived = recvData(data, bitsDesired);
  if (bitsDesired != bitsReceived) {
    msg("GOT %.2x BITS RESPONSE", bitsReceived);
    msg("WANTED %.2x", bitsDesired);
  }
  __enable_irq();
  if (bitsReceived == 0)
    Serial.write(CMD_NO_RESPONSE);
  else {
    Serial.write(CMD_SEND_DATA);
    Serial.write(bitsReceived / 8);
    Serial.write(data, bitsReceived / 8);
  }


  /*
  if (bitsReceived == 24) {
    Serial.print("RECV: ");
    Serial.println(bitsReceived);
    Serial.println(data[0], HEX);
    Serial.println(data[1], HEX);
    Serial.println(data[2], HEX);
  }
  */
}
