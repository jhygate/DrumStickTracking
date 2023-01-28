"""Take drum hits and convert to sheet music pdf"""

import os
import math

#Array of hits where each index is a note of the highest subdivision
hits = [1,1,1,1 ,0,0,0,0 ,1,1,0,0 ,1,0,1,0]

def frameHitListToSubdivisionHitList(fps,bpm,frameHitList,subdivision):
    #Do the maths youve already done loads
    numFrames = len(frameHitList)
    
    #bps = bpm / 60
    spb = 60/bpm
    spSubdiv = spb/(subdivision/4) # Only for 4/4
    spf = 1/fps

    videoLength = spf*numFrames
    numSubdivisons = int(videoLength/spSubdiv)+1

    subHitList = [[] for sub in range(numSubdivisons)]

    secondsPassed = 0

    firstIndexSet = False

    for frameHit in frameHitList:
        if len(frameHit) >= 1:
            subIndex = int(round(secondsPassed/spSubdiv,0))
            if not firstIndexSet:
                firstIndexSet = True
                firstIndex = subIndex
            subHitList[subIndex-firstIndex].append(frameHit[0])

        secondsPassed += spf

    return subHitList

def createSnareMusic(subHitist,subdivion):
    musicStr = ''
    for hit in subHitist:
        if 'sn' in hit:
            musicStr += 'sn'+str(subdivion)
        else:
            musicStr += 'r'+str(subdivion)

    with open('lilypad.ly', 'w') as f:
        opener = """\\version "2.22.2"
                    \\score {
                        \\drums {
                            \\tempo 4 = 60
                        """

        closer = "}}"

        f.write(opener)
        f.write(musicStr)
        f.write(closer)

    os.system("lilypond lilypad.ly")
    

    


def addDrumMode(drumArray,name,drumModeString):#
    #Return drumModeString after adding 
    #down = \drummode {
    #  bassdrum4 snare8 bd r bd sn4
    #}
    pass







lilyString = ""
for hit in hits:
    if hit:
        lilyString += "sn16 "
    else:
        lilyString += "r16 "
    





