from tkinter import *
from threading import Thread
from time import sleep
from re import split


class exceptionHandler(Exception):
    def __init__(self):
        self.errorType = None
        self.errorData = None
    
    def set_error(self, errorType, errorData):
        self.errorType = errorType
        self.errorData = errorData

    def get_errorMessage(self):
        errorMessage = self.errorData[:]
        errorMessage[0] = self.errorType + ": " + self.errorData[0]
        return errorMessage

class LMC:
    def __init__(self):
        #controls
        self.pause_status = False
        self.control_type = 0
        self.reset_status = False
        self.clockSpeed = 1 #speed

        #porcessing
        self.instr_code = []

        #RAM
        self.RAM = []
        self.ram_access_type = "None"

        #CPU
        self.pc_count = 0

        #expection handler
        self.exception_handler = exceptionHandler()

        #assembler
        self.asm = assembler(self.exception_handler)

        #Fetch decode execute cycle
        self.fetchDecodeExecuteCycle = FDE_cycle(self)

    def pause_procs(self):
        if self.pause_status == False:
            self.pause_status = True
        else:
            self.pause_status = False

    def control_command(self):
        self.pc_display.configure(state = NORMAL)
        self.update_pc_display() 
        self.pc_display.configure(state = "readonly")

        if self.control_type == 0:
            self.control_type = 1
            self.control_button.configure(text = "Pause")
            self.reset_status = False
            self.pc_display.configure(state = "readonly")

            self.FDE_thread = Thread(target = self.fetchDecodeExecuteCycle.start, daemon = False)
            self.FDE_thread.start()
        elif self.control_type == 1:
            self.control_type = 2
            self.control_button.configure(text = "Play")
            self.pause_procs()
        else:
            self.control_type = 1
            self.control_button.configure(text = "Pause")
            self.pause_procs()

    def reset_command(self):
        #update RAM--------------------------------------------------
        for i in range(100):
            self.RAM[i][1].delete(0, END)
            if i < len(self.instr_code):
                self.RAM[i][0] = self.instr_code[i]
                self.RAM[i][1].insert(0, self.instr_code[i])
            else:
                self.RAM[i][0] = "000"
                self.RAM[i][1].insert(0, "000")
        #------------------------------------------------------------

        self.reset_status = True
        self.pause_status = False
        self.control_type = 0

        self.pc_display.configure(state = NORMAL)
        self.pc_display.delete(0, END)
        self.pc_display.insert(0, self.int_to_instr(0))
        self.update_pc_display() 

        self.control_button.configure(text = "Run")

        self.insert_to_entry(self.acc_display, 0, "000", True)
        self.insert_to_entry(self.input_entry, None, False, True)
        self.insert_to_entry(self.ir_display, None, False, True)
        self.insert_to_entry(self.ar_display, None, False, True)
        self.insert_to_textbox(self.output_display, None, False, True)

    def adjustSpeed(self, direction):
        adjusted_clockSpeed = self.clockSpeed + direction

        if adjusted_clockSpeed > 5:
            self.clockSpeed = 5
        elif adjusted_clockSpeed < 1:
            self.clockSpeed = 1
        else:
            self.clockSpeed = adjusted_clockSpeed

        self.insert_to_entry(self.speed_display, 0, "speed " + str(self.clockSpeed), True)

    def check_for_int(self, instr):
            try:
                int(instr)
                return True
            except:
                return False

    def int_to_instr(self, integer):
        if integer < 10:
            return "0" + str(integer)
        else:
            return str(integer)

    def nstr_to_instr(self, nstr):
        number = int(nstr)
        if number < 10:
            return "0" + str(number)
        else:
            return str(number)

    def update_ML(self, event, i):
        new_instr = event.widget.get()

        if new_instr == "-000":
            new_instr = "000"
        elif self.check_for_int(new_instr) == False or len(new_instr) == 0 or int(new_instr) > 999:
            new_instr = self.RAM[i][0]
        elif new_instr[0] == "-":
            if len(new_instr) == 2:
                new_instr = "-00" + new_instr
            elif len(new_instr) == 3:
                new_instr = "-0" + new_instr
        else:
            if len(new_instr) == 1:
                new_instr = "00" + new_instr
            elif len(new_instr) == 2:
                new_instr = "0" + new_instr

        self.RAM[i][0] = new_instr

        event.widget.delete(0, END)
        event.widget.insert(0, new_instr)
        
    def update_pc_display(self):
        pc_value = self.pc_display.get()
        if self.check_for_int(pc_value) == False or len(pc_value) == 0 or pc_value[0] == "-" or int(pc_value) > 99:
            pc_value = self.int_to_instr(self.pc_count)
        elif int(pc_value) != self.pc_count:
            self.RAM[self.pc_count][2].configure(bg = self.default_bg)
            self.pc_count = int(pc_value)

        self.pc_display.delete(0, END)
        self.pc_display.insert(0, self.nstr_to_instr(pc_value))

        self.RAM[self.pc_count][2].configure(bg = "#bbbbbb")

    def insert_to_textbox(self, widget, index, insert_text, clear):
        widget.configure(state = NORMAL)
        if clear == True:
            widget.delete(1.0, END)
        if insert_text != False:
            widget.insert(index, insert_text)
        widget.configure(state = DISABLED)

    def insert_to_entry(self, widget, index, insert_text, clear):
        widget.configure(state = NORMAL)
        if clear == True:
            widget.delete(0, END)
        if insert_text != False:
            widget.insert(index, insert_text)
        widget.configure(state = "readonly")

    def procTerminal_print(self, output_text):
        self.procTerminal_display.configure(state = NORMAL)
        for line in output_text:
            self.procTerminal_display.insert(END, line + "\n")
        self.procTerminal_display.insert(END, ">")
        self.procTerminal_display.configure(state = DISABLED)

    def set_ram_access_type(self, access_type):
        self.ram_access_type = access_type
        self.ram_access_indicator_label.configure(text = f"Access: {access_type}")

    def assemble_to_ram(self):
        self.procTerminal_print(["Assembling..."])
        code = self.codeTerimnal.get("1.0", END).split("\n")

        self.padded_code, self.assembly_code, self.instr_code, errorFlag = self.asm.assemble(code)

        if errorFlag == True:
            errorMessage = self.exception_handler.get_errorMessage() + ["Assembling halted"]
            self.procTerminal_print(errorMessage)
        else:
            #update code terminal ----------------------------------------------------------------------------------------
            self.codeTerimnal.delete("1.0", END)
            for line in self.padded_code:
                self.codeTerimnal.insert(END, line + "\n")
            self.codeTerimnal.config(state = DISABLED)
            self.codeTerimnal.config(state = NORMAL)
            #-------------------------------------------------------------------------------------------------------------

            #update assembly terminal ------------------------------------------------------------------------------------
            self.asmTerminal.config(state = NORMAL)
            self.asmTerminal.delete("1.0", END)
            for line in self.assembly_code:
                self.asmTerminal.insert(END, line + "\n")
            self.asmTerminal.config(state = DISABLED)
            #-------------------------------------------------------------------------------------------------------------

            self.reset_command()
        
            self.procTerminal_print(["Assembling compleated"])

    def start(self):
        self.window = Tk()
        self.window.title("Little Man Computer v2.0")
        self.window.geometry("1150x655")
        self.default_bg = self.window["bg"]

        #handling elements----------------------------------------------------------------------------------
        #coding terminal
        self.codeTerimnal = Text(self.window, height = 12, width = 40, borderwidth = 1, relief = "solid")
        self.codeTerimnal.place(x = 10, y = 10, width = 200, height = 600)

        #assembly code terminal
        self.asmTerminal = Text(self.window, height = 12, width = 40, borderwidth = 1, relief = "solid")
        self.asmTerminal.place(x = 220, y = 10, width = 150, height = 600)
        self.asmTerminal.config(state = DISABLED)

        self.ATR_button = Button(
            self.window, text = "Assmeble to ram", font = ("Helvetica", 13), 
            command = self.assemble_to_ram
        )
        self.ATR_button.place(x = 10, y = 620, width = 135, height = 25)

        self.control_button = Button(
            self.window, text = "Run", font = ("Helvetica", 13),
            command = self.control_command
        )
        self.control_button.place(x = 155, y = 620, width = 55, height = 25)

        self.reset_button = Button(
            self.window, text = "Reset", font = ("Helvetica", 13),
            command = self.reset_command
        )
        self.reset_button.place(x = 220, y = 620, width = 55, height = 25)

        self.speed_display = Entry(self.window, font = ("Helvetica", 11), state = "readonly")
        self.speed_display.place(x = 300, y = 620, width = 55, height = 25)

        self.adjustSpeed(0)

        self.speedDown_button = Button(
            self.window, text = "<", font = ("Helvetica", 12, "bold"), 
            command = lambda: self.adjustSpeed(-1)
        )
        self.speedDown_button.place(x = 285, y = 620, width = 15, height = 25)

        self.speedUp_button = Button(
            self.window, text = ">", font = ("Helvetica", 12, "bold"), 
            command = lambda: self.adjustSpeed(1)
        )
        self.speedUp_button.place(x = 355, y = 620, width = 15, height = 25)

        #-------------------------------------------------------------------------------------------------------------

        #IO devices --------------------------------------------------------------------------------------------
        self.output_label = Label(self.window, text = "output", font = ("Times", 14), border = 1, relief = "sunken")
        self.output_label.place(x = 420, y = 10, width = 80, height = 25)
        self.output_display = Text(self.window, font = ("Helvetica", 13), state = DISABLED, bg = self.default_bg, border = 1, relief = SOLID)
        self.output_display.place(x = 420, y = 35, width = 80, height = 150)

        self.input_label = Label(self.window, text = "input", font = ("Times", 14), border = 1, relief = "sunken")
        self.input_label.place(x = 420, y = 595, width = 80, height = 25)
        self.input_entry = Entry(self.window, font = ("Helvetica", 13), state = "readonly", border = 1, relief = SOLID)
        self.input_entry.place(x = 420, y = 620, width = 80, height = 25)
        #-------------------------------------------------------------------------------------------------------------

        #RAM elements ------------------------------------------------------------------------------------------------
        self.ram_frame = Frame(self.window, borderwidth = 1, relief = "solid")
        self.ram_frame.place(x = 675, y = 20, width = 465, height = 440)
        self.ram_label = Label(self.ram_frame, text = "RAM", font = ("Times", 15))
        self.ram_label.place(x = 207, y = 5, width = 50, height = 25)
        self.ram_access_indicator_label = Label(
            self.ram_frame, text = f"Access: {self.ram_access_type}", font = ("Times", 11), 
            border = 1, relief = SOLID
            )
        self.ram_access_indicator_label.place(x = 390, y = 10, width = 70, height = 18)

        for y in range(10):
            for x in range(10):
                self.RAM.append(["000"])

                memoryLocation = Entry(self.ram_frame, font = ("Times", 13), justify = "center", borderwidth = 1, relief = "solid")
                memoryLocation.insert(0, "000")
                memoryLocation.bind("<FocusOut>", lambda event, i = y * 10 + x: self.update_ML(event, i))
                memoryLocation.bind("<Return>", lambda event, i = y * 10 + x: self.update_ML(event, i))
                memoryLocation.place(x = x * 45 + 10, y = y * 40 + 50, width = 40, height = 20)
                self.RAM[-1].append(memoryLocation)
                
                memoryAddress = Label(self.ram_frame, text = y * 10 + x, font = "Courier", borderwidth = 1, relief = "solid")
                memoryAddress.place(x = x * 45 + 17, y = y * 40 + 36, width = 25, height = 15)
                self.RAM[-1].append(memoryAddress)
        #-------------------------------------------------------------------------------------------------------------

        #CPU elements ------------------------------------------------------------------------------------------------
        self.cpu_frame = Frame(self.window, borderwidth = 1, relief = "solid")
        self.cpu_frame.place(x = 420, y = 250, width = 200, height = 198)
        self.cpu_label = Label(self.cpu_frame, text = "CPU", font = ("Times", 14))
        self.cpu_label.place(x = 75, y = 0, width = 50, height = 25)

        self.pc_frame = Frame(self.cpu_frame, borderwidth = 1, relief = "solid")
        self.pc_frame.place(x = -1, y = 25, width = 200, height = 40)

        self.pc_label = Label(self.pc_frame, text = "Program Counter", font = ("Times", 12))
        self.pc_label.place(x = 5, y = 5)
        
        self.pc_display = Entry(
            self.pc_frame, justify = "center", font = ("Helvetica", 13), 
            bg = self.default_bg, borderwidth = 1, relief = "solid"
            )
        self.pc_display.place(x = 150, y = 5, width = 40, height = 25)
        self.pc_display.insert(0, "00")
        self.update_pc_display()
        self.pc_display.bind("<FocusOut>", lambda event: self.update_pc_display())
        self.pc_display.bind("<Return>", lambda event: self.update_pc_display())

        self.ir_frame = Frame(self.cpu_frame, borderwidth = 1, relief = "solid")
        self.ir_frame.place(x = -1, y = 64, width = 200, height = 40)
        self.ir_label = Label(self.ir_frame, text = "Instruction Registor", font = ("Times", 12))
        self.ir_label.place(x = 5, y = 5)
        self.ir_display = Entry(
            self.ir_frame, justify = "center", font = ("Helvetica", 13), 
            state = "readonly", borderwidth = 1, relief = "solid"
            )
        self.ir_display.place(x = 150, y = 5, width = 20, height = 25)

        self.ar_frame = Frame(self.cpu_frame, borderwidth = 1, relief = "solid")
        self.ar_frame.place(x = -1, y = 103, width = 200, height = 40)
        self.ar_label = Label(self.ar_frame, text = "Address Registor", font = ("Times", 12))
        self.ar_label.place(x = 5, y = 5)
        self.ar_display = Entry(
            self.ar_frame, justify = "center", font = ("Helvetica", 13), 
            state = "readonly", borderwidth = 1, relief = "solid"
            )
        self.ar_display.place(x = 150, y = 5, width = 40, height = 25)

        self.acc_frame = Frame(self.cpu_frame, borderwidth = 1, relief = "solid")
        self.acc_frame.place(x = -1, y = 142, width = 200, height = 55)
        self.acc_label = Label(self.acc_frame, text = "Accumulator", font = ("Times", 12))
        self.acc_label.place(x = 50, y = 2, width = 100)
        self.acc_display = Entry(
            self.acc_frame, justify = "center", font = ("Helvetica", 13), 
            state = "readonly", borderwidth = 1, relief = "solid"
            )
        self.acc_display.place(x = 72, y = 24, width = 60, height = 25)
        self.insert_to_entry(self.acc_display, 0, "000", False)

        self.alu_label = Label(
            self.window, text = "ALU", 
            font = ("Times", 14), bg = "#dddddd", 
            border = 1, relief = "solid"
            )
        self.alu_label.place(x = 420, y = 468, width = 70, height = 40)
        #-------------------------------------------------------------------------------------------------------------

        #process terminal --------------------------------------------------------------------------------------------
        self.procTerminal_frame = Frame(self.window)
        self.procTerminal_frame.place(x = 675, y = 485, width = 465, height = 160)

        self.procTerminal_display = Text(self.procTerminal_frame, state = DISABLED)
        self.procTerminal_display.place(x = 0, y = 0, width = 450, height = 160)
        self.insert_to_textbox(self.procTerminal_display, END, ">", False)

        self.procTerminal_yscrollbar = Scrollbar(self.procTerminal_frame, command = self.procTerminal_display.yview)
        self.procTerminal_yscrollbar.place(x = 450, y = 0, height = 160, width = 15)
        self.procTerminal_display['yscrollcommand'] = self.procTerminal_yscrollbar.set
        #-------------------------------------------------------------------------------------------------------------

        #buses -------------------------------------------------------------------------------------------------------
        to_alu_bus = Label(self.window, bg = "#bbbbbb")
        to_alu_bus.place(x = 430, y = 448, width = 20, height = 20)
        from_alu_bus = Label(self.window, bg = "#bbbbbb")
        from_alu_bus.place(x = 460, y = 448, width = 20, height = 20)

        from_output_bus_1 = Label(self.window, bg = "#bbbbbb")
        from_output_bus_1.place(x = 500, y = 90, width = 33, height = 20)
        from_output_bus_2 = Label(self.window, bg = "#bbbbbb")
        from_output_bus_2.place(x = 513, y = 110, width = 20, height = 140)

        from_input_bus_1 = Label(self.window, bg = "#bbbbbb")
        from_input_bus_1.place(x = 500, y = 610, width = 33, height = 20)
        from_input_bus_2 = Label(self.window, bg = "#bbbbbb")
        from_input_bus_2.place(x = 513, y = 448, width = 20, height = 162)

        general_ram_bus_1 = Label(self.window, bg = "#bbbbbb")
        general_ram_bus_1.place(x = 581, y = 448, width = 20, height = 50)
        general_ram_bus_2 = Label(self.window, bg = "#bbbbbb")
        general_ram_bus_2.place(x = 601, y = 478, width = 30, height = 20)
        general_ram_bus_3 = Label(self.window, bg = "#bbbbbb")
        general_ram_bus_3.place(x = 630, y = 70, width = 20, height = 428)

        for i in range(10):
            general_ram_bus_r = Label(self.window, bg = "#bbbbbb")
            general_ram_bus_r.place(x = 650, y = 40 * i + 70, width = 25, height = 20)
        #-------------------------------------------------------------------------------------------------------------

        #signals -----------------------------------------------------------------------------------------------------
        self.cpu_signal = Label(self.window, font = ("Times", 13), borderwidth = 1, relief = "solid")
        self.ram_signal = Label(self.window, font = ("Times", 13), borderwidth = 1, relief = "solid")
        self.pc_signal = Label(self.window, font = ("Times", 13), borderwidth = 1, relief = "solid")
        self.acc_signal = Label(self.window, font = ("Times", 13), borderwidth = 1, relief = "solid")
        self.aluOperation_label = Label(self.window, font = ("Times", 12), bg = "#ffffff")
        #-------------------------------------------------------------------------------------------------------------

        self.window.mainloop()

