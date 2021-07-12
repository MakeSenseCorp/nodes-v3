#include <SerialProtocol.h>
#include <EEPROM.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define MAX_NODES_INDEX 32
#define SERIAL_COMMAND_TABLE_SIZE 18

typedef struct {
  uint8_t node_id;
  uint8_t opcode;
  uint8_t size;
  uint8_t payload[12];
  uint8_t crc;
} message_t;

void check_timeout_nodes(void);
void initiate_radio(void);
void itterate_radio(void);
uint8_t itterate_serial(void);
uint8_t append_polling_node(uint8_t node_id);
uint8_t remove_polling_node(uint8_t node_id);

int get_config_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int set_config_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_basic_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int set_basic_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int pause_with_timeout(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_device_type(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_device_uuid(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_device_additional(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int heartbeat(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int rx_data(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int tx_data(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int set_address(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_address(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int add_node_index(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int del_node_index(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_node_info(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_nodes_map(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_nodes_list(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);

commands_table_t handlers_map[] = {
  { OPCODE_GET_CONFIG_REGISTER,     get_config_registor },
  { OPCODE_SET_CONFIG_REGISTER,     set_config_registor },
  { OPCODE_GET_BASIC_SENSOR_VALUE,  get_basic_registor },
  { OPCODE_SET_BASIC_SENSOR_VALUE,  set_basic_registor },
  { OPCODE_PAUSE_WITH_TIMEOUT,      pause_with_timeout },
  { OPCODE_GET_DEVICE_TYPE,         get_device_type },
  { OPCODE_GET_DEVICE_UUID,         get_device_uuid },
  { OPCODE_GET_DEVICE_ADDITIONAL,   get_device_additional },
  { OPCODE_HEARTBEAT,               heartbeat },
  { OPCODE_SET_ADDRESS,             set_address},
  { OPCODE_GET_ADDRESS,             get_address},
  { OPCODE_ADD_NODE_INDEX,          add_node_index},
  { OPCODE_DEL_NODE_INDEX,          del_node_index},
  { OPCODE_GET_NODE_INFO,           get_node_info},
  { OPCODE_GET_NODES_MAP,           get_nodes_map},
  { OPCODE_RX_DATA,                 rx_data },
  { OPCODE_TX_DATA,                 tx_data },
  { OPCODE_GET_NODES_LIST,          get_nodes_list }
};

uint8_t polling_nodes[MAX_NODES_INDEX] = {  1,2,5,0,0,0,0,0,0,0,
                                            0,0,0,0,0,0,0,0,0,0,
                                            0,0,0,0,0,0,0,0,0,0,
                                            0,0};
typedef struct {
  // uint8_t last_message[16];
  uint8_t status;
  uint8_t timeout_count;
} sensor_db_t;
sensor_db_t polling_nodes_db[MAX_NODES_INDEX];

uint8_t polling_nodes_count = 3;
uint8_t current_polling_node_index = 0;

unsigned char DEVICE_TYPE[] = { '2','0','2','0' };
unsigned char DEVICE_SUB_TYPE = GATWAY;
unsigned char NODE_ID = 0;

RF24 radio(7, 8); // CE, CSN
const byte rx[6] = "00001";
const byte tx[6] = "00002";
byte nrf_rx_buff[16];
byte nrf_tx_buff[16];
message_t* rx_buff_ptr = (message_t *)nrf_rx_buff;
message_t* tx_buff_ptr = (message_t *)nrf_tx_buff;

void initiate_radio(void) {
  radio.begin();
  radio.enableAckPayload();
  radio.openWritingPipe(tx);
  radio.openReadingPipe(1,rx);
  radio.setPALevel(RF24_PA_MAX);
  radio.stopListening();
}

void itterate_radio(void) {
  if (polling_nodes_count) {

    unsigned long started_waiting_at = millis();
    bool timeout = false;
    
    tx_buff_ptr->node_id  = polling_nodes[current_polling_node_index];
    tx_buff_ptr->opcode   = OPCODE_GET_NODE_INFO;
    tx_buff_ptr->size     = 1;
    tx_buff_ptr->crc      = 0xff;

    radio.stopListening();
    radio.write(&nrf_tx_buff, sizeof(nrf_tx_buff));
    radio.startListening();

    while (!radio.available() && !timeout) {
      if (millis() - started_waiting_at > 1000) {
        timeout = true;
      } 
    }

    if (timeout) {
      if (polling_nodes_db[tx_buff_ptr->node_id-1].timeout_count > 5) {
        polling_nodes_db[tx_buff_ptr->node_id-1].status = 0;
      } else {
        polling_nodes_db[tx_buff_ptr->node_id-1].timeout_count++;
      }
    } else {
      radio.read(&nrf_rx_buff, sizeof(nrf_rx_buff));

      // Update locla DB
      // memcpy((polling_nodes_db[rx_buff_ptr->node_id-1].last_message), nrf_rx_buff, sizeof(message_t));
      polling_nodes_db[tx_buff_ptr->node_id-1].status = 1;
      polling_nodes_db[tx_buff_ptr->node_id-1].timeout_count = 0;

      delay(1000);
    }

    // Next node
    current_polling_node_index++; 
    if (current_polling_node_index == MAX_NODES_INDEX || 
        current_polling_node_index == polling_nodes_count)
    {
      current_polling_node_index = 0;
    }
  }
}

uint8_t itterate_serial(void) {
  int len = 0;
  if (read_serial_buffer()) {
    handler_serial(handlers_map, SERIAL_COMMAND_TABLE_SIZE);
    return 1;
  }

  return 0;
}

uint8_t append_polling_node(uint8_t node_id) {
  if (polling_nodes_count > MAX_NODES_INDEX) {
    return 0x1;
  }

  polling_nodes[polling_nodes_count] = node_id;
  polling_nodes_count++;

  return 0x0;
}

uint8_t remove_polling_node(uint8_t node_id) {
  if (!polling_nodes_count) {
    return 0x0;
  }

  for (uint8_t i = 0; i < MAX_NODES_INDEX-1; i++) {
    if (node_id == polling_nodes[i]) {
      // Found you node and we need to fill the hole if exist
      if (i == (polling_nodes_count-1)) {
        // The last in poll
        polling_nodes[i] = 0;
      } else {
        uint8_t nodes_id_move_count = (polling_nodes_count-1) - i;
        for (uint8_t j = i; j < i + nodes_id_move_count + 1; j++) {
          polling_nodes[j] = polling_nodes[j+1];
        }
        polling_nodes[i + nodes_id_move_count] = 0;
      }
      polling_nodes_count--;
      break;
    }
  }

  return 0x0;
}

void setup() {
  Serial.begin(115200);
  delay(10);
  
  Serial.println("Loading Firmware ...");
  Serial.print("Initiate Radio... ");
  initiate_radio();
  Serial.println("Done.");

  pinMode(LED_BUILTIN, OUTPUT);
  NODE_ID = EEPROM.read(0);

  for (uint8_t i = 0; i < MAX_NODES_INDEX; i++) {
    polling_nodes_db[i].timeout_count = 0;
    polling_nodes_db[i].status        = 0;
  }
}

void loop() {
  // itterate_serial();
  if (itterate_serial()) {
  } else {
    itterate_radio();
  }

  delay(10);
}

int get_config_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int set_config_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int get_basic_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int set_basic_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int pause_with_timeout(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int get_device_type(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  memcpy(buff_tx, DEVICE_TYPE, DEVICE_TYPE_SIZE);
}

int get_device_uuid(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int get_device_additional(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  buff_tx[0] = DEVICE_SUB_TYPE;
  buff_tx[1] = NODE_ID;
}

int heartbeat(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int rx_data(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  unsigned long started_waiting_at = millis();
  bool timeout = false;

  uint8_t node_id = buff_rx[0];
  uint8_t opcode  = buff_rx[1];
  uint8_t size    = buff_rx[2];

  tx_buff_ptr->node_id  = node_id;
  tx_buff_ptr->opcode   = opcode;
  tx_buff_ptr->size     = size;
  tx_buff_ptr->crc      = 0xff;
  
  radio.stopListening();
  radio.write(&nrf_tx_buff, sizeof(nrf_tx_buff));
  radio.startListening();

  while (!radio.available() && !timeout) {
    if (millis() - started_waiting_at > 1000) {
      timeout = true;
    }
  }

  if (timeout) {
    if (polling_nodes_db[tx_buff_ptr->node_id-1].timeout_count > 5) {
      polling_nodes_db[tx_buff_ptr->node_id-1].status = 0;
    } else {
      polling_nodes_db[tx_buff_ptr->node_id-1].timeout_count++;
    }
  } else {
    radio.read(&nrf_rx_buff, sizeof(nrf_rx_buff));
    // Update locla DB
    // memcpy((polling_nodes_db[rx_buff_ptr->node_id-1].last_message), nrf_rx_buff, sizeof(message_t));
    polling_nodes_db[rx_buff_ptr->node_id-1].status         = 1;
    polling_nodes_db[rx_buff_ptr->node_id-1].timeout_count  = 0;
  }

  memcpy(buff_tx, nrf_rx_buff, sizeof(nrf_rx_buff));
  memset(nrf_tx_buff, 0x0, sizeof(nrf_tx_buff));
  memset(nrf_rx_buff, 0x0, sizeof(nrf_rx_buff));

  return sizeof(nrf_rx_buff);
}

int tx_data(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {

}

int set_address(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  EEPROM.write(0, buff_rx[0]);
  NODE_ID = EEPROM.read(0);
  buff_tx[0] = NODE_ID;
}

int get_address(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  NODE_ID = EEPROM.read(0);
  buff_tx[0] = NODE_ID;
}

int add_node_index(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  uint8_t index = buff_rx[0];
  uint8_t status = append_polling_node(index);
  if (!status) {
    buff_tx[0] = index;
  } else {
    buff_tx[0] = 0;
  }

  return 1;
}

int del_node_index(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  uint8_t index = buff_rx[0];
  uint8_t status = remove_polling_node(index);
  if (!status) {
    buff_tx[0] = index;
  } else {
    buff_tx[0] = 0;
  }

  return 1;
}

int get_node_info(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  node_info_header_t* node_header = (node_info_header_t*)buff_tx;
  node_header->type = DEVICE_SUB_TYPE;
  node_header->payload_length = 0;
  return sizeof(node_info_header_t);
}

int get_nodes_map(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  memcpy(buff_tx, polling_nodes, sizeof(polling_nodes));
  return sizeof(polling_nodes);
}

int get_nodes_list(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  uint16_t offset = 0;
  for (uint8_t i = 0; i < polling_nodes_count; i++) {
    buff_tx[offset] = polling_nodes[i]; // node_id
    offset++;
    buff_tx[offset] = polling_nodes_db[polling_nodes[i]-1].status; // status
    offset++;
  }

  return offset;
}
