#include <SerialProtocol.h>
#include <EEPROM.h>
#include <DHT.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define MESSAGE_HEADER_PAYLOAD_SIZE   2
#define MAX_COMMAND_TABLE_SIZE        128
#define SERIAL_COMMAND_TABLE_SIZE     12
#define RADIO_COMMAND_TABLE_SIZE      1
#define DHT_PIN                       2

typedef int	(*NrfCallbackPtr)(void);
typedef struct {
  unsigned char     command;
  NrfCallbackPtr    handler;
} nrf_commands_table_t;

typedef struct {
  uint8_t node_id;
  uint8_t opcode;
  uint8_t size;
  uint8_t payload[12];
  uint8_t crc;
} message_t;

typedef struct {
  uint8_t cmd;
  uint8_t size;
} payload_t;

typedef struct {
  uint8_t type;
} sensor_t;

typedef struct {
  uint8_t type;
  uint16_t value;
} sensor_temperature_t;

typedef struct {
  uint8_t type;
  uint16_t value;
} sensor_humidity_t;

typedef struct {
  uint8_t type;
  uint8_t value;
} sensor_relay_t;

uint16_t dummy_value = 0;

void initiate_radio(void);
void itterate_radio(void);
uint8_t itterate_serial(void);

int get_config_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int set_config_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_basic_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int set_basic_registor(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int pause_with_timeout(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_device_type(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_device_uuid(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_device_additional(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int heartbeat(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int set_address(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_address(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);
int get_node_info(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx);

int nrf_get_node_info(void);
int nrf_set_node_data(void);
int nrf_get_node_data(void);

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
  { OPCODE_GET_NODE_INFO,           get_node_info}
};

nrf_commands_table_t nrf_handlers_map[] = {
  { OPCODE_GET_NODE_INFO,           nrf_get_node_info},
  { OPCODE_SET_NODES_DATA,          nrf_set_node_data},
  { OPCODE_GET_NODES_DATA,          nrf_get_node_data}
};

sensor_temperature_t temperature = { 1, 30 };
sensor_humidity_t humidity = { 2, 70 };
sensor_relay_t relay = { 3, 1 };

DHT dht(DHT_PIN, DHT11);

RF24 radio(7, 8); // CE, CSN
const byte rx[6] = "00001";
const byte tx[6] = "00002";
byte nrf_rx_buff[16];
byte nrf_tx_buff[16];
message_t* rx_buff_ptr = (message_t *)nrf_rx_buff;
message_t* tx_buff_ptr = (message_t *)nrf_tx_buff;

unsigned char DEVICE_TYPE[] = { '2','0','2','0' };
unsigned char DEVICE_SUB_TYPE = NODE;
unsigned char NODE_ID = 0;

void initiate_radio(void) {
  radio.begin();
  radio.enableAckPayload();
  radio.openWritingPipe(rx);
  radio.openReadingPipe(1,tx);
  radio.setPALevel(RF24_PA_MAX);
  radio.startListening();
}

void itterate_radio(void) {
  if (radio.available()) {
    radio.read(&nrf_rx_buff, sizeof(nrf_rx_buff));
    radio.stopListening();
    
    /* for (uint8_t i = 0; i < 16; i++) {
      Serial.print(nrf_rx_buff[i], HEX);
    } Serial.println(); */

    if (rx_buff_ptr->node_id == NODE_ID) {
      delay(100);

      for (unsigned char idx = 0; idx < RADIO_COMMAND_TABLE_SIZE; idx++) {
        if (nrf_handlers_map[idx].command == rx_buff_ptr->opcode) {
          nrf_handlers_map[idx].handler();
          radio.write(&nrf_tx_buff, sizeof(nrf_tx_buff));

          memset(nrf_rx_buff, 0x0, sizeof(nrf_rx_buff));
          memset(nrf_tx_buff, 0x0, sizeof(nrf_tx_buff));

          break;
        }
      }
    }

    radio.startListening();
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

void setup() {
  Serial.begin(115200);
  delay(10);
  
  Serial.println("Loading Firmware ...");
  Serial.print("Initiate Radio... ");
  initiate_radio();
  Serial.println("Done.");
  radio.startListening();

  pinMode(LED_BUILTIN, OUTPUT);
  NODE_ID = EEPROM.read(0);
  dht.begin();
}

void loop() {
  // itterate_serial();

  if (itterate_serial()) {
    Serial.println("Serial handled.");
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

int get_node_info(unsigned char* buff_tx, int len_tx, unsigned char* buff_rx, int len_rx) {
  node_info_header_t* node_header = (node_info_header_t*)buff_tx;
  uint8_t offset = sizeof(node_info_header_t);
  node_header->type = DEVICE_SUB_TYPE;
  node_header->payload_length = sizeof(sensor_temperature_t) + sizeof(sensor_humidity_t) + sizeof(sensor_relay_t);

  memcpy(&buff_tx[offset], (uint8_t*)&temperature, sizeof(sensor_temperature_t));
  offset += sizeof(sensor_temperature_t);
  memcpy(&buff_tx[offset], (uint8_t*)&humidity, sizeof(sensor_humidity_t));
  offset += sizeof(sensor_humidity_t);
  memcpy(&buff_tx[offset], (uint8_t*)&relay, sizeof(sensor_relay_t));
  offset += sizeof(sensor_relay_t);

  return (sizeof(node_info_header_t) + node_header->payload_length);
}

int nrf_get_node_info(void) {
  node_info_header_t* node_header = (node_info_header_t*)&(tx_buff_ptr->payload[0]);
  uint8_t offset = sizeof(node_info_header_t);

  Serial.println("nrf_get_node_info");

  node_header->type = 50;
  node_header->payload_length = sizeof(sensor_temperature_t) + sizeof(sensor_humidity_t) + sizeof(sensor_relay_t);

  temperature.value = (uint16_t)dht.readTemperature();
  humidity.value = (uint16_t)dht.readHumidity();

  memcpy(&tx_buff_ptr->payload[offset], (uint8_t*)&temperature, sizeof(sensor_temperature_t));
  offset += sizeof(sensor_temperature_t);
  memcpy(&tx_buff_ptr->payload[offset], (uint8_t*)&humidity, sizeof(sensor_humidity_t));
  offset += sizeof(sensor_humidity_t);
  memcpy(&tx_buff_ptr->payload[offset], (uint8_t*)&relay, sizeof(sensor_relay_t));
  offset += sizeof(sensor_relay_t);

  tx_buff_ptr->node_id  = NODE_ID;
  tx_buff_ptr->opcode   = rx_buff_ptr->opcode;
  tx_buff_ptr->size     = offset;
  tx_buff_ptr->crc      = 0xff;

  return 0;
}

int nrf_set_node_data(void) {

}

int nrf_get_node_data(void) {

}
