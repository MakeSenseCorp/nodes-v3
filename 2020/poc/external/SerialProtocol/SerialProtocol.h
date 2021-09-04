#ifndef SerialProtocol_h
#define SerialProtocol_h

#include "Arduino.h"

#define MAX_LENGTH 									  64
#define MAX_COMMAND_TABLE_SIZE        128
#define DEVICE_TYPE_SIZE              4
#define MKS_HEADER_SIZE               5
#define DEVICE_ADDITIONAL_SIZE        2
#define DEVICE_ADDRESS_SIZE           1

#define OPCODE_GET_CONFIG_REGISTER                    1
#define OPCODE_SET_CONFIG_REGISTER                    2
#define OPCODE_GET_BASIC_SENSOR_VALUE                 3
#define OPCODE_SET_BASIC_SENSOR_VALUE                 4
#define OPCODE_PAUSE_WITH_TIMEOUT                     5

#define OPCODE_GET_DEVICE_TYPE                        50
#define OPCODE_GET_DEVICE_UUID                        51
#define OPCODE_GET_DEVICE_ADDITIONAL                  52
#define OPCODE_HEARTBEAT                              53

#define OPCODE_RX_DATA                                100
#define OPCODE_TX_DATA                                101
#define OPCODE_SET_ADDRESS                            102
#define OPCODE_GET_ADDRESS                            103
#define OPCODE_ADD_NODE_INDEX                         105
#define OPCODE_DEL_NODE_INDEX                         106
#define OPCODE_GET_NODE_INFO                          107
#define OPCODE_GET_NODES_MAP                          108
#define OPCODE_GET_NODES_LIST                         109
#define OPCODE_SET_NODES_DATA                         110
#define OPCODE_GET_NODES_DATA                         111
#define OPCODE_DEVICE_COMM_LOSS                       112

#define MKS_ACK                                       0x1
#define MKS_NACK                                      0x2

#define SYNC_REQUEST                                  0x1
#define SYNC_RESPONSE                                 0x2
#define ASYNC                                         0x3

#define GATWAY			0x2
#define NODE			  0x3

typedef int	(*SerialCallbackPtr)(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);

typedef struct {
  unsigned char     command;
  SerialCallbackPtr handler;
} commands_table_t;

typedef struct {
  unsigned char type;
  unsigned char payload_length;
} node_info_header_t;

typedef struct {
  unsigned char     type;
  unsigned short    value;
} node_sensor_t;

struct mks_header {
  unsigned char   magic_number[2];
  unsigned char   direction;
  unsigned char   op_code;
  unsigned char   content_length;
};

void blink(unsigned int interval);
int read_serial_buffer();
void handler_serial(commands_table_t* handler_table, uint8_t length);
unsigned char find_handler_index(unsigned char command, commands_table_t* handler_table, uint8_t length);
void send_data_to_master(uint8_t opcode, uint8_t* payload, uint16_t size);
void send_async_data_to_uart(uint16_t opcode, uint8_t* payload, uint16_t size);
#endif
