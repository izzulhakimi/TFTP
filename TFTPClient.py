#!/usr/bin/python3
import socket

SERVER_IP = "203.250.133.88"
SERVER_PORT = 69
BUFFER_SIZE = 516
TIMEOUT = 5

def tftp_client(host_ip, filename, mode, operation):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    client_socket.bind(("", 0))

    request = bytearray()
    request.extend([0x00, operation])
    request.extend(filename.encode("ascii"))
    request.extend([0x00])
    request.extend(mode.encode("ascii"))
    request.extend([0x00])

    try:
        client_socket.sendto(request, (host_ip, SERVER_PORT))

        if operation == 1:  # GET
            receive_file(client_socket, filename)
        elif operation == 2:  # PUT
            send_file(client_socket, filename)

    except socket.timeout:
        print("Timeout occurred. Connection closed.")
    finally:
        client_socket.close()

def receive_file(client_socket, filename):
    received_file = bytearray()
    while True:
        data, server_address = client_socket.recvfrom(BUFFER_SIZE)
        opcode = data[1]
        if opcode == 3:  # DATA packet
            block_number = int.from_bytes(data[2:4], byteorder="big")
            received_file.extend(data[4:])
            ack_packet = bytearray([0x00, 0x04]) + data[2:4]
            client_socket.sendto(ack_packet, server_address)
            if len(data) < BUFFER_SIZE:
                break
        elif opcode == 5:  # ERROR packet
            error_code = int.from_bytes(data[2:4], byteorder="big")
            error_message = data[4:-1].decode("ascii")
            print(f"Error occurred: {error_code} - {error_message}")
            return

    with open(filename, "wb") as file:
        file.write(received_file)
    print(f"File '{filename}' downloaded successfully.")

def send_file(client_socket, filename):
    with open(filename, "rb") as file:
        file_data = file.read()

    block_number = 1
    while len(file_data) > 0:
        data_packet = bytearray([0x00, 0x03]) + block_number.to_bytes(2, byteorder="big") + file_data[:512]
        client_socket.sendto(data_packet, (SERVER_IP, SERVER_PORT))

        while True:
            try:
                ack_packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
                if ack_packet[1] == 4 and int.from_bytes(ack_packet[2:4], byteorder="big") == block_number:
                    block_number += 1
                    file_data = file_data[512:]
                    break
            except socket.timeout:
                print("Timeout occurred. Resending data packet.")
                client_socket.sendto(data_packet, server_address)

    print(f"File '{filename}' uploaded successfully.")

# 클라이언트 실행
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python tftp_client.py host_address [get|put] filename")
        sys.exit(1)

    host_address = sys.argv[1]
    operation = sys.argv[2]
    filename = sys.argv[3]

    if operation.lower() not in ["get", "put"]:
        print("Invalid operation. Available options: get, put")
        sys.exit(1)

    mode = "netascii"  # 전송 모드 (netascii 모드만 지원)

    tftp_client(host_address, filename, mode, 1 if operation.lower() == "get" else 2)
