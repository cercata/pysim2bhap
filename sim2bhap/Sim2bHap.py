#!/usr/bin/python
# -*- coding: utf-8 -*-

#########################################
fuente = ("courier new", "10")
fuenteNeg = ("courier new", "10", "bold")
ancho = 160
alto =  16
windowTitleBase = "Sim2bHaptcis"
autoScroll = True
cycleTime = 0.042
configFile = 'Sim2bHap.ini'
logfile    = 'Sim2bHap.log'
hostListValid = ['127.0.0.1']
port = 500
activeSim = 'MSFS'
speedThreshold = 75
rpmThreshold = 95  
aoaThreshold = 75
gfeThreshold = 3
maxSpeed = 700
maxRpm = 3000
maxAoA   = 20
fullArms = False
accelThreshold = 0.5
forceMultiplier = 1.0
durationMultiplier = 1.0
iconFile = 'mini_plane.ico'
#########################################

import os, sys, os.path
import time
import traceback
import configparser
import base64

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
    aoaThreshold   = float(aoaEntry.get())/100
    gfeThreshold   = float(gfeEntry.get())
    maxSpeed       = float(maxSpeedEntry.get())
    maxRpm         = float(maxRpmEntry.get())
    maxAoA         = float(maxAoAEntry.get())
    fullArms       = varArms.get()
    accelThreshold  = float(accelEntry.get())
    forceMultiplier = float(multiEntry.get())
    durationMultiplier = float(multi2Entry.get())
    if simName == 'MSFS':
      import msfsBHap
      sim = msfsBHap.Sim(port, ipAddr)
    elif simName == 'IL2BoX':
      import il2bBHap
      sim = il2bBHap.Sim(port, ipAddr)
    elif simName == 'DCS':
      try:
        import dcs2bBHap
        sim = dcs2bBHap.Sim(port, ipAddr)
      except:
        sim = dummySim(port, ipAddr)
    else:
      display_msg("Invalid sim\n", tag = "error")  
      run = 0
    if run:
      sim.speedThreshold = speedThreshold
      sim.rpmThreshold   = rpmThreshold
      sim.aoaThreshold   = aoaThreshold
      sim.gfeThreshold   = gfeThreshold
      sim.fullArms       = fullArms
      sim.accelThreshold  = accelThreshold
      sim.maxSpeed       = maxSpeed
      sim.maxRpm         = maxRpm
      sim.maxAoA         = maxAoA
      sim.forceMultiplier= forceMultiplier
      sim.durationMultiplier = durationMultiplier
      output = sim.start()
      time.sleep(1)
      display_msg(output[0], tag = output[1])
      if (output[1] != 'error'):
        connectedLabel['background'] = 'green'
      else:
        connectedLabel['background'] = 'red'
        run = 0
    while run:
      try:
        startTime = time.time()
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
        elapsed = time.time() - startTime
        sleepTime = cycleTime - elapsed
        if sleepTime > 0:
          time.sleep(sleepTime)
      except:
        display_msg(traceback.format_exc(), tag = "error")
        log.exception('')
        time.sleep(cycleTime*2)
    output = sim.stop()
    sim = None
    if (output[1] == 'error'):
      connectedLabel['background'] = 'red'
    display_msg(output[0], tag = output[1])
    sim = None
  
  except:
    run = 0
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
  
valuesVarlist = ['activeSim', 'speedThreshold', 'rpmThreshold', 'aoaThreshold', 'gfeThreshold', 
   'maxSpeed', 'maxRpm', 'maxAoA', 'fullArms', 'accelThreshold', 'forceMultiplier', 'durationMultiplier']
def loadVars(altSection = ""):
  for varName in valuesVarlist:
    if altSection and parser.has_option(altSection, varName):
      section = altSection
    elif parser.has_option('values', varName):
      section = 'values'
    else:
      continue
    #print ("{} {}".format(section,varName))
    if varName in ('activeSim',):
      globals()[varName] = parser.get(section,varName).strip()
    elif varName in ('fullArms',):
      globals()[varName] = parser.getboolean(section,varName)
    else:
      globals()[varName] = parser.getfloat(section,varName)
      
def setEntry(entry, value):
  entry.delete(0, END)
  entry.insert(0, value)

def simSelected(event = None):
  globals()['activeSim'] = simCombo.get()
  updatePortToSim()

def updatePortToSim():
  try:
    simPort = parser.getint("host", activeSim + "_port")
    setEntry(portEntry, str(simPort))
  except:
    pass
      
def loadPreset(event = None):
  section = presetCombo.get()
  loadVars (section)
  try:
    simCombo.current(simCombo['values'].index(activeSim))
  except:
    simCombo.current(0)
    
  updatePortToSim()
   
  setEntry(speedEntry, str(speedThreshold))
  setEntry(rpmEntry, str(rpmThreshold))
  setEntry(aoaEntry ,str(aoaThreshold))
  setEntry(gfeEntry, str(gfeThreshold))
  setEntry(maxSpeedEntry, str(maxSpeed))
  setEntry(maxRpmEntry, str(maxRpm))
  setEntry(maxAoAEntry, str(maxAoA))
  setEntry(accelEntry, str(accelThreshold))
  setEntry(multiEntry, str(forceMultiplier))
  setEntry(multi2Entry, str(durationMultiplier))
  varArms.set(fullArms)


