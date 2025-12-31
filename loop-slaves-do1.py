from pymodbus.client import ModbusSerialClient
import time
import signal
import sys
import argparse

## Ohjelman käyttö:
##  $: sudo python3 loop-slaves-do1.py --port ttyUSB1
##  $: sudo python3 loop-slaves-do1.py --port /dev/ttyUSB1

parser = argparse.ArgumentParser(description="Cycle Modbus DO coils on R1212")
parser.add_argument(
    "--port",
    required=True,
    help="Serial port, e.g. ttyUSB0, ttyUSB1 or /dev/ttyUSB0"
)
args = parser.parse_args()

PORT = args.port if args.port.startswith("/") else f"/dev/{args.port}"

SLAVES = [1, 2]

DO0_COIL_ADDR = 0x0140
DO1_COIL_ADDR = 0x0141
DO2_COIL_ADDR = 0x0142
DO3_COIL_ADDR = 0x0143
DO4_COIL_ADDR = 0x0144
DO5_COIL_ADDR = 0x0145
DO6_COIL_ADDR = 0x0146
DO7_COIL_ADDR = 0x0147

ON_TIME = 2.0
OFF_TIME = 1.0
BETWEEN_TIME = 3.0

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

def cleanup_and_exit(signum=None, frame=None):
    print("\nStopping, turning DO OFF on all slaves...")
    for sid in SLAVES:
        try:
            client.write_coil(DO1_COIL_ADDR, False, slave=sid)
            print(f"Slave {sid}: DO1 OFF")
        except Exception as e:
            print(f"Slave {sid}: cleanup failed ({e})")
    client.close()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

def write_do(slave_id, state: bool):
    wr = client.write_coil(DO1_COIL_ADDR, state, slave=slave_id)
    if wr.isError():
        print(f"Slave {slave_id}: write error {wr}")
        return False
    return True

def read_do(slave_id):
    rr = client.read_coils(DO1_COIL_ADDR, count=1, slave=slave_id)
    if rr.isError():
        print(f"Slave {slave_id}: read error {rr}")
        return None
    return bool(rr.bits[0])

print("Starting loop. Press Ctrl+C to stop.")

try:
    while True:
        for slave in SLAVES:
            print(f"\n=== Slave {slave} ===")

            print(f"Slave {slave}: DO1 ON")
            write_do(slave, True)
            time.sleep(0.2)

            state = read_do(slave)
            print(f"Slave {slave}: DO1 state = {state}")

            time.sleep(ON_TIME)

            print(f"Slave {slave}: DO1 OFF")
            write_do(slave, False)
            time.sleep(0.2)

            state = read_do(slave)
            print(f"Slave {slave}: DO1 state = {state}")

            time.sleep(BETWEEN_TIME)

except KeyboardInterrupt:
    cleanup_and_exit()
