from tkinter import *
from threading import Thread
from time import sleep
from keyboard import wait
from re import split

window = Tk()
window.title("Little Man Computer")
window.geometry("1150x655")

def assemble_to_ram():
    def assemble(code):
        def line_syntax_parser(line):
            def check_chr(chr):
                chr = ord(chr)
                if chr == 45:
                    return True
                elif chr >= 48 and chr <= 57:
                    return True
                elif chr >= 97 and chr <= 122:
                    return True
                elif chr >= 65 and chr <= 90:
                    return True
                elif chr == 32 or chr == 10:
                    return True
                else:
                    return False

            if line == []:
                return False, None, None

            try:
                for item in line:
                    for chr in item:
                        if check_chr(chr) == False:
                            return False, line, None
            except:
                return False, line, None

            #order and BNF checking---
            varRow = ["", "", ""]

            if line[0].lower() in MNCS:
                varRow[1] = line[0].upper() 
                if len(line) > 1:
                    varRow[2] = line[1]
            elif len(line) > 1 and line[1].lower() in MNCS:
                varRow[1] = line[1].upper()
                if line[0] != "":
                    varRow[0] = line[0]
                if len(line) > 2 and line[2] != "":
                    varRow[2] = line[2]
            else:
                return False, line, None

            count = 0
            for item in varRow:
                if item.lower() in MNCS:
                    count += 1
            if count > 1:
                return False, line, None

            return True, line, varRow

        def int_to_padstring(number):
            if number < -9:
                return str(number) 
            if number < 0:
                return "-0" + str(0 - number) 
            elif number < 10:
                return "0" + str(number) 
            else:
                return str(number)

        def pad_line(line):
            padded_line = ""

            if line[0].lower() in MNCS:
                padded_line += " " * 8
                padded_line += line[0]
            elif len(line[0]) < 8:
                padded_line += line[0]
                padded_line += " " * (7 - len(line[0]))

            for i in range(1, len(line)):
                padded_line = padded_line + " " + line[i]
            return padded_line

        def translate_line(line):
            def fuse_instruction_and_var(instruction, variable):
                if variable[0] == "-":
                    return "-" + instruction + variable[1: ]
                else:
                    return instruction + variable
            instruction = line[3 : 6]

            if instruction == "HLT" or instruction == "":
                return "000"
            elif instruction == "INP":
                return "901"
            elif instruction == "OUT":
                return "902"

            if line[0] != "-":
                if len(line) < 7:
                    variable = "00"
                else:
                    variable = line[7: ]

            if instruction == "DAT":
                if len(variable) == 3:
                    return variable
                else:
                    return fuse_instruction_and_var("0", variable)
            elif instruction == "ADD":
                return fuse_instruction_and_var("1", variable)
            elif instruction == "SUB":
                return fuse_instruction_and_var("2", variable)
            elif instruction == "STA":
                return fuse_instruction_and_var("3", variable)
            elif instruction == "LDA":
                return fuse_instruction_and_var("5", variable)
            elif instruction == "BRA":
                return fuse_instruction_and_var("6", variable)
            elif instruction == "BRZ":
                return fuse_instruction_and_var("7", variable)
            else: #BRP
                return fuse_instruction_and_var("8", variable)
            

        #mnemonics
        MNCS = ["hlt", "dat", "add", "sub", "sta", "lda", "bra", "brz", "brp", "inp", "out"]

        varTable = []
        listed_code = []
        listed_code_ = []
        add_to_list = True
        for line in code:
            line = split(" |\t", line)
            line = list(filter(None, line))
            if line != []:
                status, despaced_line, varRow = line_syntax_parser(line)
                if status == False:
                    errorMessage = f"SyntaxError: '{''.join(line)}' contains invalid syntax"
                    insert_to_textbox(process_box, END, errorMessage, False)
                    add_to_list = False
                elif add_to_list == True:
                    listed_code.append(despaced_line)
                    varTable.append(varRow)
                listed_code_.append(despaced_line)
            
        varList = []
        i = 0
        for line in varTable:
            if line[0] != "" and check_number(line[0]) == False:
                if line[2] == "":
                    varList.append([i, line[0], 0])
                elif check_number(line[2]) == True:
                    varList.append([i, line[0], int(line[2])])
                else:
                    varList.append([i, line[0], line[2]])
            i += 1

        for i in range(len(varList)):
            if check_number(varList[i][2]) == False:
                found = False
                for v in varList:
                    if v[1] == varList[i][2]:
                        varList[i][2] = v[0]
                        found = True
                if found == False:
                    errorMessage = f"VariableError: '{varTable[i][2]}' not found --> [line{varList[i][0]}]"
                    insert_to_textbox(process_box, END, errorMessage, False)
                    del varTable[varList[i][0]: ]
                    del listed_code[varList[i][0]: ]
                    break

        for i in range(len(varTable)):
            found = False
            v = 0
            if varTable[i][2] != "" and check_number(varTable[i][2]) == False:
                while found == False and v < len(varList):
                    found = False
                    if varList[v][1] == varTable[i][2]:
                        varTable[i][2] = varList[v][0]
                        found = True
                    v += 1
                if found == False:
                    errorMessage = f"VariableError: '{varTable[i][2]}' not found --> [line{varList[i][0]}]"
                    insert_to_textbox(process_box, END, errorMessage, False)
                    del varTable[i: ]
                    del listed_code[i: ]
                    break 

        padded_code = []
        i = 0
        while i < len(listed_code):
            padded_line = pad_line(listed_code[i])
            padded_code.append(padded_line)
            i += 1
        while i < len(listed_code_):
            padded_line = pad_line(listed_code_[i])
            padded_code.append(padded_line)
            i += 1
        
        assembly_code = []
        i = 0
        for line in varTable:
            assembly_code.append(int_to_padstring(i) + " ")
            if line[1] == "INP" or line[1] == "OUT" or line[1] == "HLT":
                assembly_code[-1] += line[1]
            else:
                if line[2] == "":
                    assembly_code[-1] = assembly_code[-1] + line[1] + " 00"
                else:
                    assembly_code[-1] = assembly_code[-1] + line[1] + " " + int_to_padstring(int(line[2]))   
            i += 1
        if len(listed_code) < len(listed_code_):
            assembly_code.append(int_to_padstring(i))

        machine_code = [translate_line(line) for line in assembly_code]

        return padded_code, assembly_code, machine_code

    global machine_code

    code = code_terimnal.get("1.0", END).split("\n")

    padded_code, assembly_code, machine_code = assemble(code)

    #update code_terminal -----------------------------------------
    code_terimnal.delete("1.0", END)
    for line in padded_code:
        code_terimnal.insert(END, line + "\n")
    code_terimnal.config(state = DISABLED)
    code_terimnal.config(state = NORMAL)
    #------------------------------------------------------------

    #update A_terminal -----------------------------------------
    A_terminal.config(state = NORMAL)
    A_terminal.delete("1.0", END)
    for line in assembly_code:
        A_terminal.insert(END, line + "\n")
    A_terminal.config(state = DISABLED)
    #------------------------------------------------------------

    Reset_command()

