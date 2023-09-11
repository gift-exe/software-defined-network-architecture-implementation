# to run this script use:  ```sudo -E env PATH=$PATH python ./test.py```
# because first of all, you need sudo priviledges to run this script
# and if you use cmd ``` sudo python ./test.py ```, then the python interpreter 
# that would be used would be the global interpreter.



from scapy.all import IP, ICMP, Ether, send, sendp
import subprocess
import argparse
import socket
import struct
import threading
import sys

parser = argparse.ArgumentParser(description='hehe')

parser.add_argument('--ip', type=str, help='IP address')
parser.add_argument('--c', type=int, help='number of times to send ping')

args = parser.parse_args()

ip_address = args.ip
c = args.c 

def get_dst_mac(ip_address):
    try:
        arp_output = subprocess.check_output(['arp', '-n']).decode('utf-8')
        lines = arp_output.split('\n')
        for line in lines:
            if ip_address in line:
                parts = line.split()
                if len(parts) >= 3:
                    mac_address = parts[2]
                    return mac_address
                break
        else:
            print(f"No MAC Address found for {ip_address}")
    except subprocess.CalledProcessError:
        print("Error running arp command")


def get_src_mac():
    try:
        mac_output = subprocess.check_output(['ip', 'link', 'show']).decode('utf-8')
        lines = mac_output.split('\n')
        return lines[-2].split()[1]
    except subprocess.CalledProcessError:
        print("Error running ip link show command")

def get_iface():
    try:
        mac_output = subprocess.check_output(['ifconfig']).decode('utf-8')
        lines = mac_output.split('\n')
        return lines[0].split()[0][:-1]
    except subprocess.CalledProcessError:
        print("Error running ip link show command")

def icmp_reply_listener(sl_e):
    # Create a raw socket that listens for ICMP packets
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
    while not sl_e.is_set():
        reply_packet, _ = sock.recvfrom(1024)
    
        icmp_header = reply_packet[20:28]
    
        icmp_type, _, _, _, _ = struct.unpack("BBHHH", icmp_header)
        
        if icmp_type == 69:
            # It's an ICMP Echo Reply packet
            # Extract the payload from the ICMP Echo Reply packet
            icmp_payload = reply_packet[48:]
            
            # Print or process the payload as needed
            print(icmp_payload.decode('utf-8'))
        
            


if __name__ == '__main__':
    ip = IP(dst=ip_address)
    eth = Ether(src=get_src_mac(), dst=get_dst_mac(ip_address))
    icmp = ICMP() / 'Hello, Neighbour'

    packet = eth/ip/icmp
    
    #create flag to stop the listener
    stop_listener = threading.Event()

    listener_thread = threading.Thread(target=icmp_reply_listener, args=[stop_listener])
    listener_thread.start()

    sendp(x=packet, inter=0.01, count=c, iface=get_iface())

    stop_listener.set()

    listener_thread.join()
    


