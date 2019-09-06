//#include "pins_arduino.h"

#define frameEndPin 6
#define slaveReadyPin 7

#define enable_attrib_byte  0x0D
#define disable_attrib_byte 0x00
#define send_no_sel_to      0x00

#define NO_SERIES 0
#define SYNC_SERIES 1
#define EDIT_TPADS_SERIES 2
#define EDIT_SELECT_SERIES 3

// 0 = Not In Series
// 1 = Sync
// 2 = Edit T-Pads
// 3 = Edit Select
int current_series = 0;

int series_count = 0;

byte rec_data = 0;
byte send_data = 0;

byte virt1_select = 0;
byte virt2_select = 0xFF;

byte v1_forward = 0;
byte v1_back = 0;
byte v1_left = 0;
byte v1_right = 0;
byte v1_a = 0;
byte v1_b = 0;
byte v1_x = 0;
byte v1_y = 0;
byte v1_slow = 0;

byte rec_attrib_byte;
byte rec_priority_byte;
byte rec_tpads[17];
byte rec_select[8];


void setup(void)
{
  Serial.begin(115200);

  pinMode(MISO, OUTPUT);  // have to send on master in, *slave out*

  pinMode(frameEndPin, INPUT);
  pinMode(slaveReadyPin, OUTPUT);

  SPCR |= _BV(SPE);  // turn on SPI in slave mode
  SPCR |= _BV(SPIE);  // turn on interrupts
}


void loop(void)
{
  while (Serial.available() > 0) {
    char inp = Serial.read();
    if (inp == '\n') {
      continue;
    }
    v1_forward = 0;
    v1_back = 0;
    v1_left = 0;
    v1_right = 0;
    v1_a = 0;
    v1_b = 0;
    v1_x = 0;
    v1_y = 0;
    switch (inp) {
      case 'w':
        v1_forward = 1;
        break;
      case 'a':
        v1_left = 1;
        break;
      case 's':
        v1_back = 1;
        break;
      case 'd':
        v1_right = 1;
        break;
      case 'u':
        v1_a = 1;
        break;
      case 'i':
        v1_b = 1;
        break;
      case 'o':
        v1_x = 1;
        break;
      case 'p':
        v1_y = 1;
        break;
    }
  }
}


