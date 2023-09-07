how to run app:  

- start ryu controller  
- start mininet topology script  



to run ryu controller, use the command:  `ryu-manager --observe-links custom_controller.py`  
to run mininet script, use command:      `sudo python3 mininet_topo_script.py`  
  
    
      

or you can as well just create a mininet topology from the terminal eg: `sudo mn --topo single,3 --mac --controller remote --switch ovsk`  

it's your choice really just start the ryu controller first.  
because that way the controller can detect network devices and their links as they are instanciated   
on the mininet network : )

