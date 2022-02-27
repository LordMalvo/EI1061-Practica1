import sys
from typing import *

# Definicion de vectores
MEM_D = []  # Memoria de datos
REG = dict()    # Banco de registros
MEM_I = []  # Memorida de isntrucciones

# INSTRUCCION
class Instruccion:

    def __init__(self, tipo, op, rd, rs, rt, inm, num):
        self.tipo = tipo
        self.op = op
        self.rd = rd
        self.rs = rs
        self.rt = rt
        self.inm = inm
        self.num = num

    def toString(self):
        if self.op == "NOP":
            return "NOP"
        if self.op == "sw" or self.op == "lw":
            return "{} {},{}({})".format(self.op, self.rt, self.inm, self.rs)
        return "{} {},{},{}".format(self.op, self.rd, self.rs, self.rt)

# REGISTROS DE SEGMENTACION
class RS_IF_ID:
    def __init__(self, instruc, tipo, op, rs, rt, rd, inm):
        self.instruc = instruc
        self.tipo = tipo
        self.op = op
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.inm = inm

    def empty(self):
        self.instruc = ""
        self.tipo = ""
        self.op = ""
        self.rs = ""
        self.rt = ""
        self.rd = ""
        self.inm = 0


class RS_ID_EX:
    def __init__(self, instruc, tipo, op, rs, rt, rd, inm, value1, value2):
        self.instruc = instruc
        self.tipo = tipo
        self.op = op
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.inm = inm
        self.value1 = value1
        self.value2 = value2


class RS_EX_MEM:
    def __init__(self, isntruc, tipo, res, rt, rd, value2):
        self.instruc = instruc
        self.tipo = tipo
        self.res = res
        self.rt = rt
        self.rd = rd
        self.value2 = value2


class RS_MEM_WB:
    def __init__(self, isntruc, tipo, res, rt, rd):
        self.instruc = instruc
        self.tipo = tipo
        self.res = res
        self.rt = rt
        self.rd = rd

# Inicializacion de los registros de segmentación
rsIfId = RS_IF_ID("", "", "", "", "", "", 0)
rsIdEx = RS_ID_EX("", "", "", "", "", "", "", 0, 0)
rsExMem = RS_EX_MEM("", "", "", "", "", 0)
rsMemWb = RS_MEM_WB("", "", "", "", "")

# Inicializamos registros
REG = {'r0': 0, 'r1': 1, 'r2': 2, 'r3': 3, 'r4': 4, 'r5': 5, 'r6': 6,
       'r7': 7, 'r8': 8, 'r9': 9, 'r10': 10, 'r11': 11, 'r12': 12,
       'r13': 13, 'r14': 14, 'r15': 15}

# Esta funcion devuelve una lista de instrucciones tal que
# [[instruccion1, [registros]], [instruccion2, [registros]], ...]
def read_data(f):
    lines = f.readlines()
    instrucciones = []
    for i in range(len(lines)):
        instrucciones.append(lines[i].split())
        instrucciones[i][1] = instrucciones[i][1].split(',')
    return instrucciones

def procesaInstrucciones(instrucciones):
    if len(instrucciones) >= 1:
        nciclos = 5

        # Sabes el numero de NOPS
        if len(instrucciones) > 1:
            i = 0
            while i < len(instrucciones)-1:
                dependencia = False
                nciclos += 1
                op1 = instrucciones[i][0]
                regs1 = instrucciones[i][1]

                op2 = instrucciones[i+1][0]
                regs2 = instrucciones[i+1][1]

                if op1 == "add" or op1 == "sub":
                    if (op2 == "add" or op2 == "sub") and (regs1[0] == regs2[1] or regs1[0] == regs2[2]):  # Riesgo de datos entre ALU y ALU
                        dependencia = True
                    elif (op2 == "sw") and (regs1[0] == regs2[0]):  # Riesgo de datos entre ALU y STORE
                        dependencia = True
                elif op1 == "lw":
                    if (op2 == "add" or op2 == "sub") and (regs1[0] == regs2[0]):  # Riesgo de datos entre LOAD y ALU
                        dependencia = True
                if dependencia:
                    instrucciones.insert(i + 1, ["NOP"])
                    instrucciones.insert(i + 1, ["NOP"])
                    i += 2
                    nciclos += 2
                i += 1
        return instrucciones, nciclos
    else:
        print("No hay instrucciones")

def cargaInstrucciones(instrucciones):
    num = 1
    lista = ()
    for inst in instrucciones:
        op = inst[0]
        if op == "NOP":
            lista.append(Instruccion("",op,"","","",0,num))
        elif op == "add" or op == "sub":
            rd = inst[1][0]
            rs = inst[1][1]
            rt = inst[1][2]
            instruccion = Instruccion("",op, rd, rs, rt, 0, num)
            lista.append(instruccion)
        else:
            rt = inst[1][0]
            rs1 = inst[1][1].split("(")
            inm = rs1[0]
            rs2 = rs1[1].split(")")
            rs = rs2[0]
            instruccion = Instruccion("",op, "", rs, rt, inm, num)
            lista.append(instruccion)
        num+=1
    return lista, num



