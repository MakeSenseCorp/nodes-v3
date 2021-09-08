#include <SerialProtocol.h>
#include <EEPROM.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <SoftwareSerial.h>

#define MAX_NODES_INDEX             32
#define SERIAL_COMMAND_TABLE_SIZE   18
#define TIMEOUT_DISCONNECT_COUNT    100
#define STATUS_CONNECTED            1
#define STATUS_DISCONNECTED         0

SoftwareSerial debug_serial(2, 3);

typedef struct {
  uint8_t node_id;
  uint8_t opcode;
  uint8_t size;
  uint8_t payload[12];
  uint8_t crc;
} message_t;

typedef struct {
  unsigned long a;
  unsigned long b;
  float freq;
} freq_t;

void check_timeout_nodes(void);
void initiate_radio(void);
void itterate_radio(void);
uint8_t itterate_serial(void);
uint8_t append_polling_node(uint8_t node_id);
uint8_t remove_polling_node(uint8_t node_id);
uint8_t find_index_by_id(uint8_t node_id);

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
  uint8_t last_message[16];
  uint8_t status;
  uint8_t timeout_count;
  uint8_t status_filter;
} sensor_db_t;
sensor_db_t polling_nodes_db[MAX_NODES_INDEX];

uint8_t polling_nodes_count         = 3;
uint8_t current_polling_node_index  = 0;

unsigned char DEVICE_TYPE[] = { '2','0','2','0' };
unsigned char DEVICE_SUB_TYPE = GATWAY;
unsigned char NODE_ID = 0;

RF24 radio(7, 8); // CE, CSN
byte rx[6] = "10000";
byte tx[6] = "20000";
byte nrf_rx_buff[16];
byte nrf_tx_buff[16];
message_t* rx_buff_ptr = (message_t *)nrf_rx_buff;
message_t* tx_buff_ptr = (message_t *)nrf_tx_buff;
freq_t nrf_itter = {0, 0, 0.0};

void initiate_radio(void) {
  radio.begin();
  // radio.setAutoAck( false ) ;
  radio.enableAckPayload();
  // radio.disableAckPayload();
  radio.openWritingPipe(tx);
  radio.openReadingPipe(1,rx);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);
  // radio.setRetries(3,5); // delay, count
  radio.stopListening();
}

void print_tx() {
  debug_serial.print("TX: ");
  for (uint8_t i = 0; i < 16; i++) {
    debug_serial.print(nrf_tx_buff[i], HEX);
    debug_serial.print(" ");
  } debug_serial.println();
}

void print_rx() {
  debug_serial.print("RX: ");
  for (uint8_t i = 0; i < 16; i++) {
    debug_serial.print(nrf_rx_buff[i], HEX);
    debug_serial.print(" ");
  } debug_serial.println();
}

void print_nrf_slaves() {
  debug_serial.println("");
  for (uint8_t i = 0; i < polling_nodes_count; i++) {
    debug_serial.print(polling_nodes[i]);
    debug_serial.print(" ");
    debug_serial.print(polling_nodes_db[i].status);
    debug_serial.print(" ");
    debug_serial.print(polling_nodes_db[i].timeout_count);
    debug_serial.println("");
  }
  debug_serial.println("");
}

