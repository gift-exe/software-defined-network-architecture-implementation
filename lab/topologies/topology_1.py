from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController, Host    

class VLANHost(Host):
    def config(self, vlan=1, **params):
        super().config(**params)
        # Create VLAN interface and assign the VLAN ID to it
        self.cmd(f'ip link add link {self.intf()} name {self.intf()}.{vlan} type vlan id {vlan}')
        self.cmd(f'ip addr add {params["ip"]} brd + dev {self.intf()}.{vlan}')
        self.cmd(f'ip link set dev {self.intf()}.{vlan} up')

    def terminate(self):
        # Delete VLAN interface when terminating the host
        vlan = int(self.intf().split('.')[-1])
        self.cmd(f'ip link delete {self.intf()}.{vlan}')
        super().terminate()


class MultiTenantSwitchTopo(Topo):

    def build(self):
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch)
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch)

        
        h1s1 = self.addHost('h1s1', cls=VLANHost, ip='172.16.10.10/24', vlan=2, xterm='xterm h1s1')
        h2s1 = self.addHost('h2s1', cls=VLANHost, ip='172.16.10.11/24', vlan=110, xterm='xterm h2s1')

        h1s2 = self.addHost('h1s2', cls=VLANHost, ip='192.168.30.10/24', vlan=2, xterm='xterm h1s2')
        h2s2 = self.addHost('h2s2', cls=VLANHost, ip='192.168.30.11/24', vlan=110, xterm='xterm h2s2')

        h1s3 = self.addHost('h1s3', cls=VLANHost, ip='172.16.20.10/24', vlan=2, xterm='xterm h1s3')
        h2s3 = self.addHost('h2s3', cls=VLANHost, ip='172.16.20.11/24', vlan=110, xterm='xterm h2s3')
        

        self.addLink(h1s1, s1)
        self.addLink(h2s1, s1)

        self.addLink(h1s2, s2)
        self.addLink(h2s2, s2)

        self.addLink(h1s3, s3)
        self.addLink(h2s3, s3)

        self.addLink(s1, s2)
        self.addLink(s2, s3)
        

if __name__ == '__main__':
    setLogLevel('info')
    topo = MultiTenantSwitchTopo()
    c0 = RemoteController('c0')
    net = Mininet(topo=topo, controller=c0)
    net.start()
    CLI(net)
    net.stop()