from pymodbus.client import ModbusSerialClient
import time
import signal
import sys

PORT = "/dev/ttyUSB0"
SLAVES = [1, 2]

COIL_ADDR = [0x0140, 0x0141, 0x0142, 0x0143, 0x0144, 0x0145, 0x0146, 0x0147]

OFF_TIME = 0.2
BETWEEN_TIME = 1.0

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
            for coil in COIL_ADDR:
                client.write_coil(coil, False, slave=sid)
                print(f"Slave {sid}: coil {coil} OFF")
        except Exception as e:
            print(f"Slave {sid}: cleanup failed ({e})")
    client.close()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

def write_do(slave_id, state: bool, ADDR):
    wr = client.write_coil(ADDR, state, slave=slave_id)
    if wr.isError():
        print(f"Slave {slave_id}: write error {wr}")
        return False
    return True

print("Starting loop. Press Ctrl+C to stop.")

try:
    while True:
        for slave in SLAVES:
            for coil in COIL_ADDR:
                if write_do(slave, True, coil):
                    print(f"Slave {slave}: coil {coil} ON")
                    time.sleep(OFF_TIME)


                if write_do(slave, False, coil):
                    print(f"Slave {slave}: coil {coil} OFF")

            time.sleep(BETWEEN_TIME)

except KeyboardInterrupt:
    cleanup_and_exit()
