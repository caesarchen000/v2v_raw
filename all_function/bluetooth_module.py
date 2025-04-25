import bluetooth
import threading

def send_bluetooth_message(target_address: str, message: str):
    """發送訊息給指定裝置"""
    port = 1 # 埠位置
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((target_address, port))
        sock.send(message)
        print(f"[藍芽訊息] 傳送至 {target_address}：{message}")
    except Exception as e:
        print(f"[藍芽錯誤]：{e}")
    finally:
        sock.close()

def bluetooth_listener(callback):
    """背景執行：持續接收訊息並交給 callback 處理"""
    def listen():
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 1
        server_sock.bind(("", port))
        server_sock.listen(1)
        print("[藍芽接收] 等待連線中...")

        while True:
            try:
                client_sock, address = server_sock.accept()
                print(f"[藍芽接收] 來自 {address} 的連線")
                data = client_sock.recv(1024)
                if data:
                    message = data.decode("utf-8")
                    print(f"[藍芽接收]：{message}")
                    callback(message)  # 將訊息傳給主程式處理
                client_sock.close()
            except Exception as e:
                print(f"[接收錯誤]：{e}")

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()