#!/usr/bin/python
# -*- coding: utf-8 -*-

#########################################
fuente = ("courier new", "10")
fuenteNeg = ("courier new", "10", "bold")
ancho = 80
alto =  16
windowTitleBase = "Sim2bHaptcis"
autoScroll = True
cycleTime = 0.125
configFile = 'Sim2bHap.ini'
logfile    = 'Sim2bHap.log'
hostListValid = ['127.0.0.1']
port = 500
#########################################

import os, sys, os.path
import time
import traceback
import configparser
#import simconnect

from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.ttk import *

import logging as log
import logging.handlers


class dummySim():
  def __init__(self, port, ipAddr = '127.0.0.1'):
    self.cycle = 0
    pass
  def start(self):
    self.cycle = 0
    return ("dummySim started\n", "valid")
  def runCycle(self):
    self.cycle += 1
    errCode = 'none'
    #import random
    #errCode = random.choice(["none", "valid", "error"])
    return ("  dummySim Cycle {}\n".format(self.cycle), errCode)
  def stop(self):
    return ("dummySim stopped\n", "valid")

def exit_program():
  try:
    if run:
      stopFunc()
    flushAreaToLog()
  except:
    pass
  root.destroy()
  
def dummyFunc(arg1 = 0):
  pass

def flushAreaToLog():
  text = textArea.get('1.0',END)
  if text.strip():
    log.info('TEXTAREA MESSAGE:\n%s' % (text.strip(),))

def display_msg(str, append=1, tag=None):
  textArea['state']=NORMAL
  if not append:
    flushAreaToLog()
    textArea.delete(1.0, END)
  if tag:
    textArea.insert(END, str, tag)
  else:
    textArea.insert(END, str,)
    #textArea.tag_add("error", CURRENT, END)
  textArea['state']=DISABLED
  textArea.update()
  if autoScroll:
    textArea.see("end")
  #log.info(str)


def runFunc():
  global run
  global sim
  if run == 1:
    return
  run = 1
  try:
    display_msg("Grabing config ...\n", 0)
    connectedLabel['background'] = 'orange'
    simName = simCombo.get()
    ipAddr  = hostCombo.get()
    port    = int(portEntry.get())
    speedThreshold = float(speedEntry.get())/100
    rpmThreshold   = float(rpmEntry.get())/100
    gfeThreshold   = float(gfeEntry.get())
    if simName == 'MSFS':
      import msfsBHap
      try:
        sim = msfsBHap.Sim(port, ipAddr)
      except:
        sim = dummySim(port, ipAddr)
      sim.speedThreshold = speedThreshold
      sim.rpmThreshold   = rpmThreshold
      sim.gfeThreshold   = gfeThreshold
      output = sim.start()
      time.sleep(1)
      display_msg(output[0], tag = output[1])
      if (output[1] != 'error'):
        connectedLabel['background'] = 'green'
      else:
        connectedLabel['background'] = 'red'
        run = 0
    else:
      display_msg("Invalid sim\n", tag = "error")  
      run = 0
    while run:
      try:
        output = sim.runCycle()
        if (output[1] != 'error'):
          connectedLabel['background'] = 'spring green'
          if (varVerbose.get() or output[1] == 'error'):
            display_msg(output[0], tag = output[1])
          else:
            textArea.update()
        else:
          connectedLabel['background'] = 'red'
          display_msg(output[0], tag = output[1])
        time.sleep(cycleTime)
      except:
        display_msg(traceback.format_exc(), tag = "error")
        time.sleep(cycleTime*2)
    output = sim.stop()
    if (output[1] == 'error'):
      connectedLabel['background'] = 'red'
    display_msg(output[0], tag = output[1])
    sim = None
  
  except:
    display_msg(traceback.format_exc(), tag = "error")

def stopFunc():
  global run
  run = 0
  connectedLabel['background'] = 'orange'

def tacopy():
  textArea.event_generate('<<Copy>>')
  pass
  
def tacopyall():
  text = textArea.get('0.0',END)
  root.clipboard_clear()
  root.clipboard_append(text)  

def popup(event):
  menu.post(event.x_root, event.y_root)