def FDE_cycle():
    def idle_cycle():
            while pause_status == True:
                sleep(0.1)
    
    def get_speed():
        if speed == 1:
            return 5, 1
        elif speed == 2:
            return 1, 3
        elif speed == 3:
            return 1, 8
        elif speed == 4:
            return 1, 15
        else:
            return 1, 30
    
    def move_x(widget, start_x, x_shift, x_direction, destination):
        idle_cycle()
        if reset_status == True:
            widget.place_forget()
            return False
        delay, shift = get_speed()
        if x_direction == 1 and destination - start_x - x_shift - shift < 0:
            widget.place_configure(x = destination)
        elif x_direction == -1 and destination - start_x - x_shift - shift > 0:
            widget.place_configure(x = destination)
        else:
            x_shift = x_shift + (x_direction * shift)
            widget.place_configure(x = start_x + x_shift)
            sleep(delay/1000)
            move_x(widget, start_x, x_shift, x_direction, destination)
    
    def move_y(widget, start_y, y_shift, y_direction, destination):
        idle_cycle()
        if reset_status == True:
            widget.place_forget()
            return False
        delay, shift = get_speed()
        if y_direction == 1 and destination - start_y - y_shift - shift < 0:
            widget.place_configure(y = destination)
        elif y_direction == -1 and destination - start_y - y_shift - shift > 0:
            widget.place_configure(y = destination)
        else:
            y_shift = y_shift + (y_direction * shift)
            widget.place_configure(y = start_y + y_shift)
            sleep(delay / 1000)
            move_y(widget, start_y, y_shift, y_direction, destination)
    
    def fetch_line(address): 
        def pc_function():
            if move_y(pc_signal, 282, 0, 1, 418) == False:
                return 
            if move_x(pc_signal, 576, 0, -1, 425) == False:
                return
            if move_y(pc_signal, 418, 0, 1, 475) == False:
                return
            pc_signal.configure(text = int_to_padstring(address + 1))
            alu_operation.configure(text = "+1")
            alu_operation.place(x = 460, y = 477, height = 20, width = 25)
            if reset_status == True:
                pc_signal.place_forget()
                return
            sleep(get_speed()[0] / 8)
            alu_operation.place_forget()
            if move_x(pc_signal, 425, 0, 1, 455) == False:
                return
            if move_y(pc_signal, 475, 0, -1, 418) == False:
                return
            if move_x(pc_signal, 455, 0, 1, 576) == False:
                return 
            if move_y(pc_signal, 418, 0, -1, 282) == False:
                return
            pc_signal.place_forget()
            pc_count = address + 1
            pc_box.configure(state = "normal")
            pc_box.delete(0, END)
            pc_box.insert(0, int_to_padstring(pc_count))
            update_pc_box(None) 
            pc_box.configure(state = "readonly")
        
        def ram_function(column, row):
            if move_y(ram_signal, 282, 0, 1, 475) == False:
                return
            if move_x(ram_signal, 576, 0, 1, 626) == False:
                return
            if move_y(ram_signal, 475, 0, -1, 40 * row + 68) == False:
                return
            if move_x(ram_signal, 626, 0, 1, 45 * column + 690) == False:
                return
            ram_signal.configure(text = Ram[address][0])
            sleep(get_speed()[0] / 10)
            if move_x(ram_signal, 45 * column + 690, 0, -1, 626) == False:
                return
            if move_y(ram_signal, 40 * row + 68, 0, 1, 475) == False:
                return
            if move_x(ram_signal, 626, 0, -1, 576) == False:
                return
            if move_y(ram_signal, 475, 0, -1, 360) == False:
                return
            
            ram_signal.configure(text = Ram[address][0])
            ar_box.configure(state = "normal")
            ar_box.delete(0, END)
            data = Ram[address][0]
            if data[0] == "-":
                ar_box.insert(0, Ram[address][0][2: ])
            else:
                ar_box.insert(0, Ram[address][0][1: ])
            ar_box.configure(state = "readonly")
            if move_y(ram_signal, 360, 0, -1, 321) == False:
                return

            ir_box.configure(state = "normal")
            ir_box.delete(0, END)
            if data[0] == "-":
                ir_box.insert(0, Ram[address][0][1])
            else:
                ir_box.insert(0, Ram[address][0][0])
            ir_box.configure(state = "readonly")
            ram_signal.place_forget()

            sleep(get_speed()[0] / 5)

        global speed, Ram, pc_count

        address = pc_count
        column = address % 10
        row = address // 10

        ram_signal.configure(text = int_to_padstring(address))
        ram_signal.place(x = 576, y = 282, width = 30, height = 25)
        pc_signal.configure(text = int_to_padstring(address))
        pc_signal.place(x = 576, y = 282, width = 30, height = 25)

        pc_thread = Thread(target = pc_function)
        pc_thread.start()

        ram_function(column, row)
        
    def decode_and_execute_line(instruction, data):
        def add_data(address, negitive):
            def accumulator_signal_function():
                accumulator_signal_value = accumulator_box.get()
                accumulator_signal.configure(text = accumulator_signal_value)
                accumulator_signal.place(x = 508, y = 418, width = 30, height = 25)
                if move_x(accumulator_signal, 508, 0, -1, 425) == False:
                    return
                if move_y(accumulator_signal, 418, 0, 1, 475) == False:
                    return

            address = int(address)
            column = address % 10
            row = address // 10

            cpu_signal_value = ar_box.get()
            cpu_signal.configure(text = cpu_signal_value)
            cpu_signal.place(x = 576, y = 360, width = 30, height = 25)
            
            if move_y(cpu_signal, 360, 0, 1, 475) == False:
                return
            if move_x(cpu_signal, 576, 0, 1, 626) == False:
                return
            if move_y(cpu_signal, 475, 0, -1, 40 * row + 68) == False:
                return
            if move_x(cpu_signal, 626, 0, 1, 45 * column + 690) == False:
                return
            cpu_signal.configure(text = Ram[address][0])
            sleep(get_speed()[0] / 10)
            if move_x(cpu_signal, 45 * column + 690, 0, -1, 626) == False:
                return
            if move_y(cpu_signal, 40 * row + 68, 0, 1, 475) == False:
                return
            if move_x(cpu_signal, 626, 0, -1, 576) == False:
                return
            if move_y(cpu_signal, 475, 0, -1, 418) == False:
                return
            accumulator_signal_thread = Thread(target = accumulator_signal_function)
            accumulator_signal_thread.start()

            if move_x(cpu_signal, 576, 0, -1, 425) == False:
                return
            if move_y(cpu_signal, 418, 0, 1, 475) == False:
                return
            if move_x(cpu_signal, 425, 0, 1, 456) == False:
                return

            if negitive == False:
                alu_operation.configure(text = "+")
            else:
                alu_operation.configure(text = "-")
            alu_operation.place(x = 447, y = 501, height = 15, width = 15)
            
            sleep(get_speed()[0] / 10)
            accumulator_signal.place_forget()
            alu_operation.place_forget()

            accumulator_value = accumulator_box.get()
            cpu_signal_value = Ram[address][0]
            if negitive == False:
                accumulator_value = str(int(accumulator_value) + int(cpu_signal_value))
            else:
                accumulator_value = str(int(accumulator_value) - int(cpu_signal_value))

            if accumulator_value[0] == "-":
                if len(accumulator_value) == 2:
                    accumulator_value = "-00" + accumulator_value[1: ]
                elif len(accumulator_value) == 3:
                    accumulator_value = "-0" + accumulator_value[1: ]
            else:
                if len(accumulator_value) <= 2:
                    accumulator_value = "0" + nstr_to_padstring(accumulator_value)

            cpu_signal.configure(text = accumulator_value)
            if move_y(cpu_signal, 475, 0, -1, 418) == False:
                return
            if move_x(cpu_signal, 456, 0, 1, 508) == False:
                return
            cpu_signal.place_forget()

            insert_to_entry(accumulator_box, 0, accumulator_value, True)
        
        def store_to_address(address):
            address = int(address)
            column = address % 10
            row = address // 10
            memoryLocation = Ram[address][1]

            cpu_signal.configure(text = accumulator_box.get())
            cpu_signal.place(x = 508, y = 418, width = 30, height = 25) #accumulator at (508, 418) 
            if move_x(cpu_signal, 508, 0, 1, 576) == False:
                return
            if move_y(cpu_signal, 360, 0, 1, 475) == False:
                return
            if move_x(cpu_signal, 576, 0, 1, 626) == False:
                return
            if move_y(cpu_signal, 475, 0, -1, 40 * row + 68) == False:
                return
            if move_x(cpu_signal, 626, 0, 1, 45 * column + 690) == False:
                return
            cpu_signal.place_forget()

            memoryLocation.delete(0, END)
            memoryLocation.insert(0, accumulator_box.get())
            Ram[address][0] = accumulator_box.get()
        
        def load_address(address):
            address = int(address)
            column = address % 10
            row = address // 10

            cpu_signal.configure(text = ar_box.get())
            cpu_signal.place(x = 576, y = 360, width = 30, height = 25)
            
            if move_y(cpu_signal, 360, 0, 1, 475) == False:
                return
            if move_x(cpu_signal, 576, 0, 1, 626) == False:
                return
            if move_y(cpu_signal, 475, 0, -1, 40 * row + 68) == False:
                return
            if move_x(cpu_signal, 626, 0, 1, 45 * column + 690) == False:
                return
            cpu_signal.configure(text = Ram[address][0])
            sleep(get_speed()[0] / 10)
            if move_x(cpu_signal, 45 * column + 690, 0, -1, 626) == False:
                return
            if move_y(cpu_signal, 40 * row + 68, 0, 1, 475) == False:
                return
            if move_x(cpu_signal, 626, 0, -1, 576) == False:
                return
            if move_y(cpu_signal, 475, 0, -1, 418) == False:
                return
            if move_x(cpu_signal, 576, 0, -1, 508) == False:
                return
            cpu_signal.place_forget()

            insert_to_entry(accumulator_box, 0, Ram[address][0], True)
        
        def branch_line(address):
            cpu_signal.configure(text = address) #ar - 576, 360
            cpu_signal.place(x = 576, y = 360, width = 30, height = 25) #pc - 576, 282
            if move_y(cpu_signal, 360, 0, -1, 282) == False:
                return
            cpu_signal.place_forget()
            pc_box.configure(state = "normal")
            pc_box.delete(0, END)
            pc_box.insert(0, address)
            update_pc_box(None) 
        
        def input_data():
            input_box.configure(state = "normal")
            input_box.delete(0, END)
            valid_input = False
            while valid_input == False:
                wait("Enter")
                user_input = input_box.get()
                if check_for_int(user_input) == True and int(user_input) < 1000 and int(user_input) > -1000:
                    valid_input = True
                else:
                    errorMessage = f"InputError: '{user_input}' is not a valid input"
                    insert_to_textbox(process_box, END, errorMessage, False)
                    insert_to_entry(input_box, None, False, True)
            input_box.configure(state = "readonly")
            if user_input[0] != "-":
                user_input = nstr_to_padstring(user_input)
                if len(user_input) == 2:
                    user_input = "0" + user_input
            else:
                user_input = str(int(user_input))
                if len(user_input) == 2:
                    user_input = "-00" + user_input[1: ]
                elif len(user_input) == 3:
                    user_input = "-0" + user_input[1: ]
            cpu_signal.configure(text = user_input)
            cpu_signal.place(x = 508, y = 418, width = 30, height = 25)
            if move_x(cpu_signal, 488, 0, 1, 508) == False:
                return
            if move_y(cpu_signal, 607, 0, -1, 418) == False:
                return
            cpu_signal.place_forget()

            insert_to_entry(accumulator_box, 0, user_input, True)

        def output_data(accumulator_value):
            cpu_signal.configure(text = accumulator_value)
            cpu_signal.place(x = 508, y = 418, width = 30, height = 25)

            if move_y(cpu_signal, 418, 0, -1, 87) == False:
                return
            if move_x(cpu_signal, 508, 0, -1, 488) == False:
                return
            cpu_signal.place_forget()

            insert_to_textbox(output_box, END, str(int(accumulator_value)) + "\n", False)

        accumulator_value = accumulator_box.get()

        if int(instruction) > 9 or instruction == "4":
            errorMessage = f"InstructionError: '{instruction}' is not a valid instruction"
            insert_to_textbox(process_box, END, errorMessage, False)
            return True
        elif instruction == "0":
            return True
        elif instruction == "1":
            add_data(data, False)
            return False
        elif instruction == "2":
            add_data(data, True)
            return False
        elif instruction == "3":
            store_to_address(data)
            return False
        elif instruction == "5":
            load_address(data)
            return False
        elif instruction == "6":
            branch_line(data)
            return False
        elif instruction == "7":
            if accumulator_value == "000":
                branch_line(data)
            return False
        elif instruction == "8":
            if int(accumulator_value) >= 0:
                branch_line(data)
            return False
        elif instruction == "9":
            if data == "01":
                input_data()
            else:
                output_data(accumulator_value)
            return False
        
    global Ram, pc_count, control_type

    termination = False
    while termination == False and reset_status == False:
        #fetch
        address = pc_count
        fetch_line(address)
        #decode and execute
        if reset_status == False:
            instruction = ir_box.get()
            data = ar_box.get()
            termination = decode_and_execute_line(instruction, data)
    control_type = 0
    pc_box.configure(state = "normal")
    Control_button.configure(text = "Run")

