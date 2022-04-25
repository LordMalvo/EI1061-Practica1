# VARIABLES GLOBALES

# Para las UF
TOTAL_UF = 3
ALU = 0
MEM = 1
MULT = 2

CICLOS_MEM = 2
CICLOS_ALU = 1
CICLOS_MULT = 5

# Eteapas de procesamiento de las instrucciones en ROB
ISS = 1
EX = 2
WB = 3


# INSTRUCCION
class Instruccion:
    def __init__(self, op, rd, rs, rt, inm, num, tipo):
        self.op = op
        self.rd = rd
        self.rs = rs
        self.rt = rt
        self.inm = inm
        self.num = num
        self.tipo = tipo

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

    def toString(self):
        return "{} {},{},{},{},{},{},{},{},{}".format(self.busy, self.op, self.opa, self.opa_ok, self.ciclo_ok_opa,
                                                      self.opb, self.opb_ok, self.ciclo_ok_opb, self.inm, self.rob)


# LINEA ROB
class LineaROB:
    def __init__(self, rob, busy, destino, valor, valor_ok, ciclo_ok, etapa):
        self.rob = rob
        self.busy = busy
        self.destino = destino
        self.valor = valor
        self.valor_ok = valor_ok
        self.ciclo_ok = ciclo_ok
        self.etapa = etapa

    def toString(self):
        return "{},{},{},{},{},{},{}".format(self.rob, self.busy, self.destino, self.valor, self.valor_ok, self.ciclo_ok,
                                             self.etapa)


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

    def libera(self):
        self.uso = 0
        self.cont_ciclos = 0
        self.rob = 0
        self.opa = 0
        self.opb = 0
        self.op = 0
        self.res = 0
        self.res_ok = 0
        self.ciclo_ok = 0


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
        REG.append(Registro(i, 1, -1, -1))

    for i in range(32):
        DAT.append(i)

    for i in range(len(instrucciones)):
        ROB.append(LineaROB(i, 0, "", "", 0, 0, ""))

    for inst in instrucciones:
        op = inst[0]
        if (op == "add") or (op == "sub"):
            rd = int(inst[1][0][1])
            rs = int(inst[1][1][1])
            rt = int(inst[1][2][1])
            INS.append(Instruccion(op, rd, rs, rt, -1, num, 0))
            num += 1
        elif (op == "lw") or (op == "sw"):
            rt = int(inst[1][0][1])
            inm = int(inst[1][1])
            rs = int(inst[1][2][1])
            INS.append(Instruccion(op, "", rs, rt, inm, num, 1))
            num += 1
        else:
            rd = int(inst[1][0][1])
            rs = int(inst[1][1][1])
            rt = int(inst[1][2][1])
            INS.append(Instruccion(op, rd, rs, rt, -1, num, 2))
            num += 1

    return REG, DAT, INS, ROB


def iniciarER(instrucciones):
    # [0] es para ALU, [1] para MEM, [2] para MULT
    UF = [0, 0, 0]
    # self, uso, cont_ciclos, rob, opa, opb, op, res, res_ok, ciclo_ok
    UF[0] = UnidadFuncional(0, 0, 0, 0, 0, 0, 0, 0, 0)
    UF[1] = UnidadFuncional(0, 0, 0, 0, 0, 0, 0, 0, 0)
    UF[2] = UnidadFuncional(0, 0, 0, 0, 0, 0, 0, 0, 0)

    # busy, op, opa, opa_ok, ciclo_ok_opa, opb, opb_ok, ciclo_ok_opb, inm, rob
    ER = list()
    for i in range(TOTAL_UF):
        ER.append(list())
        for j in range(len(instrucciones)):
            ER[i].append(LineaER(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1))

    return ER, UF


def etapa_COMMIT(parametros):
    REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo = parametros

    linea_rob = ROB[p_rob_cabeza]

    if linea_rob.busy == 1 and linea_rob.etapa == "WB" and linea_rob.valor_ok == 1 and linea_rob.ciclo_ok<ciclo:

        id_reg = linea_rob.destino
        if linea_rob.rob == REG[id_reg].rob:
            REG[id_reg].contenido = linea_rob.valor
            REG[id_reg].ok = 1
            REG[id_reg].ciclo_ok = ciclo #+ 1
            REG[id_reg].rob = -1

        linea_rob.etapa = "COMMIT"
        linea_rob.busy = 0

        p_rob_cabeza += 1
        inst_rob -= 1

    return REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo


