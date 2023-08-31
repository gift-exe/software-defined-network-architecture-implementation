from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI

def create_topology():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    # Add two switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    # Add three hosts
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')

    # Add links between switches and hosts
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s2, h3)

    # Start the network
    net.start()

    # Add the controller
    c0 = RemoteController
    net.addController('c0')

    # Start the CLI (you can interact with the network now)
    CLI(net)

    # Stop the network when the CLI is closed
    net.stop()

if __name__ == '__main__':
    create_topology()