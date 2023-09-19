import socket
import struct
from scapy.all import IP, ICMP, Ether, send, sendp
from termcolor import colored

print(colored('listerner started', 'red'))

def icmp_listerner():
    # Create a raw socket that listens for ICMP packets
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    while True:
        try:
            packet, addr = sock.recvfrom(1024)

            payload = packet[28:]
            payload_msg = payload.decode('utf-8')
            print(colored('packet received', 'green'))
            print(colored(f'msg: {payload_msg} \n', 'yellow'))
            
            icmp_header = packet[20:28]

            icmp_type, code, checksum, _, _ = struct.unpack("BBHHH", icmp_header)
            
            #Check if it's an ICMP echo request
            if icmp_type == 8:
                # Craft an ICMP echo reply packet
                icmp_reply = struct.pack("BBHHH", 0, code, 0, checksum, 0)
                reply_packet = packet[:20] + icmp_reply + b'Heyyy, How are ya?'

                # Send the ICMP echo reply back to the source
                sock.sendto(reply_packet, addr)
        except KeyboardInterrupt:
            print(colored('\nClosing ...', 'red'))
            sock.close()
            break

if __name__ == '__main__':
    icmp_listerner()