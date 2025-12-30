from pymodbus.client import ModbusSerialClient
import time

PORT = "/dev/ttyUSB0"
SLAVE_ID = 4
DO1_COIL_ADDR = 0x0140
DO2_COIL_ADDR = 0x0141

client = ModbusSerialClient(
    port=PORT,
    baudrate=9600,
    parity="N",
    stopbits=1,
    bytesize=8,
    timeout=1.0,
)

if not client.connect():
    raise SystemExit(f"Unable to connect to serial port {PORT}")

def read_do1():
    rr = client.read_coils(DO1_COIL_ADDR, count=1, slave=SLAVE_ID)
    if rr.isError():
        print(f"Error reading DO1: {rr}")
        return None
    return bool(rr.bits[0])

def write_do1(state: bool):
    wr = client.write_coil(DO1_COIL_ADDR, value=state, slave=SLAVE_ID)
    if wr.isError():
        print(f"Error writing DO1: {wr}")
        return False
    return True

def read_do2():
    rr = client.read_coils(DO2_COIL_ADDR, count=1, slave=SLAVE_ID)
    if rr.isError():
        print(f"Error reading DO2: {rr}")
        return None
    return bool(rr.bits[0])

def write_do2(state: bool):
    wr = client.write_coil(DO2_COIL_ADDR, value=state, slave=SLAVE_ID)
    if wr.isError():
        print(f"Error writing DO2: {wr}")
        return False
    return True


try:
    print("DO now:", read_do1())
    print("Write ON:", write_do1(True))
    time.sleep(1)
    print("DO now:", read_do1())
    time.sleep(3)
    print("Write OFF:", write_do1(False))
    time.sleep(1)
    print("DO now:", read_do1())

    time.sleep(1)

    print("DO2 now:", read_do2())
    print("Write ON:", write_do2(True))
    time.sleep(1)
    print("DO2 now:", read_do2())
    time.sleep(3)
    print("Write OFF:", write_do2(False))
    time.sleep(1)
    print("DO2 now:", read_do2())



finally:
    client.close()
