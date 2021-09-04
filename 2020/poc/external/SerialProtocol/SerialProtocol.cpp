#include "SerialProtocol.h"

unsigned char uart_tx_buffer[MAX_LENGTH];
unsigned char uart_rx_buffer[MAX_LENGTH];

int serial_rx_len = 0;
int serial_tx_len = 0;

void blink(unsigned int interval) {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(interval);
  digitalWrite(LED_BUILTIN, LOW);
  delay(interval);
}

void send_async_data_to_uart(uint16_t opcode, uint8_t* payload, uint16_t size) {
  mks_header* uart_tx_header = (mks_header *)(&uart_tx_buffer[0]);

  uart_tx_header->magic_number[0] = 0xDE;
  uart_tx_header->magic_number[1] = 0xAD;
  uart_tx_header->direction       = ASYNC;
  uart_tx_header->op_code         = opcode;
  uart_tx_header->content_length  = size;
  serial_tx_len                   = MKS_HEADER_SIZE + size;

  memcpy(&uart_tx_buffer[MKS_HEADER_SIZE], payload, size);

  uart_tx_buffer[serial_tx_len]     = 0xAD;
  uart_tx_buffer[serial_tx_len + 1] = 0xDE;
  Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
}

void handler_serial(commands_table_t* handler_table, uint8_t length) {
  mks_header* uart_rx_header = (mks_header *)(&uart_rx_buffer[0]);
  mks_header* uart_tx_header = (mks_header *)(&uart_tx_buffer[0]);

	if (uart_rx_buffer[0] != 0xDE || uart_rx_buffer[1] != 0xAD) {
    uart_rx_buffer[serial_rx_len] = '\n';
    Serial.write(&uart_rx_buffer[0], serial_rx_len + 1);
  } else {
    switch (uart_rx_header->op_code) {
      case OPCODE_GET_DEVICE_TYPE: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_GET_DEVICE_TYPE;
        uart_tx_header->content_length  = DEVICE_TYPE_SIZE;
        serial_tx_len                   = MKS_HEADER_SIZE + DEVICE_TYPE_SIZE;

        unsigned char index = find_handler_index(OPCODE_GET_DEVICE_TYPE, handler_table, length);
        if (index != 0xff) {
          handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        }

        // TODO - Python can't manage this // memset(&uart_tx_buffer[MKS_HEADER_SIZE], 0xff, DEVICE_TYPE_SIZE);

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_GET_DEVICE_ADDITIONAL: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_GET_DEVICE_ADDITIONAL;
        uart_tx_header->content_length  = DEVICE_ADDITIONAL_SIZE;
        serial_tx_len                   = MKS_HEADER_SIZE + DEVICE_ADDITIONAL_SIZE;

        unsigned char index = find_handler_index(OPCODE_GET_DEVICE_ADDITIONAL, handler_table, length);
        if (index != 0xff) {
          handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - DEVICE_ADDITIONAL_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        }

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
        blink(500);
      }
      break;
      case OPCODE_SET_ADDRESS: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_SET_ADDRESS;
        uart_tx_header->content_length  = DEVICE_ADDRESS_SIZE;
        serial_tx_len                   = MKS_HEADER_SIZE + DEVICE_ADDRESS_SIZE;

        unsigned char index = find_handler_index(OPCODE_SET_ADDRESS, handler_table, length);
        handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - DEVICE_ADDRESS_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_GET_ADDRESS: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_GET_ADDRESS;
        uart_tx_header->content_length  = DEVICE_ADDRESS_SIZE;
        serial_tx_len                   = MKS_HEADER_SIZE + DEVICE_ADDRESS_SIZE;

        unsigned char index = find_handler_index(OPCODE_GET_ADDRESS, handler_table, length);
        handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - DEVICE_ADDRESS_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_GET_NODE_INFO: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_GET_NODE_INFO;

        unsigned char index = find_handler_index(OPCODE_GET_NODE_INFO, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_GET_NODES_MAP: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_GET_NODES_MAP;
        
        unsigned char index = find_handler_index(OPCODE_GET_NODES_MAP, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_ADD_NODE_INDEX: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_ADD_NODE_INDEX;
        
        unsigned char index = find_handler_index(OPCODE_ADD_NODE_INDEX, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_DEL_NODE_INDEX: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_DEL_NODE_INDEX;
        
        unsigned char index = find_handler_index(OPCODE_DEL_NODE_INDEX, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_PAUSE_WITH_TIMEOUT: {
      }
      break;
      case OPCODE_RX_DATA: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_RX_DATA;
        
        unsigned char index = find_handler_index(OPCODE_RX_DATA, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_TX_DATA: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_TX_DATA;
        
        unsigned char index = find_handler_index(OPCODE_TX_DATA, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_GET_NODES_LIST: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_GET_NODES_LIST;
        
        unsigned char index = find_handler_index(OPCODE_GET_NODES_LIST, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_SET_NODES_DATA: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_SET_NODES_DATA;
        
        unsigned char index = find_handler_index(OPCODE_SET_NODES_DATA, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      case OPCODE_GET_NODES_DATA: {
        uart_tx_header->magic_number[0] = 0xDE;
        uart_tx_header->magic_number[1] = 0xAD;
        uart_tx_header->direction       = SYNC_RESPONSE;
        uart_tx_header->op_code         = OPCODE_GET_NODES_DATA;
        
        unsigned char index = find_handler_index(OPCODE_GET_NODES_DATA, handler_table, length);
        int size = handler_table[index].handler(&uart_tx_buffer[MKS_HEADER_SIZE], MAX_LENGTH - MKS_HEADER_SIZE, &uart_rx_buffer[MKS_HEADER_SIZE], uart_rx_header->content_length);
        uart_tx_header->content_length  = size;
        serial_tx_len                   = MKS_HEADER_SIZE + size;

        uart_tx_buffer[serial_tx_len]     = 0xAD;
        uart_tx_buffer[serial_tx_len + 1] = 0xDE;
        Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
      }
      break;
      default: {
        uart_rx_buffer[serial_rx_len] = '\n';
        Serial.write(&uart_rx_buffer[0], serial_rx_len + 1);
      }
      break;
    }
  }
}

int read_serial_buffer() {
  if (Serial.available() > 0) {
    delay(10);
    serial_rx_len = Serial.readBytesUntil('\n', uart_rx_buffer, MAX_LENGTH);
    // Serial.flush();
  } else {
    serial_rx_len = 0;
  }

  return serial_rx_len;
}

unsigned char find_handler_index(unsigned char command, commands_table_t* handler_table, uint8_t length) {
  if (length > MAX_COMMAND_TABLE_SIZE) {
    return 0xff;
  }

  for (unsigned char idx = 0; idx < length; idx++) {
    if (handler_table[idx].command == command) {
      return idx;
    }
  }

  return 0xff;
}

void send_data_to_master(uint8_t opcode, uint8_t* payload, uint16_t size) {
  mks_header* uart_tx_header = (mks_header *)(&uart_tx_buffer[0]);
  uart_tx_header->magic_number[0] = 0xDE;
  uart_tx_header->magic_number[1] = 0xAD;
  uart_tx_header->direction       = SYNC_RESPONSE;
  uart_tx_header->op_code         = opcode;
  uart_tx_header->content_length  = size;
  serial_tx_len                   = MKS_HEADER_SIZE + size;

  memcpy(&uart_tx_buffer[MKS_HEADER_SIZE], payload, size);

  uart_tx_buffer[serial_tx_len]     = 0xAD;
  uart_tx_buffer[serial_tx_len + 1] = 0xDE;
  Serial.write(&uart_tx_buffer[0], serial_tx_len + 2);
}