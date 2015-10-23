/*
/	A ONE-WIRE LIBRARY FOR THE DALLAS DS18B20D TEMPERATURE SENSOR	/
/	WRITTEN BY SARGIS S YONAN	-	21 OCTOBER 2015					/
/	CODE PARTIALLY BORROWED FROM MIKE RODDEWIG (mike@dietfig.org)	/
/	OPTIMIZED FOR THE ATMEL AVR ATMEGA 2560 MICROCONTROLLER			/
*/

// OneWire.h

#ifndef ONEWIRE_H
#define ONEWIRE_H

/////////////
// Defines //
/////////////

// AVR clock frequency
#define F_CPU 16000000UL // 16 MHz

// Pin defines

#define DALLAS_PORT 	PORTC
#define DALLAS_PORT_IN 	PINC
#define DALLAS_DDR 		DDRC
#define DALLAS_PIN 		0

// The number of devices on the bus.
#define DALLAS_NUM_DEVICES 1

// The number of bits in an identifier.
#define DALLAS_NUM_IDENTIFIER_BITS 64

// One Wire Commands
#define MATCH_ROM_COMMAND 			0x55
#define SKIP_ROM_COMMAND			0xCC
#define SEARCH_ROM_COMMAND 			0xF0
#define READ_ROM_COMMAND 			0x33
#define CONVERT_TEMP__COMMAND 		0x44
#define READ_SCRATCHPAD_COMMAND 	0xBE


//Paku - add timing constants to be used across lib

//timing details in uS
#define DALLAS_TIME_FRAME 		120 //target at least 60us
#define DALLAS_TIME_ONE   		5 	//target not more then 15us
#define DALLAS_TIME_ZERO  		90 	//target at least 60us

#define DALLAS_TIME_RESET  		500 //8xframe or 480us at least
#define DALLAS_TIME_PRESENCE  	50 	//slave response pull down for at least 60us, start it no later then 60us after reset end.

#define DALLAS_TIME_COMMAND_REST 1  //let bus stabilize after each byte sent.


////////////////
// Structures //
////////////////

typedef struct {
	uint8_t identifier[DALLAS_NUM_IDENTIFIER_BITS / 8];
} DALLAS_IDENTIFIER_t;

typedef struct {
	DALLAS_IDENTIFIER_t identifiers[DALLAS_NUM_DEVICES];
	uint8_t num_devices;
} DALLAS_IDENTIFIER_LIST_t;

///////////////
// Functions //
///////////////

// Writes the LSB of the argument to the bus.
void dallas_write(uint8_t);

// Write a byte to the bus.
void dallas_write_byte(uint8_t);

// Write the specified number of bytes to the bus from the supplied buffer.
void dallas_write_buffer(uint8_t * buffer, uint8_t buffer_length);

// Read a bit from the bus and returns it as the LSB.
uint8_t dallas_read(void);

// Reads a byte from the bus.
uint8_t dallas_read_byte(void);

// Reads the specified number of bytes from the bus into the supplied buffer.
void dallas_read_buffer(uint8_t * buffer, uint8_t buffer_length);

// Resets the bus. Returns...
// 1 - if a device or devices indicate presence
// 0 - otherwise
uint8_t dallas_reset(void);

// Powers the bus from the AVR (max 40 mA).
void dallas_drive_bus(void);

// Sends a MATCH ROM command to the specified device. Automatically resets the
// bus.
void dallas_match_rom(DALLAS_IDENTIFIER_t *);

// Sends a SKIP ROM command. Automatically resets the bus.
void dallas_skip_rom(void);

// Populates the identifier list. Returns...
// 0 - if devices were found and there was no error
// 1 - if there was a bus error
// 2 - if there were more devices than specified by DALLAS_NUM_DEVICES
uint8_t dallas_search_identifiers(void);

// Returns the list of identifiers.
DALLAS_IDENTIFIER_LIST_t * get_identifier_list(void);

uint8_t dallas_command(uint8_t command, uint8_t with_reset);


#endif