class assembler:
    def __init__(self, exception_handler):
        #asmssembly instructions as mnemonics
        self.asm_instrs = ["hlt", "dat", "add", "sub", "sta", "lda", "bra", "brz", "brp", "inp", "out"]

        self.exception_handler = exception_handler

    def check_for_int(self, instr):
            try:
                int(instr)
                return True
            except:
                return False

    def check_chr(self, character):
        chr_code = ord(character)
        if chr_code == 45:
            return True
        elif chr_code >= 48 and chr_code <= 57:
            return True
        elif chr_code >= 97 and chr_code <= 122:
            return True
        elif chr_code >= 65 and chr_code <= 90:
            return True
        elif chr_code == 32 or chr_code == 10:
            return True
        else:
            return False

    def instr_syntax_parser(self, listed_instr):
        if listed_instr == []:
            return False, None, None

        try:
            for item in listed_instr:
                for chr in item:
                    if self.check_chr(chr) == False:
                        return False, listed_instr, None
        except:
            return False, listed_instr, None

        #order and BNF checking---
        varRow = ["", "", ""]

        if listed_instr[0].lower() in self.asm_instrs:
            varRow[1] = listed_instr[0].upper() 
            if len(listed_instr) > 1:
                varRow[2] = listed_instr[1]
        elif len(listed_instr) > 1 and listed_instr[1].lower() in self.asm_instrs:
            varRow[1] = listed_instr[1].upper()
            if listed_instr[0] != "":
                varRow[0] = listed_instr[0]
            if len(listed_instr) > 2 and listed_instr[2] != "":
                varRow[2] = listed_instr[2]
        else:
            return False, listed_instr, None

        count = 0
        for item in varRow:
            if item.lower() in self.asm_instrs:
                count += 1
        if count > 1:
            return False, listed_instr, None

        return True, listed_instr, varRow

    def int_to_instr(self, integer):
        if integer < -9:
            return str(integer) 
        if integer < 0:
            return "-0" + str(0 - integer) 
        elif integer < 10:
            return "0" + str(integer) 
        else:
            return str(integer)

    def pad_instr(self, listed_instr):
        padded_instr = ""

        if listed_instr[0].lower() in self.asm_instrs:
            padded_instr += " " * 8
            padded_instr += listed_instr[0]
        elif len(listed_instr[0]) < 8:
            padded_instr += listed_instr[0]
            padded_instr += " " * (7 - len(listed_instr[0]))

        for i in range(1, len(listed_instr)):
            padded_instr = padded_instr + " " + listed_instr[i]
        return padded_instr

    def fuse_instr_and_var(self, instr, var):
        if var[0] == "-":
            return "-" + instr + var[1: ]
        else:
            return instr + var

    def translate_instr(self, instr):
        instr_type = instr[3 : 6]

        if instr_type == "HLT" or instr_type == "":
            return "000"
        elif instr_type == "INP":
            return "901"
        elif instr_type == "OUT":
            return "902"

        if instr[0] != "-":
            if len(instr) < 7:
                var = "00"
            else:
                var = instr[7: ]

        if instr_type == "DAT":
            if len(var) == 3:
                return var
            else:
                return self.fuse_instr_and_var("0", var)
        elif instr_type == "ADD":
            return self.fuse_instr_and_var("1", var)
        elif instr_type == "SUB":
            return self.fuse_instr_and_var("2", var)
        elif instr_type == "STA":
            return self.fuse_instr_and_var("3", var)
        elif instr_type == "LDA":
            return self.fuse_instr_and_var("5", var)
        elif instr_type == "BRA":
            return self.fuse_instr_and_var("6", var)
        elif instr_type == "BRZ":
            return self.fuse_instr_and_var("7", var)
        else: #BRP
            return self.fuse_instr_and_var("8", var)

    def assemble(self, code):
        try:
            self.varTable = []
            self.listed_code = []
            self.listed_code_ = []
            self.add_to_list = True

            for i in range(len(code)):
                line = split(" |\t", code[i])
                #filter out items in line that are "None"
                line = list(filter(None, line))
                if line != []:
                    status, despaced_line, varRow = self.instr_syntax_parser(line)
                    if status == False:
                        errorData = [f"'{''.join(line)}' on [line {i}] contains invalid syntax"]
                        self.exception_handler.set_error("SyntaxError", errorData)
                        raise self.exception_handler
                    else:
                        self.listed_code.append(despaced_line)
                        self.varTable.append(varRow)
                    self.listed_code_.append(despaced_line)
                
            varList = []
            i = 0
            for line in self.varTable:
                if line[0] != "" and self.check_for_int(line[0]) == False:
                    if line[2] == "":
                        varList.append([i, line[0], 0])
                    elif self.check_for_int(line[2]) == True:
                        varList.append([i, line[0], int(line[2])])
                    else:
                        varList.append([i, line[0], line[2]])
                i += 1

            for i in range(len(varList)):
                if self.check_for_int(varList[i][2]) == False:
                    found = False
                    for v in varList:
                        if v[1] == varList[i][2]:
                            varList[i][2] = v[0]
                            found = True
                    if found == False:
                        errorData = [f"'{self.varTable[i][2]}' not found --> [line {i}]"]
                        del self.varTable[varList[i][0]: ]
                        del self.listed_code[varList[i][0]: ]
                        self.exception_handler.set_error("VariableError", errorData)
                        raise self.exception_handler

            for i in range(len(self.varTable)):
                found = False
                v = 0
                if self.varTable[i][2] != "" and self.check_for_int(self.varTable[i][2]) == False:
                    while found == False and v < len(varList):
                        found = False
                        if varList[v][1] == self.varTable[i][2]:
                            self.varTable[i][2] = varList[v][0]
                            found = True
                        v += 1
                    if found == False:
                        errorData = [f"'{self.varTable[i][2]}' not found --> [line {i}]"]
                        del self.varTable[i: ]
                        del self.listed_code[i: ]
                        self.exception_handler.set_error("VariableError", errorData)
                        raise self.exception_handler

            padded_code = []
            i = 0
            while i < len(self.listed_code):
                padded_line = self.pad_instr(self.listed_code[i])
                padded_code.append(padded_line)
                i += 1
            while i < len(self.listed_code_):
                padded_line = self.pad_instr(self.listed_code_[i])
                padded_code.append(padded_line)
                i += 1
            
            assembly_code = []
            i = 0
            for line in self.varTable:
                assembly_code.append(self.int_to_instr(i) + " ")
                if line[1] == "INP" or line[1] == "OUT" or line[1] == "HLT":
                    assembly_code[-1] += line[1]
                else:
                    if line[2] == "":
                        assembly_code[-1] = assembly_code[-1] + line[1] + " 00"
                    else:
                        assembly_code[-1] = assembly_code[-1] + line[1] + " " + self.int_to_instr(int(line[2]))   
                i += 1
            if len(self.listed_code) < len(self.listed_code_):
                assembly_code.append(self.int_to_instr(i))

            machine_code = [self.translate_instr(line) for line in assembly_code]

            return padded_code, assembly_code, machine_code, False
        except exceptionHandler:
            return None, None, None, True

