# triprot
ICT-2 project with 3 protocols named TriProt

## Installation

It is needed to set a bridged adapter in VM settings before you start virtual machines. Otherwise you can have connectivity problems.

Requires dnp3-python, pymodbus, c104, which can be installed with pip:

```bash
pip install pymodbus
pip install dnp3-python
pip install c104
```

## Start application

After cloning or unpacking an archive with an application and entering the application folder via terminal, you need to start machines using the file startup.py:
```bash
python3 startup.py
```
and then select, which machine you want to be on in this particular instance.
Due to it's architecture, the application will guaranteedly work if you start machines 1 and 3 before the second one.

On machine 2, it will require to enter "your IP address" which is a Modbus VM IP address.

On machines 2 and 3 you will require to select protocol that will be used to translate Modbus. You will need to choose the same on both instances, and then type the third machine IP on your second instance.

Program actively prints out results in console.

## Modbus attack

To make Modbus attack, you can use the fourth VM (although doing the same from third VM using another terminal must work too). 
It is recommended to run the program without an attack first so you could see the difference, Modbus VM does not shutdown or restart after connecting from second VM, so results wil be easy to see.

You need to enter `/modbus/unauthorized_access/` folder and enter this command:
```bash
python3 edit_regs.py
```
It abuses the lack of authentication and authorization, pretends to be a Master and updates some registers with values from 3 to 6 (normal values set in Modbus in start are 17).

After that, run normal program on second and third VM. Results must change.