def pause_code():
    global pause_status
    if pause_status == False:
        pause_status = True
    else:
        pause_status = False

def Control_command():
    global control_type, reset_status
    pc_box.configure(state = "normal")
    update_pc_box(None) 
    pc_box.configure(state = "readonly")
    if control_type == 0:
        control_type = 1
        Control_button.configure(text = "Pause")
        reset_status = False
        pc_box.configure(state = "readonly")
        FDE_thread = Thread(target = FDE_cycle)
        FDE_thread.start()
    elif control_type == 1:
        control_type = 2
        Control_button.configure(text = "Play")
        pause_code()
    else:
        control_type = 1
        Control_button.configure(text = "Pause")
        pause_code()

def Reset_command():
    global control_type, reset_status, pause_status, pc_count, machine_code, Ram

    #update RAM--------------------------------------------------
    for i in range(100):
        Ram[i][1].delete(0, END)
        if i < len(machine_code):
            Ram[i][0] = machine_code[i]
            Ram[i][1].insert(0, machine_code[i])
        else:
            Ram[i][0] = "000"
            Ram[i][1].insert(0, "000")
    #------------------------------------------------------------

    reset_status = True
    pause_status = False
    control_type = 0

    pc_box.configure(state = "normal")
    pc_box.delete(0, END)
    pc_box.insert(0, int_to_padstring(0))
    update_pc_box(None) 

    Control_button.configure(text = "Run")

    insert_to_entry(accumulator_box, 0, "000", True)
    insert_to_entry(input_box, None, False, True)
    insert_to_entry(ir_box, None, False, True)
    insert_to_entry(ar_box, None, False, True)
    insert_to_textbox(output_box, None, False, True)

