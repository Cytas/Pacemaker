import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QWidget, QComboBox, QLineEdit
from PyQt5.uic import loadUi
import json
import struct
import serial
import serial.tools.list_ports
from pyqtgraph import PlotWidget, mkPen
"""
Loads json file containing all the users, passwords and parameters
"""
def load_file(): #loads the json
    try:
        with open("profiles.json", "r") as user_file:
            return json.load(user_file)
    except FileNotFoundError:
        return {}
    
class login(QDialog):
    def __init__(self,file):     #when opening, load the buttons and blur password
        super(login,self).__init__()
        loadUi("pmlogin.ui",self)
        self.file = file

        self.user_password.setEchoMode(QtWidgets.QLineEdit.Password) #blurs the passwords
        #initializing buttons and combobox
        self.update_users.clicked.connect(self.update_combobox)
        self.loginbutton.clicked.connect(self.loginfun)
        self.toreg_button.clicked.connect(self.gotoregister)

        self.userlist = [user["username"] for user in file["users"]]
        self.user_input.addItems(self.userlist) #add users to combobox

    '''
    Since combobox isn't updated after going back to register, this updates it
    '''
    def update_combobox(self):
        self.user_input.clear()
        self.user_password.clear()
        new_list = [user["username"] for user in file["users"]]
        self.user_input.addItems(new_list)
        self.log_err_label.setText("List updated")
        print('list updated')


    '''
    if 10 or more users, takes it to the screen to delete a user, otherwise, goes to register screen
    '''
    def gotoregister(self): #when register button clicked, add frame, go to register class
        #print("number of users:",len(file["users"]))
        self.user_password.clear()  #clears the current password typed in
        if len(file["users"])>=10: #if more than 10 users, takes them to the delete user window instead
            delete = deleteuser(file)
            widget.addWidget(delete)
            self.log_err_label.setText("")
            widget.setCurrentIndex(widget.currentIndex()+2) #adding 2 to go to the proper widget index
        else:
            self.log_err_label.setText("")
            widget.setCurrentIndex(widget.currentIndex()+1)
    
    '''
    logs in
    '''
    def loginfun(self):
        print('attempting to login')
        input_user = self.user_input.currentText() #get the current user selection
        input_password = self.user_password.text() #get the password typed in

        if input_password:
            for u in file["users"]:
                #print('checking user:',u)
                #iterating through every user in the file, checking if the username and passwords both match
                if u["username"]==input_user and u["password"]== input_password:
                    #print('found user',u)
                    #updates the temp json file with the current user's parameter numbers
                    with open('temp.json', 'w') as temp_file:
                        json.dump(u, temp_file, indent=2)
                    print("Logged in with", input_user, input_password)
                    self.log_err_label.setText("") #reset the error message textbox
                    main = system(self.file)  #call the system class  
                    widget.addWidget(main) #create new widget, since everything needs to be updated
                    self.user_password.clear() #clear the inputted password
                    widget.setCurrentIndex(widget.currentIndex()+2)
                    break
                elif u["username"]==input_user and u["password"]!= input_password:
                    self.log_err_label.setText("Wrong password")
        else:
            self.log_err_label.setText("hmmm, weird you shouldn't be seeing this")


'''
Gives user option to choose which profile to delete
'''

class deleteuser(QDialog):
    def __init__(self, file):
        super(deleteuser,self).__init__()
        loadUi("delete_user.ui",self)
        self.file = file

        self.deleteuserbutton.clicked.connect(self.deleteuser)

        self.userlist = [user["username"] for user in file["users"]]
        self.user_select.addItems(self.userlist)  #add usernames to the combobox

    def deleteuser(self):
        deluser = self.user_select.currentText()
        delindex = None

        #find the index of the user to delete
        for i, user in enumerate(file['users']):
            if user['username'] == deluser:
                delindex = i
                print('delete index', i)
                break

        #once the user is found, delete the user at that index
        del file['users'][delindex]

        #update the json with the deleted user
        with open("profiles.json", 'w') as user_file:
            json.dump(file, user_file,indent=2)

        #after, move to register user
        current_page_index = widget.currentIndex()
        current_page_widget = widget.widget(current_page_index)
        widget.setCurrentIndex(widget.currentIndex()-1)
        current_page_widget.deleteLater()

