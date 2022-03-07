# MEMORIA DE DATOS
MEM_D = [i for i in range(31)]  # Memoria de datos (de 0 a 31)


# CLASE INSTRUCCION
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
        self.instruc = Instruccion("", "", "", "", "", 0, 0)
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

    def empty(self):
        self.instruc = Instruccion("", "", "", "", "", 0, 0)
        self.tipo = ""
        self.op = ""
        self.rs = ""
        self.rt = ""
        self.rd = ""
        self.inm = 0
        self.value1 = 0
        self.value2 = 0


class RS_EX_MEM:
    def __init__(self, instruc, tipo, res, rt, rd, value2):
        self.instruc = instruc
        self.tipo = tipo
        self.res = res
        self.rt = rt
        self.rd = rd
        self.value2 = value2

    def empty(self):
        self.instruc = Instruccion("", "", "", "", "", 0, 0)
        self.tipo = ""
        self.res = ""
        self.rt = ""
        self.rd = ""
        self.value2 = 0


class RS_MEM_WB:
    def __init__(self, instruc, tipo, res, rt, rd):
        self.instruc = instruc
        self.tipo = tipo
        self.res = res
        self.rt = rt
        self.rd = rd

    def empty(self):
        self.instruc = Instruccion("", "", "", "", "", 0, 0)
        self.tipo = ""
        self.res = ""
        self.rt = ""
        self.rd = ""


# INICIALIZACION REGISTROS DE SEGMENTACION
inst = Instruccion("", "", "", "", "", 0, 0)
rsIfId = RS_IF_ID(inst, "", "", "", "", "", 0)
rsIdEx = RS_ID_EX(inst, "", "", "", "", "", "", 0, 0)
rsExMem = RS_EX_MEM(inst, "", "", "", "", 0)
rsMemWb = RS_MEM_WB(inst, "", "", "", "")


# INICIALIZACION REGISTROS
REG = {'r0': 0, 'r1': 1, 'r2': 2, 'r3': 3, 'r4': 4, 'r5': 5, 'r6': 6,
       'r7': 7, 'r8': 8, 'r9': 9, 'r10': 10, 'r11': 11, 'r12': 12,
       'r13': 13, 'r14': 14, 'r15': 15}


# Esta funcion devuelve una lista de instrucciones tal que
# [[instruccion1, [registros]], [instruccion2, [registros]], ...]
def read_data():
    f = open("instrucciones.txt")
    lines = f.readlines()
    instrucciones = []
    for i in range(len(lines)):
        if str(lines[i]) == "NOP\n":
            instrucciones.append("NOP")
        else:
            instrucciones.append(lines[i].split())
            instrucciones[i][1] = instrucciones[i][1].split(',')
    return instrucciones

# Deteccion de riesgo LOAD-ALU e inserción de NOP
def procesaInstrucciones(instrucciones):
    if len(instrucciones) >= 1:
        nciclos = 5

        # Sabes el numero de NOPS
        if len(instrucciones) > 1:
            i = 0
            while i < len(instrucciones) - 1:
                if instrucciones[i] != "NOP" or instrucciones[i + 1] != "NOP":
                    dependencia = False
                    nciclos += 1
                    op1 = instrucciones[i][0]
                    regs1 = instrucciones[i][1]

                    op2 = instrucciones[i + 1][0]
                    regs2 = instrucciones[i + 1][1]

                    if op1 == "lw":
                        if (op2 == "add" or op2 == "sub") and (
                                regs1[0] == regs2[1] or regs1[0] == regs2[2]):  # Riesgo de datos entre LOAD y ALU
                            dependencia = True
                    if dependencia:
                        instrucciones.insert(i + 1, "NOP")
                        i += 1
                        nciclos += 1
                else:
                    nciclos += 1
                i += 1

        return instrucciones, nciclos
    else:
        print("No hay instrucciones")