def etapa_WD(parametros):
    REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo = parametros
    i = 0
    cont = 0

    while cont == 0 and i < TOTAL_UF:
        uf = UF[i]

        if uf.uso == 1 and uf.res_ok == 1 and uf.ciclo_ok < ciclo:
            # linea a actualizar:
            id = uf.rob
            # Actualizar ROB con el resultado
            ROB[id].valor = uf.res
            ROB[id].valor_ok = 1
            ROB[id].ciclo_ok = ciclo #+ 1
            ROB[id].etapa = "WB"

            # Etapa a WB
            # Dejar libre Unidad FUncional: Poner todo a cero
            uf.libera()

            # Como se ha escrito un dato ya no se deja escribir mas
            cont = 1

            # Actualizar estaciones de reserva donde hay lineas que esperan el dato
            for k in range(TOTAL_UF):
                fin = p_er_cola[k]
                for j in range(fin):
                    if ER[k][j].busy == 1:
                        if ER[k][j].opa_ok == 0 and ER[k][j].opa == id:
                            ER[k][j].opa = ROB[id].valor
                            ER[k][j].opa_ok = 1
                            ER[k][j].ciclo_ok_opa = ciclo #+ 1

                        if ER[k][j].opb_ok == 0 and ER[k][j].opb == id:
                            ER[k][j].opb = ROB[id].valor
                            ER[k][j].opb_ok = 1
                            ER[k][j].ciclo_ok_opb = ciclo #+ 1
        else:
            i = i + 1

    return REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo


def etapa_EX(parametros):  # faltaría pasarle como argumento a la función el UF
    global max
    REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo = parametros

    i = 0
    enviar = 0

    while i < TOTAL_UF:
        uf = UF[i]
        if i == 0:
            max = CICLOS_ALU
        elif i == 1:
            max = CICLOS_MEM
        elif i == 2:
            max = CICLOS_MULT

        if uf.uso == 1:
            if uf.cont_ciclos < max:
                uf.cont_ciclos += 1

                if uf.cont_ciclos == max:
                    # Generar resultado, validarlo y almacenar ciclo donde se haya hecho la validación
                    if uf.op == "add":
                        uf.res = uf.opa + uf.opb
                    elif uf.op == "sub":
                        uf.res = uf.opa - uf.opb
                    elif uf.op == "lw":
                        uf.res = uf.opa + uf.opb
                    elif uf.op == "sw":
                        uf.res = uf.opa + uf.opb
                    elif uf.op == "mult":
                        uf.res = uf.opa * uf.opb

                    uf.res_ok = 1
                    uf.ciclo_ok = ciclo #+ 1

        elif enviar == 0:
            er = ER[i]
            fin = p_er_cola[i]
            j = 0

            while enviar == 0 and j < fin:
                if er[j].busy == 1:
                    if er[j].opa_ok == 1 and er[j].ciclo_ok_opa < ciclo and er[j].opb_ok == 1 and er[j].ciclo_ok_opb < ciclo:
                        uf.uso = 1
                        uf.cont_ciclos = 1
                        if er[j].op == "add" or er[j].op == "sub" or er[j].op == "mult":
                            uf.opa = er[j].opa
                            uf.opb = er[j].opb
                        elif er[j].op == "lw" or er[j].op == "sw":
                            uf.opa = er[j].opa
                            uf.opb = er[j].inm

                        uf.rob = er[j].rob
                        uf.op = er[j].op
                        ROB[uf.rob].etapa = "EX"
                        enviar = 1
                        er[j].busy = 0
                    else:
                        j = j + 1
        i = i + 1

    return REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo


def etapa_ID_ISS(parametros):
    REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo = parametros

    if inst_prog > 0:
        # Instruccion correspondiente
        inst = INS[PC]

        # Actualizamos la linea correspondiente de la estacion de reserva
        linea_er = ER[inst.tipo][p_er_cola[inst.tipo]]
        linea_er.busy = 1
        linea_er.op = inst.op

        if REG[inst.rs].ok == 1 and REG[inst.rs].ciclo_ok < ciclo:
            # cargar operando en opa y validarlo en ok_opa
            linea_er.opa = REG[inst.rs].contenido
            linea_er.opa_ok = 1
            linea_er.ciclo_ok_opa = ciclo #+ 1
        else:
            # cargar etiqueta ROB en opa y 0 en ok_opa
            linea_er.opa = REG[inst.rs].rob
            linea_er.opa_ok = 0

        if REG[inst.rt].ok == 1 and REG[inst.rt].ciclo_ok < ciclo:
            # cargar operando en opb y validarlo en ok_opb
            linea_er.opb = REG[inst.rt].contenido
            linea_er.opb_ok = 1
            linea_er.ciclo_ok_opb = ciclo #+ 1
        else:
            linea_er.opb = REG[inst.rt].rob
            linea_er.opb_ok = 0
        linea_er.inm = inst.inm
        p_er_cola[inst.tipo] += 1


        linea_rob = ROB[p_rob_cola]
        linea_rob.busy = 1

        if inst.op == "sw":
            linea_rob.destino = 0
        else:
            linea_rob.destino = inst.rd

        linea_rob.valor_ok = 0
        linea_rob.etapa = "ISS"
        inst_rob += 1
        linea_er.rob = linea_rob.rob

        p_rob_cola += 1

        # Actualizamos el registro destino con el ROB correspondiente
        if inst.op != "sw":
            if inst.op == "lw":
                REG[inst.rt].ok = 0
                REG[inst.rt].rob = linea_rob.rob
            else:
                REG[inst.rd].ok = 0
                REG[inst.rd].rob = linea_rob.rob

        # Actualizamos el número de instrucciones que tendrá el programa
        inst_prog -= 1
        PC += 1

    datos = REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo
    return datos


