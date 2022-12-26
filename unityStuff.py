import UdpComms as U

def send_to_unity(pointA,pointB):
    sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)

    RPoint = ['R',pointA[0],pointA[1],pointA[2]]
    BPoint = ['B',pointB[0],pointB[1],pointB[2]]
    

    sock.SendData(str(RPoint)) # Send this string to other application
    sock.SendData(str(BPoint)) # Send this string to other applications
