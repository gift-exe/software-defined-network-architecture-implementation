import subprocess
import re
import argparse

parser = argparse.ArgumentParser(description='hehe')

parser.add_argument('--ip', type=str, help='IP address')
parser.add_argument('--c', type=int, help='number of times to send ping')

def ping_and_extract_rtt(host, count):
    try:
        
        result = subprocess.run(['ping', '-c', str(count), '-i', '0.1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        #stdout=subprocess.PIPE captures the ourput and stores in the result object. so that we can use it in the code : )
        
        if result.returncode == 0: #if sucessful
            #extract RTT values
            rtt_values = re.findall(r'time=([\d.]+) ms', result.stdout)
            return [float(rtt) for rtt in rtt_values]
        else:
            print('ping command failed')
            return None
        

    except Exception as e:
        print('Error: ', e)
        return None

if __name__ == '__main__':
    args = parser.parse_args()
    ip_address = args.ip
    c = args.c 
    rtt_values = ping_and_extract_rtt(ip_address, c)
    if rtt_values:
        print(rtt_values)
    else:
        print('unable to ge rtt values')