def Adjust_speed(adjustment):
    global speed
    
    adjusted_speed = speed + adjustment

    if adjusted_speed > 5:
        speed = 5
    elif adjusted_speed < 1:
        speed = 1
    else:
        speed = adjusted_speed

    insert_to_entry(speed_box, 0, "speed " + str(speed), True)

def check_for_int(line):
        try:
            int(line)
        except:
            return False
        return True

def int_to_padstring(number):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)

def nstr_to_padstring(number):
    number = int(number)
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)

def check_number(number):
    try:
        int(number)
        return True
    except:
        return False

def update_ML(event, i):
    global Ram

    line = event.widget.get()
    if line == "-000":
        line = "000"
    elif check_for_int(line) == False or len(line) == 0 or int(line) > 999:
        line = Ram[i][0]
    elif line[0] == "-":
        if len(line) == 2:
            line = "-00" + line
        elif len(line) == 3:
            line = "-0" + line
    else:
        if len(line) == 1:
            line = "00" + line
        elif len(line) == 2:
            line = "0" + line

    Ram[i][0] = line

    event.widget.delete(0, END)
    event.widget.insert(0, line)
    
def update_pc_box(event):
    global pc_count, Ram

    line = pc_box.get()
    if check_for_int(line) == False or len(line) == 0 or line[0] == "-" or int(line) > 99:
        line = int_to_padstring(pc_count)
    elif int(line) != pc_count:
        Ram[pc_count][2].configure(bg = "#f0f0f0")
        pc_count = int(line)

    pc_box.delete(0, END)
    pc_box.insert(0, nstr_to_padstring(line))

    Ram[pc_count][2].configure(bg = "#bbbbbb")