def mostrar_ER(ER):
    print("ESTACIONES DE RESERVA---------------------------------\n")
    nombres = ["ALU", "MEM", "MULT"]
    for e in range(len(ER)):
        for l in range(len(ER[e])):
            lineaER = ER[e][l]
            if lineaER.busy != -1:
                print("ER "+nombres[e]+" "+str(l)+":")
                print("val: {0} | "
                      "op: {1} | "
                      "opa: {2} | "
                      "opa_ok: {3} | "
                      "clk_ok_opa: {4} | "
                      "opb: {5} | "
                      "opb_ok: {6} | "
                      "clk_ok_opb: {7} | "
                      "inm: {8} | "
                      "rob: {9}".format(lineaER.busy, lineaER.op, lineaER.opa, lineaER.opa_ok, lineaER.ciclo_ok_opa,
                      lineaER.opb, lineaER.opb_ok, lineaER.ciclo_ok_opb, lineaER.inm, lineaER.rob))
                print()
def mostrar_ROB(ROB):
    print()
    print("Buffer de Reordenamiento---------------------------------\n")
    for i in range(len(ROB)):
        lineaROB = ROB[i]
        print("ROB{0}\n"
              "val: {1} | "
              "dest {2} | "
              "valor {3} | "
              "valor_ok: {4} | "
              "ciclo_ok: {5} | "
              "etapa: {6}".format(lineaROB.rob, lineaROB.busy, lineaROB.destino, lineaROB.valor, lineaROB.valor_ok, lineaROB.ciclo_ok, lineaROB.etapa))
        print()

def mostrar_REG(REG):
    print()
    print("Banco de registros---------------------------------\n")
    for i in range(len(REG)):
        reg = REG[i]
        print("R"+str(i)+":\n"
              "contenido: {0} | "
              "ok: {1} | "
              "ciclo_ok: {2} | "
              "rob: {3}".format(reg.contenido, reg.ok, reg.ciclo_ok, reg.rob))
        print()
def mostrar_MEM(MEM):
    print()
    print("Memoria de datos---------------------------------\n")
    for i in range(len(MEM)):
        print("M"+str(i)+": "+str(MEM[i]))

if __name__ == '__main__':

    # Inicializamos estructuras (Registros, memoria de datos y memoria de isntrucciones)
    instrucciones = read_data()
    print(instrucciones)
    REG, DAT, INS, ROB = iniciarEstructuras(instrucciones)
    for ins in INS:
        print(ins.op)
        print("inm:"+str(ins.inm))
        print(ins.rs)
        print(ins.rd)
        print(ins.rt)
        print()
    ER, UF = iniciarER(INS)
    PC = 0
    ciclo = 1

    inst_prog = len(instrucciones)
    p_er_cola = [0, 0, 0]
    inst_rob = 0
    p_rob_cabeza = 0
    p_rob_cola = 0

    datos = [REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo]

    while inst_rob > 0 or inst_prog > 0:
        print("---------------------- CICLO " + str(ciclo) + "----------------------")
        print("inst_rob:" + str(inst_rob))
        print("inst_prog:" + str(inst_prog))
        datos = etapa_COMMIT(datos)
        datos = etapa_WD(datos)
        datos = etapa_EX(datos)
        datos = etapa_ID_ISS(datos)
        """datos = etapa_ID_ISS(datos)
        datos = etapa_EX(datos)
        datos = etapa_WD(datos)
        datos = etapa_COMMIT(datos)"""

        REG, DAT, INS, ROB, ER, UF, inst_prog, p_er_cola, inst_rob, p_rob_cabeza, p_rob_cola, PC, ciclo = datos
        ciclo += 1

        mostrar_ER(ER)
        mostrar_ROB(ROB)
        mostrar_REG(REG)
    mostrar_MEM(DAT)
