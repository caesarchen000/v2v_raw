import bluetooth
import threading
import json

def connect_bluetooth(target_address: str, port: int = 1):
    """
    Establish a Bluetooth connection and return the socket.
    
    Args:
        target_address (str): The MAC address of the target device.
        port (int): The port to connect to (default is 1). 
    Returns:
        BluetoothSocket: The connected Bluetooth socket.
    """
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_address, port))
    print(f"[Bluetooth Connected] Connected to {target_address}")
    return sock

def send_string(sock, message: str):
    """
    Send a string message over Bluetooth.
    
    Args:
        sock (BluetoothSocket): The connected Bluetooth socket.
        message (str): The string message to send.
    """
    try:
        sock.send(message.encode('utf-8'))
        print(f"[Sent String] {message}")
    except Exception as e:
        print(f"[String Sending Error] {e}")

def send_json(sock, json_data: dict):
    """
    Send JSON data over Bluetooth.
    
    Args:
        sock (BluetoothSocket): The connected Bluetooth socket.
        json_data (dict): The dictionary to send as JSON.
    """
    try:
        json_string = json.dumps(json_data)
        sock.send(json_string.encode('utf-8'))
        print(f"[Sent JSON] {json_string}")
    except Exception as e:
        print(f"[JSON Sending Error] {e}")

def close_bluetooth(sock):
    """
    Close the Bluetooth connection.
    
    Args:
        sock (BluetoothSocket): The Bluetooth socket to close.
    """
    try:
        sock.close()
        print("[Bluetooth Connection Closed]")
    except Exception as e:
        print(f"[Closing Error] {e}")

def listen_bluetooth(callback, port: int = 1, buffer_size: int = 4096):
    """
    Start a background Bluetooth listener. Received data will be passed to the callback function.
    
    Args:
        callback (function): Function to call with the received data (str or dict).
        port (int): Port to listen on (default is 1).
        buffer_size (int): Buffer size for receiving data (default is 4096 bytes).
    """
    def listen():
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", port))
        server_sock.listen(1)
        print(f"[Bluetooth Listening] Waiting on port {port}...")

        while True:
            try:
                client_sock, address = server_sock.accept()
                print(f"[Incoming Connection] From {address}")

                data = client_sock.recv(buffer_size)
                if data:
                    try:
                        decoded = data.decode("utf-8")
                        try:
                            json_data = json.loads(decoded)
                            print(f"[Received JSON] {json_data}")
                            callback(json_data)
                        except json.JSONDecodeError:
                            print(f"[Received String] {decoded}")
                            callback(decoded)
                    except UnicodeDecodeError as e:
                        print(f"[Decoding Error] {e}")
                client_sock.close()

            except Exception as e:
                print(f"[Receiving Error] {e}")

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
    print("[Background Listening Started]")