def insert_to_textbox(widget, index, text, clear):
    widget.configure(state = NORMAL)
    if clear == True:
        widget.delete(1.0, END)
    if text != False:
        widget.insert(index, text)
    widget.configure(state = DISABLED)

def insert_to_entry(widget, index, text, clear):
    widget.configure(state = NORMAL)
    if clear == True:
        widget.delete(0, END)
    if text != False:
        widget.insert(index, text)
    widget.configure(state = "readonly")

#handling elements----------------------------------------------------------------------------------
code_terimnal = Text(window, height = 12, width = 40, borderwidth = 1, relief = "solid")
code_terimnal.place(x = 10, y = 10, width = 200, height = 600)

A_terminal = Text(window, height = 12, width = 40, borderwidth = 1, relief = "solid")
A_terminal.place(x = 220, y = 10, width = 150, height = 600)
A_terminal.config(state = DISABLED)

ATR_button = Button(
    window, text = "Assmeble to ram", font = ("Helvetica", 13),
    command = assemble_to_ram
    )
ATR_button.place(x = 10, y = 620, width = 135, height = 25)

global control_type, pause_status
pause_status = False
control_type = 0
Control_button = Button(
    window, text = "Run", font = ("Helvetica", 13),
    command = Control_command
    )
Control_button.place(x = 155, y = 620, width = 55, height = 25)