# Creacion de objetos Instruccion
def cargaInstrucciones(instrucciones):
    num = 0
    lista = []
    for inst in instrucciones:
        op = inst[0]
        if inst == "NOP":
            lista.append(Instruccion("", "NOP", "", "", "", 0, 0))
        elif op == "add" or op == "sub":
            rd = inst[1][0]
            rs = inst[1][1]
            rt = inst[1][2]
            instruccion = Instruccion("", op, rd, rs, rt, 0, num + 1)
            lista.append(instruccion)
        else:
            rt = inst[1][0]
            rs1 = inst[1][1].split("(")
            inm = int(rs1[0])
            rs2 = rs1[1].split(")")
            rs = rs2[0]
            instruccion = Instruccion("", op, "", rs, rt, inm, num + 1)
            lista.append(instruccion)
        num += 1
    return lista, num


# UNA FUNCION PARA CADA EJECUCION DE ETAPA
def etapa_if(instruccion: Instruccion):
    op = instruccion.op
    rd = instruccion.rd
    rs = instruccion.rs
    rt = instruccion.rt
    inm = instruccion.inm

    # Pasamos los componentes al registro de segmentacion
    rsIfId.instruc = instruccion
    rsIfId.op = op
    rsIfId.rs = rs
    rsIfId.rt = rt
    if (op != "NOP"):
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


def etapa_id():
    if rsIfId.tipo != "NOP":
        print("Etapa ID/OF de I{}: Contenido del registro RS_ID_EX:".format(rsIfId.instruc.num))
        print("\t>> Instruccion: {}".format(rsIfId.instruc.toString()))
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
        rsIdEx.instruc = rsIfId.instruc

        # Vaciamos RS_IF_ID
        rsIfId.empty()


def etapa_ex():
    if rsIdEx.tipo != "NOP":
        instruc = rsIdEx.instruc
        print("Etapa EX de I{}: Contenido del registro RS_EX_MEM:".format(instruc.num))
        print("\t>> Instruccion: {}".format(instruc.toString()))
        print("\t>> Tipo de instruccion: {}".format(rsIdEx.tipo))

        rsExMem.instruc = rsIdEx.instruc
        rsExMem.tipo = rsIdEx.tipo
        rsExMem.rd = rsIdEx.rd
        rsExMem.rt = rsIdEx.rt
        rsExMem.value2 = rsIdEx.value2

        if rsIdEx.tipo == "ALU":
            if rsIdEx.op == "add":
                resultado = rsIdEx.value1 + rsIdEx.value2
                print("\t>> res: {} + {} = {}".format(rsIdEx.value1, rsIdEx.value2, resultado))
            else:
                resultado = rsIdEx.value1 - rsIdEx.value2
                print("\t>> res: {} - {} = {}".format(rsIdEx.value1, rsIdEx.value2, resultado))
            rsExMem.res = resultado
        elif rsIdEx.tipo == "LOAD" or rsIdEx.tipo == "STORE":
            resultado = rsIdEx.value1 + rsIdEx.inm
            print("\t>> res: {} + {} = {}".format(rsIdEx.value1, rsIdEx.inm, resultado))
            rsExMem.res = resultado

        # Vaciamos RS_ID_EX
        rsIdEx.empty()


def etapa_mem():
    if rsExMem.tipo != "NOP":
        instruc = rsExMem.instruc
        print("Etapa MEM de I{}: Contenido del registro RS_MEM_WB:".format(instruc.num))
        print("\t>> Instruccion: {}".format(instruc.toString()))
        print("\t>> Tipo de instruccion: {}".format(rsExMem.tipo))

        rsMemWb.instruc = rsExMem.instruc
        rsMemWb.tipo = rsExMem.tipo

        if rsExMem.tipo == "ALU":
            rsMemWb.res = rsExMem.res
            rsMemWb.rd = rsExMem.rd
            print("\t>> res: {}".format(rsMemWb.res))
            print("\t>> rd: {}".format(rsMemWb.rd))
        elif rsExMem.tipo == "LOAD":
            rsMemWb.res = MEM_D[rsExMem.res]
            rsMemWb.rt = rsExMem.rt
            print("\t>> res: {}".format(rsMemWb.res))
            print("\t>> rt: {}".format(rsMemWb.rt))
        elif rsExMem.tipo == "STORE":
            MEM_D[rsExMem.res] = REG[rsExMem.rt]
            print("\t>> Dato {} del registro {} almacenado en la direccion {} de memoria".format(REG[rsExMem.rt],
                                                                                                 rsExMem.rt,
                                                                                                 rsExMem.res))

        # Vaciamos RS_EX_MEM
        rsExMem.empty()


