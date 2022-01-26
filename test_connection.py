#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# A short test script based on the 'enocean_example.py' by kipe/enocean
# It creates the connection to the EnOcean Pi module and starts listening

from enocean.consolelogger import init_logging
import enocean.utils
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback

try:
    import queue
except ImportError:
    import Queue as queue

# for printing object attributes
import pprint
pp = pprint.PrettyPrinter(indent=2).pprint

# for interpreting the raw data of the nodon temp and hum sensor
from sensors.nodon import Nodon


if __name__ =="__main__":
    init_logging()

    # create new nodon sensor
    nodonSensor = Nodon()

    print("> create SerialCommunicator")
    communicator = SerialCommunicator()

    print("> start SerialCommunicator")
    communicator.start()

    # query base id of the module
    print('> The base ID of your module is (if this works, that means the EnOcean Pi module is recognized properly)')
    print('>> original: \t \t %s' % communicator.base_id)
    print(">> translated to hex: \t %s" % enocean.utils.to_hex_string(communicator.base_id))

    # if communicator.base_id is not None:
    #     print()
    #     print('> Sending example package.')
    #     print()
    #     communicator.send(assemble_radio_packet(communicator.base_id))

    # endless loop receiving radio packets
    while communicator.is_alive():
        try:
            # receive a packet if there is one
            packet = communicator.receive.get(block=True, timeout=1)

            # informative output
            print("----------------------------------------------")
            print("> packet of type %s received:" % (type(packet)))
            print(">> attributes:")
            pp(vars(packet))
            print(">> content:")
            print(packet)
        
            # RORG.BS4 = 0xA4 = 165 = id of the sensor type.
            # 0xA4 is sensor for temperature (cf SUPPORTED_PROFILES.md at kipe/enocean on github)
            # PACKET.RADIO_ERP1 = 1, I think
            if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS4:
                # here starts my own part:
                # translate the raw data
                
                parsed_tye, parsed_data = nodonSensor.translate(packet.data)
                if parsed_tye == "unkown":
                    print("> Unrecognized sensor data")
                elif parsed_tye == "learning message":
                    print("> Learning signal detected")
                elif parsed_tye == "temp_and_hum":
                    # Interpretation after some crude experiments:
                    print("Temperature: ", parsed_data[0])
                    print("Humidity: ", parsed_data[1])
                else:
                    print("> Cannot translate BS4 message")
            else:
                print("> Unrecognized sensor data")
            print("----------------------------------------------")

        except queue.Empty:
            # there's just no message for us at the moment
            continue
        except KeyboardInterrupt:
            # ctrl + c was pressed
            break
        except Exception:
            print("ERROR:")
            traceback.print_exc(file=sys.stdout)
            break

    # properly stop communicator on exiting the script
    if communicator.is_alive():
        communicator.stop()