global reset_status
reset_status = False
Reset_button = Button(
    window, text = "Reset", font = ("Helvetica", 13),
    command = Reset_command
    )
Reset_button.place(x = 220, y = 620, width = 55, height = 25)

global speed
speed = 1
speed_box = Entry(window, font = ("Helvetica", 11), state = "readonly")
speed_box.place(x = 300, y = 620, width = 55, height = 25)

Adjust_speed(0)

downSpeed_button = Button(
    window, text = "<", font = ("Helvetica", 12, "bold"), 
    command = lambda: Adjust_speed(-1)
    )
downSpeed_button.place(x = 285, y = 620, width = 15, height = 25)

upSpeed_button = Button(
    window, text = ">", font = ("Helvetica", 12, "bold"), 
    command = lambda: Adjust_speed(1)
    )
upSpeed_button.place(x = 355, y = 620, width = 15, height = 25)

#-------------------------------------------------------------------------------------------------------------

#external devices --------------------------------------------------------------------------------------------
output_label = Label(window, text = "output", font = ("Times", 14), border = 1, relief = "sunken")
output_label.place(x = 420, y = 10, width = 80, height = 25)
output_box = Text(window, font = ("Helvetica", 13), state = DISABLED, bg = "#f0f0f0")
output_box.place(x = 420, y = 35, width = 80, height = 150)

