from machine import ADC, Pin
from time import sleep
import bluetooth
import struct

# Initialize ADC for the potentiometer
pot = ADC(Pin(26))  # GPIO 26 (ADC0)

# Initialize Bluetooth
ble = bluetooth.BLE()
ble.active(True)

# BLE service and characteristic UUIDs
SERVICE_UUID = bluetooth.UUID(0x181A)  # Environmental Sensing (example)
CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)  # Temperature (example, use custom if needed)
CHARACTERISTIC = (CHARACTERISTIC_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)
SERVICE = (SERVICE_UUID, (CHARACTERISTIC,),)

# Register service
handles = ble.gatts_register_services([SERVICE])
characteristic_handle = handles[0][0]

# Function to create an advertising payload
def create_advertising_payload(name):
    payload = bytearray()
    
    # Add Flags (General Discoverable Mode + BLE only)
    payload += bytes([0x02, 0x01, 0x06])  # 0x06 = General Discoverable Mode, BLE only

    # Add Complete Local Name (must be <= 29 bytes to fit the payload size)
    name_bytes = name.encode("utf-8")
    name_length = len(name_bytes) + 1
    if name_length > 29:  # Ensure name does not exceed payload size
        name_length = 29
        name_bytes = name_bytes[:29]
    payload += bytes([name_length, 0x09]) + name_bytes

    return payload

# Function to encode potentiometer value
def encode_pot_value(value):
    return struct.pack('<H', value)  # Encode as little-endian unsigned short

# Function to advertise potentiometer value
def advertise_pot_value(value):
    payload = create_advertising_payload("PicoW-RideHeight")
    additional_data = encode_pot_value(value)
    payload += additional_data
    ble.gap_advertise(100, payload)

# Start advertising
ble.gap_advertise(100, create_advertising_payload("PicoW-RideHeight"))

# Allow 30 seconds for Bluetooth connection before sending data
print("Waiting for 30 seconds to allow Bluetooth connection...")
sleep(30)

while True:
    # Read potentiometer value (0-65535)
    pot_value = pot.read_u16()
    
    # Advertise the potentiometer value over Bluetooth
    advertise_pot_value(pot_value)
    
    # Print the value for debugging
    print("Potentiometer Value:", pot_value)
    
    # Delay to avoid flooding
    sleep(1)