'''
Allows user to register
'''
class register(QDialog):
    def __init__(self, file):
        super(register,self).__init__()
        loadUi("pmregister.ui",self)
        self.file = file
        
        self.register_button.clicked.connect(self.registerfun)
        self.backtologin.clicked.connect(self.gotologin)

        self.reg_err_label.setText("")
        self.pass_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        self.newuser_password.setEchoMode(QtWidgets.QLineEdit.Password)
    
    def gotologin(self): #first clears anything that the current user has typed in, then go back to login screen
        self.input_newuser.clear()
        self.pass_confirm.clear()
        self.newuser_password.clear()
        self.reg_err_label.setText("")
        widget.setCurrentIndex(widget.currentIndex()-1)

    def registerfun(self):
        #get values inputted
        newuser = self.input_newuser.text()
        password = self.newuser_password.text()
        confirm_password = self.pass_confirm.text()

        #see if all boxes are filled
        if not newuser or not password or not confirm_password:
            print('not all boxes are filled')
            self.reg_err_label.setText("Please fill in all boxes")
            return
        else:
        #check if username is taken:
            user_taken = any(user['username'] == newuser for user in file['users'])

            #register the new user with default values
            if not user_taken:
                if newuser and password==confirm_password:
                    new_user = {
                        "username": newuser,
                        "password": password,
                        "values": {
                            "mode": 1,
                            "LRL": 60,
                            "URL": 120,
                            "atr_amp": 5.0,
                            "Atr_Pul_Wid": 1,
                            "Atr_sens": 0.75,
                            "ARP": 250,
                            "Ven_amp": 5.0,
                            "Ven_Pul_Wid": 1,
                            "Ven_Sen": 2.5,
                            "VRP": 250,
                            "MSR": 120,
                            "Act_Thresh": 4,
                            "Rxn_Time": 30,
                            "RF": 8,
                            "Rec_Time": 5
                        }
                    }
                    file["users"].append(new_user)
                    print('new user registered with', newuser,password)

                    #update profile
                    with open('profiles.json','w') as user_file:
                        json.dump(file,user_file,indent=2)
                    #clears user inputs
                    self.input_newuser.clear()
                    self.pass_confirm.clear()
                    self.newuser_password.clear()
                    self.reg_err_label.setText("")
                    widget.setCurrentIndex(widget.currentIndex()-1)
                
                else:
                    self.reg_err_label.setText("Passwords do not match")
            else:
                print('user taken')
                self.reg_err_label.setText("User taken, please choose another username")

