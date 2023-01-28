import tkinter as tk
from tkinter import filedialog as fd

import numpy as np
import cv2
from PIL import Image, ImageTk

import drumCircleSelection
import projectTypes




class startPage:
    def __init__(self, master):
        self.master = master

        self.videoPath = None
        self.drums = []


        self.showStartPage()



    def clearPage(self):
        self.frame.destroy()
        



    def showStartPage(self):
        self.frame = tk.Frame(self.master)

        self.button1 = tk.Button(self.frame, text ='Saved Transcriptions', width = 25)
        self.button1.pack()

        self.button2 = tk.Button(self.frame, text ='Transcribe New Video', width = 25,command = lambda:self.transcribe())
        self.button2.pack()
        self.frame.pack()

    def showDrumCircleSelectionPage(self):
        self.clearPage()

        self.frame = tk.Frame(self.master)

        image = cv2.imread(self.videoPath)
        height, width, no_channels = image.shape

        sf = 500/height
        # image = cv2.resize(image,[int(width*sf),int(height*sf)])

        for drum in self.drums:
            cv2.circle(image,drum.centre,drum.radius,[255,200,255],-1)
            cv2.putText(image,drum.name,drum.centre,cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),1)





        #Rearrang the color channel
        b,g,r = cv2.split(image)
        img = cv2.merge((r,g,b))

        

        # Convert the Image object into a TkPhoto object
        im = Image.fromarray(img)
        self.imgtk = ImageTk.PhotoImage(image=im) 

        # Put it in the display window
        label1 = tk.Label(self.frame, image=self.imgtk)
        label1.pack()

        self.addSnareButton = tk.Button(self.frame, text ='Add Snare', width = 25,command=lambda:self.addDrum(image,'Snare','sn'))
        self.addSnareButton.pack()

        self.addHihatButton = tk.Button(self.frame, text ='Add Hihat', width = 25,command=lambda:self.addDrum(image,'Hihat','hh'))
        self.addHihatButton.pack()

        self.startTranscription = tk.Button(self.frame, text ='Begin Transcription', width = 25)
        self.addHihatButton.pack()


    
        self.frame.pack()

    def addDrum(self,img,name,notation):
        centre,radius = drumCircleSelection.drumSelector(img)
        if centre:
            newDrum = projectTypes.drumCircle(centre,radius,notation,name)
            self.drums.append(newDrum)
        self.showDrumCircleSelectionPage()




    




    def new_window(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Demo2(self.newWindow)

    def transcribe(self):
        self.videoPath = fd.askopenfilename()
        self.clearPage()
        self.showDrumCircleSelectionPage()



class Demo2:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
    def close_windows(self):
        self.master.destroy()

def main(): 
    root = tk.Tk()
    app = startPage(root)
    root.mainloop()

if __name__ == '__main__':
    main()