ISR (SPI_STC_vect)
{
  digitalWrite(slaveReadyPin, HIGH); // We are NOT ready for a new byte.

  byte rec_data = SPDR;
  // Serial.println(rec_data, HEX);

  // NO SERIES
  if (current_series == NO_SERIES) {
    if (rec_data == 0xc6) {
      current_series = SYNC_SERIES;
      series_count = 1;
      send_data = 0x81;

    } else if (rec_data == 0xc3) {
      current_series = EDIT_TPADS_SERIES;
      series_count = 1;
      send_data = 0x80;

    } else if (rec_data == 0xc4) {
      current_series = EDIT_SELECT_SERIES;
      series_count = 1;
      send_data = 0x80;

    } else {
      current_series = NO_SERIES;
      series_count = 0;
      send_data = 0x00;
    }


    // SYNC SERIES
  } else if (current_series == SYNC_SERIES) {
    if (series_count == 1) {
      series_count = 2;
      send_data = enable_attrib_byte;

    } else if (series_count == 2) {
      current_series = NO_SERIES;
      series_count = 0;
      send_data = send_no_sel_to;
    }


    // EDIT TPADS SERIES
  } else if (current_series == EDIT_TPADS_SERIES) {
    if (series_count == 1) {
      series_count = 2;
      rec_tpads[0] = rec_data; // Select
      send_data = rec_tpads[0] & 0b11001111;

    } else if (series_count == 2) {
      series_count = 3;
      rec_tpads[1] = rec_data; // Left Trigger (Last Select)
      send_data = rec_tpads[1] & 0b11001111;

    } else if (series_count == 3) {
      series_count = 4;
      rec_tpads[2] = rec_data; // Sharing Mode (1 = allow sharing);
      send_data = rec_tpads[2] & 0b11001111;

    } else if (series_count == 4) {
      series_count = 5;
      rec_tpads[3] = rec_data; // RESERVED
      send_data = rec_tpads[3];

    } else if (series_count == 5) {
      series_count = 6;
      rec_tpads[4] = rec_data; // IS16SEL?
      send_data = 0xFF; //rec_tpads[4] & 0b11001111;

    } else if (series_count == 6) {
      series_count = 7;
      rec_tpads[5] = rec_data; // D Pad Up
      if (v1_forward == 0) {
        send_data = rec_tpads[5] & 0b11101111;
      } else {
        send_data = rec_tpads[5] | 0b00010000;
      }

    } else if (series_count == 7) {
      series_count = 8;
      rec_tpads[6] = rec_data; // D Pad Down
      if (v1_back == 0) {
        send_data = rec_tpads[6] & 0b11101111;
      } else {
        send_data = rec_tpads[6] | 0b00010000;
      }

    } else if (series_count == 8) {
      series_count = 9;
      rec_tpads[7] = rec_data; // D Pad Right
      if (v1_right == 0) {
        send_data = rec_tpads[7] & 0b11101111;
      } else {
        send_data = rec_tpads[7] | 0b00010000;
      }

    } else if (series_count == 9) {
      series_count = 10;
      rec_tpads[8] = rec_data; // D Pad Left
      if (v1_left == 0) {
        send_data = rec_tpads[8] & 0b11101111;
      } else {
        send_data = rec_tpads[8] | 0b00010000;
      }

    } else if (series_count == 10) {
      series_count = 11;
      rec_tpads[9] = rec_data; // A
      if (v1_a == 0) {
        send_data = rec_tpads[9] & 0b11101111;
      } else {
        send_data = rec_tpads[9] | 0b00010000;
      }

    } else if (series_count == 11) {
      series_count = 12;
      rec_tpads[10] = rec_data; // B
      if (v1_b == 0) {
        send_data = rec_tpads[10] & 0b11101111;
      } else {
        send_data = rec_tpads[10] | 0b00010000;
      }

    } else if (series_count == 12) {
      series_count = 13;
      rec_tpads[11] = rec_data; // X
      if (v1_x == 0) {
        send_data = rec_tpads[11] & 0b11101111;
      } else {
        send_data = rec_tpads[11] | 0b00010000;
      }

    } else if (series_count == 13) {
      series_count = 14;
      rec_tpads[12] = rec_data; // Y
      if (v1_y == 0) {
        send_data = rec_tpads[12] & 0b11101111;
      } else {
        send_data = rec_tpads[12] | 0b00010000;
      }

    } else if (series_count == 14) {
      series_count = 15;
      rec_tpads[13] = rec_data; // RESERVED
      send_data = rec_tpads[13];

    } else if (series_count == 15) {
      series_count = 16;
      rec_tpads[14] = rec_data; // RESERVED
      send_data = rec_tpads[14];

    } else if (series_count == 16) {
      series_count = 17;
      rec_tpads[15] = rec_data; // Right Trigger (Slow)
      if (v1_slow == 0) {
        send_data = rec_tpads[15] & 0b11101111;
      } else {
        send_data = rec_tpads[15] | 0b00010000;
      }

    } else if (series_count == 17) {
      series_count = 18;
      rec_tpads[16] = rec_data; // Spare
      send_data = rec_tpads[16];

    } else if (series_count == 18) {
      current_series = NO_SERIES;
      series_count = 0;
      rec_priority_byte = rec_data; // Priority Byte
      send_data = rec_priority_byte | 0b00110000; //rec_priority_byte;
    }


    // EDIT SELECT SERIES
  } else if (current_series == EDIT_SELECT_SERIES) {
    if (series_count == 1) {
      series_count = 2;
      rec_select[0] = rec_data;
      send_data = rec_select[0];

    } else if (series_count == 2) {
      series_count = 3;
      rec_select[1] = rec_data;
      send_data = rec_select[1];

    } else if (series_count == 3) {
      series_count = 4;
      rec_select[2] = rec_data;
      send_data = rec_select[2];

    } else if (series_count == 4) {
      series_count = 5;
      rec_select[3] = rec_data;
      send_data = rec_select[3];

    } else if (series_count == 5) {
      series_count = 6;
      rec_select[4] = rec_data;
      send_data = virt1_select;

    } else if (series_count == 6) {
      series_count = 7;
      rec_select[5] = rec_data;
      send_data = virt2_select;

    } else if (series_count == 7) {
      series_count = 8;
      rec_select[6] = rec_data;
      send_data = 0xFF;

    } else if (series_count == 8) {
      series_count = 9;
      rec_select[7] = rec_data;
      send_data = 0xFF;

    } else if (series_count == 9) {
      current_series = NO_SERIES;
      series_count = 0;
      send_data = 0x00;
      // Timer Value Received, Send Null
    }


    // CATCH ALL
  } else {
    current_series = NO_SERIES;
    series_count = 0;
    send_data = 0x00;
  }

  SPDR = send_data;

  digitalWrite(slaveReadyPin, LOW); // We are ready for a new byte.
}