if __name__ == "__main__": 

  try:
  
    run = 0
    basename = os.path.basename(sys.argv[0])

    try:
      log.getLogger().setLevel(log.DEBUG)
      logformat = "%(asctime)s - PID %(process)5d - %(levelname)-8s - %(message)s - %(module)s - %(funcName)s - line:%(lineno)d"

      if basename.endswith('.exe'):
        Sim2bHapPath = os.path.dirname(os.path.realpath(argv[0]))
      else:
        Sim2bHapPath = os.path.dirname(os.path.realpath(__file__))
      os.chdir(Sim2bHapPath)
      logpath   = os.path.join (Sim2bHapPath, logfile)
      print (logpath)
      
      formatter1 = logging.Formatter(logformat)
      ch1 = logging.handlers.RotatingFileHandler(logpath, maxBytes=10000000, backupCount=3)
      ch1.setLevel(log.DEBUG)
      ch1.setFormatter(formatter1)
      log.getLogger().addHandler(ch1)
      
    except:
      pass
      
    windowTitle = windowTitleBase
    parser = configparser.ConfigParser()
    parser.read(configFile)

    try:
      if parser.has_section('window'):
        if parser.has_option('window', 'font'):  
          fuente = eval(parser.get('window', 'font'))
        if parser.has_option('window', 'fontBold'):  
          fuenteNeg = eval(parser.get('window', 'fontBold'))
        if parser.has_option('window', 'width'):  
          ancho = parser.getint('window', 'width')
        if parser.has_option('window', 'height'):  
          alto = parser.getint('window', 'height')
        if parser.has_option('window', 'caption'):  
          windowTitle = windowTitleBase + ' - ' + parser.get('window', 'caption').strip()
      if parser.has_section('host'):
        if parser.has_option('host','hostlist'):
          hostListValid = []
          hostlist = parser.get('host','hostlist').split(',')
          for hostip in hostlist:
            hostip = hostip.strip()
            hostListValid.append(hostip.strip())
      if parser.has_option('host','port'):
        port = parser.getint('host','port')
    except:
      log.exception('Error reading configuration file')


    root =Tk()
    root.title(windowTitle)
    root.protocol("WM_DELETE_WINDOW", exit_program)

    f0 = Frame(root)
     
    simLabel = Label(f0, text="Sim:")
    simLabel.grid(row=0, column=0, padx=1, pady=2, sticky=W)
    simCombo = Combobox(f0, width=15)
    simCombo.grid(row=0, column=1, padx=2, pady=2, sticky=W)
    #hostCombo.bind('<<ComboboxSelected>>', conversion)
    simCombo['values']=['MSFS']
    simCombo.current(0)

    hostLabel = Label(f0, text="IP:")
    hostLabel.grid(row=0, column=2, padx=1, pady=2, sticky=W)
    hostCombo = Combobox(f0, width=15)
    hostCombo.grid(row=0, column=3, padx=2, pady=2, sticky=W)
    #hostCombo.bind('<<ComboboxSelected>>', conversion)
    hostCombo['values'] =hostListValid
    hostCombo.current(0)

    portLabel = Label(f0, text="Port:")
    portLabel.grid(row=0, column=4, padx=(8,1), pady=2, sticky=W)
    portEntry = Entry(f0, width=10)
    portEntry.grid(row=0, column=5, padx=0, pady=2, sticky=W)
    portEntry.insert(0, str(port))

    connectedLabel = Label(f0, text="    ", background="orange", relief=SUNKEN)
    connectedLabel.grid(row=0, column=6, padx=1, pady=2, sticky=W)
    
    connectBtn = Button(f0, text="dummy", command=dummyFunc)
    #connectBtn.grid(row=0, column=7, padx=(10,2), pady=5, sticky=W)

    disconnectBtn = Button(f0, text="dummy", command=dummyFunc)
    #disconnectBtn.grid(row=0, column=8, padx=(3,2), pady=5, sticky=W)
    
    validBtn = Button(f0, text="dummy", command=lambda:dummyFunc(1))
    #validBtn.grid(row=0, column=10, padx=(10,2), pady=5, sticky=W)

    runBtn = Button(f0, text=" RUN ", command=runFunc)
    runBtn.grid(row=0, column=11, padx=(15,2), pady=5, sticky=W)

    stopBtn = Button(f0, text=" STOP ", command=stopFunc)
    stopBtn.grid(row=0, column=12, padx=(15,2), pady=5, sticky=W)

    varVerbose = IntVar()
    verbose= Checkbutton(f0, text="Verbose", variable = varVerbose, onvalue = 1, offvalue = 0)
    verbose.grid(row=0, column=13, columnspan=2, padx=2, pady=5, sticky=W)
    
    f0.pack(side=TOP, fill=X, padx=5, pady=(7,1))
    
    configEleList = []
    f1 = Frame(root)

    f1_0 = Frame(f1, relief=SUNKEN, width = "500")

    speedLabel = Label(f1_0, text="Speed Threshold (%): ")
    speedLabel.grid(row=2, column=0, padx=(10,2), pady=3, sticky=W)
    speedEntry = Entry(f1_0, width=10)
    speedEntry.grid(row=2, column=1, padx=2, pady=(10,6), sticky=W)
    speedEntry.insert(0,"75")

    rpmLabel = Label(f1_0, text="RPM Threshold (%): ")
    rpmLabel.grid(row=3, column=0, padx=(10,2), pady=3, sticky=W)
    rpmEntry = Entry(f1_0, width=10)
    rpmEntry.grid(row=3, column=1, padx=2, pady=(6,6), sticky=W)
    rpmEntry.insert(0,"95")

    gfeLabel = Label(f1_0, text="G Force Threshold (Gs): ")
    gfeLabel.grid(row=4, column=0, padx=(10,2), pady=3, sticky=W)
    gfeEntry = Entry(f1_0, width=10)
    gfeEntry.grid(row=4, column=1, padx=2, pady=(6,6), sticky=W)
    gfeEntry.insert(0,"3")


    f1_0.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5,sticky=W+N+S+E)

    f1_1 = Frame(f1, relief=SUNKEN)
    
    dummy1Label = Label(f1_1, text="dummy label: ")
    dummy1Label.grid(row=2, column=0, padx=(10,2), pady=3, sticky=W)
    dummy1Entry = Entry(f1_1, width=10)
    dummy1Entry.grid(row=2, column=1, padx=2, pady=(10,6), sticky=W)
    dummy1Entry.insert(0,"0")

    dummy2Label = Label(f1_1, text="dummy label: ")
    dummy2Label.grid(row=3, column=0, padx=(10,2), pady=3, sticky=W)
    dummy2Entry = Entry(f1_1, width=10)
    dummy2Entry.grid(row=3, column=1, padx=2, pady=(6,6), sticky=W)
    dummy2Entry.insert(0,"0")

    dummy3Label = Label(f1_1, text="dummy label: ")
    dummy3Label.grid(row=4, column=0, padx=(10,2), pady=3, sticky=W)
    dummy3Entry = Entry(f1_1, width=10)
    dummy3Entry.grid(row=4, column=1, padx=2, pady=(6,6), sticky=W)
    dummy3Entry.insert(0,"0")
    
    #f1_1.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5,sticky=W+N+S+E)
      
    f1.pack(padx=0, pady=0, side=TOP, fill=X)

    f2 = Frame(root)

    scrollbar = Scrollbar(f2, orient=VERTICAL)
    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbarh = Scrollbar(f2, orient=HORIZONTAL)
    scrollbarh.pack(side=BOTTOM, fill=X)
    textArea = Text(f2, wrap=NONE, height=alto, width=ancho, font=fuente, yscrollcommand=scrollbar.set, xscrollcommand=scrollbarh.set)
    textArea.pack(fill=BOTH, expand=Y)
    #textArea.tag_config("error", foreground="red")
    textArea.tag_config("error", foreground="red", font=fuenteNeg)
    textArea.tag_config("valid", foreground="#0007ff000", font=fuenteNeg)
    scrollbar.config(command=textArea.yview)
    scrollbarh.config(command=textArea.xview)
    f2.pack(side=TOP, padx=5, pady=3,fill=BOTH, expand=Y)
    
    # create a popup menu
    menu = Menu(textArea, tearoff=0)
    menu.add_command(label="Copy", command=tacopy)
    menu.add_command(label="Copy All", command=tacopyall)

    # attach popup to textarea
    textArea.bind("<Button-3>", popup)

  except:
    log.exception('UNEXPECTED EXCEPTION WHILE RUNNING')
 
  try:
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())

    root.mainloop()
    
    log.info('Ending Sim2bHaptcis properly')
  except:
    log.exception('UNEXPECTED EXCEPTION WHILE RUNNING')
