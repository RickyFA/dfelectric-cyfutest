#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import os
import time
import tkinter as tk
from tkinter import filedialog, font

import adafruit_ads1x15.ads1115
import board
import busio
import RPi.GPIO as GPIO
import serial
from librpiplc import rpiplc

    ########################################################
    #### Rutas a directorios para carga/guarda archivos ####
    ########################################################
path_CargarReferencias="/home/pi/Desktop/Referencias/"
path_GuardarInformes="/home/pi/Desktop/Test_Reports/"
#path_CargarReferencias="/mnt/referencias_gg/"
#path_GuardarInformes="/mnt/testreports/"

    ##################################
    #### Monta Sensor Temperatura ####
    ##################################
try:
    SENS=serial.Serial('/dev/ttyACM0',9600,timeout=1)
except:
    print("Unable to initialize Serial Communication")

    ##################################
    #### Monta objetos en bus i2c ####
    ##################################

try:
    rpiplc.init("RPIPLC_V6", "RPIPLC_21", restart=False)
    rpiplc.analog_write("A0.7", 0)
    DATA=Adafruit_ADS1x15.ADS1115()
except:
    print("Unable to find I2C bus devices")

    #####################
    #### Declara IOs ####
    #####################
RelayPd=40 #Relé
RelayNoFus=31 #Relé
RelayFus=33 #Relé
BalizaVerde=32 #Relé
BalizaAmarilla=36 #Relé
BalizaRoja=38 #Relé
Fuente=37 # Relé (Contactor fon)
FinEnsayo=22 #Entrada
ParoEmerg=29 #Entrada

    ########################
    #### Inizializa IOs ####
    ########################
try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(RelayPd,GPIO.OUT)
    GPIO.output(RelayPd,1)
    GPIO.setup(RelayNoFus,GPIO.OUT)
    GPIO.output(RelayNoFus,1)
    GPIO.setup(RelayFus,GPIO.OUT)
    GPIO.output(RelayFus,1)
    GPIO.setup(BalizaVerde,GPIO.OUT)
    GPIO.output(BalizaVerde,0)
    GPIO.setup(BalizaAmarilla,GPIO.OUT)
    GPIO.output(BalizaAmarilla,1)
    GPIO.setup(BalizaRoja,GPIO.OUT)
    GPIO.output(BalizaRoja,1)
    GPIO.setup(Fuente,GPIO.OUT)
    GPIO.output(Fuente,0)
    GPIO.setup(FinEnsayo,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ParoEmerg,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    time.sleep(1)

except:
    print("Unable to load GPIOs")

    #######################################################
    #### Define clase Tk Aplicacion como MainRoot ####
    #######################################################

class Aplicacion():

    def __init__(self):
        self.root=tk.Tk()
        # self.root.geometry('1024x550+0+0')
        self.root.after(100, lambda: self.root.attributes('-fullscreen', True))
        self.root.title('Ensayo de Fusibles Cilíndricos')

        #############################################
        #### Declara tipos de fuente not default ####
        #############################################

        ButtonsFont1=tk.font.Font(size=26,weight=tk.font.BOLD)
        ButtonsFont2=tk.font.Font(size=14)
        ButtonsFont3=tk.font.Font(size=12)
        ResultsFont=tk.font.Font(size=10,weight=tk.font.BOLD)
        ClockFont=tk.font.Font(size=18)
        TempFont=tk.font.Font(size=14,weight=tk.font.BOLD)
        FontDisplays=tk.font.Font(family="Piboto",size=14,weight=tk.font.BOLD)

        ######################################
        #### Declara variables de control ####
        ######################################

        self.maintesttype=tk.IntVar()
        self.EDensayo=tk.IntVar()
        self.EDtalla=tk.IntVar()
        self.EDcable=tk.IntVar()
        self.EDPos=tk.IntVar()
        self.EDPosSondaCDT=tk.StringVar()
        self.EDtiempo=tk.IntVar()
        self.EDCorriente=tk.DoubleVar()
        self.EDTestM1=tk.StringVar()
        self.EDTestM2=tk.StringVar()
        self.EDTestM3=tk.StringVar()
        self.EDTestM4=tk.StringVar()
        self.EDTestM5=tk.StringVar()
        self.EDReportMessage=tk.StringVar()
        self.ReportName=tk.StringVar()
        self.fin_ensayo=tk.BooleanVar()
        self.Resultado=tk.StringVar()
        self.EAReferencia=tk.StringVar()
        self.EApath_referencia=tk.StringVar()
        self.EADatosEnsayo=tk.StringVar()
        self.EAOF=tk.StringVar()
        self.EAResM1=tk.StringVar()
        self.EAResM2=tk.StringVar()
        self.EAResM3=tk.StringVar()
        self.EACorriente1=tk.DoubleVar()
        self.EACorriente2=tk.DoubleVar()
        self.EACorriente3=tk.DoubleVar()
        self.EAtipo=tk.StringVar()
        self.EAtalla=tk.StringVar()
        self.EAPos=tk.IntVar()
        self.EAPosSondaCDT=tk.StringVar()
        self.last_corriente=tk.DoubleVar()
        self.Temperatura=tk.DoubleVar()
        self.Corriente_medida=tk.DoubleVar()
        self.CDT_medida=tk.DoubleVar()
        self.Last_Current=tk.DoubleVar()


        ####################################
        #### Declara variables a seguir ####
        ####################################

        self.EDtalla.trace('w',self.F_EDcalcularPos)
        self.EDcable.trace('w',self.F_EDcalcularPos)
        self.EDensayo.trace('w',self.F_EDcalcularPos)

        #########################
        #### Declara widgets ####
        #########################

        self.Clock=tk.Label(self.root,text="",font=ClockFont)
        self.TempFrame=tk.LabelFrame(self.root,text="T.amb.")
        self.TempLabel=tk.Label(self.TempFrame,text="",font=FontDisplays,bg='black',fg='white')
        self.CorrienteMedidaFrame=tk.LabelFrame(self.root,text="Corriente")
        self.CorrienteMedidaLabel=tk.Label(self.CorrienteMedidaFrame,textvariable=self.Corriente_medida,bg='black',fg='white',font=FontDisplays)
        self.CDTMedidaFrame=tk.LabelFrame(self.root,text="CDT")
        self.CDTMedidaLabel=tk.Label(self.CDTMedidaFrame,textvariable=self.CDT_medida,font=FontDisplays,bg='black',fg='white')
        self.mainbutton_ensayodirecto=tk.Radiobutton(self.root,indicatoron=0,text="ENSAYO\nESPECIFICO",font=ButtonsFont3,padx=20,variable=self.maintesttype,value=1,command=self.F_EnsayoDirecto)
        self.mainbutton_ensayoautomatico=tk.Radiobutton(self.root,indicatoron=0,text="ENSAYO\nAUTOMATICO",font=ButtonsFont3,padx=20,variable=self.maintesttype,value=2,command=self.F_EnsayoAutomatico)
        self.mainbutton_salir=tk.Button(self.root,text="SALIR",font=ButtonsFont3,padx=20,command=self.F_mainSalir)
        self.mainbutton_limpiarDatos=tk.Button(self.root,text="BORRAR\nDATOS",font=ButtonsFont3,padx=20,command=self.F_BorrarDatos)
        self.EDFrameEnsayo=tk.LabelFrame(self.root,text="Tipo de Ensayo",padx=5,pady=5)
        self.EDPotDis=tk.Radiobutton(self.EDFrameEnsayo,indicatoron=0,text="Potencia disipada",padx=20,variable=self.EDensayo,value=1,command=self.F_EnsayoPotDis)
        self.EDNoFusion=tk.Radiobutton(self.EDFrameEnsayo,indicatoron=0,text="No Fusión",padx=20,variable=self.EDensayo,value=2,command=self.F_EnsayoNoFusion)
        self.EDFusion=tk.Radiobutton(self.EDFrameEnsayo,indicatoron=0,text="Fusión",padx=20,variable=self.EDensayo,value=3,command=self.F_EnsayoFusion)
        self.EDFrameTalla=tk.LabelFrame(self.root,text="Talla",padx=5,pady=5)
        self.ED10x38=tk.Radiobutton(self.EDFrameTalla,indicatoron=0,text="10x38",padx=20,variable=self.EDtalla,value=100,command=self.F_cable10x38)
        self.ED14x51=tk.Radiobutton(self.EDFrameTalla,indicatoron=0,text="14x51",padx=20,variable=self.EDtalla,value=200,command=self.F_cable14x51)
        self.ED22x58=tk.Radiobutton(self.EDFrameTalla,indicatoron=0,text="22x58",padx=20,variable=self.EDtalla,value=300,command=self.F_cable22x58)
        self.EDFrameCable=tk.LabelFrame(self.root,text="Sección de cable",padx=5,pady=5)
        self.ED1mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="1mm",padx=20,variable=self.EDcable,value=10)
        self.ED1_5mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="1,5mm",padx=20,variable=self.EDcable,value=20)
        self.ED2_5mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="2,5mm",padx=20,variable=self.EDcable,value=30)
        self.ED4mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="4mm",padx=20,variable=self.EDcable,value=40)
        self.ED6mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="6mm",padx=20,variable=self.EDcable,value=50)
        self.ED10mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="10mm",padx=20,variable=self.EDcable,value=60)
        self.ED16mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="16mm",padx=20,variable=self.EDcable,value=70)
        self.ED25mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="25mm",padx=20,variable=self.EDcable,value=80)
        self.ED35mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="35mm",padx=20,variable=self.EDcable,value=90)
        self.ED50mm=tk.Radiobutton(self.EDFrameCable,indicatoron=0,text="50mm",padx=20,variable=self.EDcable,value=100)
        self.EDFrameTiempo=tk.LabelFrame(self.root,text="Tiempo de Ensayo",padx=5,pady=5)
        self.ED1hora=tk.Radiobutton(self.EDFrameTiempo,indicatoron=0,text="1 hora",padx=20,variable=self.EDtiempo,value=3600)
        self.ED2horas=tk.Radiobutton(self.EDFrameTiempo,indicatoron=0,text="2 horas",padx=20,variable=self.EDtiempo,value=7200)
        self.ED1min=tk.Radiobutton(self.EDFrameTiempo,indicatoron=0,text="1 minuto",padx=20,variable=self.EDtiempo,value=60)

        self.EDFrameCorriente=tk.LabelFrame(self.root,text="Corriente de Ensayo",padx=5,pady=5)
        self.EDLabelCorriente=tk.Label(self.EDFrameCorriente,text="Corriente de ensayo ")
        self.EDcorrienteEntry=tk.Entry(self.EDFrameCorriente,textvariable=self.EDCorriente,justify=tk.CENTER,font=TempFont)


        self.EDFramePosiCur=tk.LabelFrame(self.root,text="Preparación del ensayo")
        self.EDLabelPos1=tk.Label(self.EDFramePosiCur,text="Cargue muestra en la base ")
        self.EDLabelPos2=tk.Label(self.EDFramePosiCur,textvariable=self.EDPos)
        self.EDLabelPos3=tk.Label(self.EDFramePosiCur,textvariable=self.EDPosSondaCDT)
