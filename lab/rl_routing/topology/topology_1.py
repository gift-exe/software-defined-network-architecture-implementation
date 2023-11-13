from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController, Host

class TopoBuilder(Topo):
    def build(self):
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch)
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch)

        h1s1 = self.addHost('h1s1', ip='192.168.1.1/8', xterm='xterm h1s1')
        h1s2 = self.addHost('h1s2', ip='192.168.1.2/8', xterm='xterm h1s2')
        h1s3 = self.addHost('h1s3', ip='192.168.1.3/8', xterm='xterm h1s3')

        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s1, s3)

        self.addLink(h1s1, s1)
        self.addLink(h1s2, s2)
        self.addLink(h1s3, s3)

if __name__ == '__main__':
    setLogLevel('info')
    topo = TopoBuilder()
    c0 = RemoteController('c0')
    net = Mininet(topo=topo, controller=c0)
    net.start()
    CLI(net)
    net.stop()