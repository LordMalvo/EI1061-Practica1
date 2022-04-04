




# VARIABLES GLOBALES

#Para las UF
TOTAL_UF = 3
ALU = 0
MEM = 1
MULT = 2

CICLOS_MEM = 2
CICLOS_ALU = 1
CICLOS_MULT = 5

#Eteapas de procesamiento de las instrucciones en ROB
ISS = 1
EX = 2
WB = 3


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
    UF = [[]*TOTAL_UF]
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


def etapa_WD():
    i = 0
    cont = 0

    while(cont == 0 and i < TOTAL_UF):
        if (UF[i].uso == 1) and (UF[i].res_ok == 1) and (UF[i].ciclo_ok < ciclo):
            # Actualizar ROB con el resultado
            # linea a actualizar:
            id = UF[i].TAG_ROB
            # Etapa a WB
            # Dejar libre Unidad FUncional: Poner todo a cero
            # Como se ha escrito un dato ya no se deja escribir mas
            bucle = 1

            # Actualizar estaciones de reserva donde hay lineas que esperan el dato
            for k in range(TOTAL_UF):
                fin = p_er_cola[k]
                for j in range(fin):
                    if(ER[k][j].busy == 1): # Linea ocupada
                        if (ER[k][j].opa_ok == 0) and (ER[k][j].opa_ok == id):
                            #Actualiza operando a (valor, ok y ciclo)
                        if (ER[k][j].opb_ok == 0) and (ER[k][j].opb_ok == id):
                            #Actualiza operando b
        else:
            i = i + 1


def etapa_EX(): #faltaría pasarle como argumento a la función el UF
    i = 0
    enviar = 0

    while(i<TOTAL_UF):
        #Revisar todas las unidades funcionales
        #En uso: incrementa ciclo
        #No esta en uso: envia una instruccion a ejecutar
        uf = UF[i]

        if i == 0: max = CICLOS_ALU
        elif i == 1: max = CICLOS_MEM
        elif i == 2: max = CICLOS_MULT

        if (uf.uso == 1):
            if (uf.cont_ciclos < max):
                uf.cont_ciclos = uf.cont_ciclos+1
                if (uf.cont_ciclos == max):
                    #Generar resultado, validarlo y almacenar ciclo donde se haya hecho la validación
                    UF[i].res = #obtener opeacion
                    uf.res_ok = 1
                    UF[i].ciclo_ok = ciclo

            elif (enviar == 0):
                er = ER[i]
                fin = p_er_cola[i]
                j = 0

                while(enviar == 0 and j < fin):
                    if (er[j].busy == 1):
                        if(er[j].opa_ok == 1 and er[j].ciclo_ok_opa < ciclo and er[j].opb_ok == 1 and er[j].ciclo_ok_opb < ciclo):
                            #Enviar operaciones a ejecutar a UF, actualizando UF[i] con los datos necesarios
                            #En ROB actualizar la etapa a EX
                            enviar = 1
                    else:
                        j = j+1
        i = i+1


def etapa_ID_ISS(): #deberíamos pasarle como argumento la variable inst_prog declarada en el main
    linea_aux = LineaER() #argumentaos
    inst = Instruccion()

    if(inst_prog > 0):
        inst = INS[PC]
        linea_aux = 0
        linea_aux.busy = 0
        linea_aux.op = cod #operacion a realizar
        #buscar operacions a realizar
        if (REG[inst.rs].ok == 1 and REG[inst.rs].ciclo_ok < ciclo):
            #cargar operando en opa y validarlo en ok_opa
        else:
            #linea ROB que proporicona el operando
            #cargar etiqueta ROB en opa y 0 en ok_opa

        #buscar operando b
            if (REG[inst.rs].ok == 1 and REG[inst.rs].ciclo_ok < ciclo):
            # cargar operando en opb y validarlo en ok_opb
            else:
        # linea ROB que proporicona el operando
        # cargar etiqueta ROB en opb y 0 en ok_opb
        linea_aux.inm = inst.inm

        #Insertar linea aux en ER correspondiente
        if (inst.cod == "add" or inst.cod == "sub"):
            tipo = ALU
        elif(inst.cod == "load" or inst.cod == "store"):
            tipo = MEM
        elif(inst.cod == "mult"):
            tipo = MULT

        # linea = p_er_cola[tipo]
        # insertar en ER[tipo][linea]
        # actualizar p_er_cola[tipo]

        if (inst.cod == "sw"):
            linea_rob.destino = 0
        else:
            linea_rob.destino = inst.rd

        #actualizar p_rob_cola +1


if __name__ == '__main__':
    int p_er_cola = [0,0,0]
    # Inicializamos estructuras (Registros, memoria de datos y memoria de isntrucciones)
    instrucciones = read_data()
    REG, DAT, INS, ROB = iniciarEstructuras(instrucciones)
    ER = iniciarER(INS)
    PC = 0
    ciclo = 1

    inst_prog = len(instrucciones)
    inst_rob = 0

    while (inst_rob > 0) or (inst_prog > 0):
        etapa_ID_ISS()
        etapa_EX()
        etapa_WD()
        etapa_COMMIT()

        ciclos = ciclos+1

        mostrar_ER(ER)
        mostrar_ROB(ROB)
        mostrar_REG(REG)

