class FDE_cycle:
    def __init__(self, lmcMainSelf):
        self.lmcMainSelf = lmcMainSelf

    def idle_cycle(self):
        while self.lmcMainSelf.pause_status == True:
            sleep(0.1)
    
    def wait_Enter(self):
        def set_stop_wait_enter(): 
            self.stop_wait_enter = True

        self.stop_wait_enter = False
        self.lmcMainSelf.input_entry.bind("<Return>", lambda event: set_stop_wait_enter())

        while self.stop_wait_enter == False:
            sleep(0.1)
        self.lmcMainSelf.input_entry.unbind("<Return>")

    def get_speed(self):
        if self.lmcMainSelf.clockSpeed == 1:
            return 5, 1
        elif self.lmcMainSelf.clockSpeed == 2:
            return 1, 3
        elif self.lmcMainSelf.clockSpeed == 3:
            return 1, 8
        elif self.lmcMainSelf.clockSpeed == 4:
            return 1, 15
        else:
            return 1, 30
    
    def move_signal(self, widget, movement_data):
        movement_axis, start_pos, shift_amount, direction, destination = movement_data
        self.idle_cycle()
        if self.lmcMainSelf.reset_status == True:
            widget.place_forget()
            return False
        delay, speed_shiftAmount = self.get_speed()
        if direction == 1 and destination - start_pos - shift_amount - speed_shiftAmount < 0:
            if movement_axis == "x":
                widget.place_configure(x = destination)
            else: #y
                widget.place_configure(y = destination)
        elif direction == -1 and destination - start_pos - shift_amount - speed_shiftAmount > 0:
            if movement_axis == "x":
                widget.place_configure(x = destination)
            else: #y
                widget.place_configure(y = destination)
        else:
            shift_amount = shift_amount + (direction * speed_shiftAmount)
            if movement_axis == "x":
                widget.place_configure(x = start_pos + shift_amount)
            else: #y
                widget.place_configure(y = start_pos + shift_amount)
            sleep(delay / 1000)
            self.move_signal(widget, (movement_axis, start_pos, shift_amount, direction, destination))
    
    def increment_pc(self, address):
        movements_from_pc = [
                ("y", 282, 0, 1, 418), 
                ("x", 576, 0, -1, 425), 
                ("y", 418, 0, 1, 475)
            ]
        movements_to_pc = [
            ("x", 425, 0, 1, 455), 
            ("y", 475, 0, -1, 418), 
            ("x", 455, 0, 1, 576),
            ("y", 418, 0, -1, 282)
        ]

        for movement_data in movements_from_pc:
            if self.move_signal(self.lmcMainSelf.pc_signal, movement_data) == False:
                return 

        self.lmcMainSelf.pc_signal.configure(text = self.lmcMainSelf.int_to_instr(address + 1))
        self.lmcMainSelf.aluOperation_label.configure(text = "+1")
        self.lmcMainSelf.aluOperation_label.place(x = 460, y = 477, height = 20, width = 25)
        if self.lmcMainSelf.reset_status == True:
            self.lmcMainSelf.pc_signal.place_forget()
            return
        sleep(self.get_speed()[0] / 8)
        self.lmcMainSelf.aluOperation_label.place_forget()

        for movement_data in movements_to_pc:
            if self.move_signal(self.lmcMainSelf.pc_signal, movement_data) == False:
                return
        
        self.lmcMainSelf.pc_signal.place_forget()
        self.lmcMainSelf.pc_display.configure(state = NORMAL)
        self.lmcMainSelf.pc_display.delete(0, END)
        self.lmcMainSelf.pc_display.insert(0, self.lmcMainSelf.int_to_instr(self.lmcMainSelf.pc_count + 1))
        self.lmcMainSelf.update_pc_display() 
        self.lmcMainSelf.pc_display.configure(state = "readonly")
    
    def fetch_from_ram(self, column, row, address):
        movements_to_ram = [
            ("y", 282, 0, 1, 475), 
            ("x", 576, 0, 1, 626), 
            ("y", 475, 0, -1, 40 * row + 68), 
            ("x", 626, 0, 1, 45 * column + 690)
        ]
        movements_from_ram = [
            ("x", 45 * column + 690, 0, -1, 626), 
            ("y", 40 * row + 68, 0, 1, 475), 
            ("x", 626, 0, -1, 576), 
            ("y", 475, 0, -1, 360)
        ]

        self.lmcMainSelf.set_ram_access_type("Read")

        for movement_data in movements_to_ram:
            if self.move_signal(self.lmcMainSelf.ram_signal, movement_data) == False:
                return

        self.lmcMainSelf.ram_signal.configure(text = self.lmcMainSelf.RAM[address][0])
        sleep(self.get_speed()[0] / 10)

        for movement_data in movements_from_ram:
            if self.move_signal(self.lmcMainSelf.ram_signal, movement_data) == False:
                return
        
        self.lmcMainSelf.ram_signal.configure(text = self.lmcMainSelf.RAM[address][0])
        self.lmcMainSelf.ar_display.configure(state = NORMAL)
        self.lmcMainSelf.ar_display.delete(0, END)
        data = self.lmcMainSelf.RAM[address][0]
        if data[0] == "-":
            self.lmcMainSelf.ar_display.insert(0, self.lmcMainSelf.RAM[address][0][2: ])
        else:
            self.lmcMainSelf.ar_display.insert(0, self.lmcMainSelf.RAM[address][0][1: ])
        self.lmcMainSelf.ar_display.configure(state = "readonly")

        if self.move_signal(self.lmcMainSelf.ram_signal, ("y", 360, 0, -1, 321)) == False:
            return

        self.lmcMainSelf.ir_display.configure(state = NORMAL)
        self.lmcMainSelf.ir_display.delete(0, END)
        if data[0] == "-":
            self.lmcMainSelf.ir_display.insert(0, self.lmcMainSelf.RAM[address][0][1])
        else:
            self.lmcMainSelf.ir_display.insert(0, self.lmcMainSelf.RAM[address][0][0])
        self.lmcMainSelf.ir_display.configure(state = "readonly")
        
        self.lmcMainSelf.ram_signal.place_forget()

        self.lmcMainSelf.set_ram_access_type("None")

        sleep(self.get_speed()[0] / 5)
    
    def get_data_from_acc(self):
        acc_signal_value = self.lmcMainSelf.acc_display.get()
        self.lmcMainSelf.acc_signal.configure(text = acc_signal_value)
        self.lmcMainSelf.acc_signal.place(x = 508, y = 418, width = 30, height = 25)
        if self.move_signal(self.lmcMainSelf.acc_signal, ("x", 508, 0, -1, 425)) == False:
            return
        if self.move_signal(self.lmcMainSelf.acc_signal, ("y", 418, 0, 1, 475)) == False:
            return
    
    def add_data_at_addr(self, address, negitive):
        address = int(address)
        column = address % 10
        row = address // 10

        movements_to_ram = [
            ("y", 360, 0, 1, 475),
            ("x", 576, 0, 1, 626), 
            ("y", 475, 0, -1, 40 * row + 68), 
            ("x", 626, 0, 1, 45 * column + 690)
        ]
        movements_from_ram = [
            ("x", 45 * column + 690, 0, -1, 626), 
            ("y", 40 * row + 68, 0, 1, 475), 
            ("x", 626, 0, -1, 576), 
            ("y", 475, 0, -1, 418)
        ]
        movements_to_alu = [
            ("x", 576, 0, -1, 425), 
            ("y", 418, 0, 1, 475),
            ("x", 425, 0, 1, 456)
        ]

        self.lmcMainSelf.set_ram_access_type("Read")

        cpu_signal_value = self.lmcMainSelf.ar_display.get()
        self.lmcMainSelf.cpu_signal.configure(text = cpu_signal_value)
        self.lmcMainSelf.cpu_signal.place(x = 576, y = 360, width = 30, height = 25)

        for movement_data in movements_to_ram:
            if self.move_signal(self.lmcMainSelf.cpu_signal, movement_data) == False:
                return
        
        self.lmcMainSelf.cpu_signal.configure(text = self.lmcMainSelf.RAM[address][0])
        sleep(self.get_speed()[0] / 10)

        for movement_data in movements_from_ram:
            if self.move_signal(self.lmcMainSelf.cpu_signal, movement_data) == False:
                return

        self.lmcMainSelf.set_ram_access_type("None")
        
        acc_signal_thread = Thread(target = self.get_data_from_acc, daemon = False)
        acc_signal_thread.start()

        for movement_data in movements_to_alu:
            if self.move_signal(self.lmcMainSelf.cpu_signal, movement_data) == False:
                return

        if negitive == False:
            self.lmcMainSelf.aluOperation_label.configure(text = "+")
        else:
            self.lmcMainSelf.aluOperation_label.configure(text = "-")
        self.lmcMainSelf.aluOperation_label.place(x = 447, y = 501, height = 15, width = 15)
        
        sleep(self.get_speed()[0] / 10)
        self.lmcMainSelf.acc_signal.place_forget()
        self.lmcMainSelf.aluOperation_label.place_forget()

        acc_value = self.lmcMainSelf.acc_display.get()
        cpu_signal_value = self.lmcMainSelf.RAM[address][0]
        if negitive == False:
            acc_value = str(int(acc_value) + int(cpu_signal_value))
        else:
            acc_value = str(int(acc_value) - int(cpu_signal_value))

        if acc_value[0] == "-":
            if len(acc_value) == 2:
                acc_value = "-00" + acc_value[1: ]
            elif len(acc_value) == 3:
                acc_value = "-0" + acc_value[1: ]
        else:
            if len(acc_value) <= 2:
                acc_value = "0" + self.lmcMainSelf.nstr_to_instr(acc_value)

        self.lmcMainSelf.cpu_signal.configure(text = acc_value)

        if self.move_signal(self.lmcMainSelf.cpu_signal, ("y", 475, 0, -1, 418)) == False:
            return
        if self.move_signal(self.lmcMainSelf.cpu_signal, ("x", 456, 0, 1, 508)) == False:
            return

        self.lmcMainSelf.cpu_signal.place_forget()

        self.lmcMainSelf.insert_to_entry(self.lmcMainSelf.acc_display, 0, acc_value, True)

    def store_to_addr(self, address):
        address = int(address)
        column = address % 10
        row = address // 10
        
        movements_to_ram = [
            ("x", 508, 0, 1, 576),
            ("y", 360, 0, 1, 475),
            ("x", 576, 0, 1, 626),
            ("y", 475, 0, -1, 40 * row + 68), 
            ("x", 626, 0, 1, 45 * column + 690)
        ]

        self.lmcMainSelf.set_ram_access_type("Write")

        self.lmcMainSelf.cpu_signal.configure(text = self.lmcMainSelf.acc_display.get())
        self.lmcMainSelf.cpu_signal.place(x = 508, y = 418, width = 30, height = 25)
        
        for movement_data in movements_to_ram:
            if self.move_signal(self.lmcMainSelf.cpu_signal, movement_data) == False:
                return
        
        self.lmcMainSelf.cpu_signal.place_forget()

        memoryLocation = self.lmcMainSelf.RAM[address][1]
        memoryLocation.delete(0, END)
        memoryLocation.insert(0, self.lmcMainSelf.acc_display.get())
        self.lmcMainSelf.RAM[address][0] = self.lmcMainSelf.acc_display.get()

        self.lmcMainSelf.set_ram_access_type("None")
    
    def load_from_addr(self, address):
        address = int(address)
        column = address % 10
        row = address // 10

        movements_to_ram = [
            ("y", 360, 0, 1, 475), 
            ("x", 576, 0, 1, 626), 
            ("y", 475, 0, -1, 40 * row + 68), 
            ("x", 626, 0, 1, 45 * column + 690)
        ]
        movements_from_ram = [
            ("x", 45 * column + 690, 0, -1, 626), 
            ("y", 40 * row + 68, 0, 1, 475), 
            ("x", 626, 0, -1, 576), 
            ("y", 475, 0, -1, 418), 
            ("x", 576, 0, -1, 508)
        ]

        self.lmcMainSelf.set_ram_access_type("Read")

        self.lmcMainSelf.cpu_signal.configure(text = self.lmcMainSelf.ar_display.get())
        self.lmcMainSelf.cpu_signal.place(x = 576, y = 360, width = 30, height = 25)
        
        for movement_data in movements_to_ram:
            if self.move_signal(self.lmcMainSelf.cpu_signal, movement_data) == False:
                return

        self.lmcMainSelf.cpu_signal.configure(text = self.lmcMainSelf.RAM[address][0])
        sleep(self.get_speed()[0] / 10)

        for movement_data in movements_from_ram:
            if self.move_signal(self.lmcMainSelf.cpu_signal, movement_data) == False:
                return

        self.lmcMainSelf.cpu_signal.place_forget()

        self.lmcMainSelf.insert_to_entry(self.lmcMainSelf.acc_display, 0, self.lmcMainSelf.RAM[address][0], True)

        self.lmcMainSelf.set_ram_access_type("None")
    
    def branch_to_addr(self, address):
        self.lmcMainSelf.cpu_signal.configure(text = address)
        self.lmcMainSelf.cpu_signal.place(x = 576, y = 360, width = 30, height = 25) 
        if self.move_signal(self.lmcMainSelf.cpu_signal, ("y", 360, 0, -1, 282)) == False:
            return
        self.lmcMainSelf.cpu_signal.place_forget()

        self.lmcMainSelf.pc_display.configure(state = "normal")
        self.lmcMainSelf.pc_display.delete(0, END)
        self.lmcMainSelf.pc_display.insert(0, address)
        self.lmcMainSelf.update_pc_display() 
    
    def input_data_to_acc(self):
        try:
            self.lmcMainSelf.input_entry.configure(state = NORMAL)
            self.lmcMainSelf.input_entry.delete(0, END)

            self.wait_Enter()
            user_input = self.lmcMainSelf.input_entry.get()
            if self.lmcMainSelf.check_for_int(user_input) == False or int(user_input) >= 1000 or int(user_input) <= -1000:
                errorData = [f"'{user_input}' is not a valid input", "please input a different value"]
                self.lmcMainSelf.exception_handler.set_error("InputError", errorData)
                raise self.lmcMainSelf.exception_handler

            self.lmcMainSelf.input_entry.configure(state = "readonly")
            if user_input[0] != "-":
                user_input = self.lmcMainSelf.nstr_to_instr(user_input)
                if len(user_input) == 2:
                    user_input = "0" + user_input
            else:
                user_input = str(int(user_input))
                if len(user_input) == 2:
                    user_input = "-00" + user_input[1: ]
                elif len(user_input) == 3:
                    user_input = "-0" + user_input[1: ]

            self.lmcMainSelf.cpu_signal.configure(text = user_input)
            self.lmcMainSelf.cpu_signal.place(x = 488, y = 607, width = 30, height = 25)
            if self.move_signal(self.lmcMainSelf.cpu_signal, ("x", 488, 0, 1, 508)) == False:
                return
            if self.move_signal(self.lmcMainSelf.cpu_signal, ("y", 607, 0, -1, 418)) == False:
                return
            self.lmcMainSelf.cpu_signal.place_forget()

            self.lmcMainSelf.insert_to_entry(self.lmcMainSelf.acc_display, 0, user_input, True)
        except exceptionHandler:
            errorMessage = self.lmcMainSelf.exception_handler.get_errorMessage()
            self.lmcMainSelf.procTerminal_print(errorMessage)
            errorType = self.lmcMainSelf.exception_handler.errorType
            if errorType == "InputError":
                self.input_data_to_acc()

    def output_data_from_acc(self, acc_value):
        self.lmcMainSelf.cpu_signal.configure(text = acc_value)
        self.lmcMainSelf.cpu_signal.place(x = 508, y = 418, width = 30, height = 25)

        if self.move_signal(self.lmcMainSelf.cpu_signal, ("y", 418, 0, -1, 87)) == False:
            return
        if self.move_signal(self.lmcMainSelf.cpu_signal, ("x", 508, 0, -1, 488)) == False:
            return
        self.lmcMainSelf.cpu_signal.place_forget()

        self.lmcMainSelf.insert_to_textbox(self.lmcMainSelf.output_display, END, str(int(acc_value)) + "\n", False)

    def decode_and_execute_instr(self, instruction, data):
        try:
            acc_value = self.lmcMainSelf.acc_display.get()

            if int(instruction) > 9 or instruction == "4":
                errorData = [f"'{instruction}' in [memory location {self.lmcMainSelf.pc_count}] is not a valid instruction"]
                self.lmcMainSelf.exception_handler.set_error("InstructionError", errorData)
                raise self.lmcMainSelf.exception_handler
            elif instruction == "0": #halt
                return True
            elif instruction == "1": #add
                self.add_data_at_addr(data, False)
                return False
            elif instruction == "2": #subtract
                self.add_data_at_addr(data, True)
                return False
            elif instruction == "3": #store data to address
                self.store_to_addr(data)
                return False
            elif instruction == "5": #load data at address
                self.load_from_addr(data)
                return False
            elif instruction == "6": #branch always to address
                self.branch_to_addr(data)
                return False
            elif instruction == "7": #branch if zero (in accumilator) to address
                if acc_value == "000":
                    self.branch_to_addr(data)
                return False
            elif instruction == "8": #branch if positive (value in accumilator) to address
                if int(acc_value) >= 0:
                    self.branch_to_addr(data)
                return False
            elif instruction == "9": #INP / OUT
                if data == "01": #input data into accumilator
                    self.input_data_to_acc()
                elif data == "02": #output data in accumilator 
                    self.output_data_from_acc(acc_value)
                return False
        except exceptionHandler:
            errorMessage = self.exception_handler.get_errorMessage()
            self.lmcMainSelf.procTerminal_print(errorMessage)
    
    def start(self):
        self.lmcMainSelf.procTerminal_print(["FDE cycle started..."])

        termination = False
        while termination == False and self.lmcMainSelf.reset_status == False:
            #fetch phase -------------------------------------------------------------------------------------------------
            address = self.lmcMainSelf.pc_count
            column = address % 10
            row = address // 10

            self.lmcMainSelf.ram_signal.configure(text = self.lmcMainSelf.int_to_instr(address))
            self.lmcMainSelf.ram_signal.place(x = 576, y = 282, width = 30, height = 25)
            self.lmcMainSelf.pc_signal.configure(text = self.lmcMainSelf.int_to_instr(address))
            self.lmcMainSelf.pc_signal.place(x = 576, y = 282, width = 30, height = 25)

            pc_thread = Thread(target = self.increment_pc, args = (address, ), daemon = False)
            pc_thread.start()

            self.fetch_from_ram(column, row, address)
            #-------------------------------------------------------------------------------------------------------------

            #decode and execute phase ------------------------------------------------------------------------------------
            if self.lmcMainSelf.reset_status == False:
                instr = self.lmcMainSelf.ir_display.get()
                data = self.lmcMainSelf.ar_display.get()
                termination = self.decode_and_execute_instr(instr, data)
            #-------------------------------------------------------------------------------------------------------------

        self.lmcMainSelf.control_type = 0
        self.lmcMainSelf.pc_display.configure(state = NORMAL)
        self.lmcMainSelf.control_button.configure(text = "Run")

        self.lmcMainSelf.procTerminal_print(["FDE cycle halted"])

lmc = LMC()
lmc.start()