void send_client(uint8_t index) {
  bool exit = false;
  uint8_t count = 0;
  uint8_t         status = false;
  sensor_db_t*    tx_sensor_item;
  sensor_db_t*    rx_sensor_item;

  unsigned long start_timer   = 0;
  unsigned long end_timer     = 0;
  unsigned long start_timeout = 0;
  bool report = false;
  uint8_t pipe;

  tx_sensor_item = &polling_nodes_db[index];

  memset(nrf_tx_buff, 0x0, sizeof(nrf_tx_buff));
  memset(nrf_rx_buff, 0x0, sizeof(nrf_rx_buff));
  // Create payload
  tx_buff_ptr->node_id  = polling_nodes[index];
  tx_buff_ptr->opcode   = OPCODE_GET_NODE_INFO;
  tx_buff_ptr->size     = 1;
  tx_buff_ptr->crc      = 0xff;

  // print_tx();

  // Set NRF address according to node id
  tx[0] = (byte)polling_nodes[index];
  radio.openWritingPipe(tx);

  while(!exit && count < 10) {
    // Send
    start_timer = micros();                                     // start the timer
    report = radio.write(&nrf_tx_buff, sizeof(nrf_tx_buff));    // transmit & save the report
    end_timer = micros();                                       // end the timer

    if (report) {
      radio.startListening();                                // put in RX mode
      start_timeout = millis();                              // timer to detect timeout
      while (!radio.available()) {                           // wait for response
        if (millis() - start_timeout > 500) {               // only wait 200 ms
          break;
        }
      }
      radio.stopListening();                                 // put back in TX mode

      if (radio.available(&pipe)) {                          // is there a payload received
        memset(nrf_rx_buff, 0x0, sizeof(nrf_rx_buff));
        radio.read(&nrf_rx_buff, sizeof(nrf_rx_buff));       // get payload from RX FIFO
        // print_rx();
        rx_sensor_item = &polling_nodes_db[find_index_by_id(rx_buff_ptr->node_id)];
        rx_sensor_item->timeout_count = 0;
        rx_sensor_item->status = STATUS_CONNECTED;
        if (rx_buff_ptr->node_id == tx_buff_ptr->node_id) {
          exit = true;
          
          if (memcmp(rx_sensor_item->last_message, nrf_rx_buff, sizeof(nrf_rx_buff))) {
            send_async_data_to_uart(OPCODE_RX_DATA, (uint8_t *)&nrf_rx_buff, sizeof(nrf_rx_buff));
            memcpy(rx_sensor_item->last_message, nrf_rx_buff, sizeof(nrf_rx_buff));
          }
        }
      } else {
        // No data from client
        if (tx_sensor_item->timeout_count < TIMEOUT_DISCONNECT_COUNT) {
          tx_sensor_item->timeout_count++;
        }
      }
    } else {
      if (tx_sensor_item->timeout_count < TIMEOUT_DISCONNECT_COUNT) {
        tx_sensor_item->timeout_count++;
      }
    }

    if (tx_sensor_item->timeout_count >= TIMEOUT_DISCONNECT_COUNT) {
      tx_sensor_item->status = STATUS_DISCONNECTED;
      tx_sensor_item->status_filter++;
      /*
      if (tx_sensor_item->status_filter % 250 == 0) {
        uint8_t node_id = tx_buff_ptr->node_id;
        send_async_data_to_uart(OPCODE_DEVICE_COMM_LOSS, (uint8_t *)&node_id, 1);
        memset(tx_sensor_item->last_message, 0, 16);
      }
      */
    }

    delay(32);
    count++;
  }
}

void handle_nrf_network() {
  send_client(current_polling_node_index);

  // Next node
  current_polling_node_index++; 
  if (current_polling_node_index == MAX_NODES_INDEX || 
      current_polling_node_index == polling_nodes_count) {
    current_polling_node_index = 0;
  }
}

void itterate_radio(void) {  
  if (polling_nodes_count) {
    // print_nrf_slaves();
    handle_nrf_network();
    delay(10);
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
    return 0x1;
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
      return 0x0;
    }
  }

  return 0x1;
}

uint8_t find_index_by_id(uint8_t node_id) {
  if (!polling_nodes_count) {
    return 0x0;
  }

  for (uint8_t i = 0; i < polling_nodes_count; i++) {
    if (node_id == polling_nodes[i]) {
      return i;
    }
  }
  return 255;
}

void setup() {
  Serial.begin(115200);
  delay(10);
  debug_serial.begin(9600);
  
  debug_serial.println("Loading Firmware ... [Gateway]");
  debug_serial.print("Initiate Radio... ");
  initiate_radio();
  debug_serial.println("Done.");

  NODE_ID = EEPROM.read(0);

  for (uint8_t i = 0; i < MAX_NODES_INDEX; i++) {
    polling_nodes_db[i].timeout_count = 0;
    polling_nodes_db[i].status        = STATUS_DISCONNECTED;
  }
}