def etapa_if(instruccion: Instruccion):
    op = instruccion.op
    rd = instruccion.rd
    rs = instruccion.rs
    rt = instruccion.rt
    inm = instruccion.inm

    # Pasamos los componentes al registro de segmentacion
    rsIfId.op = op
    rsIfId.rs = rs
    rsIfId.rt = rt

    print("Etapa IF de I{}: Contenido del registro RS_IF_ID:".format(instruccion.num))
    print("\t>> Instruccion: {}".format(instruccion.toString()))
    if op == "NOP":
        rsIfId.tipo = "NOP"
    elif op == "add" or op == "sub":
        rsIfId.tipo = "ALU"
        rsIfId.rd = rd
    elif op == "lw" or op == "sw":
        rsIfId.tipo = "MEM"
        rsIfId.inm = inm

    print("\t>> Tipo de instruccion: {}".format(rsIfId.tipo))
    print("\t>> rd: {} - rs: {} - rt: {} - inm: {}".format(rd, rs, rt, inm))

def etapa_id(instruccion: Instruccion):
    print("Etapa ID/OF de I{}: Contenido del registro RS_ID_EX:".format(instruccion.num))
    print("\t>> Instruccion: {}".format(instruccion.toString()))
    # Cargamos los componentes del registro de segmentacion
    # Buscamos los valores de rs y rt en REG
    rsIdEx.value1 = REG[rsIfId.rs]
    rsIdEx.value2 = REG[rsIfId.rt]
    rsIdEx.rs = rsIfId.rs
    rsIdEx.rt = rsIfId.rt

    if rsIfId.tipo == "ALU":
        rsIdEx.rd = rsIfId.rd
        rsIdEx.tipo = rsIfId.tipo
    if rsIfId.tipo == "MEM":
        rsIdEx.inm = rsIfId.inm
        if rsIfId.op == "lw":
            rsIdEx.tipo = "LOAD"
        else:
            rsIdEx.tipo = "STORE"

    rsIdEx.op = rsIfId.op
    print("\t>> Tipo de instruccion: {}".format(rsIdEx.tipo))
    print("\t>> rs: {} - Valor rs: {}".format(rsIdEx.rs, rsIdEx.value1))
    print("\t>> rt: {} - Valor rt: {}".format(rsIdEx.rt, rsIdEx.value2))
    print("\t>> rd: {} - inm: {}".format(rsIdEx.rd, rsIdEx.inm))

    # Vaciamos RS_IF_ID
    rsIfId.empty()


def etapa_ex(RS_ID_EX, RS_EX_MEM):
    pass

def etapa_mem(RS_EX_MEM, RS_MEM_WB, MEM_D):
    pass

def etapa_wb(RS_MEM_WB, REG):
    pass

if __name__ == '__main__':

    # Cargamos las intrucciones en memoria
    instrucciones, nciclos = read_data(sys.stdin)
    lista_inst = procesaInstrucciones(instrucciones)
    MEM_I, numInst = cargaInstrucciones(lista_inst)

    # Contador
    PC = 0 # Para acceder a la memoria de instrucciones
    continua = True
    ciclos = 1 # Para contar el numero de ciclos

    # Comienza la simulacion
    print("Listado de instrucciones final:")
    for elem in instrucciones:
        print("{}".format(elem))
    print("Numero total de ciclos: {}".format(nciclos))
    print(" ")

    while continua:  # Continua mientras hayan datos en los registros de segmentacion

        # COMPROBAMOS SI HAY ALGUN RIESGO

        # ALU ALU
        if (RS_ID_EX.rs == RS_EX_MEM.rd) and (RS_EX_MEM.tipo == "ALU") and (RS_ID_EX.tipo == "ALU"):
            RS_ID_EX.value1 = RS_EX_MEM.res
        if (RS_ID_EX.rt == RS_EX_MEM.rd) and (RS_EX_MEM.tipo == "ALU") and (RS_ID_EX.tipo == "ALU"):
            RS_ID_EX.value2 = RS_EX_MEM.res

        # LOAD ALU
        if (RS_ID_EX.rs == RS_MEM_WB.rt) and (RS_ID_EX.tipo == "ALU") and (RS_MEM_WB.tipo == "LOAD"):
            RS_ID_EX.value1 = RS_MEM_WB.res
        if (RS_ID_EX.rt == RS_MEM_WB.rt) and (RS_ID_EX.tipo == "ALU") and (RS_MEM_WB.tipo == "LOAD"):
            RS_ID_EX.value2 = RS_MEM_WB.res

        # ALU STORE
        if (RS_EX_MEM.rt == RS_MEM_WB.rd) and (RS_EX_MEM.tipo == "STORE") and (RS_MEM_WB.tipo == "ALU"):
            RS_EX_MEM.value2 = RS_MEM_WB.res

        # SEGMENTACION
        print("Ciclo: {}".format(ciclos))

        # En caso de que un registro de segmentacion este vacio
        # es porque ninguna instruccion ha llegado aun a esa etapa
        if rsMemWb.tipo != "":
            pass
        if rsExMem.tipo != "" :
            pass
        if rsIdEx.tipo != "":
            etapa_id(rsIfId.instruc)
        if PC != numInst:
            etapa_if(MEM_I[PC])