#        self.EDLabelCorriente=tk.Label(self.EDFramePosiCur,text="Corriente de ensayo ")
#        self.EDcorrienteEntry=tk.Entry(self.EDFramePosiCur,textvariable=self.EDCorriente)
        self.EDStartButton=tk.Button(self.root,text="ENSAYAR",command=self.F_EDstart,bg='green',activebackground='green',font=ButtonsFont1)
        self.EDStopButton=tk.Button(self.root,text="PARAR",command=self.F_EDstopButton,state=tk.DISABLED,bg='red',activebackground='red',font=ButtonsFont1)

        self.EDFrameTest=tk.LabelFrame(self.root,text="Resultados de ensayo")
        self.EDMessageTest1=tk.Label(self.EDFrameTest,textvariable=self.EDTestM1,justify=tk.LEFT,font=ResultsFont)
        self.EDMessageTest2=tk.Label(self.EDFrameTest,textvariable=self.EDTestM2,justify=tk.LEFT)
        self.EDMessageTest3=tk.Label(self.EDFrameTest,textvariable=self.EDTestM3,justify=tk.LEFT,font=ResultsFont)
        self.EDMessageTest4=tk.Label(self.EDFrameTest,textvariable=self.EDTestM4,justify=tk.LEFT,font=ResultsFont)
        self.EDMessageTest5=tk.Label(self.EDFrameTest,textvariable=self.EDTestM5,justify=tk.LEFT,font=ResultsFont)
        self.EDLabelTestReport=tk.Label(self.EDFrameTest,text="Comentario para el informe de ensayo",justify=tk.LEFT)
        self.EDEntryTestReport=tk.Text(self.EDFrameTest,state=tk.DISABLED)
        self.EDButtonTestReport=tk.Button(self.EDFrameTest,text="GENERAR INFORME",command=self.F_ReportGenerate,state=tk.DISABLED,font=ButtonsFont2)

        self.EAStartButton=tk.Button(self.root,text="ENSAYAR",command=self.F_EAstart,state=tk.DISABLED,bg='green',activebackground='green',font=ButtonsFont1)
        self.EAFrameCargarDatos=tk.LabelFrame(self.root,text="Datos de ensayo")
        self.EALabelReferencia=tk.Label(self.EAFrameCargarDatos,text="Referencia a ensayar",justify=tk.LEFT)
        self.EAEntryReferencia=tk.Entry(self.EAFrameCargarDatos,textvariable=self.EAReferencia,justify=tk.CENTER)
        self.EAButtonCargar=tk.Button(self.EAFrameCargarDatos,text="Cargar datos",command=self.F_EACargarDatos)
        self.EAButtonBuscar=tk.Button(self.EAFrameCargarDatos,text="Buscar",command=self.F_EABuscar)
        self.EALabelDatos=tk.Label(self.EAFrameCargarDatos,textvariable=self.EADatosEnsayo,justify=tk.LEFT)
        self.EAFrameDatosMuestras=tk.LabelFrame(self.root,text="Datos de las Muestras")
        self.EALabelOF=tk.Label(self.EAFrameDatosMuestras,text="Orden de Fabricación")
        self.EAEntryOF=tk.Entry(self.EAFrameDatosMuestras,textvariable=self.EAOF,justify=tk.CENTER)
        self.EALabelResistencias=tk.Label(self.EAFrameDatosMuestras,text="Valores de resistencia (mOhm)")
        self.EALabelRes1=tk.Label(self.EAFrameDatosMuestras,text="Muestra 1")
        self.EAEntryResM1=tk.Entry(self.EAFrameDatosMuestras,textvariable=self.EAResM1,justify=tk.CENTER)
        self.EALabelRes2=tk.Label(self.EAFrameDatosMuestras,text="Muestra 2")
        self.EAEntryResM2=tk.Entry(self.EAFrameDatosMuestras,textvariable=self.EAResM2,justify=tk.CENTER)
        self.EALabelRes3=tk.Label(self.EAFrameDatosMuestras,text="Muestra 3")
        self.EAEntryResM3=tk.Entry(self.EAFrameDatosMuestras,textvariable=self.EAResM3,justify=tk.CENTER)

        self.EAFramePos=tk.LabelFrame(self.root,text="Preparación del ensayo")
        self.EALabelPos1=tk.Label(self.EAFramePos,text="Cargue las muestras en las bases: ")
        self.EALabelPos2=tk.Label(self.EAFramePos,textvariable=self.EAPos)
        self.EALabelPos3=tk.Label(self.EAFramePos,textvariable=self.EAPosSondaCDT)

        #######################################
        #### Posiciona widgets permanentes ####
        #######################################

        self.mainbutton_ensayodirecto.place(x=25,y=50,width=120,height=75)
        self.mainbutton_ensayoautomatico.place(x=25,y=150,width=120,height=75)
        self.mainbutton_limpiarDatos.place(x=25,y=250,width=120,height=75)
        self.mainbutton_salir.place(x=25,y=475,width=120,height=75)
        self.Clock.place(x=900,y=45,width=100,height=40)
        self.TempFrame.place(x=905,y=90,width=110,height=60)
        self.TempLabel.place(relx=0.5,rely=0.5,width=90,height=35,anchor=tk.CENTER)
        self.CorrienteMedidaFrame.place(x=905,y=170,width=110,height=60)
        self.CorrienteMedidaLabel.place(relx=0.5,rely=0.5,width=90,height=35,anchor=tk.CENTER)
        self.CDTMedidaFrame.place(x=905,y=250,width=110,height=60)
        self.CDTMedidaLabel.place(relx=0.5,rely=0.5,width=95,height=35,anchor=tk.CENTER)

        ##################
        #### MAINLOOP ####
        ##################

        self.update_clock()
        self.update_temperature()
        self.root.mainloop()

        ######################################
        #### Define funciones principales ####
        ######################################

    def update_clock(self):
        now=time.strftime('%H:%M')
        self.Clock.configure(text=now)
        self.root.after(10000,self.update_clock)

    def update_temperature(self):
        try:
                SENS.write(('T').encode())
                temp=SENS.readline().decode("utf-8")
                temp=float(temp)
                #print(temp)
                last_temp=self.Temperatura.get()
                if last_temp==0.0:
                        last_temp=temp
                if temp>(last_temp+0.6):
                        self.Temperatura.set(last_temp*1.01)
                if temp<(last_temp-0.6):
                        self.Temperatura.set(last_temp*0.99)
                if (temp>(last_temp-0.6)) and (temp<(last_temp+0.6)):
                        #last_temp=temp
                        self.Temperatura.set(last_temp)
                self.TempLabel.configure(text= str("%.1f"%(last_temp)) + u"\u2103")
        except:
                print("No temperature data")
                self.TempLabel.configure(text=("--" + u"\u2103"))
        self.root.after(10000,self.update_temperature)





    def F_EnsayoDirecto(self):

        self.EAFrameCargarDatos.place_forget()
        self.EAFrameDatosMuestras.place_forget()
        self.EAFramePos.place_forget()
        self.EAStartButton.place_forget()
        self.EDStopButton.place_forget()
        self.EDFrameTest.place_forget()
        self.EDMessageTest1.place_forget()
        self.EDMessageTest2.place_forget()
        self.EDMessageTest3.place_forget()
        self.EDMessageTest4.place_forget()
        self.EDMessageTest5.place_forget()
        self.EDLabelTestReport.place_forget()
        self.EDEntryTestReport.place_forget()
        self.EDButtonTestReport.place_forget()


        self.EDensayo.set(0)
        self.EDtalla.set(0)
        self.EDcable.set(0)
        self.EDPos.set(0)
        self.EDPosSondaCDT.set("")
        self.EDtiempo.set(0)
        self.EDCorriente.set("")
        self.EDTestM1.set("")
        self.EDTestM2.set("")
        self.EDTestM3.set("")
        self.EDTestM4.set("")
        self.EDTestM5.set("")
        self.EDReportMessage.set("")
        self.ReportName.set("")
        self.Resultado.set("")
        self.EAReferencia.set("")
        self.EADatosEnsayo.set("")
        self.EAOF.set("")
        self.EAResM1.set("")
        self.EAResM2.set("")
        self.EAResM3.set("")
        self.EACorriente1.set(0)
        self.EACorriente2.set(0)
        self.EACorriente3.set(0)
        self.EAtipo.set("")
        self.EAtalla.set("")
        self.EAPos.set("")
        self.EAPosSondaCDT.set("")
        self.last_corriente.set(0)


        self.EDFrameEnsayo.place(x=170,y=45,width=140,height=160)
        self.EDPotDis.place(relx=0.5,rely=0.2,anchor=tk.CENTER,width=120,height=25)
        self.EDNoFusion.place(relx=0.5,rely=0.5,anchor=tk.CENTER,width=120,height=25)
        self.EDFusion.place(relx=0.5,rely=0.8,anchor=tk.CENTER,width=120,height=25)
        self.EDFrameTalla.place(x=327,y=45,width=140,height=160)
        self.ED10x38.place(relx=0.5,rely=0.2,anchor=tk.CENTER,width=120,height=25)
        self.ED14x51.place(relx=0.5,rely=0.5,anchor=tk.CENTER,width=120,height=25)
        self.ED22x58.place(relx=0.5,rely=0.8,anchor=tk.CENTER,width=120,height=25)
        self.EDFrameCable.place(x=484,y=45,width=250,height=160)
        self.ED1mm.place(relx=0.25,rely=0.1,anchor=tk.CENTER,width=105,height=25)
        self.ED1_5mm.place(relx=0.25,rely=0.3,anchor=tk.CENTER,width=105,height=25)
        self.ED2_5mm.place(relx=0.25,rely=0.5,anchor=tk.CENTER,width=105,height=25)
        self.ED4mm.place(relx=0.25,rely=0.7,anchor=tk.CENTER,width=105,height=25)
        self.ED6mm.place(relx=0.25,rely=0.9,anchor=tk.CENTER,width=105,height=25)
        self.ED10mm.place(relx=0.75,rely=0.1,anchor=tk.CENTER,width=105,height=25)
        self.ED16mm.place(relx=0.75,rely=0.3,anchor=tk.CENTER,width=105,height=25)
        self.ED25mm.place(relx=0.75,rely=0.5,anchor=tk.CENTER,width=105,height=25)
        self.ED35mm.place(relx=0.75,rely=0.7,anchor=tk.CENTER,width=105,height=25)
        self.ED50mm.place(relx=0.75,rely=0.9,anchor=tk.CENTER,width=105,height=25)
        self.EDFrameTiempo.place(x=750,y=45,width=140,height=105)
        self.ED1hora.place(relx=0.5,rely=0.14,anchor=tk.CENTER,width=120,height=25)
        self.ED2horas.place(relx=0.5,rely=0.5,anchor=tk.CENTER,width=120,height=25)
        self.ED1min.place(relx=0.5,rely=0.86,anchor=tk.CENTER,width=120,height=25)
        self.EDFrameCorriente.place(x=750,y=150,width=140,height=55)
        self.EDcorrienteEntry.place(x=20,rely=0.5,width=90,height=30,anchor=tk.W)

        self.EDFramePosiCur.place(x=170,y=235,width=260,height=90)
        self.EDLabelPos1.place(x=12,rely=0.3,width=160,height=15,anchor=tk.W)
        self.EDLabelPos2.place(x=194,rely=0.3,width=40,height=15,anchor=tk.W)
        self.EDLabelPos3.place(x=14,rely=0.65,width=210,height=15,anchor=tk.W)

        self.EDStartButton.place(x=450,y=236,width=210,height=90)
        self.EDStartButton.config(state=tk.ACTIVE,bg='green')
        self.EDStopButton.place(x=680,y=236,width=210,height=90)
        self.EDStopButton.config(state=tk.DISABLED)

        self.EDFrameTest.place(x=170,y=350,width=720,height=200)
        self.EDMessageTest1.place(x=25,rely=0.10)
        self.EDMessageTest2.place(x=25,rely=0.30)
        self.EDMessageTest3.place(x=25,rely=0.75)
        self.EDMessageTest4.place(x=25,rely=0.75)
        self.EDMessageTest5.place(x=25,rely=0.75)
        self.EDLabelTestReport.place(x=470,y=8,width=215,height=12)
        self.EDEntryTestReport.place(x=470,y=27,width=215,height=80)
        self.EDEntryTestReport.delete('1.0',tk.END)
        self.EDEntryTestReport.config(state=tk.DISABLED)
        self.EDButtonTestReport.place(x=470,y=115,width=215,height=50)
        self.EDButtonTestReport.config(state=tk.DISABLED)



        self.EDcorrienteEntry.focus()
        self.F_EDcalcularPos()


    def F_EnsayoAutomatico(self):

        self.EDFrameEnsayo.place_forget()
        self.EDFrameTalla.place_forget()
        self.EDFrameCable.place_forget()
        self.EDFrameTiempo.place_forget()
        self.EDFrameCorriente.place_forget()
        self.EDFramePosiCur.place_forget()
        self.EDStartButton.place_forget()
        self.EDStopButton.place_forget()
        self.EDFrameTest.place_forget()
        self.EDMessageTest1.place_forget()
        self.EDMessageTest2.place_forget()
        self.EDMessageTest3.place_forget()
        self.EDMessageTest4.place_forget()
        self.EDMessageTest5.place_forget()
        self.EDLabelTestReport.place_forget()
        self.EDEntryTestReport.place_forget()
        self.EDButtonTestReport.place_forget()


        self.EDensayo.set(0)
        self.EDtalla.set(0)
        self.EDcable.set(0)
        self.EDPos.set(0)
        self.EDPosSondaCDT.set("")
        self.EDtiempo.set(0)
        self.EDCorriente.set(0)
        self.EDTestM1.set("")
        self.EDTestM2.set("")
        self.EDTestM3.set("")
        self.EDTestM4.set("")
        self.EDTestM5.set("")
        self.EDReportMessage.set("")
        self.ReportName.set("")
        self.Resultado.set("")
        self.EAReferencia.set("")
        self.EApath_referencia.set("")
        self.EADatosEnsayo.set("")
        self.EAOF.set("")
        self.EAResM1.set("")
        self.EAResM2.set("")
        self.EAResM3.set("")
        self.EACorriente1.set(0)
        self.EACorriente2.set(0)
        self.EACorriente3.set(0)
        self.EAtipo.set("")
        self.EAtalla.set("")
        self.EAPos.set("")
        self.EAPosSondaCDT.set("")
        self.last_corriente.set(0)


        self.EAFrameCargarDatos.place(x=170,y=45,width=470,height=175)
        self.EALabelReferencia.place(x=22,y=25,width=120,height=12,anchor=tk.W)
        self.EAEntryReferencia.place(x=152,y=25,width=90,height=30,anchor=tk.W)
        self.EAButtonCargar.place(x=255,y=25,width=90,height=30,anchor=tk.W)
        self.EAButtonBuscar.place(x=365,y=25,width=90,height=30,anchor=tk.W)
        self.EALabelDatos.place(x=18,y=50,width=280,height=100)

        self.EAFrameDatosMuestras.place(x=660,y=45,width=230,height=175)
        self.EALabelOF.place(x=22,y=15,width=120,height=10,anchor=tk.W)
        self.EAEntryOF.place(x=100,y=35,width=90,height=25,anchor=tk.W)
        self.EALabelResistencias.place(x=20,y=60,width=180,height=10,anchor=tk.W)
        self.EALabelRes1.place(x=20,y=80,width=80,height=10,anchor=tk.W)
        self.EAEntryResM1.place(x=100,y=80,width=90,height=25,anchor=tk.W)
        self.EALabelRes2.place(x=20,y=110,width=80,height=10,anchor=tk.W)
        self.EAEntryResM2.place(x=100,y=110,width=90,height=25,anchor=tk.W)
        self.EALabelRes3.place(x=20,y=140,width=80,height=10,anchor=tk.W)
        self.EAEntryResM3.place(x=100,y=140,width=90,height=25,anchor=tk.W)

        self.EAFramePos.place(x=170,y=235,width=260,height=90)
        self.EALabelPos1.place(x=18,y=18,width=200,height=15,anchor=tk.W)
        self.EALabelPos2.place(x=60,y=37,width=140,height=15,anchor=tk.W)
        self.EALabelPos3.place(x=17,y=55,width=210,height=15,anchor=tk.W)
        self.EAStartButton.place(x=450,y=236,width=210,height=90)
        self.EAStartButton.config(state=tk.DISABLED)
        self.EDStopButton.place(x=680,y=236,width=210,height=90)
        self.EDStopButton.config(state=tk.DISABLED)
        self.EDFrameTest.place(x=170,y=350,width=720,height=200)
        self.EDMessageTest1.place(x=25,y=15)
        #self.EDMessageTest2.place(x=25,y=30)
        self.EDMessageTest3.place(x=25,y=40)
        self.EDMessageTest4.place(x=25,y=100)
        self.EDMessageTest5.place(x=25,y=140)
        self.EDLabelTestReport.place(x=470,y=8,width=215,height=12)
        self.EDEntryTestReport.place(x=470,y=27,width=215,height=80)
        self.EDEntryTestReport.delete('1.0',tk.END)
        self.EDEntryTestReport.config(state=tk.DISABLED)
        self.EDButtonTestReport.place(x=470,y=115,width=215,height=50)
        self.EDButtonTestReport.config(state=tk.DISABLED)

        self.EAEntryReferencia.focus()

    def F_BorrarDatos(self):
        def Borrar():
            TOPMensaje.destroy()
            self.EDensayo.set(0)
            self.EDtalla.set(0)
            self.EDcable.set(0)
            self.EDPos.set(0)
            self.EDPosSondaCDT.set("")
            self.EDtiempo.set(0)
            self.EDCorriente.set("")
            self.EDTestM1.set("")
            self.EDTestM2.set("")
            self.EDTestM3.set("")
            self.EDTestM4.set("")
            self.EDTestM5.set("")
            self.EDReportMessage.set("")
            self.ReportName.set("")
            self.Resultado.set("")
            self.EAReferencia.set("")
            self.EApath_referencia.set("")
            self.EADatosEnsayo.set("")
            self.EAOF.set("")
            self.EAResM1.set("")
            self.EAResM2.set("")
            self.EAResM3.set("")
            self.EACorriente1.set(0)
            self.EACorriente2.set(0)
            self.EACorriente3.set(0)
            self.EAtipo.set("")
            self.EAtalla.set("")
            self.EAPos.set("")
            self.EAPosSondaCDT.set("")
            self.last_corriente.set(0)
            self.EDEntryTestReport.delete('1.0',tk.END)

            self.EDPotDis.config(state=tk.ACTIVE)
            self.EDNoFusion.config(state=tk.ACTIVE)
            self.EDFusion.config(state=tk.ACTIVE)
            self.ED10x38.config(state=tk.ACTIVE)
            self.ED14x51.config(state=tk.ACTIVE)
            self.ED22x58.config(state=tk.ACTIVE)
            self.ED1mm.config(state=tk.ACTIVE)
            self.ED1_5mm.config(state=tk.ACTIVE)
            self.ED2_5mm.config(state=tk.ACTIVE)
            self.ED4mm.config(state=tk.ACTIVE)
            self.ED6mm.config(state=tk.ACTIVE)
            self.ED10mm.config(state=tk.ACTIVE)
            self.ED16mm.config(state=tk.ACTIVE)
            self.ED25mm.config(state=tk.ACTIVE)
            self.ED35mm.config(state=tk.ACTIVE)
            self.ED50mm.config(state=tk.ACTIVE)
            self.ED1hora.config(state=tk.ACTIVE)
            self.ED2horas.config(state=tk.ACTIVE)
            self.ED1min.config(state=tk.ACTIVE)
            self.EDcorrienteEntry.config(state=tk.NORMAL)
            self.EDStartButton.config(state=tk.ACTIVE)
            self.EAStartButton.config(state=tk.DISABLED)
            self.EAEntryReferencia.config(state=tk.NORMAL)
            self.EDEntryTestReport.config(state=tk.DISABLED)
            self.EDButtonTestReport.config(state=tk.DISABLED)
            self.EAButtonCargar.config(state=tk.ACTIVE)
            self.EAButtonBuscar.config(state=tk.ACTIVE)

            GPIO.output(RelayPd,1)
            GPIO.output(RelayNoFus,1)
            GPIO.output(RelayFus,1)
            GPIO.output(BalizaVerde,0)
            GPIO.output(BalizaAmarilla,1)
            GPIO.output(BalizaRoja,1)
            try:
                rpiplc.analog_write("A0.7", 0)
            except:
                print("Error en rpiplc.analog_write(\"A0.7\", 0)")

            #############
            #############
            #self.EDButtonTestReport.config(state=tk.ACTIVE)
            #self.EDEntryTestReport.config(state=tk.NORMAL)


        TOPMensaje=tk.Toplevel()
        TOPMensaje.geometry('180x150+200+200')
        TOPMensaje.config(relief=tk.RIDGE)
        TOPMensaje.title(" ")
        MensajeMessage=tk.Label(TOPMensaje,text="Se borrarán todos los datos \nde ensayo.\nDesea continuar?",justify=tk.LEFT)
        MensajeMessage.pack(fill=tk.X,expand=True)
        OKbutton=tk.Button(TOPMensaje, text="Borrar", command=Borrar)
        OKbutton.pack(fill=tk.X,padx=10,pady=5)
        CancelarButton=tk.Button(TOPMensaje,text="Cancelar",command=TOPMensaje.destroy)
        CancelarButton.pack(fill=tk.X,padx=10,pady=5)
        TOPMensaje.transient(self.root)
        TOPMensaje.grab_set()
        TOPMensaje.wait_window()

    def F_EnsayoPotDis(self):
        self.EDtiempo.set(0)
        self.ED1hora.config(state=tk.ACTIVE)
        self.ED2horas.config(state=tk.ACTIVE)
        self.ED1min.config(state=tk.DISABLED)
    def F_EnsayoNoFusion(self):
        self.EDtiempo.set(0)
        self.ED1hora.config(state=tk.ACTIVE)
        self.ED2horas.config(state=tk.ACTIVE)
        self.ED1min.config(state=tk.ACTIVE)
    def F_EnsayoFusion(self):
        self.EDtiempo.set(0)
        self.ED1hora.config(state=tk.ACTIVE)
        self.ED2horas.config(state=tk.ACTIVE)
        self.ED1min.config(state=tk.ACTIVE)



    def F_cable10x38(self):
        self.EDcable.set(0)
        self.ED10mm.config(state=tk.DISABLED)
        self.ED16mm.config(state=tk.DISABLED)
        self.ED25mm.config(state=tk.DISABLED)
        self.ED35mm.config(state=tk.DISABLED)
        self.ED50mm.config(state=tk.DISABLED)
    def F_cable14x51(self):
        self.EDcable.set(0)
        self.ED10mm.config(state=tk.ACTIVE)
        self.ED16mm.config(state=tk.DISABLED)
        self.ED25mm.config(state=tk.DISABLED)
        self.ED35mm.config(state=tk.DISABLED)
        self.ED50mm.config(state=tk.DISABLED)
    def F_cable22x58(self):
        self.EDcable.set(0)
        self.ED10mm.config(state=tk.ACTIVE)
        self.ED16mm.config(state=tk.ACTIVE)
        self.ED25mm.config(state=tk.ACTIVE)
        self.ED35mm.config(state=tk.ACTIVE)
        self.ED50mm.config(state=tk.ACTIVE)

    def F_EDcalcularPos(self,*args):
        ensayo=self.EDensayo.get()
        talla=self.EDtalla.get()
        cable=self.EDcable.get()
        Pos=ensayo+talla+cable
        self.EDPosSondaCDT.set("")
        if ((talla==300) & (cable>50)):
            Pos=Pos+50
        if ((ensayo>0)&(talla>0)&(cable>0)):
            self.EDPos.set(Pos)
        else:
            self.EDPos.set(" ")
        if ((ensayo==1)&(talla>0)&(cable>0)):
            self.EDPosSondaCDT.set("Conecte la sonda CDT a la base   "+str(Pos))
            if (self.maintesttype.get()==2):
                self.EAPosSondaCDT.set("Conecte la sonda CDT a la base  "+str(Pos))
        else:
            self.EDPosSondaCDT.set("")


    def F_EDstart(self):

        def Lectura_Corriente_NO():             ### FUNCION OBSOLETA / RESERVA ###
            coef=1.018
            SENS.write(("C").encode())
            lectura=SENS.readline().decode("utf-8")
            lectura=abs(float(lectura))
            return coef*lectura

        def Lectura_Corriente():
            coef=1.02
            try:
                lectura=(float(abs(DATA.read_adc_difference(0,gain=16)))/65535.0)*2.0*0.256*200.0/0.06
                self.last_corriente.set(coef*lectura)
                return coef*lectura
            except:
                print("Error en Lectura_Corriente()")
                return self.last_corriente.get()

        def Lectura_CDT_NO():                   ### FUNCION OBSOLETA / RESERVA ###
            SENS.write(("V").encode())
            lectura=SENS.readline().decode("utf-8")
            lectura=abs(float(lectura)/1000.0)
            return lectura

        def Lectura_CDT():
            try:
                lectura=(float(abs(DATA.read_adc_difference(3,gain=2/3)))/65535.0)*2.0*6.144
                time.sleep(0.1)
                if (lectura<8.192):
                    lectura=(float(abs(DATA.read_adc_difference(3,gain=1)))/65535.0)*2.0*4.096
                    time.sleep(0.1)
                    if (lectura<4.096):
                        lectura=(float(abs(DATA.read_adc_difference(3,gain=2)))/65535.0)*2.0*2.048
                        time.sleep(0.1)
                        if (lectura<2.048):
                            lectura=(float(abs(DATA.read_adc_difference(3,gain=4)))/65535.0)*2.0*1.024
                            time.sleep(0.1)
                            if (lectura<1.024):
                                lectura=(float(abs(DATA.read_adc_difference(3,gain=8)))/65535.0)*2.0*0.512
                                time.sleep(0.1)
                                if (lectura<0.512):
                                    lectura=(float(abs(DATA.read_adc_difference(3,gain=16)))/65535.0)*2.0*0.256
                return lectura
            except:
                print("Error en Lectura_CDT()")
                return 0.0

        def Corriente_Consigna(val):
            val=float(val)
            if val>220:
                val=220
            if val<0:
                val=0
            val=int(float(val)/220.0*2048.0)
            try:
                rpiplc.analog_write("A0.7", val)
                print("CORRIENTE CONSIGNA : val="+str(val))
            except:
                print("Error en Corriente_Consigna()")

        def Calibrar_Corriente(consigna):
            consigna=float(consigna)
            if consigna>220.0:
                consigna=220.0
            consignaI=consigna
            c1=Lectura_Corriente()
            time.sleep(0.05)
            c2=Lectura_Corriente()
            time.sleep(0.05)
            c3=Lectura_Corriente()
            corriente_real=(c1+c2+c3)/3
            time1=time.time()
            dif=abs(corriente_real-consignaI)
            while (dif>(0.1)):
                if ((time.time()-time1)>5.0):
                    self.EDTestM1.set("NO SE PUDO ESTABLECER CORRIENTE DE ENSAYO")
                    self.root.update()
                    self.fin_ensayo.set(True)
                    GPIO.output(RelayPd,1)
                    GPIO.output(RelayNoFus,1)
                    GPIO.output(RelayFus,1)
                    GPIO.output(BalizaVerde,1)
                    GPIO.output(BalizaAmarilla,1)
                    GPIO.output(BalizaRoja,0)
                    Corriente_Consigna(0)
                    break
                if corriente_real>consigna:
                    consignaI=consignaI-dif
                    Corriente_Consigna(consignaI)
                if corriente_real<consigna:
                    consignaI=consignaI+dif
                    Corriente_Consigna(consignaI)
                time.sleep(0.5)
                c1=Lectura_Corriente()
                time.sleep(0.05)
                c2=Lectura_Corriente()
                time.sleep(0.05)
                c3=Lectura_Corriente()
                corriente_real=(c1+c2+c3)/3
                dif=abs(corriente_real-consigna)
            self.Last_Current.set(consignaI)


                    ##########################
                    ##########################
                    ##########################


        def Ensayar(corriente,ensayo,tiempo):
            time_start=time.time()
            Corriente_Consigna(corriente)
            self.fin_ensayo.set(False)
            if ensayo==1:
                timeI=time.time()
                timeN=time.time()
                times=[]
                time_passed=0
                Resultado=""
                average=0.0
                GPIO.output(RelayPd,0)
                GPIO.output(RelayNoFus,1)
                GPIO.output(RelayFus,1)
                GPIO.output(BalizaVerde,1)
                GPIO.output(BalizaAmarilla,0)
                GPIO.output(BalizaRoja,1)
                time.sleep(0.5)
                Calibrar_Corriente(corriente)
                corrientes=[]
                ultima_consigna=self.Last_Current.get()
                if (self.fin_ensayo.get()==False):
                    while not(self.fin_ensayo.get()):
                        dif_time=int(timeN-timeI)
                        if GPIO.input(ParoEmerg)==False:
                            self.fin_ensayo.set(True)
                            self.EDTestM1.set("PARO DE ENSAYO: PARO DE EMERGENCIA ACTIVADO")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                            break
                        corrientes.append(Lectura_Corriente())
                        if corrientes[len(corrientes)-1]<1:
                            if GPIO.input(FinEnsayo)==True:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if len(corrientes)<10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                        if len(corrientes)>10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                            dif=media_corrientes-corriente
                            if dif>0.1:
                                ultima_consigna=ultima_consigna-0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            if dif<-0.1:
                                ultima_consigna=ultima_consigna+0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            corrientes=[]
                        self.Corriente_medida.set(str("%.2f"%media_corrientes)+"A")
                        if ((time_passed %10)==0):
                            try:
                                SENS.write(("M").encode())
                                time.sleep(0.2)
                                message=SENS.readline().decode("utf-8")
                                if message != "OK\r\n":
                                    self.fin_ensayo.set(True)
                                    self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                    GPIO.output(BalizaAmarilla,1)
                                    GPIO.output(BalizaVerde,1)
                                    GPIO.output(BalizaRoja,0)
                                    break
                            except:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN EL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break

                        if GPIO.input(FinEnsayo)==False:
                            valor_corriente=Lectura_Corriente()
                            if valor_corriente<0.5*corriente:           #se modifica fecha 30-07-2019. antes "<3"
                                self.fin_ensayo.set(True)
                                Resultado="Resultado: NO CONFORME (Fusible fundido)"
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)

                        if time_passed>tiempo:
                            self.fin_ensayo.set(True)
                            self.EDTestM1.set("FIN DE ENSAYO: TIEMPO SUPERIOR A TIEMPO CONVENCIONAL")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                        if dif_time>15:
                            valor_tension=Lectura_CDT()
                            print(valor_tension)
                            self.CDT_medida.set(str("%.2f"%(valor_tension*1000))+"mV")
                            val_Pd=valor_tension*corriente
                            times.append(val_Pd)
                            timeI=time.time()
                            i=len(times)
                            Resultado="Potencia Disipada: " + str("%.3f" % round(val_Pd,3)) + "W"
                            if i>(0.25*tiempo/15):
                                average=(times[i-1]+times[i-21]+times[i-41])/3
                                if ((times[i-1]<(1.005*average))&(times[i-1]>(0.995*average))):
                                    self.fin_ensayo.set(True)
                                    GPIO.output(BalizaAmarilla,1)
                                    GPIO.output(BalizaVerde,0)
                                    GPIO.output(BalizaRoja,1)

                        time.sleep(0.5)
                        timeN=time.time()
                        time_passed=int(timeN-time_start)
                        Resultado_tiempo=("Tiempo transcurrido: " + str(datetime.timedelta(seconds=time_passed))+"s")

                        self.EDTestM3.set(Resultado_tiempo+"\n"+Resultado)

                        self.root.update()
                        if (Resultado=="Resultado: NO CONFORME (Fusible fundido)"):
                                continue
                        else:
                                self.EDTestM3.set(Resultado_tiempo+ "\n"+"Potencia Disipada: "+str("%.3f" % round(average,3)) + "W")

            if ensayo==2:
                GPIO.output(RelayPd,1)
                GPIO.output(RelayNoFus,0)
                GPIO.output(RelayFus,1)
                GPIO.output(BalizaVerde,1)
                GPIO.output(BalizaAmarilla,0)
                GPIO.output(BalizaRoja,1)
                time.sleep(0.2)
                Calibrar_Corriente(corriente)
                valor_corriente=Lectura_Corriente()
                corrientes=[]
                ultima_consigna=self.Last_Current.get()
                time_passed=1
                if (self.fin_ensayo.get()==False):
                    while not(self.fin_ensayo.get()):
                        if GPIO.input(ParoEmerg)==False:
                            self.fin_ensayo.set(True)
                            self.EDTestM1.set("PARO DE ENSAYO: PARO DE EMERGENCIA ACTIVADO")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                            break
                        corrientes.append(Lectura_Corriente())
                        if corrientes[len(corrientes)-1]<1:
                            if GPIO.input(FinEnsayo)==True:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if len(corrientes)<10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                        if len(corrientes)>10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                            dif=media_corrientes-corriente
                            if dif>0.1:
                                ultima_consigna=ultima_consigna-0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            if dif<-0.1:
                                ultima_consigna=ultima_consigna+0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            corrientes=[]
                        self.Corriente_medida.set(str("%.2f"%media_corrientes)+"A")

                        if ((time_passed %10)==0):

                            try:
                                SENS.write(("M").encode())
                                time.sleep(0.2)
                                message=SENS.readline().decode("utf-8")
                                if message != "OK\r\n":
                                    self.fin_ensayo.set(True)
                                    self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                    GPIO.output(BalizaAmarilla,1)
                                    GPIO.output(BalizaVerde,1)
                                    GPIO.output(BalizaRoja,0)
                                    break
                            except:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN EL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        timeN=time.time()
                        time_passed=int(timeN-time_start)
                        if time_passed>tiempo:
                            self.fin_ensayo.set(True)
                            self.Resultado.set("Resultado: CONFORME")
                            print("CONFORME")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,0)
                            GPIO.output(BalizaRoja,1)
                        if GPIO.input(FinEnsayo)==False:
                            valor_corriente=Lectura_Corriente()
                            if valor_corriente<0.5*corriente:           #se modifica fecha 30-07-2019. antes "<3"
                                self.fin_ensayo.set(True)
                                self.Resultado.set("Resultado: NO CONFORME")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                print("NO CONFORME")
                        time.sleep(0.5)
                        self.EDTestM5.set("Tiempo transcurrido: " + str(datetime.timedelta(seconds=time_passed))+"s")
                        self.root.update()
                    self.EDTestM5.set(self.EDTestM5.get()+"\n"+self.Resultado.get())
                    self.root.update()

            if ensayo==3:
                GPIO.output(RelayPd,1)
                GPIO.output(RelayNoFus,1)
                GPIO.output(RelayFus,0)
                GPIO.output(BalizaVerde,1)
                GPIO.output(BalizaAmarilla,0)
                GPIO.output(BalizaRoja,1)
                time.sleep(0.2)
                Calibrar_Corriente(corriente)
                valor_corriente=Lectura_Corriente()
                corrientes=[]
                ultima_consigna=self.Last_Current.get()
                if (self.fin_ensayo.get()==False):
                    while not(self.fin_ensayo.get()):
                        timeN=time.time()
                        time_passed=int(timeN-time_start)
                        if GPIO.input(ParoEmerg)==False:
                            self.fin_ensayo.set(True)
                            self.EDTestM1.set("PARO DE ENSAYO: PARO DE EMERGENCIA ACTIVADO")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                            break
                        corrientes.append(Lectura_Corriente())
                        if corrientes[len(corrientes)-1]<1:
                            if GPIO.input(FinEnsayo)==True:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if len(corrientes)<10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                        if len(corrientes)>10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                            dif=media_corrientes-corriente
                            if dif>0.1:
                                ultima_consigna=ultima_consigna-0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            if dif<-0.1:
                                ultima_consigna=ultima_consigna+0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            corrientes=[]
                        self.Corriente_medida.set(str("%.2f"%media_corrientes)+"A")

                        if ((time_passed %10)==0):
                            try:
                                SENS.write(("M").encode())
                                time.sleep(0.2)
                                message=SENS.readline().decode("utf-8")
                                if message != "OK\r\n":
                                    self.fin_ensayo.set(True)
                                    self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                    GPIO.output(BalizaAmarilla,1)
                                    GPIO.output(BalizaVerde,1)
                                    GPIO.output(BalizaRoja,0)
                                    break
                            except:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN EL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if time_passed>tiempo:
                            self.fin_ensayo.set(True)
                            self.Resultado.set("Resultado: NO CONFORME")
                            print("NO CONFORME")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                        if GPIO.input(FinEnsayo)==False:
                            valor_corriente=Lectura_Corriente()         
                            if valor_corriente<0.5*corriente:           #se modifica fecha 30-07-2019. antes "<3"
                                self.fin_ensayo.set(True)
                                self.Resultado.set("Resultado: CONFORME")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,0)
                                GPIO.output(BalizaRoja,1)
                                print("CONFORME")
                        time.sleep(0.5)
                        self.EDTestM5.set("Tiempo transcurrido: " + str(datetime.timedelta(seconds=time_passed))+"s")
                        self.root.update()
                    self.EDTestM5.set(self.EDTestM5.get()+"\n"+self.Resultado.get())
                    self.root.update()

            Corriente_Consigna(0)
            self.Corriente_medida.set("0.0A")
            self.CDT_medida.set("0.0mV")
            GPIO.output(RelayPd,1)
            GPIO.output(RelayNoFus,1)
            GPIO.output(RelayFus,1)
            if self.EDTestM1.get()==("...ENSAYANDO..."):
                self.EDTestM1.set("ENSAYO FINALIZADO")
            self.EDStopButton.config(state=tk.DISABLED)
            self.mainbutton_ensayodirecto.config(state=tk.ACTIVE)
            self.mainbutton_ensayoautomatico.config(state=tk.ACTIVE)
            self.mainbutton_salir.config(state=tk.ACTIVE)
            self.mainbutton_limpiarDatos.config(state=tk.ACTIVE)
            self.EDEntryTestReport.config(state=tk.NORMAL)
            self.EDButtonTestReport.config(state=tk.ACTIVE)

        ############################################
        #### FIN DEFINICIONES FUNCIONES INTERNAS ###
        ############################################

        ensayo=self.EDensayo.get()
        talla=self.EDtalla.get()
        cable=self.EDcable.get()
        tiempo=self.EDtiempo.get()
        error=False
        try:
            Pos=self.EDPos.get()
        except:
            TOPerror=tk.Toplevel()
            TOPerror.geometry('250x100+200+200')
            TOPerror.title("Error")
            ErrorMessage=tk.Label(TOPerror,text="Seleccione las características de ensayo",justify=tk.LEFT)
            ErrorMessage.pack(padx=10,pady=15)
            OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
            OKbutton.pack(fill=tk.X,padx=10,pady=10)
            TOPerror.transient(self.root)
            TOPerror.grab_set()
            TOPerror.wait_window()
            error=True
        if not(error):
            try:
                corriente=float(self.EDCorriente.get())
            except:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('250x100+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Introduzca un valor numérico sin letras",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            if ((ensayo==1)&(corriente>125.0)):
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x130+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Para el ensayo de Potencia Disipada, el valor de \ncorriente está limitado a 125A.\nIntroduzca un valor de corriente inferior a 125",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
            if ((ensayo==2)&(corriente>160.0)):
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x130+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Para el ensayo de No Fusión, el valor de corriente \nestá limitado a 160A.\nIntroduzca un valor de corriente inferior a 160",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
            if ((ensayo==3)&(corriente>210.0)):
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x130+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Para el ensayo de Fusión, el valor de corriente \nestá limitado a 210A.\nIntroduzca un valor de corriente inferior a 210",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            if corriente<2:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x105+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Introduzca un valor de corriente mayor a 2A",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            if tiempo==0:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x105+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Seleccione un valor de tiempo convencional",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            if GPIO.input(ParoEmerg)==False:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x105+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Paro de Emergencia activado.\nDesenclávelo para ejecutar el ensayo",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            try:
                SENS.write(("M").encode())
                time.sleep(0.2)
                message=SENS.readline().decode("utf-8")
                if message != "OK\r\n":
                    TOPerror=tk.Toplevel()
                    TOPerror.geometry('300x105+200+200')
                    TOPerror.title("Error")
                    ErrorMessage=tk.Label(TOPerror,text="Fallo en las protecciones internas del equipo",justify=tk.LEFT)
                    ErrorMessage.pack(padx=10,pady=15)
                    OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                    OKbutton.pack(fill=tk.X,padx=10,pady=10)
                    TOPerror.transient(self.root)
                    TOPerror.grab_set()
                    TOPerror.wait_window()
                    error=True
            except:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x130+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Fallo de comunicación en el equipo. \nNo se pudo acceder al estado de las\nprotecciones internas del equipo",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True

        if not(error):
            if GPIO.input(FinEnsayo)==True:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('350x105+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="No se detecta funcionamiento de la fuente. \nRevise el equipo y sus protecciones y vuelva a intentarlo",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True

        if not(error):
            self.EDTestM1.set("...ENSAYANDO...")
            self.EDCorriente.set(str(corriente)+"A")
            self.EDcorrienteEntry.config(state=tk.DISABLED)

            self.EDStartButton.config(state=tk.DISABLED)
            self.EDStopButton.config(state=tk.ACTIVE)
            self.mainbutton_ensayodirecto.config(state=tk.DISABLED)
            self.mainbutton_ensayoautomatico.config(state=tk.DISABLED)
            self.mainbutton_limpiarDatos.config(state=tk.DISABLED)
            self.mainbutton_salir.config(state=tk.DISABLED)

            self.EDPotDis.config(state=tk.DISABLED)
            self.EDNoFusion.config(state=tk.DISABLED)
            self.EDFusion.config(state=tk.DISABLED)
            self.ED10x38.config(state=tk.DISABLED)
            self.ED14x51.config(state=tk.DISABLED)
            self.ED22x58.config(state=tk.DISABLED)
            self.ED1mm.config(state=tk.DISABLED)
            self.ED1_5mm.config(state=tk.DISABLED)
            self.ED2_5mm.config(state=tk.DISABLED)
            self.ED4mm.config(state=tk.DISABLED)
            self.ED6mm.config(state=tk.DISABLED)
            self.ED10mm.config(state=tk.DISABLED)
            self.ED16mm.config(state=tk.DISABLED)
            self.ED25mm.config(state=tk.DISABLED)
            self.ED35mm.config(state=tk.DISABLED)
            self.ED50mm.config(state=tk.DISABLED)
            self.ED1hora.config(state=tk.DISABLED)
            self.ED2horas.config(state=tk.DISABLED)
            self.ED1min.config(state=tk.DISABLED)
            self.EDEntryTestReport.config(state=tk.DISABLED)
            self.EDButtonTestReport.config(state=tk.DISABLED)

            if talla==100:
                EDTestMainMessageM2="Talla 10x38 - "
            if talla==200:
                EDTestMainMessageM2="Talla 14x51 - "
            if talla==300:
                EDTestMainMessageM2="Talla 22x58 - "
            if cable==10:
                EDTestMainMessageM2+= "Seccion de cable 1mm"
            if cable==20:
                EDTestMainMessageM2+= "Seccion de cable 1,5mm"
            if cable==30:
                EDTestMainMessageM2+= "Seccion de cable 2,5mm"
            if cable==40:
                EDTestMainMessageM2+= "Seccion de cable 4mm"
            if cable==50:
                EDTestMainMessageM2+= "Seccion de cable 6mm"
            if cable==60:
                EDTestMainMessageM2+= "Seccion de cable 10mm"
            if cable==70:
                EDTestMainMessageM2+= "Seccion de cable 16mm"
            if cable==80:
                EDTestMainMessageM2+= "Seccion de cable 25mm"
            if cable==90:
                EDTestMainMessageM2+= "Seccion de cable 35mm"
            if cable==100:
                EDTestMainMessageM2+= "Seccion de cable 50mm"
            if ensayo==1:
                EDTestMainMessageM2+="\nEnsayo: POTENCIA DISIPADA"
            if ensayo==2:
                EDTestMainMessageM2+="\nEnsayo: NO FUSION"
            if ensayo==3:
                EDTestMainMessageM2+="\nEnsayo: FUSION"
            EDTestMainMessageM2+=("\nCorriente de ensayo: "+str(corriente)+"A")
            EDTestMainMessageM2+=("\nTiempo convencional: "+str(tiempo)+"s")
            EDTestMainMessageM2+=("\nBase portafusibles: "+str(Pos))
            self.EDTestM2.set(EDTestMainMessageM2)
            self.EDTestM3.set("")
            self.EDTestM4.set("")
            self.EDTestM5.set("")
            self.root.update()
            time.sleep(0.2)

            Ensayar(corriente,ensayo,tiempo)



    def F_EDstopButton(self):
        def PararEnsayo():
            TOPerror.destroy()
            GPIO.output(RelayPd,1)
            GPIO.output(RelayNoFus,1)
            GPIO.output(RelayFus,1)
            GPIO.output(BalizaVerde,0)
            GPIO.output(BalizaAmarilla,1)
            GPIO.output(BalizaRoja,1)
            rpiplc.analog_write("A0.7", 0)
            self.EDStopButton.config(state=tk.DISABLED)
            self.mainbutton_ensayodirecto.config(state=tk.ACTIVE)
            self.mainbutton_ensayoautomatico.config(state=tk.ACTIVE)
            self.mainbutton_salir.config(state=tk.ACTIVE)
            self.mainbutton_limpiarDatos.config(state=tk.ACTIVE)
            if self.EDTestM1.get()==("...ENSAYANDO..."):
                self.EDTestM1.set("ENSAYO PARADO POR EL USUARIO")
            self.EDEntryTestReport.config(state=tk.NORMAL)
            self.EDButtonTestReport.config(state=tk.ACTIVE)
            self.fin_ensayo.set(True)
            if ((self.EDensayo.get()==2) or (self.EDensayo.get()==3)):
                self.Resultado.set("SIN RESULTADO")

        TOPerror=tk.Toplevel()
        TOPerror.geometry('250x150+200+200')
        TOPerror.title("Paro")
        ErrorMessage=tk.Label(TOPerror,text="Desea parar el ensayo?",justify=tk.LEFT)
        ErrorMessage.pack(fill=tk.X,padx=10,pady=15)
        CANCELARbutton=tk.Button(TOPerror, text="Cancelar", command=TOPerror.destroy)
        CANCELARbutton.pack(fill=tk.X,padx=10,pady=5)
        PARARbutton=tk.Button(TOPerror, text="Confirmar Paro", command=PararEnsayo)
        PARARbutton.pack(fill=tk.X,padx=10,pady=5)
        TOPerror.transient(self.root)
        TOPerror.grab_set()
        TOPerror.wait_window()






    def F_ReportGenerate(self,*args):

        self.root.filename=tk.filedialog.asksaveasfilename(initialdir=path_GuardarInformes,title="Save as",filetypes=(("text files","*.txt"),("all files","*.")))
        file=open(self.root.filename,'w')

        if self.maintesttype.get()==1:
            file.write("Ensayo Directo\r\n")
        if self.maintesttype.get()==2:
            file.write("Ensayo Automatico\r\n")
            file.write("REFERENCIA: "+str(self.EAReferencia.get())+"\r\n")
            if (self.EAOF.get() != ("")):
                file.write("ORDEN DE FABRICACION: " + self.EAOF.get() + "\r\n")
        file.write(((self.EDTestM1.get()).replace("\n","\r\n")+"\r\n"+((self.EDTestM2.get())).replace("\n","\r\n")).encode('utf-8'))
                #if (self.maintesttype==2):
                #    file.write(self.EAReferencia.get().encode('utf-8'))
        file.write("\r\n"+"Fecha y hora de ensayo: "+time.strftime('%d/%m/%y') +" - "+ time.strftime('%H:%M'))
        try:
            file.write("\r\n"+"Temperatura ambiental: "+str("%.1f"%(self.Temperatura.get()))+"\xb0"+"C\r\n")
                    #file.write("\n"+"Temperatura ambiental: "+str(self.Temperatura.get())+"C\r\n")
        except:
            file.write("\r\n"+"Temperatura ambiental: SIN DATOS\r\n")
        
        if (self.EAResM1.get() != ("")):
            file.write("\r\nResistencia Muestra 1: " + self.EAResM1.get() + "mOhm")
        if (self.EDTestM3.get() != ("")):
            file.write("\r\n"+((self.EDTestM3.get()).replace("\n","\r\n")).encode('utf-8')+"\r\n")
        if (self.EAResM2.get() != ("")):
            file.write("\r\nResistencia Muestra 2: " + self.EAResM2.get() + "mOhm")        
        if (self.EDTestM4.get()!=""):
            file.write("\r\n"+((self.EDTestM4.get()).replace("\n","\r\n")).encode('utf-8')+"\r\n")
        if (self.EAResM3.get() != ("")):
            file.write("\r\nResistencia Muestra 3: " + self.EAResM3.get() + "mOhm")        
        if (self.EDTestM5.get()!=""):
            file.write("\r\n"+((self.EDTestM5.get()).replace("\n","\r\n")).encode('utf-8')+"\r\n")
        file.write("\r\n" + "COMENTARIO: " + ((self.EDEntryTestReport.get("1.0",tk.END)).replace("\n","\r\n")).encode('utf-8'))
        file.close()

        rpiplc.analog_write("A0.7", 0)
        GPIO.output(BalizaVerde,0)
        GPIO.output(BalizaAmarilla,1)
        GPIO.output(BalizaRoja,1)



    def F_EACargarDatos(self):
        self.EADatosEnsayo.set("")
        if (self.EApath_referencia.get()!=""):
            path=self.EApath_referencia.get()
            existe=True
        else:
            path=path_CargarReferencias+str(self.EAReferencia.get())+".txt"
            existe=os.path.exists(path)
        if existe==False:
            TOPerror=tk.Toplevel()
            TOPerror.geometry('280x130+200+200')
            TOPerror.title("Error")
            InformeMessage=tk.Label(TOPerror,text="Error al cargar la referencia.\nIntroduzca una referencia válida",justify=tk.LEFT)
            InformeMessage.pack(fill=tk.X,padx=10,pady=15)
            VolverButton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
            VolverButton.pack(fill=tk.X,padx=10,pady=10)
            TOPerror.transient(self.root)
            TOPerror.grab_set()
            TOPerror.wait_window()
            error=True
        if existe==True:

            file=open(path,'r')
            referencia_archivo=file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","")
            talla=file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("X","x").replace("\r","")
            tipo=file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","")
            I_Pd=float(file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","").replace("A","").replace("-","").replace(",","."))
            tension=file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","")
            ind_perc=file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","")
            cable=file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","").replace(".",",")
            tiempo=int(file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","").replace("h",""))
            I_NoFus=float(file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","").replace("A","").replace("-","").replace(",","."))
            I_Fus=float(file.readline().split(":",1)[1].replace(" ","").replace("\n","").replace("\r","").replace("A","").replace("-","").replace(",","."))
            file.close()
            error=False
        if error==False:
            Datos_Ensayo="REFERENCIA:  "+referencia_archivo+"\n"
            Datos_Ensayo+="FUSIBLE:    "+talla+"   "+tipo+"   "+str(I_Pd)+"A   "+tension+"   "+ind_perc+"\n"
            Datos_Ensayo+=" --- DATOS  DE  ENSAYO ---"+"\n"
            Datos_Ensayo+="Tiempo convencional:  "+str(tiempo)+"h"+"\n"
            Datos_Ensayo+="Seccion de cable:  "+cable+"\n"
            Datos_Ensayo+="Intensidades de ensayo:"+"\n"
            Datos_Ensayo+="I(Pd)=" +str(I_Pd)+"   /   I(nofus)=" +str(I_NoFus)+"A  /  I(fus)= "+str(I_Fus)+"A"
            self.EADatosEnsayo.set(Datos_Ensayo)
            if talla=="10x38":
                self.EDtalla.set(100)
            if talla=="14x51":
                self.EDtalla.set(200)
            if talla=="22x58":
                self.EDtalla.set(300)
            if cable=="1mm":
                self.EDcable.set(10)
            if cable=="1,5mm":
                self.EDcable.set(20)
            if cable=="2,5mm":
                self.EDcable.set(30)
            if cable=="4mm":
                self.EDcable.set(40)
            if cable=="6mm":
                self.EDcable.set(50)
            if cable=="10mm":
                self.EDcable.set(60)
            if cable=="16mm":
                self.EDcable.set(70)
            if cable=="25mm":
                self.EDcable.set(80)
            if cable=="35mm":
                self.EDcable.set(90)
            if cable=="50mm":
                self.EDcable.set(100)
            self.EDtiempo.set(tiempo*3600)
            self.EACorriente1.set(I_Pd)
            self.EACorriente2.set(I_NoFus)
            self.EACorriente3.set(I_Fus)
            self.EAtipo.set(tipo) 
            self.EAtalla.set(talla)
            try:
                self.EDensayo.set(1)
                self.F_EDcalcularPos()
                pos1=str(self.EDPos.get())
                self.EDensayo.set(2)
                if (tipo=="aM"):
                    cable=self.EDcable.get()
                    self.EDcable.set(self.EDcable.get()+10)
                    if (I_Pd>16):
                        self.EDcable.set(self.EDcable.get()+10)
                self.F_EDcalcularPos()
                pos2=str(self.EDPos.get())
                self.EDensayo.set(3)
                self.F_EDcalcularPos()
                pos3=str(self.EDPos.get())
                self.EDPos.set(pos1+pos2+pos3)
                self.EAPos.set(pos1+"   "+pos2+"   "+pos3)
                if (tipo=="aM"):
                    self.EDcable.set(cable)
            except:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('280x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="Error al cargar el archivo. \nNo se pueden leer los datos",justify=tk.LEFT)
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                VolverButton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                VolverButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if error==False:
            self.EAStartButton.config(state=tk.ACTIVE)


    def F_EABuscar(self):
        self.root.filename=tk.filedialog.askopenfilename(initialdir=path_CargarReferencias,title="Select file",filetypes=(("text files","*.txt"),("all files","*.")))
        path=self.root.filename
        self.EAReferencia.set(path.split("/")[-1].replace(".txt",""))
        self.EApath_referencia.set(self.root.filename)




    def F_EAstart(self):

        def Lectura_Corriente_NO():             ### FUNCION OBSOLETA / RESERVA ###
            coef=1.018
            SENS.write(("C").encode())
            lectura=SENS.readline().decode("utf-8")
            lectura=abs(float(lectura))
            return coef*lectura

        def Lectura_Corriente():
            coef=1.02
            try:
                lectura=(float(abs(DATA.read_adc_difference(0,gain=16)))/65535.0)*2.0*0.256*200.0/0.06
                self.last_corriente.set(coef*lectura)
                return coef*lectura
            except:
                print("Error en Lectura_Corriente()")
                return self.last_corriente.get()

        def Lectura_CDT_NO():                   ### FUNCION OBSOLETA / RESERVA ###
            SENS.write(("V").encode())
            lectura=SENS.readline().decode("utf-8")
            lectura=abs(float(lectura)/1000.0)
            return lectura

        def Lectura_CDT():
            try:
                lectura=(float(abs(DATA.read_adc_difference(3,gain=2/3)))/65535.0)*2.0*6.144
                time.sleep(0.1)
                if (lectura<8.192):
                    lectura=(float(abs(DATA.read_adc_difference(3,gain=1)))/65535.0)*2.0*4.096
                    time.sleep(0.1)
                    if (lectura<4.096):
                        lectura=(float(abs(DATA.read_adc_difference(3,gain=2)))/65535.0)*2.0*2.048
                        time.sleep(0.1)
                        if (lectura<2.048):
                            lectura=(float(abs(DATA.read_adc_difference(3,gain=4)))/65535.0)*2.0*1.024
                            time.sleep(0.1)
                            if (lectura<1.024):
                                lectura=(float(abs(DATA.read_adc_difference(3,gain=8)))/65535.0)*2.0*0.512
                                time.sleep(0.1)
                                if (lectura<0.512):
                                    lectura=(float(abs(DATA.read_adc_difference(3,gain=16)))/65535.0)*2.0*0.256
                return lectura
            except:
                print("Error en Lectura_CDT()")
                return 0.0

        def Corriente_Consigna(val):
            val=float(val)
            if val>220:
                val=220
            if val<0:
                val=0
            val=int(float(val)/220.0*2048.0)
            try:
                rpiplc.analog_write("A0.7", val)
                print("CORRIENTE CONSIGNA : val="+str(val))
            except:
                print("Error en Corriente_Consigna()")

        def Calibrar_Corriente(consigna):
            consigna=float(consigna)
            if consigna>220.0:
                consigna=220.0
            consignaI=consigna
            c1=Lectura_Corriente()
            time.sleep(0.05)
            c2=Lectura_Corriente()
            time.sleep(0.05)
            c3=Lectura_Corriente()
            corriente_real=(c1+c2+c3)/3
            time1=time.time()
            dif=abs(corriente_real-consignaI)
            while (dif>(0.1)):
                if ((time.time()-time1)>5.0):
                    self.EDTestM1.set("NO SE PUDO ESTABLECER CORRIENTE DE ENSAYO")
                    self.root.update()
                    self.fin_ensayo.set(True)
                    GPIO.output(RelayPd,1)
                    GPIO.output(RelayNoFus,1)
                    GPIO.output(RelayFus,1)
                    GPIO.output(BalizaVerde,1)
                    GPIO.output(BalizaAmarilla,1)
                    GPIO.output(BalizaRoja,0)
                    Corriente_Consigna(0)
                    break
                if corriente_real>consigna:
                    consignaI=consignaI-dif
                    Corriente_Consigna(consignaI)
                if corriente_real<consigna:
                    consignaI=consignaI+dif
                    Corriente_Consigna(consignaI)
                time.sleep(0.5)
                c1=Lectura_Corriente()
                time.sleep(0.05)
                c2=Lectura_Corriente()
                time.sleep(0.05)
                c3=Lectura_Corriente()
                corriente_real=(c1+c2+c3)/3
                dif=abs(corriente_real-consigna)
            self.Last_Current.set(consignaI)




                    ############################
                    ############################

        def Ensayar(Ipd,Inf,If,tiempo,tipo):
            self.fin_ensayo.set(False)
            fin_ensayo_interno=False

            #### Ensayo POTENCIA DISIPADA ####
            if (self.fin_ensayo.get()==False):
                time_start=time.time()
                Corriente_Consigna(Ipd)
                timeI=time.time()
                timeN=time.time()
                times=[]
                time_passed=0
                Resultado=""
                average=0.0
                GPIO.output(RelayPd,0)
                GPIO.output(RelayNoFus,1)
                GPIO.output(RelayFus,1)
                GPIO.output(BalizaVerde,1)
                GPIO.output(BalizaAmarilla,0)
                GPIO.output(BalizaRoja,1)
                time.sleep(0.2)
                Calibrar_Corriente(Ipd)
                corrientes=[]
                ultima_consigna=self.Last_Current.get()
                if (self.fin_ensayo.get()==False):
                    while ((not(self.fin_ensayo.get())) and (not(fin_ensayo_interno))):
                        dif_time=int(timeN-timeI)
                        if GPIO.input(ParoEmerg)==False:
                            self.fin_ensayo.set(True)
                            self.EDTestM1.set("PARO DE ENSAYO: PARO DE EMERGENCIA ACTIVADO")
                            self.Resultado.set("Sin resultado")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                            break
                        corrientes.append(Lectura_Corriente())
                        if corrientes[len(corrientes)-1]<1:
                            if GPIO.input(FinEnsayo)==True:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                self.Resultado.set("Sin resultado")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if len(corrientes)<10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                        if len(corrientes)>10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                            dif=media_corrientes-Ipd
                            if dif>0.1:
                                ultima_consigna=ultima_consigna-0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            if dif<-0.1:
                                ultima_consigna=ultima_consigna+0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            corrientes=[]
                        self.Corriente_medida.set(str("%.2f"%media_corrientes)+"A")

                        if ((time_passed %10)==0):

                            try:
                                SENS.write(("M").encode())
                                time.sleep(0.2)
                                message=SENS.readline().decode("utf-8")
                                if message != "OK\r\n":
                                    self.fin_ensayo.set(True)
                                    self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                    self.Resultado.set("Sin resultado")
                                    GPIO.output(BalizaAmarilla,1)
                                    GPIO.output(BalizaVerde,1)
                                    GPIO.output(BalizaRoja,0)
                                    break
                            except:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN EL EQUIPO")
                                self.Resultado.set("Sin resultado")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break

                        if GPIO.input(FinEnsayo)==False:
                            valor_corriente=Lectura_Corriente()
                            if valor_corriente<0.5*Ipd:         #se modifica fecha 30-07-2019. antes "<3"                       
                                self.fin_ensayo.set(True)
                                Resultado=" NO CONFORME (Fusible fundido)"
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaRoja,0)
                        if time_passed>tiempo:
                            fin_ensayo_interno=True
                            Resultado=Resultado+" SUPERIOR A TIEMPO CONVENCIONAL"
                        if dif_time>15:
                            valor_tension=Lectura_CDT()
                            self.CDT_medida.set(str("%.2f"%(valor_tension*1000))+"mV")
                            val_Pd=valor_tension*float(Ipd)
                            times.append(val_Pd)
                            timeI=time.time()
                            i=len(times)
                            Resultado="Potencia Disipada: " + str("%.3f" % round(val_Pd,3)) + "W"
                            if i>(0.25*tiempo/15):
                                average=(times[i-1]+times[i-21]+times[i-41])/3
                                if ((times[i-1]<(1.002*average))&(times[i-1]>(0.998*average))):
                                    fin_ensayo_interno=True
                        time.sleep(0.5)
                        timeN=time.time()
                        time_passed=int(timeN-time_start)
                        Resultado_tiempo=("Tiempo transcurrido: " + str(datetime.timedelta(seconds=time_passed))+"s")
                        self.EDTestM3.set("Ensayo POTENCIA DISIPADA \n" +Resultado_tiempo+"\n"+Resultado)
                        self.root.update()
                    Corriente_Consigna(0)
                    GPIO.output(RelayPd,1)
                    GPIO.output(RelayNoFus,1)
                    GPIO.output(RelayFus,1)
                    self.Corriente_medida.set("0.0A")
                    self.CDT_medida.set("0.0mV")
                    time.sleep(1)


            if (tipo=="aM" or tipo=="AM" or tipo=="am"):
                tiempo=60
            #### Ensayo NO FUSION ####
            if (self.fin_ensayo.get()==False):
                time_start=time.time()
                fin_ensayo_interno=False
                Corriente_Consigna(Inf)
                GPIO.output(RelayPd,1)
                GPIO.output(RelayNoFus,0)
                GPIO.output(RelayFus,1)
                time.sleep(0.2)
                Calibrar_Corriente(Inf)
                corrientes=[]
                ultima_consigna=self.Last_Current.get()
                self.Resultado.set("")
                if (self.fin_ensayo.get()==False):
                    while (not(self.fin_ensayo.get()) and not(fin_ensayo_interno)):
                        timeN=time.time()
                        time_passed=int(timeN-time_start)
                        if GPIO.input(ParoEmerg)==False:
                            self.fin_ensayo.set(True)
                            self.EDTestM1.set("PARO DE ENSAYO: PARO DE EMERGENCIA ACTIVADO")
                            self.Resultado.set("Sin resultado")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                            break
                        corrientes.append(Lectura_Corriente())
                        if corrientes[len(corrientes)-1]<1:
                            if GPIO.input(FinEnsayo)==True:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                self.Resultado.set("Sin resultado")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if len(corrientes)<10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                        if len(corrientes)>10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                            dif=media_corrientes-Inf
                            if dif>0.1:
                                ultima_consigna=ultima_consigna-0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            if dif<-0.1:
                                ultima_consigna=ultima_consigna+0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            corrientes=[]
                        self.Corriente_medida.set(str("%.2f"%media_corrientes)+"A")

                        if ((time_passed %10)==0):
                            try:
                                SENS.write(("M").encode())
                                time.sleep(0.2)
                                message=SENS.readline().decode("utf-8")
                                if message != "OK\r\n":
                                    self.fin_ensayo.set(True)
                                    self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                    self.Resultado.set("Sin resultado")
                                    GPIO.output(BalizaAmarilla,1)
                                    GPIO.output(BalizaVerde,1)
                                    GPIO.output(BalizaRoja,0)
                                    break
                            except:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN EL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if time_passed>tiempo:
                            fin_ensayo_interno=True
                            self.Resultado.set(" : CONFORME")
                        if GPIO.input(FinEnsayo)==False:
                            valor_corriente=Lectura_Corriente()
                            if valor_corriente<0.5*Inf:         #se modifica fecha 30-07-2019. antes "<3"
                                self.fin_ensayo.set(True)
                                self.Resultado.set(":  NO CONFORME")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                        time.sleep(0.5)
                        self.EDTestM4.set("Ensayo NO FUSION \nTiempo transcurrido: " + str(datetime.timedelta(seconds=time_passed))+"s")
                        self.root.update()
                    self.EDTestM4.set(self.EDTestM4.get()+self.Resultado.get())
                    self.root.update()
                Corriente_Consigna(0)
                GPIO.output(RelayPd,1)
                GPIO.output(RelayNoFus,1)
                GPIO.output(RelayFus,1)
                self.Corriente_medida.set("0.0A")
                time.sleep(1)

            #### Ensayo FUSION ####
            if (self.fin_ensayo.get()==False):
                time_start=time.time()
                fin_ensayo_interno=False
                Corriente_Consigna(If)
                GPIO.output(RelayPd,1)
                GPIO.output(RelayNoFus,1)
                GPIO.output(RelayFus,0)
                time.sleep(0.2)
                Calibrar_Corriente(If)
                corrientes=[]
                ultima_consigna=self.Last_Current.get()
                if (self.fin_ensayo.get()==False):
                    while (not(self.fin_ensayo.get()) and not(fin_ensayo_interno)):
                        timeN=time.time()
                        time_passed=int(timeN-time_start)
                        if GPIO.input(ParoEmerg)==False:
                            self.fin_ensayo.set(True)
                            self.EDTestM1.set("PARO DE ENSAYO: PARO DE EMERGENCIA ACTIVADO")
                            self.Resultado.set("Sin resultado")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                            break
                        corrientes.append(Lectura_Corriente())
                        if corrientes[len(corrientes)-1]<1:
                            if GPIO.input(FinEnsayo)==True:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                self.Resultado.set("Sin resultado")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if len(corrientes)<10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                        if len(corrientes)>10:
                            sum=0.0
                            for i in range(0,len(corrientes)):
                                sum=sum+corrientes[i]
                            media_corrientes=sum/len(corrientes)
                            dif=media_corrientes-If
                            if dif>0.1:
                                ultima_consigna=ultima_consigna-0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            if dif<-0.1:
                                ultima_consigna=ultima_consigna+0.1
                                Corriente_Consigna(ultima_consigna)
                                print("Corrigiendo Corriente_Consigna()")
                            corrientes=[]
                        self.Corriente_medida.set(str("%.2f"%media_corrientes)+"A")

                        if ((time_passed %10)==0):
                            try:
                                SENS.write(("M").encode())
                                time.sleep(0.2)
                                message=SENS.readline().decode("utf-8")
                                if message != "OK\r\n":
                                    self.fin_ensayo.set(True)
                                    self.EDTestM1.set("PARO DE ENSAYO: FALLO EN PROTECCIONES DEL EQUIPO")
                                    self.Resultado.set("Sin resultado")
                                    GPIO.output(BalizaAmarilla,1)
                                    GPIO.output(BalizaVerde,1)
                                    GPIO.output(BalizaRoja,0)
                                    break
                            except:
                                self.fin_ensayo.set(True)
                                self.EDTestM1.set("PARO DE ENSAYO: FALLO EN EL EQUIPO")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,1)
                                GPIO.output(BalizaRoja,0)
                                break
                        if time_passed>tiempo:
                            self.fin_ensayo.set(True)
                            self.Resultado.set(" : NO CONFORME")
                            print("NO CONFORME")
                            GPIO.output(BalizaAmarilla,1)
                            GPIO.output(BalizaVerde,1)
                            GPIO.output(BalizaRoja,0)
                        if GPIO.input(FinEnsayo)==False:
                            valor_corriente=Lectura_Corriente()
                            if valor_corriente<0.5*If:          #se modifica fecha 30-07-2019. antes "<3"
                                self.fin_ensayo.set(True)
                                self.Resultado.set(" : CONFORME")
                                GPIO.output(BalizaAmarilla,1)
                                GPIO.output(BalizaVerde,0)
                                GPIO.output(BalizaRoja,1)
                                print("CONFORME")
                        time.sleep(0.5)
                        self.EDTestM5.set("Ensayo FUSION  \nTiempo transcurrido: " + str(datetime.timedelta(seconds=time_passed))+"s")
                        self.root.update()
                    self.EDTestM5.set(self.EDTestM5.get()+self.Resultado.get())
                    self.root.update()

            Corriente_Consigna(0)
            GPIO.output(RelayPd,1)
            GPIO.output(RelayNoFus,1)
            GPIO.output(RelayFus,1)
            self.Corriente_medida.set("0.0A")
            if self.EDTestM1.get()==("...ENSAYANDO..."):
                self.EDTestM1.set("ENSAYO FINALIZADO")
            self.EDStopButton.config(state=tk.DISABLED)
            self.mainbutton_ensayodirecto.config(state=tk.ACTIVE)
            self.mainbutton_ensayoautomatico.config(state=tk.ACTIVE)
            self.mainbutton_salir.config(state=tk.ACTIVE)
            self.mainbutton_limpiarDatos.config(state=tk.ACTIVE)
            self.EDEntryTestReport.config(state=tk.NORMAL)
            self.EDButtonTestReport.config(state=tk.ACTIVE)

        #############################################
        #### FIN DEFINICIONES FUNCIONES INTERNAS ####
        #############################################

        tiempo=self.EDtiempo.get()
        Ipd=self.EACorriente1.get()
        Inf=self.EACorriente2.get()
        If=self.EACorriente3.get()
        Pos=self.EDPos.get()
        tipo=self.EAtipo.get()
        talla=self.EAtalla.get()
        error=False
        if ((tipo=="aM") or (tipo=="AM") or (tipo=="am")):
            if ((talla=="10x38") and (Ipd>20)):
                TOPerror=tk.Toplevel()
                TOPerror.geometry('330x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="Para los fusibles 10x38 aM la corriente \nasignada no puede ser mayor que 20A.\nModifique el valor en el archivo de datos de ensayo",justify=tk.LEFT)
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                OKButton=tk.Button(TOPerror, text="OK", command=TOPerror.destroy)
                OKButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
            if ((talla=="14x51") and (Ipd>25)):
                TOPerror=tk.Toplevel()
                TOPerror.geometry('330x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="Para los fusibles 14x51 aM la corriente \nasignada no puede ser mayor que 25A.\nModifique el valor en el archivo de datos de ensayo",justify=tk.LEFT)
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                OKButton=tk.Button(TOPerror, text="OK", command=TOPerror.destroy)
                OKButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
            if ((talla=="22x58") and (Ipd>32)):
                TOPerror=tk.Toplevel()
                TOPerror.geometry('330x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="Para los fusibles 22x58 aM la corriente \nasignada no puede ser mayor que 32A.\nModifique el valor en el archivo de datos de ensayo",justify=tk.LEFT)
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                OKButton=tk.Button(TOPerror, text="OK", command=TOPerror.destroy)
                OKButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True

        if not(error):
            if Ipd>125:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('330x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="La corriente del ensayo de Potencia Disipada \nno puede ser mayor que 125A.\nModifique el valor en el archivo de datos de ensayo",justify=tk.LEFT)
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                OKButton=tk.Button(TOPerror, text="OK", command=TOPerror.destroy)
                OKButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
            if Inf>160:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('330x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="La corriente del ensayo de No Fusión \nno puede ser mayor que 160A.\nModifique el valor en el archivo de datos de ensayo")
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                OKButton=tk.Button(TOPerror, text="OK", command=TOPerror.destroy)
                OKButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True

        if not(error):
            if If>210:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('330x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="La corriente del ensayo de Fusión \nno puede ser mayor que 210A.\nModifique el valor en el archivo de datos de ensayo")
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                OKButton=tk.Button(TOPerror, text="OK", command=TOPerror.destroy)
                OKButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            if Ipd<2 or Inf<2 or If<2:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('330x130+200+200')
                TOPerror.title("Error")
                InformeMessage=tk.Label(TOPerror,text="Toda corriente de ensayo debe ser mayor de 2A.\nModifique el valor en el archivo de datos de ensayo")
                InformeMessage.pack(fill=tk.X,padx=10,pady=15)
                OKButton=tk.Button(TOPerror, text="OK", command=TOPerror.destroy)
                OKButton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            if GPIO.input(ParoEmerg)==False:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x105+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Paro de Emergencia activado.\nDesenclávelo para ejecutar el ensayo",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True
        if not(error):
            try:
                SENS.write(("M").encode())
                time.sleep(0.2)
                message=SENS.readline().decode("utf-8")
                if message != "OK\r\n":
                    TOPerror=tk.Toplevel()
                    TOPerror.geometry('300x105+200+200')
                    TOPerror.title("Error")
                    ErrorMessage=tk.Label(TOPerror,text="Fallo en las protecciones internas del equipo",justify=tk.LEFT)
                    ErrorMessage.pack(padx=10,pady=15)
                    OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                    OKbutton.pack(fill=tk.X,padx=10,pady=10)
                    TOPerror.transient(self.root)
                    TOPerror.grab_set()
                    TOPerror.wait_window()
                    error=True
            except:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('300x130+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="Fallo de comunicación en el equipo. \nNo se pudo acceder al estado de las\nprotecciones internas del equipo",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True

        if not(error):
            if GPIO.input(FinEnsayo)==True:
                TOPerror=tk.Toplevel()
                TOPerror.geometry('350x105+200+200')
                TOPerror.title("Error")
                ErrorMessage=tk.Label(TOPerror,text="No se detecta funcionamiento de la fuente. \nRevise el equipo y sus protecciones y vuelva a intentarlo",justify=tk.LEFT)
                ErrorMessage.pack(padx=10,pady=15)
                OKbutton=tk.Button(TOPerror, text="Volver", command=TOPerror.destroy)
                OKbutton.pack(fill=tk.X,padx=10,pady=10)
                TOPerror.transient(self.root)
                TOPerror.grab_set()
                TOPerror.wait_window()
                error=True


        if not(error):
            self.EDTestM1.set("...ENSAYANDO...")
            self.EAStartButton.config(state=tk.DISABLED)
            self.EDStopButton.config(state=tk.ACTIVE)
            self.mainbutton_ensayodirecto.config(state=tk.DISABLED)
            self.mainbutton_ensayoautomatico.config(state=tk.DISABLED)
            self.mainbutton_limpiarDatos.config(state=tk.DISABLED)
            self.mainbutton_salir.config(state=tk.DISABLED)
            self.EAEntryReferencia.config(state=tk.DISABLED)
            self.EAButtonCargar.config(state=tk.DISABLED)
            self.EAButtonBuscar.config(state=tk.DISABLED)
            self.EDEntryTestReport.config(state=tk.DISABLED)
            self.EDButtonTestReport.config(state=tk.DISABLED)

            self.root.update()
            time.sleep(0.5)

            Ensayar(Ipd,Inf,If,tiempo,tipo)













    def F_mainSalir(self):
        GPIO.cleanup()
        try:
            SENS.close()
        except:
            print("Unable to Quit serial communication")
        self.root.destroy()






def main():
    mi_app=Aplicacion()
    return 0

if __name__=='__main__' :
    main()