def etapa_wb():
    instruc = rsMemWb.instruc
    print("Etapa WB de I{}:".format(instruc.num))
    print("\t>> Instruccion: {}".format(instruc.toString()))
    print("\t>> Tipo de instruccion: {}".format(rsMemWb.tipo))

    if rsMemWb.tipo == "ALU":
        REG[rsMemWb.rd] = rsMemWb.res
    elif rsMemWb.tipo == "LOAD":
        REG[rsMemWb.rt] = rsMemWb.res

    # Vaciamos RS_MEM_WB
    rsMemWb.empty()


# PROGRAMA PRINCIPAL
if __name__ == '__main__':

    # Cargamos las intrucciones en memoria
    instrucciones = read_data()
    lista_inst, nciclos = procesaInstrucciones(instrucciones)
    MEM_I, numInst = cargaInstrucciones(lista_inst)

    # Contador
    PC = 0  # Para acceder a la memoria de instrucciones
    contCiclos = 1  # Para saber cuando parar

    # Comienza la simulacion
    print("Sea un programa formado por las siguientes instrucciones")
    i = 1
    for instruc in MEM_I:
        print("I{}: {}".format(i, instruc.toString()))
        i += 1

    print(" ")
    print("Numero total de instrucciones: {}".format(numInst))
    print("Numero total de ciclos: {}".format(nciclos))
    print(" ")
    print("----------------COMIENZO SIMULACIÓN---------------")

    while contCiclos <= nciclos:
        # COMPROBAMOS SI HAY ALGUN RIESGO

        # ALU ALU
        if (rsIdEx.rs == rsExMem.rd) and (rsExMem.tipo == "ALU") and (rsIdEx.tipo == "ALU"):
            rsIdEx.value1 = rsExMem.res
        if (rsIdEx.rt == rsExMem.rd) and (rsExMem.tipo == "ALU") and (rsIdEx.tipo == "ALU"):
            rsIdEx.value2 = rsExMem.res

        # LOAD ALU
        if (rsIdEx.rs == rsMemWb.rt) and (rsIdEx.tipo == "ALU") and (rsMemWb.tipo == "LOAD"):
            rsIdEx.value1 = rsMemWb.res
        if (rsIdEx.rt == rsMemWb.rt) and (rsIdEx.tipo == "ALU") and (rsMemWb.tipo == "LOAD"):
            rsIdEx.value2 = rsMemWb.res

        # ALU STORE
        if (rsExMem.rt == rsMemWb.rd) and (rsExMem.tipo == "STORE") and (rsMemWb.tipo == "ALU"):
            rsExMem.value2 = rsMemWb.res

        #ALU + INST + ALU
        if (rsIdEx.rs == rsMemWb.rd) and (rsMemWb.tipo == "ALU") and (rsIdEx.tipo == "ALU"):
            rsIdEx.value1 = rsMemWb.res
        if (rsIdEx.rt == rsMemWb.rd) and (rsMemWb.tipo == "ALU") and (rsIdEx.tipo == "ALU"):
            rsIdEx.value2 = rsMemWb.res

        # SEGMENTACION
        print(" ")
        print("---------------------Ciclo: {}---------------------".format(contCiclos))

        # En caso de que un registro de segmentacion este vacio
        # es porque ninguna instruccion ha llegado aun a esa etapa
        if rsMemWb.tipo != "":
            etapa_wb()
        if rsExMem.tipo != "":
            etapa_mem()
        if rsIdEx.tipo != "":
            etapa_ex()
        if rsIfId.tipo != "":
            etapa_id()
        if PC < numInst:
            etapa_if(MEM_I[PC])

        PC += 1

        contCiclos += 1

    print(" ")
    print("---------------------Resultados---------------------")
    print("Contenido de la Memoria de datos (MEM_D):")
    for i in range(len(MEM_D)):
        print("MEM_D[{}] = {}".format(i, MEM_D[i]))

    print(" ")
    print("Contenido del Banco de registros (REG):")
    i = 0
    for registro in REG.values():
        print("REG[{}] = {}".format(i, registro))
        i += 1
