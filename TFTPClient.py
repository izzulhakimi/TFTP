#!/usr/bin/python3
import socket
import sys

# TFTP 클라이언트 클래스
class TFTPClient:
    def __init__(self, server_ip, server_port=69):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP 소켓 생성
        self.socket.settimeout(5)  # 타임아웃 설정 (5초)

    def send_request(self, opcode, filename, mode):
        # RRQ(Read Request) 또는 WRQ(Write Request) 패킷 생성
        request_packet = bytearray()
        request_packet.extend(bytes([0, opcode]))  # Opcode 추가
        request_packet.extend(filename.encode())  # 파일 이름 추가
        request_packet.extend(b'\x00')  # 0 바이트 추가
        request_packet.extend(mode.encode())  # 전송 모드 추가
        request_packet.extend(b'\x00')  # 0 바이트 추가

        # 서버에 요청 패킷 전송
        self.socket.sendto(request_packet, (self.server_ip, self.server_port))

    def receive_data(self):
        try:
            data, server = self.socket.recvfrom(1024)  # 데이터 수신 (최대 1024바이트)
            opcode = data[1]  # Opcode 확인

            if opcode == 3:
                # 데이터 패킷일 경우, 파일에 데이터를 기록
                return data[4:]  # 데이터 부분만 반환
            elif opcode == 5:
                # 에러 패킷일 경우, 오류 메시지 출력 및 프로그램 종료
                error_code = data[3]
                error_message = data[4:].decode()
                print(f"Error {error_code}: {error_message}")
                sys.exit(1)
        except socket.timeout:
            # 타임아웃 발생 시 프로그램 종료
            print("Connection timed out.")
            sys.exit(1)

    def download_file(self, filename):
        # RRQ(Read Request) 패킷 전송
        self.send_request(1, filename, "netascii")

        # 파일 열기
        with open(filename, "wb") as file:
            while True:
                data = self.receive_data()
                if not data:
                    break
                file.write(data)

        print(f"File {filename} downloaded successfully.")

    def upload_file(self, filename):
        # WRQ(Write Request) 패킷 전송
        self.send_request(2, filename, "netascii")

        # 파일 읽기
        with open(filename, "rb") as file:
            while True:
                data = file.read(512)  # 최대 512바이트씩 읽음
                if not data:
                    break
                data_packet = bytearray()
                data_packet.extend(b'\x00\x03')  # 데이터 패킷 Opcode 추가
                data_packet.extend(data)  # 파일 데이터 추가
                self.socket.sendto(data_packet, (self.server_ip, self.server_port))

        print(f"File {filename} uploaded successfully.")

    def close(self):
        self.socket.close()  # 소켓 닫기

# 클라이언트 실행
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: mytftp host_address [get|put] filename [-p port]")
        sys.exit(1)

    host_address = sys.argv[1]
    operation = sys.argv[2]
    filename = sys.argv[3]
    port = 69  # 기본 포트 번호

    if len(sys.argv) == 6 and sys.argv[4] == "-p":
        port = int(sys.argv[5])

    client = TFTPClient(host_address, port)

    if operation == "get":
        client.download_file(filename)
    elif operation == "put":
        client.upload_file(filename)
    else:
        print("Invalid operation. Use 'get' or 'put'.")
        sys.exit(1)

    client.close()
