
# TFTP
코드 예시에서는 TFTPclient.py 파일을 실행할 때 명령줄 인수를 사용하여 호스트 주소, 작업 유형 (get 또는 put), 파일 이름 및 포트 번호를 전달합니다. 따라서 명령 프롬프트에서 다음과 같이 실행할 수 있습니다:

$ python mytftp.py 203.250.133.88 get tftp.conf
$ python mytftp.py 203.250.133.88 put tftp.txt
$ python mytftp.py 203.250.133.88 put tftp.txt -p 9988