if __name__ == "__main__": 

  try:
  
    run = 0
    basename = os.path.basename(sys.argv[0])

    try:
      log.getLogger().setLevel(log.DEBUG)
      logformat = "%(asctime)s - PID %(process)5d - %(levelname)-8s - %(message)s - %(module)s - %(funcName)s - line:%(lineno)d"

      if basename.endswith('.exe'):
        Sim2bHapPath = os.path.dirname(os.path.realpath(sys.argv[0]))
      else:
        Sim2bHapPath = os.path.dirname(os.path.realpath(__file__))
      os.chdir(Sim2bHapPath)
      logpath   = os.path.join (Sim2bHapPath, logfile)
      
      formatter1 = logging.Formatter(logformat)
      ch1 = logging.handlers.RotatingFileHandler(logpath, maxBytes=10000000, backupCount=3)
      ch1.setLevel(log.INFO)
      ch1.setFormatter(formatter1)
      log.getLogger().addHandler(ch1)
      
    except:
      pass
      
    windowTitle = windowTitleBase
    parser = configparser.ConfigParser()
    parser.read(configFile)
    
    presetList = []

    try:
      for section in parser.sections():
        if section not in ('window', 'host', 'values'):
          presetList.append(section)
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
      if parser.has_section('values'):
        loadVars()
        #if parser.has_option('values','activeSim'):
        #  activeSim = parser.get('values','activeSim').strip()
        #if parser.has_option('values','speedThreshold'):
        #  speedThreshold = parser.getfloat('values','speedThreshold')
        #if parser.has_option('values','rpmThreshold'):
        #  rpmThreshold = parser.getfloat('values','rpmThreshold')
        #if parser.has_option('values','aoaThreshold'):
        #  aoaThreshold = parser.getfloat('values','aoaThreshold')
        #if parser.has_option('values','gfeThreshold'):
        #  gfeThreshold = parser.getfloat('values','gfeThreshold')
        #if parser.has_option('values','maxSpeed'):
        #  maxSpeed = parser.getfloat('values','maxSpeed')
        #if parser.has_option('values','maxRpm'):
        #  maxRpm = parser.getfloat('values','maxRpm')
        #if parser.has_option('values','maxAoA'):
        #  maxAoA = parser.getfloat('values','maxAoA')
        #if parser.has_option('values','fullArms'):
        #  fullArms = parser.getboolean('values','fullArms')
        #if parser.has_option('values','accelThreshold'):
        #  accelThreshold = parser.getfloat('values','accelThreshold')
        #if parser.has_option('values','forceMultiplier'):
        #  forceMultiplier = parser.getfloat('values','forceMultiplier')
        #if parser.has_option('values','durationMultiplier'):
        #  durationMultiplier = parser.getfloat('values','durationMultiplier')
          
    except:
      log.exception('Error reading configuration file')


    root =Tk()
    root.title(windowTitle)
    root.protocol("WM_DELETE_WINDOW", exit_program)

    try:
      root.wm_iconbitmap(iconFile)
    except:
      log.exception('Error setting ico file')      

    f0 = Frame(root)
     
    simLabel = Label(f0, text="Sim:")
    simLabel.grid(row=0, column=0, padx=1, pady=2, sticky=W)
    simCombo = Combobox(f0, width=12, state="readonly")
    simCombo.grid(row=0, column=1, padx=2, pady=2, sticky=W)
    #hostCombo.bind('<<ComboboxSelected>>', conversion)
    simCombo['values']=['MSFS', 'IL2BoX', 'DCS']
    simCombo.bind("<<ComboboxSelected>>", simSelected)
    
    try:
      simCombo.current(simCombo['values'].index(activeSim))
    except:
      simCombo.current(0)

    hostLabel = Label(f0, text="IP:")
    hostLabel.grid(row=0, column=2, padx=1, pady=2, sticky=W)
    hostCombo = Combobox(f0, width=12)
    hostCombo.grid(row=0, column=3, padx=2, pady=2, sticky=W)
    #hostCombo.bind('<<ComboboxSelected>>', conversion)
    hostCombo['values'] =hostListValid
    hostCombo.current(0)

    portLabel = Label(f0, text="Port:")
    portLabel.grid(row=0, column=4, padx=(8,1), pady=2, sticky=W)
    portEntry = Entry(f0, width=8)
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
    
    f0.pack(side=TOP, fill=X, padx=5, pady=(1,1))
    
    f0bis = Frame(root)
    presetLabel = Label(f0bis, text="Preset:")
    presetLabel.grid(row=0, column=0, padx=1, pady=2, sticky=W)
    presetCombo = Combobox(f0bis, width=24, state="readonly", height=24)
    presetCombo.grid(row=0, column=1, padx=2, pady=2, sticky=W)
    presetCombo['values']=["Default"] + sorted(presetList)
    presetCombo.bind("<<ComboboxSelected>>", loadPreset)
    
    presetBtn = Button(f0bis, text="LOAD", command=loadPreset)
    presetBtn.grid(row=0, column=2, padx=(10,2), pady=2, sticky=W)
    
    f0bis.pack(side=TOP, fill=X, padx=5, pady=(7,1))
    
    f1 = Frame(root)

    f1_0 = Frame(f1, relief=SUNKEN, width = "500")
    
    speedLabel = Label(f1_0, text="Speed Threshold (%): ")
    speedLabel.grid(row=1, column=0, padx=(10,2), pady=3, sticky=W)
    speedEntry = Entry(f1_0, width=10)
    speedEntry.grid(row=1, column=1, padx=2, pady=(10,6), sticky=W)
    speedEntry.insert(0,str(speedThreshold))

    rpmLabel = Label(f1_0, text="RPM Threshold (%): ")
    rpmLabel.grid(row=2, column=0, padx=(10,2), pady=3, sticky=W)
    rpmEntry = Entry(f1_0, width=10)
    rpmEntry.grid(row=2, column=1, padx=2, pady=(6,6), sticky=W)
    rpmEntry.insert(0,str(rpmThreshold))
    
    aoaLabel = Label(f1_0, text="AoA Threshold (%): ")
    aoaLabel.grid(row=3, column=0, padx=(10,2), pady=3, sticky=W)
    aoaEntry = Entry(f1_0, width=10)
    aoaEntry.grid(row=3, column=1, padx=2, pady=(6,6), sticky=W)
    aoaEntry.insert(0,str(aoaThreshold))

    gfeLabel = Label(f1_0, text="G Force Threshold (Gs): ")
    gfeLabel.grid(row=4, column=0, padx=(10,2), pady=3, sticky=W)
    gfeEntry = Entry(f1_0, width=10)
    gfeEntry.grid(row=4, column=1, padx=2, pady=(6,6), sticky=W)
    gfeEntry.insert(0,str(gfeThreshold))


    f1_0.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5,sticky=W+N+S+E)

    f1_1 = Frame(f1, relief=SUNKEN)
    
    maxSpeedLabel = Label(f1_1, text="Max Speed(Kmh): ")
    maxSpeedLabel.grid(row=1, column=0, padx=(10,2), pady=3, sticky=W)
    maxSpeedEntry = Entry(f1_1, width=10)
    maxSpeedEntry.grid(row=1, column=1, padx=2, pady=(10,6), sticky=W)
    maxSpeedEntry.insert(0,maxSpeed)

    maxRpmLabel = Label(f1_1, text="Max RPM: ")
    maxRpmLabel.grid(row=2, column=0, padx=(10,2), pady=3, sticky=W)
    maxRpmEntry = Entry(f1_1, width=10)
    maxRpmEntry.grid(row=2, column=1, padx=2, pady=(6,6), sticky=W)
    maxRpmEntry.insert(0,maxRpm)
    
    maxAoALabel = Label(f1_1, text="Max AoA(º): ")
    maxAoALabel.grid(row=3, column=0, padx=(10,2), pady=3, sticky=W)
    maxAoAEntry = Entry(f1_1, width=10)
    maxAoAEntry.grid(row=3, column=1, padx=2, pady=(6,6), sticky=W)
    maxAoAEntry.insert(0,maxAoA)

    accelLabel = Label(f1_1, text="Accel. Threshold (m/s2): ")
    accelLabel.grid(row=4, column=0, padx=(10,2), pady=3, sticky=W)
    accelEntry = Entry(f1_1, width=10)
    accelEntry.grid(row=4, column=1, padx=2, pady=(10,6), sticky=W)
    accelEntry.insert(0,str(accelThreshold))
    
    f1_1.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5,sticky=W+N+S+E)
    
    f1_2 = Frame(f1, relief=SUNKEN)
    
    varArms = IntVar()
    arms= Checkbutton(f1_2, text="All in Arms", variable = varArms, onvalue = 1, offvalue = 0)
    arms.grid(row=1, column=0, columnspan=2, padx=(10,2), pady=5, sticky=W)
    varArms.set(fullArms)
    
    multiLabel = Label(f1_2, text="Force Multiplier: ")
    multiLabel.grid(row=3, column=0, padx=(10,2), pady=3, sticky=W)
    multiEntry = Entry(f1_2, width=10)
    multiEntry.grid(row=3, column=1, padx=2, pady=(6,6), sticky=W)
    multiEntry.insert(0,forceMultiplier)

    multi2Label = Label(f1_2, text="Duration Multiplier: ")
    multi2Label.grid(row=4, column=0, padx=(10,2), pady=3, sticky=W)
    multi2Entry = Entry(f1_2, width=10)
    multi2Entry.grid(row=4, column=1, padx=2, pady=(6,6), sticky=W)
    multi2Entry.insert(0,durationMultiplier)

    f1_2.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5,sticky=W+N+S+E)
      
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
