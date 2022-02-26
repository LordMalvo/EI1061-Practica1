import sys

# Definicion de vectores
MEM_D = []  # Memoria de datos
REG = dict()    # Banco de registros
MEM_I = []  # Memorida de isntrucciones
RS_IF_ID = []   # Registro de segmentacion etapa de IF a ID
RS_ID_EX = []   # Registro de segmentacion etapa de ID a EX
RS_EX_MEM = []  # Registro de segmentacion etapa de EX a MEM
RS_MEM_WD = []  # Registro de segmentacion etapa de MEM a WD

# REGISTROS DE SEGMENTACION
class RS_IF_ID:
    def __init__(self, tipo, op, rs, rt, rd, inm):
        self.tipo = tipo
        self.op = op
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.inm = inm


class RS_ID_EX:
    def __init__(self, tipo, op, rs, rt, rd, inm, value1, value2):
        self.tipo = tipo
        self.op = op
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.inm = inm
        self.value1 = value1
        self.value2 = value2


class RS_EX_MEM:
    def __init__(self, tipo, res, rt, rd, value2):
        self.tipo = tipo
        self.res = res
        self.rt = rt
        self.rd = rd
        self.value2 = value2


class RS_MEM_WB:
    def __init__(self, tipo, res, rt, rd):
        self.tipo = tipo
        self.res = res
        self.rt = rt
        self.rd = rd

# Program Counter
pc = 0

# Esta funcion devuelve una lista de instrucciones tal que
# [[instruccion1, [registros]], [instruccion2, [registros]], ...]
def read_data(f):
    lines = f.readlines()
    instrucciones = []
    for i in range(len(lines)):
        instrucciones.append(lines[i].split())
        instrucciones[i][1] = instrucciones[i][1].split(',')
    return instrucciones

# Control de errores
def checkErrorAluAlu(RS_ID_EX: RS_ID_EX, RS_EX_MEM: RS_EX_MEM):
    if (RS_ID_EX.rs == RS_EX_MEM.rd) and (RS_EX_MEM.tipo == "ALU") and (RS_ID_EX.tipo == "ALU"):
        RS_ID_EX.value1 = RS_EX_MEM.res
    if (RS_ID_EX.rt == RS_EX_MEM.rd) and (RS_EX_MEM.tipo == "ALU") and (RS_ID_EX.tipo == "ALU"):
        RS_ID_EX.value2 = RS_EX_MEM.res

def checkErrorLoadAlu(RS_ID_EX: RS_ID_EX, RS_MEM_WB: RS_MEM_WD):
    if (RS_ID_EX.rs == RS_MEM_WB.rt) and (RS_ID_EX.tipo == "ALU") and (RS_MEM_WB.tipo == "LOAD"):
        RS_ID_EX.value1 = RS_MEM_WB.res
    if (RS_ID_EX.rt == RS_MEM_WB.rt) and (RS_ID_EX.tipo == "ALU") and (RS_MEM_WB.tipo == "LOAD"):
        RS_ID_EX.value2 = RS_MEM_WB.res

def checkErrorAluStore(RS_EX_MEM: RS_EX_MEM, RS_MEM_WB: RS_MEM_WD):
    if (RS_EX_MEM.rt == RS_MEM_WB.rd) and (RS_EX_MEM.tipo == "STORE") and (RS_MEM_WB.tipo == "ALU"):
        RS_EX_MEM.value2 = RS_MEM_WB.res

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
                    instrucciones.insert(i + 1, "NOP")
                    instrucciones.insert(i + 1, "NOP")
                    i += 2
                    nciclos += 2
                i += 1
        return instrucciones, nciclos

    else:
        print("No hay instrucciones")


def etapa_if(MEM_I, RS_IF_ID):
    pass

def etapa_id(RS_IF_ID, RS_ID_EX, REG, n):
    pass

def etapa_ex(RS_ID_EX, RS_EX_MEM):
    pass

def etapa_mem(RS_EX_MEM, RS_MEM_WB, MEM_D):
    pass

def etapa_wb(RS_MEM_WB, REG):
    pass

if __name__ == '__main__':

    # Cargamos las intrucciones en memoria
    instrucciones, nciclos = read_data(sys.stdin)
    MEM_I = procesaInstrucciones(instrucciones)

    # Inicializamos registros
    REG = {'r0': 0, 'r1': 1, 'r2': 2, 'r3': 3, 'r4': 4, 'r5': 5, 'r6': 6,
           'r7': 7, 'r8': 8, 'r9': 9, 'r10': 10, 'r11': 11, 'r12': 12,
           'r13': 13, 'r14': 14, 'r15': 15}

    # Contador
    PC = 0

    # Comienza la simulacion
    print("Listado de instrucciones final:")
    for elem in instrucciones:
        print("{}".format(elem))
    print("Numero total de ciclos: {}".format(nciclos))
    print(" ")




