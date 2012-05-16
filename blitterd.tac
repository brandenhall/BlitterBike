import os
from twisted.application import service, internet
from blitterbike import BlitterBikeServerFactory

application = service.Application("BlitterBike")

# attach the service to its parent application
service = internet.TCPServer(31337, BlitterBikeServerFactory())
service.setServiceParent(application)