input_label = Label(window, text = "input", font = ("Times", 14), border = 1, relief = "sunken")
input_label.place(x = 420, y = 595, width = 80, height = 25)
input_box = Entry(window, font = ("Helvetica", 13), state = "readonly")
input_box.place(x = 420, y = 620, width = 80, height = 25)
#-------------------------------------------------------------------------------------------------------------

#RAM elements ------------------------------------------------------------------------------------------------
global Ram, machine_code
machine_code = []
Ram = []

ram = Frame(window, borderwidth = 1, relief = "solid")
ram.place(x = 675, y = 20, width = 465, height = 440)
ram_label = Label(ram, text = "RAM", font = ("Times", 15))
ram_label.place(x = 207, y = 5, width = 50, height = 25)

for y in range(10):
    for x in range(10):
        Ram.append(["000"])

        MemoryLocation = Entry(ram, font = ("Times", 13), justify = "center", borderwidth = 1, relief = "solid")
        MemoryLocation.insert(0, "000")
        MemoryLocation.bind("<FocusOut>", lambda event, i = y * 10 + x: update_ML(event, i))
        MemoryLocation.bind("<Return>", lambda event, i = y * 10 + x: update_ML(event, i))
        MemoryLocation.place(x = x * 45 + 10, y = y * 40 + 50, width = 40, height = 20)
        Ram[-1].append(MemoryLocation)
        
        MemoryAddress = Label(ram, text = y * 10 + x, font = "Courier", borderwidth = 1, relief = "solid")
        MemoryAddress.place(x = x * 45 + 17, y = y * 40 + 36, width = 25, height = 15)
        Ram[-1].append(MemoryAddress)
#-------------------------------------------------------------------------------------------------------------

#CPU elements ------------------------------------------------------------------------------------------------
cpu = Frame(window, borderwidth = 1, relief = "solid")
cpu.place(x = 420, y = 250, width = 200, height = 198)
cpu_label = Label(cpu, text = "CPU", font = ("Times", 14))
cpu_label.place(x = 75, y = 0, width = 50, height = 25)

global pc_count
pc_count = 0
pc = Frame(cpu, borderwidth = 1, relief = "solid")
pc.place(x = -1, y = 25, width = 200, height = 40)
pc_label = Label(pc, text = "Program Counter", font = ("Times", 12))
pc_label.place(x = 5, y = 5)
pc_box = Entry(
    pc, justify = "center", font = ("Helvetica", 13), 
    bg = "#f0f0f0", borderwidth = 1, relief = "solid"
    )
pc_box.place(x = 150, y = 5, width = 40, height = 25)
pc_box.insert(0, "00")
update_pc_box(None)
pc_box.bind("<FocusOut>", update_pc_box)
pc_box.bind("<Return>", update_pc_box)

ir = Frame(cpu, borderwidth = 1, relief = "solid")
ir.place(x = -1, y = 64, width = 200, height = 40)
ir_label = Label(ir, text = "Instruction Registor", font = ("Times", 12))
ir_label.place(x = 5, y = 5)
ir_box = Entry(
    ir, justify = "center", font = ("Helvetica", 13), 
    state = "readonly", borderwidth = 1, relief = "solid"
    )