'''
Main control system
'''
class system(QDialog):
    def __init__(self, file):
        super(system,self).__init__()
        loadUi("system.ui",self)
        self.file = file
        with open('temp.json', 'r') as temp_file:
            self.temp = json.load(temp_file)

        #connect to ports:
        self.portlist = serial.tools.list_ports.comports()
        self.connected = False
        for p in self.portlist:
            if p.manufacturer=="SEGGER":
                self.connected=True
                self.com = p.device
            
        if self.connected:
            self.con_label.setText("Connected to "+ self.com)
        else:
            self.con_label.setText("Device not found")
        
        #comboboxes:
        self.start_box()
        
        #parameter displays:
        self.displayparams() #set the values of each number

        #buttons:
        self.save_data.clicked.connect(self.updateval)
        self.take_data.setCheckable(True)
        self.take_data.clicked.connect(self.start_stop_graph)
        self.send_data.clicked.connect(self.sending_data)
        self.app_m.clicked.connect(self.apply_mode)
        self.logout.clicked.connect(self.log_out)

        #graph setup
        self.sampleperiod= 50
        self.get_timer=QtCore.QTimer()
        self.get_timer.setInterval(self.sampleperiod)
        self.get_timer.timeout.connect(self.get_graph)
        self.ventricleData = []
        self.atriumData = []
        self.timeData = []
        self.counter = 0
        self.atrialP.setBackground('w')
        penred = mkPen(color=(255, 0, 0))
        self.Adata_line = self.atrialP.plot([], [], pen=penred)
        

        self.ventricleP.setBackground('w')
        penblue = mkPen(color=(0, 0, 255))
        self.Vdata_line = self.ventricleP.plot([], [], pen=penblue)
        

        self.GraphTimer = QtCore.QTimer()
        self.GraphTimer.setInterval(500)
        self.GraphTimer.timeout.connect(self.plot)

        self.atrialP.setLabel("left", "Amplitude")
        self.atrialP.setLabel("bottom", "Time")
        self.atrialP.setTitle("Atrium")
        self.atrialP.setYRange(-1,1)
        
        self.ventricleP.setLabel("left", "Amplitude")
        self.ventricleP.setLabel("bottom", "Time")
        self.ventricleP.setTitle("Ventricle")
        self.ventricleP.setYRange(-1,1)

        #self.atrialP.setYRange(-10,-5)
        #self.ventricleP.setYRange(-10,5)


    '''
    when the system is opened, intializes all the comboboxes
    '''
    
    def start_box(self):
        #self.myComboBox.addItems(map(str, range(30, 176, 5)))
        self.mode_c.addItem("")
        modes = ["AOO", "VOO", "AAI", "VVI", "AOOR", "VOOR", "AAIR", "VVIR"]
        self.mode_c.addItems(modes)

        self.lrl_c.addItem("")
        self.lrl_c.addItems(map(str, range(30, 176, 5)))
        '''
        self.lrl_c.setEditable(True)
        self.lrl_c.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.lrl_c.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        '''

        self.url_c.addItem("")
        self.url_c.addItems(map(str, range(50, 176, 5)))

        self.aa_c.addItem("")
        self.aa_c.addItems(map(str, [num/10.0 for num in range(0, 51)]))

        self.apw_c.addItem("")
        self.apw_c.addItems(map(str, range(0,31)))

        self.asen_c.addItem("")
        self.asen_c.addItems(map(str, [num/10.0 for num in range(0, 51)]))

        self.arp_c.addItem("")
        self.arp_c.addItems(map(str, range(150,501,10)))

        self.va_c.addItem("")
        self.va_c.addItems(map(str, [num/10.0 for num in range(0, 51)]))

        self.vpw_c.addItem("")
        self.vpw_c.addItems(map(str, range(0,31)))

        self.vs_c.addItem("")
        self.vs_c.addItems(map(str, [num/10.0 for num in range(0, 51)]))

        self.vrp_c.addItem("")
        self.vrp_c.addItems(map(str, range(150,501,10)))

        self.msr_c.addItem("")
        self.msr_c.addItems(map(str, range(50,176,5)))

        self.at_c.addItem("")
        act_thresh = ["V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High"]
        self.at_c.addItems(act_thresh)
        #function to add items to all the comboboxes

        self.react_c.addItem("")
        self.react_c.addItems(map(str, range(10,51,10)))

        self.rf_c.addItem("")
        self.rf_c.addItems(map(str, range(1,17)))

        self.rest_c.addItem("")
        self.rest_c.addItems(map(str, range(2,17)))

    '''
    Moves the graph such that the x axis is the same size
    '''
    def plot(self):
    #Remove the first element when graph data is too large (makes graph "move")
        if(len(self.atriumData) > 220):
            self.atriumData = self.atriumData[-220:]
            self.ventricleData = self.ventricleData[-220:]
            self.timeData = self.timeData[-220:]
        
        self.Adata_line.setData(self.timeData, self.atriumData)
        self.Vdata_line.setData(self.timeData, self.ventricleData)

    '''
    when the start graph is pressed, starts or stops the graph
    '''
   
    def get_graph(self):
        #check if board is connected
        self.connected = False
        self.portlist = serial.tools.list_ports.comports()
        for p in self.portlist:
            if p.manufacturer=="SEGGER":
                self.connected=True
                self.com = p.device
        if self.connected:
            self.con_label.setText("Connected to "+ self.com)
        else:
            self.con_label.setText("Device not found")

        if not self.connected:
            self.err_label.setText("Cannot get data, device not connected")
            return
        #writing bytes to get data from board
        ser = serial.Serial(self.com, baudrate=115200, timeout=1)
        get_data_bytes = b"\x16\x55" + b"."*121
        ser.write(get_data_bytes)

        data = ser.read(137)
        if len(data)==0:
            self.err_label.setText("can't get data")
            return
        else:
            self.err_label.setText("Getting graph data")
        #unpacking egram data
        atrium_temp = struct.unpack("d",data[0:8])
        ventricle_temp = struct.unpack("d",data[8:16])

        self.counter+=self.sampleperiod
        self.atriumData.append(atrium_temp[0])
        self.ventricleData.append(ventricle_temp[0])
        self.timeData.append(self.counter)


    def start_stop_graph(self):
        #check if board is connected
        self.err_label.setText("")
        self.connected=False
        self.portlist = serial.tools.list_ports.comports()
        for p in self.portlist:
            if p.manufacturer=="SEGGER":
                self.connected=True
                self.com = p.device
        if not self.connected:
            self.err_label.setText("Device not detected")
            self.con_label.setText("Device not found")
            return
        #if the button is never pressed, start timers
        if self.take_data.isChecked():
            self.take_data.setText("Stop Graph")
            self.ventricleData = []
            self.atriumData = []
            self.timeData = []
            self.GraphTimer.start()
            self.get_timer.start()
        #if they have been pressed, stop the timer
        else:
            self.take_data.setText("Start Graph")
            self.GraphTimer.stop()
            self.get_timer.stop()
        #changes the button when clicked from start graph to pause graph
        #depending on state, either start or stop timer for graph

    '''
    checks first to see if the values are valid, then displays the values found in the temp file
    '''
    def displayparams(self):
        #checks if the values are within range of lower rate limit
        if self.temp['values']['LRL'] >=30 and self.temp['values']['LRL'] <= 175:
            #if within range, display visually the temp file values
            self.lrl.setText(f"{self.temp['values']['LRL']}")
        else:
            #if not within limit, update the file value to a default value
            self.err_label.setText("invalid values detected, value was reset")
            self.temp['values']['LRL'] = 60
            self.lrl.setText(f"{self.temp['values']['LRL']}")
            self.update_profile()
        if self.temp['values']['URL'] >=50 and self.temp['values']['URL'] <=175:
            self.url.setText(f"{self.temp['values']['URL']}")
        else:
            self.err_label.setText("invalid values detected, value was reset")
            self.temp['values']['URL'] =120
            self.lrl.setText(f"{self.temp['values']['LRL']}")
            self.update_profile()

        
        if self.temp['values']['atr_amp'] >=0 and self.temp['values']['atr_amp'] <=5.0:
            self.aa.setText(f"{self.temp['values']['atr_amp']}")
        else:
            self.err_label.setText("invalid values detected, value was reset")
            self.temp['values']['atr_amp'] =120
            self.aa.setText(f"{self.temp['values']['atr_amp']}")
            self.update_profile()

        if self.temp['values']['Atr_Pul_Wid'] >=1 and self.temp['values']['Atr_Pul_Wid'] <=30:
            self.apw.setText(f"{self.temp['values']['Atr_Pul_Wid']}")
        else:
            self.err_label.setText("invalid values detected, value was reset")
            self.temp['values']['Atr_Pul_Wid'] =1
            self.apw.setText(f"{self.temp['values']['Atr_Pul_Wid']}")
            self.update_profile()
        
        if self.temp['values']['Atr_sens'] >=0 and self.temp['values']['Atr_sens'] <=5:
            self.asen.setText(f"{self.temp['values']['Atr_sens']}")
        else:
            self.err_label.setText("invalid values detected, value was reset")
            self.temp['values']['Atr_sens'] =0.75
            self.asen.setText(f"{self.temp['values']['Atr_sens']}")
            self.update_profile()

        if self.temp['values']['ARP'] >=150 and self.temp['values']['ARP'] <=500:
            self.arp.setText(f"{self.temp['values']['ARP']}")
        else:
            self.err_label.setText("invalid values detected, value was reset")
            self.temp['values']['ARP'] =250
            self.arp.setText(f"{self.temp['values']['ARP']}")
            self.update_profile()
        
        if self.temp['values']['Ven_amp'] >=0 and self.temp['values']['Ven_amp'] <=5.0:
            self.va.setText(f"{self.temp['values']['Ven_amp']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['Ven_amp'] =5.0
            self.va.setText(f"{self.temp['values']['Ven_amp']}")
            self.update_profile()

        if self.temp['values']['Ven_Pul_Wid'] >=1 and self.temp['values']['Ven_Pul_Wid'] <=30:
            self.vpw.setText(f"{self.temp['values']['Ven_Pul_Wid']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['Ven_Pul_Wid'] =1
            self.vpw.setText(f"{self.temp['values']['Ven_Pul_Wid']}")
            self.update_profile()

        if self.temp['values']['Ven_Sen'] >=0 and self.temp['values']['Ven_Sen'] <=5:
            self.vs.setText(f"{self.temp['values']['Ven_Sen']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['Ven_Sen'] =2.5
            self.vs.setText(f"{self.temp['values']['Ven_Sen']}")
            self.update_profile()
        
        if self.temp['values']['VRP'] >=150 and self.temp['values']['VRP'] <=500:
            self.vrp.setText(f"{self.temp['values']['VRP']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['VRP'] =250
            self.vrp.setText(f"{self.temp['values']['VRP']}")
            self.update_profile()
        
        if self.temp['values']['MSR'] >=50 and self.temp['values']['MSR'] <=175:
            self.msr.setText(f"{self.temp['values']['MSR']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['MSR'] =120
            self.msr.setText(f"{self.temp['values']['MSR']}")
            self.update_profile()
        
        if self.temp['values']['Act_Thresh'] >=1 and self.temp['values']['Act_Thresh'] <=7:
            act_thresh = ["V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High"]
            if self.temp['values']['Act_Thresh']==1:
                self.at.setText(act_thresh[0])
            elif self.temp['values']['Act_Thresh']==2:
                self.at.setText(act_thresh[1])
            elif self.temp['values']['Act_Thresh']==3:
                self.at.setText(act_thresh[2])
            elif self.temp['values']['Act_Thresh']==4:
                self.at.setText(act_thresh[3])
            elif self.temp['values']['Act_Thresh']==5:
                self.at.setText(act_thresh[4])
            elif self.temp['values']['Act_Thresh']==6:
                self.at.setText(act_thresh[5])
            elif self.temp['values']['Act_Thresh']==7:
                self.at.setText(act_thresh[6])
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['Act_Thresh'] =4
            self.at.setText(f"{self.temp['values']['Act_Thresh']}")
            self.update_profile()
        
        if self.temp['values']['Rxn_Time'] >=10 and self.temp['values']['Rxn_Time'] <=50:
            self.react.setText(f"{self.temp['values']['Rxn_Time']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['Rxn_Time'] =30
            self.react.setText(f"{self.temp['values']['Rxn_Time']}")
            self.update_profile()

        if self.temp['values']['RF'] >=1 and self.temp['values']['RF'] <=16:
            self.rf.setText(f"{self.temp['values']['RF']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['RF'] =8
            self.rf.setText(f"{self.temp['values']['RF']}")
            self.update_profile()

        if self.temp['values']['Rec_Time'] >=2 and self.temp['values']['Rec_Time'] <=16:
            self.rest.setText(f"{self.temp['values']['Rec_Time']}")
        else:
            self.err_label.setText("invalid values detected, the value was reset")
            self.temp['values']['Rec_Time'] =5
            self.rest.setText(f"{self.temp['values']['Rec_Time']}")
            self.update_profile()
        
        
        #calls the respective mode
        mode = int(self.temp['values']['mode'])
        if mode == 1:
            self.aoo()
        elif mode == 2:
            self.voo()
        elif mode == 3:
            self.aai()
        elif mode == 4:
            self.vvi()
        elif mode == 5:
            self.aoor()
        elif mode == 6:
            self.voor()
        elif mode == 7:
            self.aair()
        elif mode == 8:
            self.vvir()

        #function to check the temp file for values and update them all


    '''
    when save param button is pressed, updates the values the user has selected in to the temp variable
    '''
    def updateval(self):
        self.err_label.setText("")
        try: 
            #if self.mode_c.isEnabled() : #can change this to if len !=0
                #self.temp['values']['mode']= int(self.mode_c.currentText())
            if self.lrl_c.isEnabled() and (self.lrl_c.currentText() != ""):
                self.temp['values']['LRL'] = int(self.lrl_c.currentText())
            if self.url_c.isEnabled() and (self.url_c.currentText() != ""):
                self.temp['values']['URL'] = int(self.url_c.currentText())
            if self.aa_c.isEnabled()and (self.aa_c.currentText() != ""):
                self.temp['values']['atr_amp'] = float(self.aa_c.currentText())
            if self.apw_c.isEnabled()and (self.apw_c.currentText() != ""):
                self.temp['values']['Atr_Pul_Wid'] = float(self.apw_c.currentText())
            if self.asen_c.isEnabled()and (self.asen_c.currentText() != ""):
                self.temp['values']['Atr_sens'] = float(self.asen_c.currentText())
            if self.arp_c.isEnabled()and (self.arp_c.currentText() != ""):
                self.temp['values']['ARP'] = int(self.arp_c.currentText())
            if self.va_c.isEnabled()and (self.va_c.currentText() != ""):
                self.temp['values']['Ven_amp'] = float(self.va_c.currentText())
            if self.vpw_c.isEnabled()and (self.vpw_c.currentText() != ""):
                self.temp['values']['Ven_Pul_Wid'] = float(self.vpw_c.currentText())
            if self.vs_c.isEnabled()and (self.vs_c.currentText() != ""):
                self.temp['values']['Ven_Sen']= float(self.vs_c.currentText())
            if self.vrp_c.isEnabled()and (self.vrp_c.currentText() != ""):
                self.temp['values']['VRP'] = int(self.vrp_c.currentText())
            if self.msr_c.isEnabled()and (self.msr_c.currentText() != ""):
                self.temp['values']['MSR'] = int(self.msr_c.currentText())
            if self.at_c.isEnabled()and (self.at_c.currentText() != ""):
                curr_thresh = self.at_c.currentText()
                act_thresh = ["V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High"]
                if curr_thresh== act_thresh[0]:
                    self.temp['values']['Act_Thresh'] = 1
                elif curr_thresh== act_thresh[1]:
                    self.temp['values']['Act_Thresh'] = 2
                elif curr_thresh== act_thresh[2]:
                    self.temp['values']['Act_Thresh'] = 3
                elif curr_thresh== act_thresh[3]:
                    self.temp['values']['Act_Thresh'] = 4
                elif curr_thresh== act_thresh[4]:
                    self.temp['values']['Act_Thresh'] = 5
                elif curr_thresh== act_thresh[5]:
                    self.temp['values']['Act_Thresh'] = 6
                elif curr_thresh== act_thresh[6]:
                    self.temp['values']['Act_Thresh'] = 7
            if self.react_c.isEnabled()and (self.react_c.currentText() != ""):
                self.temp['values']['Rxn_Time'] = int(self.react_c.currentText())
            if self.rf_c.isEnabled()and (self.rf_c.currentText() != ""):
                self.temp['values']['RF'] = int(self.rf_c.currentText())
            if self.rest_c.isEnabled()and (self.rest_c.currentText() != ""):
                self.temp['values']['Rec_Time'] = int(self.rest_c.currentText())
        except:
            self.err_label.setText('Please fill in all inputs')

        
        self.displayparams()

        self.update_profile()

        

        #function to update the temp file, then display them
        #call display params after to update them visually
    
 
    '''
    when the send data is pressed, saves any new changes and then connects it 
    '''
    def sending_data(self):
        self.err_label.setText("")
        self.updateval() 
        self.connected=False
        self.portlist = serial.tools.list_ports.comports()
        for p in self.portlist:
            if p.manufacturer=="SEGGER":
                self.connected=True
                self.com = p.device
            
        if self.connected:
            self.con_label.setText("Connected to "+ self.com)
        else:
            self.con_label.setText("Device not found")
        if not self.connected:
            self.err_label.setText("No device connected, cannot send data")
            return
        print('connected,sending data')

        params = list(self.temp['values'].values())
        print("sending",params)
        #pack the data and send it
        mode = struct.pack("B", int(params[0]))
        LRL = struct.pack("d", float(params[1]))
        URL = struct.pack("d", float(params[2]))
        Atr_Amp = struct.pack("d", float(params[3]))
        atr_pul_wid = struct.pack("d", float(params[4]))
        atr_sens = struct.pack("d", float(params[5]))
        ARP = struct.pack("d", float(params[6]))
        ven_Amp = struct.pack("d", float(params[7]))
        ven_pul_wid=struct.pack("d", float(params[8]))
        ven_sens = struct.pack("d", float(params[9]))
        VRP = struct.pack("d", float(params[10]))
        MSR = struct.pack("d", float(params[11]))
        Act_thresh = struct.pack("d", float(params[12]))
        React_time = struct.pack("d", float(params[13]))
        RF = struct.pack("d", float(params[14]))
        Rec_time = struct.pack("d", float(params[15]))

        data = b"\x16\x22" + mode+LRL+URL+Atr_Amp+atr_pul_wid+atr_sens+ARP+ven_Amp+ven_pul_wid+ven_sens+VRP+MSR+Act_thresh+React_time+RF+Rec_time
        
        print(len(data))
        print('packed data',data)

        ser = serial.Serial(self.com, baudrate=115200, timeout=1)
        ser.write(data)

        #now tell the board to write back data to double check parameter values
        get_data_bytes = b"\x16\x55" + b"."*121
        ser.write(get_data_bytes)

        import time
        time.sleep(0.25)
        data = ser.read(137)
        #unpacking data
        #print('sending data')
        m = struct.unpack("B",data[16:17])
        #print('mode:', m[0], int(params[0])) 
        lrl = struct.unpack("d",data[17:25])
        #print('lrl:', round(lrl[0],4), round(float(params[1]),4))
        url = struct.unpack("d",data[25:33])
        #print('url:', url[0], params[2])
        aa = struct.unpack("d",data[33:41])
        apw = struct.unpack("d",data[41:49])
        asens = struct.unpack("d",data[49:57])
        arp = struct.unpack("d",data[57:65])
        va = struct.unpack("d",data[65:73])
        vpw = struct.unpack("d",data[73:81])
        vs = struct.unpack("d",data[81:89])
        vrp = struct.unpack("d",data[89:97])
        msr = struct.unpack("d",data[97:105])
        at = struct.unpack("d",data[105:113])
        react = struct.unpack("d",data[113:121])
        rf = struct.unpack("d",data[121:129])
        rect = struct.unpack("d",data[129:137])

##        if int(params[0]) == m[0]:
##            print('correct1')
##        if round(float(params[1]),4)==round(float(lrl[0]),4):
##            print('correct2')
##        if round(float(params[2]),4)==round(float(url[0]),4):
##            print('correct3')
##        if round(float(params[3]),4)==round(float(aa[0]),4):
##            print('correct4')
##        if round(float(params[4]),4)==round(float(apw[0]),4):
##            print('correct 5')
##        if round(float(params[5]),4)==round(float(asens[0]),4):
##            print('c6')
##        if round(float(params[6]),4)==round(float(arp[0]),4):
##            print('c7')
##        if round(float(params[7]),4)==round(float(va[0]),4):
##            print('c8')
##        if round(float(params[8]),4)==round(float(vpw[0]),4):
##            print('c9')
##        if round(float(params[9]))==round(float(vs[0]),4):
##            print('c10')
##        if round(float(params[10]),4)==round(float(vrp[0]),4):
##            print('c11')
##        if round(float(params[11]),4)==round(float(msr[0]),4):
##            print('c12')
##        if round(float(params[12]),4)==round(float(at[0]),4):
##            print('c13')
##        if round(float(params[13]),4)==round(float(react[0]),4):
##            print('c14')
##        if round(float(params[14]),4)==round(float(rf[0]),4):
##            print('c15')
##        if round(float(params[15]),4)==round(float(rect[0]),4):
##            print('c16')

##        if round(float(params[1]),4)==round(float(lrl[0]),4):
##            print('correct')
##        else:
##            print('incorrect')
        

        #check to see if the data received is correct by comparing received and sent data
        #if int(params[0]) == int(m) and round(float(params[1]))==round(float(lrl)) and round(float(params[2]))==round(float(url)) and round(float(params[3]))==round(float(aa)) and round(float(params[4]))==round(float(apw)) and round(float(params[5]))==round(float(asens)) and round(float(params[6]))==round(float(arp)) and round(float(params[7]))==round(float(va)) and round(float(params[8]))==round(float(vpw)) and round(float(params[9]))==round(float(vs)) and round(float(params[10]))==round(float(vrp)) and round(float(params[11]))==round(float(msr)) and round(float(params[12]))==round(float(at)) and round(float(params[13]))==round(float(react)) and round(float(params[14]))==round(float(rf)) and round(float(params[15]))==round(float(rect)):
        #if int(params[0]) == m[0] and round(float(params[1]),4)==round(lrl[0],4) and round(float(params[2]),4)==round(url[0],4) and round(float(params[3]),4)==round(aa[0],4) and round(float(params[4]),4)==round(apw[0],4) and round(float(params[5]),4)==round(asens[0],4) and round(float(params[6]),4)==round(arp[0],4) and round(float(params[7]),4)==round(va[0],4) and round(float(params[8]),4)==round(vpw[0],4) and round(float(params[9]))==round(vs[0],4) and round(float(params[10]),4)==round(vrp[0],4) and round(float(params[11]),4)==round(msr[0],4) and round(float(params[12]),4)==round(at[0],4) and round(float(params[13]),4)==round(react[0],4) and round(float(params[14]),4)==round(rf[0],4) and round(float(params[15]),4)==round(rect[0],4):
        if int(params[0]) == m[0] and round(float(params[1]),4)==round(float(lrl[0]),4) and round(float(params[2]),4)==round(float(url[0]),4) and round(float(params[3]),4)==round(float(aa[0]),4) and round(float(params[4]),4)==round(float(apw[0]),4) and round(float(params[5]),4)==round(float(asens[0]),4) and round(float(params[6]),4)==round(float(arp[0]),4) and round(float(params[7]),4)==round(float(va[0]),4) and round(float(params[8]),4)==round(float(vpw[0]),4) and round(float(params[9]))==round(float(vs[0]),4) and round(float(params[10]),4)==round(float(vrp[0]),4) and round(float(params[11]),4)==round(float(msr[0]),4) and round(float(params[12]),4)==round(float(at[0]),4) and round(float(params[13]),4)==round(float(react[0]),4) and round(float(params[14]),4)==round(float(rf[0]),4) and round(float(params[15]),4)==round(float(rect[0]),4):
            self.err_label.setText("Data Correct")
            print('data correct')
        
        else:
            self.err_label.setText("Data Correct")
            print('data incorrect')
        

            


    def apply_mode(self):
        self.err_label.setText("")
        curr_mode = self.mode_c.currentText()
        if curr_mode=="":
            self.err_label.setText("Please choose a mode")
            return
        if curr_mode == "AOO":
            self.temp['values']['mode']= 1
        elif curr_mode == "VOO":
            self.temp['values']['mode']= 2
        elif curr_mode == "AAI":
            self.temp['values']['mode']= 3
        elif curr_mode == "VVI":
            self.temp['values']['mode']= 4
        elif curr_mode == "AOOR":
            self.temp['values']['mode']= 5
        elif curr_mode == "VOOR":
            self.temp['values']['mode']= 6
        elif curr_mode == "AAIR":
            self.temp['values']['mode']= 7
        elif curr_mode == "VVIR":
            self.temp['values']['mode']= 8
        
        self.update_profile()
        self.displayparams()
        #change the mode, and then update the temp file as well


        #get data to graph

    def update_temp(self):
        with open('temp.json', 'w') as temp_file:
            json.dump(self.temp, temp_file, indent=2)

    '''
updates the temp and profiles JSON file
'''
    def update_profile(self):
        self.update_temp()
        # Read the JSON data from the main file

        # Find the index of the user with the same username in the main file
        index_to_update = None
        for i, user in enumerate(self.file['users']):
            if user['username'] == self.temp['username']:
                index_to_update = i
                break

        # Update the user profile in the main file
        if index_to_update is not None:
            self.file['users'][index_to_update] = self.temp
            print(f"User profile for '{self.temp['username']}' updated.")
        else:
            print(f"User profile for '{self.temp['username']}' not found.")

        # Write the updated JSON data back to the main file
        with open('profiles.json', 'w') as ufile:
            json.dump(self.file, ufile, indent=2)

    def log_out(self):
        self.update_profile()
        current_page_index = widget.currentIndex()
        current_page_widget = widget.widget(current_page_index)
        widget.setCurrentIndex(widget.currentIndex()-2)
        current_page_widget.deleteLater()
        #
        #logout, delete this widget, update profiles.json

    def aoo(self):
        self.cur_m.setText("AOO")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)
        self.apw_c.setDisabled(False)
        self.aa_c.setDisabled(False)

        self.vpw_c.setDisabled(True)
        self.va_c.setDisabled(True)
        self.asen_c.setDisabled(True)
        self.arp_c.setDisabled(True)
        self.vs_c.setDisabled(True)
        self.vrp_c.setDisabled(True)
        self.msr_c.setDisabled(True)
        self.at_c.setDisabled(True)
        self.react_c.setDisabled(True)
        self.rf_c.setDisabled(True)
        self.rest_c.setDisabled(True)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        
    def voo(self):
        self.cur_m.setText("VOO")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)

        self.apw_c.setDisabled(True)
        self.aa_c.setDisabled(True)

        self.vpw_c.setDisabled(False)
        self.va_c.setDisabled(False)

        self.asen_c.setDisabled(True)
        self.arp_c.setDisabled(True)
        self.vs_c.setDisabled(True)
        self.vrp_c.setDisabled(True)
        self.msr_c.setDisabled(True)
        self.at_c.setDisabled(True)
        self.react_c.setDisabled(True)
        self.rf_c.setDisabled(True)
        self.rest_c.setDisabled(True)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')

    def aai(self):
        self.cur_m.setText("AAI")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)

        self.apw_c.setDisabled(False)
        self.aa_c.setDisabled(False)

        self.vpw_c.setDisabled(True)
        self.va_c.setDisabled(True)

        self.asen_c.setDisabled(False)
        self.arp_c.setDisabled(False)

        self.vs_c.setDisabled(True)
        self.vrp_c.setDisabled(True)
        self.msr_c.setDisabled(True)
        self.at_c.setDisabled(True)
        self.react_c.setDisabled(True)
        self.rf_c.setDisabled(True)
        self.rest_c.setDisabled(True)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')

    def vvi(self):
        self.cur_m.setText("VVI")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)

        self.apw_c.setDisabled(True)
        self.aa_c.setDisabled(True)

        self.vpw_c.setDisabled(False)
        self.va_c.setDisabled(False)

        self.asen_c.setDisabled(True)
        self.arp_c.setDisabled(True)

        self.vs_c.setDisabled(False)
        self.vrp_c.setDisabled(False)

        self.msr_c.setDisabled(True)
        self.at_c.setDisabled(True)
        self.react_c.setDisabled(True)
        self.rf_c.setDisabled(True)
        self.rest_c.setDisabled(True)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')

    def aoor(self):
        self.cur_m.setText("AOOR")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)
        self.apw_c.setDisabled(False)
        self.aa_c.setDisabled(False)

        self.vpw_c.setDisabled(True)
        self.va_c.setDisabled(True)
        self.asen_c.setDisabled(True)
        self.arp_c.setDisabled(True)
        self.vs_c.setDisabled(True)
        self.vrp_c.setDisabled(True)

        self.msr_c.setDisabled(False)
        self.at_c.setDisabled(False)
        self.react_c.setDisabled(False)
        self.rf_c.setDisabled(False)
        self.rest_c.setDisabled(False)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')

    def voor(self):
        self.cur_m.setText("VOOR")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)
        self.apw_c.setDisabled(True)
        self.aa_c.setDisabled(True)

        self.vpw_c.setDisabled(False)
        self.va_c.setDisabled(False)
        self.asen_c.setDisabled(True)
        self.arp_c.setDisabled(True)
        self.vs_c.setDisabled(True)
        self.vrp_c.setDisabled(True)

        self.msr_c.setDisabled(False)
        self.at_c.setDisabled(False)
        self.react_c.setDisabled(False)
        self.rf_c.setDisabled(False)
        self.rest_c.setDisabled(False)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')


    def aair(self):
        self.cur_m.setText("AAIR")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)
        self.apw_c.setDisabled(False)
        self.aa_c.setDisabled(False)

        self.vpw_c.setDisabled(True)
        self.va_c.setDisabled(True)
        self.asen_c.setDisabled(False)
        self.arp_c.setDisabled(False)
        self.vs_c.setDisabled(True)
        self.vrp_c.setDisabled(True)

        self.msr_c.setDisabled(False)
        self.at_c.setDisabled(False)
        self.react_c.setDisabled(False)
        self.rf_c.setDisabled(False)
        self.rest_c.setDisabled(False)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')


    def vvir(self):
        self.cur_m.setText("VVIR")
        self.lrl_c.setDisabled(False)
        self.url_c.setDisabled(False)
        self.apw_c.setDisabled(True)
        self.aa_c.setDisabled(True)

        self.vpw_c.setDisabled(False)
        self.va_c.setDisabled(False)
        self.asen_c.setDisabled(True)
        self.arp_c.setDisabled(True)
        self.vs_c.setDisabled(False)
        self.vrp_c.setDisabled(False)

        self.msr_c.setDisabled(False)
        self.at_c.setDisabled(False)
        self.react_c.setDisabled(False)
        self.rf_c.setDisabled(False)
        self.rest_c.setDisabled(False)

        self.lrl_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.url_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.apw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vpw_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.aa_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.va_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.asen_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.arp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:red;
                        ''')
        self.vs_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.vrp_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.msr_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.at_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.react_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rf_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')
        self.rest_d.setStyleSheet('''
                        font-size: 14pt;
                        color:white;
                        ''')


if __name__ == "__main__":    
    app = QApplication(sys.argv)

    file = load_file() #load json file
    firstwindow = login(file) #open first window
    
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(firstwindow)    

    reg = register(file)
    widget.addWidget(reg)


    
    # maincontrol = maincontrol(file)
    # widget.addWidget(maincontrol)
    
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
