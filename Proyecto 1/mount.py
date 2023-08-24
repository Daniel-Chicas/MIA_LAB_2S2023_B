import os
import sys
import time
import random
import Structs
import struct
import main as main
import disk as Disco



class Mount:
    def __init__(self):
        self.alfabeto = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        self.discoMontado = []   
        for _ in range(99): 
            tmp = Structs.DiscoMontado()
            self.discoMontado.append(tmp) 

    def validarDatos(self, context): 
        if not context:
            self.listaMount()
            return
        required = ["name", "path"]
        path = ""
        name = ""

        for current in context:
            id = current.split('=')[0]
            current = current.split('=')[1]
            if current[0] == "\"":
                current = current[1:-1]

            if main.Scanner.comparar(id, "name"):
                if id in required:
                    required.remove(id)
                    name = current
            elif main.Scanner.comparar(id, "path"):
                if id in required:
                    required.remove(id)
                    path = current

        if required:
            print("MOUNT", "requiere ciertos parámetros obligatorios")
            return
        self.mount(path, name)
 
    def mount(self, p, n):
        try:
            if not os.path.exists(p):
                raise RuntimeError("disco no existente")

            disk = Structs.MBR()  # Replace with actual initialization
            try: 
                with open(p, "rb") as file:
                    mbr_data = file.read()
                    disk.mbr_tamano = struct.unpack("<i", mbr_data[:4])[0]
                    disk.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
                    disk.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
                    disk.disk_fit = mbr_data[12:14].decode('utf-8')

                    partition_size = struct.calcsize("<iii16s")
                    partition_data = mbr_data[14:14 + partition_size]
                    disk.mbr_Partition_1.__setstate__(partition_data)
                     
                    partition_data = mbr_data[13 + partition_size:14 + 2 * partition_size]
                    disk.mbr_Partition_2.__setstate__(partition_data)
                    
                    partition_data = mbr_data[12 + 2 * partition_size:14 + 3 * partition_size]
                    disk.mbr_Partition_3.__setstate__(partition_data)
                    
                    partition_data = mbr_data[11 + 3 * partition_size:14 + 4 * partition_size]
                    disk.mbr_Partition_4.__setstate__(partition_data)

            except Exception as e:
                print(e)

            partition = Disco.Disk.buscarParticiones(disk, n, p) 
            if partition.part_type == 'E':
                if partition.part_name == n:
                    raise RuntimeError("no se puede montar una partición extendida")
                else:
                    ebrs = Disco.Disk.get_logicas(partition, p)
                    if ebrs:
                        for ebr in ebrs:
                            if ebr.part_name == n and ebr.part_status == '1':
                                n = ebr.part_name
 
            for i in range(99):
                if self.discoMontado[i].path == p:
                    for j in range(26):
                        if self.discoMontado[i].particiones[j].estado == '0':
                            self.discoMontado[i].particiones[j].estado = '1'
                            self.discoMontado[i].particiones[j].letra = self.alfabeto[j]
                            self.discoMontado[i].particiones[j].nombre = n
                            re = str(i + 1) + self.alfabeto[j]
                            print("MOUNT", "se ha realizado correctamente el mount -id=79" + re)
                            return

            for i in range(99):
                if self.discoMontado[i].estado == '0':
                    self.discoMontado[i].estado = '1'
                    self.discoMontado[i].path = p
                    for j in range(26):
                        if self.discoMontado[i].particiones[j].estado == '0':
                            self.discoMontado[i].particiones[j].estado = '1'
                            self.discoMontado[i].particiones[j].letra = self.alfabeto[j]
                            self.discoMontado[i].particiones[j].nombre = n
                            re = str(i + 1) + self.alfabeto[j]

                            #Para mí era los ID'S se calculaban de la siguiente manera: *Últimos dos dígitos del Carnet + Número + Letra Ejemplo: carnet = 201404106
                            #Id ́s = 061A, 061B, 061C, 062A, 063A
                            
                            print("MOUNT", "se ha realizado correctamente el mount -id=79" + re)
                            return
        except Exception as e:
            print("MOUNT", e)
 
    def validarDatosU(self, context):
        required = ["id"]
        id_ = ""

        for current in context:
            id = current.split('=')[0]
            current = current.split('=')[1]

            if main.Scanner.comparar(id, "id"):
                if id in required:
                    required.remove(id)
                    id_ = current

        if required:
            print("UNMOUNT", "requiere ciertos parámetros obligatorios")
            return
        self.unmount(id_)
 
    def unmount(self, id):
        try:
            if not (id[0] == '7' and id[1] == '9'):
                raise RuntimeError("el primer identificador no es válido")
            past = id
            letter = id[-1]
            id = id[2:-1]
            i = int(id) - 1
            if i < 0:
                raise RuntimeError("identificador de disco inválido")

            for j in range(26):
                if self.discoMontado[i].particiones[j].estado == '1':
                    if self.discoMontado[i].particiones[j].letra == letter:
                        mp = Structs.ParticionMontada()
                        self.discoMontado[i].particiones[j] = mp
                        print("UNMOUNT", "se ha realizado correctamente el unmount -id=" + past)
                        return
            raise RuntimeError("No se encontró el id= " + id + ", no se desmontó nada")
        except ValueError:
            print("UNMOUNT", "identificador de disco incorrecto, debe ser entero")
        except Exception as e:
            print("UNMOUNT", e)
 
    def getmount(self, id, p):
        if not (id[0] == '7' and id[1] == '9'):
            raise RuntimeError("el primer identificador no es válido")
        past = id
        letter = id[-1]
        id = id[2:-1]
        i = int(id) - 1
        if i < 0:
            raise RuntimeError("identificador de disco inválido")

        for j in range(26):
            if self.discoMontado[i].particiones[j].estado == '1':
                if self.discoMontado[i].particiones[j].letra == letter:
                    if not os.path.exists(self.discoMontado[i].path):
                        raise RuntimeError("disco no existente")

                    disk = Structs.MBR()  # Replace with actual initialization
                    with open(self.discoMontado[i].path, "rb") as validate:
                        validate.seek(0)
                        validate.readinto(disk)
                    p[0] = self.discoMontado[i].path
                    return Disco.Disk.buscarParticiones(disk, self.discoMontado[i].particiones[j].nombre, self.discoMontado[i].path)
        raise RuntimeError("partición no existente")
 
    def listaMount(self):
        print("\n<-------------------------- LISTADO DE MOUNTS -------------------------->")
        for i in range(99):
            for j in range(26):
                if self.discoMontado[i].particiones[j].estado == '1':
                    print("> 87" + str(i + 1) + self.alfabeto[j] + ", " + self.discoMontado[i].particiones[j].nombre)
