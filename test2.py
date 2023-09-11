import socket
import struct
from scapy.all import IP, ICMP, Ether, send, sendp

# Create a raw socket that listens for ICMP packets
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

while True:
    packet, addr = sock.recvfrom(1024)



    payload = packet[28:]
    payload_msg = payload.decode('utf-8')
    print(payload_msg)
    
    icmp_header = packet[20:28]

    icmp_type, code, checksum, _, _ = struct.unpack("BBHHH", icmp_header)
    
    #Check if it's an ICMP echo request
    if icmp_type == 8:
        # Craft an ICMP echo reply packet
        icmp_reply = struct.pack("BBHHH", 0, code, 0, checksum, 0)
        reply_packet = packet[:20] + icmp_reply + b'Heyyy, How are ya?'

        # Send the ICMP echo reply back to the source
        sock.sendto(reply_packet, addr)