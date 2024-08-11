## How to run app:  
---
Basic Steps (Outline)
- start ryu controller  
- start mininet topology script  

to run the ryu controller, use the command:  `ryu-manager --observe-links custom_controller.py`  
to run the mininet script, use the command:      `sudo python3 mininet_topo_script.py`  

or you can as well create a mininet topology from the terminal eg: `sudo mn --topo single,3 --mac --controller remote --switch ovsk`  

Make sure to start the ryu controller first.  
So that way the controller can detect network devices and their links as they are instantiated   
on the mininet network (^_^ )

---

[Here](https://the-garden-iota.vercel.app/notes/exploring-computer-networks/building-a-simple-software-defined-network-with-ryu-and-mininet-in-python) I talk about my implementation of the SDN in detail : )