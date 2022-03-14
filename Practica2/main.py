
# INSTRUCCION
class Instruccion:
    def __init__(self, op, rd, rs, rt, inm, num):
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

# REGISTRO
class Registro:
    def __init__(self, contenido, ok, ciclo_ok, rob):
        self.contenido = contenido
        self.ok = ok
        self.ciclo_ok = ciclo_ok
        self.rob = rob

# LINEA ESTACION DE RESRERVA
class LineaER:
    def __init__(self, busy, op, opa, opa_ok, ciclo_ok_opa, opb, opb_ok, ciclo_ok_opb, inm, rob):
        self.busy = busy
        self.op = op
        self.opa = opa
        self.opa_ok = opa_ok
        self.ciclo_ok_opa = ciclo_ok_opa
        self.opb = opb
        self.opb_ok = opb_ok
        self.ciclo_ok_opb = ciclo_ok_opb
        self.inm = inm
        self.rob = rob

# LINEA ROB
class LineaROB:
    def __init__(self, rob, busy, rd, valor, valor_ok, ciclo_ok, etapa):
        self.rob = rob
        self.busy = busy
        self.rd = rd
        self.valor = valor
        self.valor_ok = valor_ok
        self.ciclo_ok = ciclo_ok
        self.etapa = etapa

# UNIDAD FUNCIONAL
class UnidadFuncional:
    def __init__(self, uso, cont_ciclos, rob, opa, opb, op, res, res_ok, ciclo_ok):
        self.uso = uso
        self.cont_ciclos = cont_ciclos
        self.rob = rob
        self.opa = opa
        self.opb = opb
        self.op = op
        self.res = res
        self.res_ok = res_ok
        self.ciclo_ok = ciclo_ok

def read_data():
    f = open("instrucciones.txt")
    lines = f.readlines()
    instrucciones = []
    for i in range(len(lines)):
        instrucciones.append(lines[i].split())
        instrucciones[i][1] = instrucciones[i][1].split(',')

        if (instrucciones[i][0] == "lw") or (instrucciones[i][0] == "sw"):
            inmSplit1 = instrucciones[i][1][1].split("(")
            inm = int(inmSplit1[0])
            inmSplit2 = inmSplit1[1].split(")")
            rs = inmSplit2[0]
            instrucciones[i][1][1] = inm
            instrucciones[i][1].append(rs)

    return instrucciones

def iniciarEstructuras(instrucciones):
    REG = []
    DAT = []
    INS = []
    ROB = []

    num = 1

    for i in range(16):
        REG.append(Registro(i, 1, 1, -1))

    for i in range(32):
        DAT.append(i)



    for i in range(len(instrucciones)):
        ROB.append(LineaROB(i,0,"","",0,0,""))

    for inst in instrucciones:
        op = inst[0]
        if (op == "add") or (op == "sub") or (op=="mult"):
            rd = inst[1][0]
            rs = inst[1][1]
            rt = inst[1][2]
            INS.append(Instruccion(op, rd, rs, rt, -1, num))
            num += 1
        else:
            rt = inst[1][0]
            inm = inst[1][1]
            rs = inst[1][2]
            INS.append(Instruccion(op, "", rs, rt, inm, num))
            num += 1

    return REG, DAT, INS, ROB


def iniciarER(instrucciones):
    ER = [[],[],[]] # [0] es para ALU, [1] para MEM, [2] para MULT
    #busy, op, opa, opa_ok, ciclo_ok_opa, opb, opb_ok, ciclo_ok_opb, inm, rob
    for ins in instrucciones:
        if ins[0] == "add" or ins[0] == "sub" :
            ER[0].append(LineaER(0,"","",0,0,"",0,0,"",0))

        elif ins[0] == "mult":
            ER[1].append(LineaER(0, "", "", 0, 0, "", 0, 0, "", 0))

        else:
            ER[2].append(LineaER(0, "", "", 0, 0, "", 0, 0, "", 0))

    return ER




def etapa_COMMIT( ):
    # Saber que linea hay que eliminar
    linea_rob = ROB[linea]


    if linea_rob.busy == 1 and linea_rob.etapa == "WB" and linea_rob.valor_ok == 1 and linea_rob.ciclo_ok:
        id_reg = linea_rob.rd

        if (linea_rob.rob == id_reg.rob):
              #actualizar contenido id_reg.contenido



if __name__ == '__main__':

    # Inicializamos estructuras (Registros, memoria de datos y memoria de isntrucciones)
    instrucciones = read_data()
    REG, DAT, INS, ROB = iniciarEstructuras(instrucciones)
    ER = iniciarER(INS)
    ciclo = 1

    inst_prog = len(instrucciones)
    inst_rob = 0

    while (inst_rob > 0) or (inst_prog > 0):
        etapa_ID_ISS()
        etapa_EX()
        etapa_WD()
        etapa_COMMIT()

        ciclos = cliclos+1

        mostrar_ER(ER)
        mostrar_ROB(ROB)
        mostrar_REG(REG)

















