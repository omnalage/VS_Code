import socket

# ==== CONFIG ====
SERVER_IP = "0.0.0.0"   # listen on all interfaces
SERVER_PORT = 12345      # <-- must match client

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (SERVER_IP, SERVER_PORT)
sock.bind(server_address)

print(f"Server is listening on {server_address}")

while True:
    data, address = sock.recvfrom(4096)
    text = data.decode()
    print(f"Received from {address}: {text}")

    # Save to file
    with open("DataLog.txt", "a") as f:
        f.write(text + "\n")
