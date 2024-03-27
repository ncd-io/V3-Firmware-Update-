# Syntax 
# $ python ncd_py_bootloader.py <com port> <ncd update file>

import sys 
from serial import Serial 
import time
################################### Defines #####################################
HI_SPEED_BR = 115200
READ_TIMEOUT=10
CRC_POLY=0x104C11DB7

BL_GET_BL_INFO = 0x10	#Get the recommended start address for flashing a new app and the available memory size
BL_SET_APP_INFO = 0x11	#Initializing flashing operation by providing the new app size in bytes
BL_FLASH_PKT = 0x12		#This command is used to write data in to different memories of the MCU
BL_SYSTEM_RESET = 0x13	#System Soft Reset

MAX_RESP_LEN=256
CHUNK_SIZE_IN_BYTES=1024
################################# Data structures ################################

################################# Methods ################################
def get_crc(data):
    Crc = 0XFFFFFFFF
    for i in data:
        Crc = Crc ^ i 
        for idx in range(0,32):
            if (Crc & 0x80000000):
                Crc = (Crc << 1) ^ CRC_POLY
            else:
                Crc = (Crc << 1)
    return Crc

def compose_get_bl_info_command():
    cmd = []
    cmd = cmd + [0x07,0x00]      
    cmd.append(BL_GET_BL_INFO)    
    cmd = cmd + [0x01, 0x00]
    crc = get_crc(cmd)
    cmd.append((crc & 0x000000FF)) 
    cmd.append((crc & 0x0000FF00) >> 8)     
    cmd.append((crc & 0x00FF0000) >> 16)   
    cmd.append(crc >> 24) 
    return cmd

def compose_reset_command():
    cmd = []
    cmd = cmd + [0x07,0x00]      
    cmd.append(BL_SYSTEM_RESET)    
    cmd = cmd + [0x01, 0x00]
    crc = get_crc(cmd)
    cmd.append((crc & 0x000000FF)) 
    cmd.append((crc & 0x0000FF00) >> 8)     
    cmd.append((crc & 0x00FF0000) >> 16)   
    cmd.append(crc >> 24) 
    return cmd

def compose_set_bl_info_command(app_size):
    cmd = []
    cmd = cmd + [0x0B,0x00]      
    cmd.append(BL_SET_APP_INFO)    
    cmd = cmd + [0x01, 0x00]
    payload = []
    payload.append((app_size & 0x000000FF)) 
    payload.append((app_size & 0x0000FF00) >> 8)     
    payload.append((app_size & 0x00FF0000) >> 16)   
    payload.append(app_size >> 24) 
    crc = get_crc(payload)
    cmd.append((crc & 0x000000FF)) 
    cmd.append((crc & 0x0000FF00) >> 8)     
    cmd.append((crc & 0x00FF0000) >> 16)   
    cmd.append(crc >> 24) 
    cmd = cmd + payload
    return cmd

def compose_set_bl_flash_pkt_command(flash_pkt, pkt_ctr):
    cmd = []
    length = len(flash_pkt) + 0x07
    cmd.append((length & 0x000FF)) 
    cmd.append((length & 0x0FF00) >> 8)   
    cmd.append(BL_FLASH_PKT)    
    cmd.append((pkt_ctr & 0x000FF)) 
    cmd.append((pkt_ctr & 0x0FF00) >> 8)   
    crc = get_crc(flash_pkt)
    cmd.append((crc & 0x000000FF)) 
    cmd.append((crc & 0x0000FF00) >> 8)     
    cmd.append((crc & 0x00FF0000) >> 16)   
    cmd.append(crc >> 24) 
    cmd = cmd + flash_pkt
    return cmd
    
com_port = sys.argv[1] # Com port 
update_file = sys.argv[2] # file name
com_port_ser = Serial(com_port, baudrate=HI_SPEED_BR, timeout=READ_TIMEOUT)

with open(update_file, mode="rb") as bin_file:
    fw_update = bin_file.read()

fw_update = bytearray(fw_update) 
fw_update.reverse()
remaining_bytes = len(fw_update)

cmd = compose_get_bl_info_command()
com_port_ser.write(cmd)
resp = com_port_ser.read(15)
print([hex(i) for i in resp])

cmd = compose_set_bl_info_command(remaining_bytes)
com_port_ser.write(cmd)
resp = com_port_ser.read(2)
print([hex(i) for i in resp])

idx = 0
pkt_ctr = 1

print("Flash Programming . .")  
while(remaining_bytes > 0):
    if remaining_bytes >= CHUNK_SIZE_IN_BYTES:
        bytes_to_write = CHUNK_SIZE_IN_BYTES
    else:
        bytes_to_write = remaining_bytes
    chunk = fw_update[idx : idx + bytes_to_write]
    
    chunk.reverse()
    chunk = list(chunk)
    cmd = compose_set_bl_flash_pkt_command(chunk, pkt_ctr)
    print("Packet ", pkt_ctr)
    time.sleep(0.1) #Slight Delay
    com_port_ser.write(cmd)
    time.sleep(0.1) #Slight Delay
    resp = com_port_ser.read(2)
    if len(resp) == 0:
        break
    
    if resp[1] == 0xb0:
        idx = idx + bytes_to_write
        pkt_ctr = pkt_ctr + 1
        remaining_bytes = remaining_bytes - bytes_to_write

cmd = compose_reset_command()
com_port_ser.write(cmd)
resp = com_port_ser.read(2)
print("Rebooting . . ")   