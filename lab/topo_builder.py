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
        h2s1 = self.addHost('h2s1', ip='192.168.1.2/8', xterm='xterm h2s1')
        h3s1 = self.addHost('h3s1', ip='192.168.1.3/8', xterm='xterm h3s1')

        h1s2 = self.addHost('h1s2', ip='192.168.1.4/8', xterm='xterm h1s2')
        h2s2 = self.addHost('h2s2', ip='192.168.1.5/8', xterm='xterm h2s2')
        h3s2 = self.addHost('h3s2', ip='192.168.1.6/8', xterm='xterm h3s2')
        

        h1s3 = self.addHost('h1s3', ip='192.168.1.7/8', xterm='xterm h1s3')
        h2s3 = self.addHost('h2s3', ip='192.168.1.8/8', xterm='xterm h2s3')
        h3s3 = self.addHost('h3s3', ip='192.168.1.9/8', xterm='xterm h3s3')
        

        self.addLink(h1s1, s1)
        self.addLink(h2s1, s1)
        self.addLink(h3s1, s1)

        self.addLink(h1s2, s2)
        self.addLink(h2s2, s2)
        self.addLink(h3s2, s2)

        self.addLink(h1s3, s3)
        self.addLink(h2s3, s3)
        self.addLink(h3s3, s3)

        self.addLink(s1, s2)
        self.addLink(s2, s3)
        
if __name__ == '__main__':
    setLogLevel('info')
    topo =  TopoBuilder()
    c0 = RemoteController('c0')
    net = Mininet(topo=topo, controller=c0)
    net.start()
    CLI(net)
    net.stop()