ir_box.place(x = 150, y = 5, width = 20, height = 25)

ar = Frame(cpu, borderwidth = 1, relief = "solid")
ar.place(x = -1, y = 103, width = 200, height = 40)
ar_label = Label(ar, text = "Address Registor", font = ("Times", 12))
ar_label.place(x = 5, y = 5)
ar_box = Entry(
    ar, justify = "center", font = ("Helvetica", 13), 
    state = "readonly", borderwidth = 1, relief = "solid"
    )
ar_box.place(x = 150, y = 5, width = 40, height = 25)

accumulator = Frame(cpu, borderwidth = 1, relief = "solid")
accumulator.place(x = -1, y = 142, width = 200, height = 55)
accumulator_label = Label(accumulator, text = "Accumulator", font = ("Times", 12))
accumulator_label.place(x = 50, y = 2, width = 100)
accumulator_box = Entry(
    accumulator, justify = "center", font = ("Helvetica", 13), 
    state = "readonly", borderwidth = 1, relief = "solid"
    )
accumulator_box.place(x = 72, y = 24, width = 60, height = 25)
insert_to_entry(accumulator_box, 0, "000", False)

alu = Label(
    window, text = "ALU", 
    font = ("Times", 14), bg = "#dddddd", 
    border = 1, relief = "solid"
    )
alu.place(x = 420, y = 468, width = 70, height = 40)
#-------------------------------------------------------------------------------------------------------------

#process terminal --------------------------------------------------------------------------------------------
process_terminal = Frame(window)
process_terminal.place(x = 675, y = 485, width = 465, height = 160)

process_box = Text(process_terminal, state = DISABLED)
process_box.place(x = 0, y = 0, width = 450, height = 160)

PB_yscrollbar = Scrollbar(process_terminal, command = process_box.yview)
PB_yscrollbar.place(x = 450, y = 0, height = 160, width = 15)
process_box['yscrollcommand'] = PB_yscrollbar.set
#-------------------------------------------------------------------------------------------------------------

#buses -------------------------------------------------------------------------------------------------------
to_alu_bus = Label(window, bg = "#bbbbbb")
to_alu_bus.place(x = 430, y = 448, width = 20, height = 20)
from_alu_bus = Label(window, bg = "#bbbbbb")
from_alu_bus.place(x = 460, y = 448, width = 20, height = 20)

from_output_bus_1 = Label(window, bg = "#bbbbbb")
from_output_bus_1.place(x = 500, y = 90, width = 33, height = 20)
from_output_bus_2 = Label(window, bg = "#bbbbbb")
from_output_bus_2.place(x = 513, y = 110, width = 20, height = 140)

from_input_bus_1 = Label(window, bg = "#bbbbbb") #accumulator at (508, 418) 
from_input_bus_1.place(x = 500, y = 610, width = 33, height = 20)
from_input_bus_2 = Label(window, bg = "#bbbbbb")
from_input_bus_2.place(x = 513, y = 448, width = 20, height = 162)

general_ram_bus_1 = Label(window, bg = "#bbbbbb")
general_ram_bus_1.place(x = 581, y = 448, width = 20, height = 50)
general_ram_bus_2 = Label(window, bg = "#bbbbbb")
general_ram_bus_2.place(x = 601, y = 478, width = 30, height = 20)
general_ram_bus_3 = Label(window, bg = "#bbbbbb")
general_ram_bus_3.place(x = 630, y = 70, width = 20, height = 428)

for i in range(10):
    general_ram_bus_r = Label(window, bg = "#bbbbbb")
    general_ram_bus_r.place(x = 650, y = 40 * i + 70, width = 25, height = 20)

cpu_signal = Label(window, font = ("Times", 13), borderwidth = 1, relief = "solid")
ram_signal = Label(window, font = ("Times", 13), borderwidth = 1, relief = "solid")
pc_signal = Label(window, font = ("Times", 13), borderwidth = 1, relief = "solid")
accumulator_signal = Label(window, font = ("Times", 13), borderwidth = 1, relief = "solid")
alu_operation = Label(window, font = ("Times", 12), bg = "#ffffff")
#-------------------------------------------------------------------------------------------------------------

window.mainloop()
