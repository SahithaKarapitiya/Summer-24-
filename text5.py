import socket
import serial
import time
import os
from datetime import datetime

def start_server():
    host = '0.0.0.0'
    port = 12345

    def setup_serial():
        return serial.Serial(
            port='/dev/serial0',  # Ensure this is the correct port
            baudrate=115200,
            timeout=1
        )

    # Get the current user's home directory
    #home_dir = os.path.expanduser("~")
    file_path = '/home/pi2/datapi2.txt'
    # print(f"Data will be written to: {file_path}")

    while True:
        ser = None
        server_socket = None
        try:
            ser = setup_serial()
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"Server listening on {host}:{port}")

            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")

            try:
                while True:
                    if ser.in_waiting > 0:
                        data = ser.readline().decode('utf-8').rstrip()
                        if data:  # Check if data is not empty
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            data_with_timestamp = f"{timestamp}, {data}"
                            print(f"Received data: {data_with_timestamp}")
                            conn.sendall(data_with_timestamp.encode('utf-8'))

                            # Write data to the text file
                            # try:
                            with open(file_path, 'a') as file:
                                    # print(f"Writing to file: {data_with_timestamp}")
                                file.write(data_with_timestamp)
                                    # Explicitly close the file
                                file.close()
                            # except Exception as file_error:
                            #     print(f"Error writing to file: {file_error}")
            except socket.error:
                print("Connection closed by client.")
            finally:
                conn.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        except OSError as e:
            if e.errno == 98:
                print(f"Address already in use, retrying in 0.25 seconds: {e}")
                time.sleep(0.25)
            else:
                print(f"Unexpected OSError: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if ser is not None:
                ser.close()
            if server_socket is not None:
                server_socket.close()
        time.sleep(1)  # Wait before attempting to reconnect

if __name__ == "__main__":
    start_server()