void loop() {
  itterate_serial();
  itterate_radio();

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
  bool exit = false;
  uint8_t count = 0;
  uint8_t node_id = buff_rx[0];
  uint8_t opcode  = buff_rx[1];
  uint8_t size    = buff_rx[2];
  uint8_t index   = find_index_by_id(node_id);

  uint8_t         status = false;
  sensor_db_t*    tx_sensor_item;
  sensor_db_t*    rx_sensor_item;

  unsigned long start_timer   = 0;
  unsigned long end_timer     = 0;
  unsigned long start_timeout = 0;
  bool report = false;
  uint8_t pipe;

  if (index == 255) {
    return 0;
  }

  // Check if NODE connected.

  memset(nrf_tx_buff, 0x0, sizeof(nrf_tx_buff));
  memset(nrf_rx_buff, 0x0, sizeof(nrf_rx_buff));
  if (size > 0) {
    memcpy((uint8_t *)&(tx_buff_ptr->payload[0]), &buff_rx[3], size);
  }

  tx_buff_ptr->node_id  = node_id;
  tx_buff_ptr->opcode   = opcode;
  tx_buff_ptr->size     = size;
  tx_buff_ptr->crc      = 0xff;
  
  debug_serial.print("Requesting node id ");
  debug_serial.print(node_id);
  debug_serial.print(" index ");
  debug_serial.print(index);
  debug_serial.println(". ");

  // ----------------------------------
  // Set NRF address according to node id
  tx[0] = (byte)polling_nodes[index];
  radio.openWritingPipe(tx);
  while(!exit && count < 10) {
    // Send
    start_timer = micros();                                     // start the timer
    report = radio.write(&nrf_tx_buff, sizeof(nrf_tx_buff));    // transmit & save the report
    end_timer = micros();                                       // end the timer

    if (report) {
      radio.startListening();                                // put in RX mode
      start_timeout = millis();                              // timer to detect timeout
      while (!radio.available()) {                           // wait for response
        if (millis() - start_timeout > 500) {               // only wait 200 ms
          break;
        }
      }
      radio.stopListening();                                 // put back in TX mode

      if (radio.available(&pipe)) {                          // is there a payload received
        radio.read(&nrf_rx_buff, sizeof(nrf_rx_buff));       // get payload from RX FIFO
        print_rx();
        rx_sensor_item = &polling_nodes_db[find_index_by_id(rx_buff_ptr->node_id)];
        rx_sensor_item->timeout_count = 0;
        rx_sensor_item->status = STATUS_CONNECTED;
        if (rx_buff_ptr->node_id == tx_buff_ptr->node_id) {
          exit = true;
        }
      } else {
        // No data from client
        if (tx_sensor_item->timeout_count < TIMEOUT_DISCONNECT_COUNT) {
          tx_sensor_item->timeout_count++;
        }
      }
    } else {
      if (tx_sensor_item->timeout_count < TIMEOUT_DISCONNECT_COUNT) {
        tx_sensor_item->timeout_count++;
      }
    }

    if (tx_sensor_item->timeout_count > TIMEOUT_DISCONNECT_COUNT) {
      tx_sensor_item->status = STATUS_DISCONNECTED;
    }

    delay(250);
    count++;
  }
  // ----------------------------------

  memcpy(buff_tx, nrf_rx_buff, sizeof(nrf_rx_buff));
  memset(nrf_tx_buff, 0x0, sizeof(nrf_tx_buff));
  memset(nrf_rx_buff, 0x0, sizeof(nrf_rx_buff));

  return sizeof(nrf_rx_buff);
}

int tx_data(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  return 0;
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
    buff_tx[offset] = polling_nodes_db[i].status; // status
    offset++;
  }

  return offset;
}


/*
radio.openWritingPipe(tx);
    unsigned long start_timer = micros();                           // start the timer
    bool report = radio.write(&nrf_tx_buff, sizeof(nrf_tx_buff));   // transmit & save the report
    unsigned long end_timer = micros();                             // end the timer

    if (report) {
      if (tx_sensor_item->timeout_count < TIMEOUT_DISCONNECT_COUNT) {
        tx_sensor_item->timeout_count++;
      }
      delay(1000);
      //debug_serial.print(F("Transmitted time "));                   // payload was delivered
      //debug_serial.print(end_timer - start_timer);                  // print the timer result
      uint8_t pipe;
      if (radio.available(&pipe)) {                                 
        radio.read(&nrf_rx_buff, sizeof(nrf_rx_buff));              // get incoming ACK payload
        rx_sensor_item = &polling_nodes_db[find_index_by_id(rx_buff_ptr->node_id)];
        rx_sensor_item->timeout_count = 0;
        rx_sensor_item->status = STATUS_CONNECTED;

        debug_serial.print("RX: ");
        for (uint8_t i = 0; i < 16; i++) {
          debug_serial.print(nrf_rx_buff[i], HEX);
          debug_serial.print(" ");
        } debug_serial.println();
        status = 1;
      } else {
        // timeout
        status = 2;
      }
    } else {
      // Not transmitted
      status = 3;
    }

    if (tx_sensor_item->timeout_count > TIMEOUT_DISCONNECT_COUNT) {
      tx_sensor_item->status = STATUS_DISCONNECTED;
    }
*/