import modbus.client.async_client as async_client
import modbus.server.async_server as async_server
import asyncio
import time


async def initialize_application():

    print("What machine do you want to start?")
    result = input("Put your number (1 to 3) here: ")

    if result == "1":
        modbus_async_server = await async_server.async_helper()
    elif result == "2":
        host = input("Put your IP here: ")
        register_info: list = []
        modbus_async_client = async_client.setup_async_client(host)
        res = await async_client.run_async_client(modbus_async_client)
        if res is not None:
            print("### Information received successfully! ###")
            print(res.registers)
            register_info = res.registers

        modbus_async_client.close()
        print("### Modbus client closed. ###")
        print("### Sending application to sleep to establish next checkpoint! ###")
        time.sleep(7)

    elif result == "3":
        pass
    else:
        print("Error, no option with such value!")


async def startup_menu():
    print("Welcome to the TriProt application!")
    print("Choose one of possible options: ")
    for i in range(0, len(options)):
        print(f"{i+1}: {options[i]}")

    result = input("Put your number here: ")

    if result == "1":
        await initialize_application()
    elif result == "2":
        pass
    elif result == "3":
        pass
    else:
        print("Error, no option with such value!")


options = ["Start app.", "Exit.", "How it works?"]

if __name__ == "__main__":
    asyncio.run(startup_menu())
