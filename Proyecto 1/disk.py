import os
import sys
import time
import random
import Structs
import struct
import main as main


class Disk:
    def __init__(self):
        pass



    @staticmethod
    def validarDatos(tokens):
        size = ""
        fit = ""
        unit = ""
        path = ""
        error = False
        for token in tokens:
            tk = token[:token.find('=')]
            token = token[token.find('=') + 1:]
            if main.Scanner.comparar(tk, "fit"):
                if not fit:
                    fit = token.upper()
                else:
                    error = True
                    print("\tMKDISK: parametro f repetido en el comando", tk)
            elif main.Scanner.comparar(tk, "size"):
                if not size:
                    size = token
                else:
                    error = True
                    print("\tMKDISK: parametro SIZE repetido en el comando", tk)
            elif main.Scanner.comparar(tk, "unit"):
                if not unit:
                    unit = token.upper()
                else:
                    error = True
                    print("\tMKDISK: parametro U repetido en el comando", tk)
            elif main.Scanner.comparar(tk, "path"):
                if not path:
                    path = token
                else:
                    error = True
                    print("\tMKDISK: parametro PATH repetido en el comando", tk)
            else:
                error = True
                print("\tMKDISK: no se esperaba el parametro", tk)
                break

        if not fit:
            fit = "FF"
        if not unit:
            unit = "M"
        if error:
            return

        if not path and not size:
            print("\tERROR: Se requiere parametro Path y Size para el comando MKDISK")
        elif not path:
            print("\tERROR: Se requiere parametro Path para el comando MKDISK")
        elif not size:
            print("\tERROR: Se requiere parametro Size para el comando MKDISK")
        elif fit not in ["BF", "FF", "WF"]:
            print("\tERROR: Valores en parametro fit del comando MKDISK no esperados")
        elif unit not in ["K", "M"]:
            print("\tERROR: Valores en parametro unit del comando MKDISK no esperados")
        else:
            Disk.make(size, fit, unit, path)

    @staticmethod
    def make(s, f, u, path):
        disco = Structs.MBR()
        try:
            size = int(s)
            if size <= 0:
                print("\tERROR: El parámetro size del comando MKDISK debe ser mayor a 0")
                return

            if u == "M":
                size = 1024 * 1024 * size
            elif u == "K":
                size = 1024 * size

            f = f[0].upper()
            disco.mbr_tamano = size
            disco.mbr_fecha_creacion = int(time.time())
            disco.disk_fit = f
            disco.mbr_disk_signature = random.randint(100, 9999)

            if os.path.exists(path):
                print("\tERROR: Disco ya existente en la ruta: "+path)
                return

            folder_path = os.path.dirname(path)
            os.makedirs(folder_path, exist_ok=True)

            disco.mbr_Partition_1 = Structs.Particion()
            disco.mbr_Partition_2 = Structs.Particion()
            disco.mbr_Partition_3 = Structs.Particion()
            disco.mbr_Partition_4 = Structs.Particion()

            if path.startswith("\""):
                path = path[1:-1]

            if not path.endswith(".dk"):
                print("\tERROR: Extensión de archivo no válida para la creación del Disco.")
                return

            try:
                with open(path, "w+b") as file:
                    file.write(b"\x00")
                    file.seek(size - 1)
                    file.write(b"\x00")
                    file.seek(0)
                    file.write(bytes(disco))
                print("\t>>>> MKDISK: Disco creado exitosamente <<<<")
            except Exception as e:
                print(e)
                print("\tERROR: Error al crear el disco en la ruta: "+path)
        except ValueError:
            print("\tERROR: El parámetro size del comando MKDISK debe ser un número entero")

    @staticmethod
    def rmdisk(tokens):
        path = ""
        if len(tokens) == 0 or len(tokens) > 1:
            print("\tERROR: Se requiere parametro Path para el comando RMDISK")
            return
        
        for token in tokens:
            tk, _, token = token.partition("=")
            if main.Scanner.comparar(tk, "path"):
                path = token
            else:
                path = ""
                print("\tERROR: Parametro \""+tk+"\" no esperado en el comando RMDISK") 
                return

        if path:
            if path.startswith("\"") and path.endswith("\""):
                path = path[1:-1]

            try:
                if os.path.isfile(path):
                    if not path.endswith(".dk"):
                        print("\tERROR: Extensión de archivo no válida para la eliminación del Disco.") 
                    if  main.Scanner.confirmar("Desea eliminar el archivo: "+path+"?"):
                        os.remove(path)
                        print("\t>>>> RMDISK: Disco eliminado exitosamente <<<<") 
                    else:
                        print("\t>>>> RMDISK: Eliminación del disco cancelada correctamente <<<<") 
                else:
                    print("\tERROR: El disco no existe en la ruta indicada.") 
            except Exception as e:
                print("\tERROR: Error al intentar eliminar el disco: "+str(e)) 

    @staticmethod
    def rep(tokens):
        path = ""
        if len(tokens) == 0 or len(tokens) > 1:
            print("\tERROR: Se requiere parametro Path para el comando RMDISK")
            return
        
        for token in tokens:
            tk, _, token = token.partition("=")
            if main.Scanner.comparar(tk, "path"):
                path = token
            else:
                path = ""
                print("\tERROR: Parametro \""+tk+"\" no esperado en el comando RMDISK") 
                return

        if path:
            if path.startswith("\"") and path.endswith("\""):
                path = path[1:-1]

        try: 
            mbr_format = "<iiiiB"
            mbr_size = struct.calcsize(mbr_format)
            with open(path, "rb") as file:
                mbr_data = file.read(mbr_size)
                mbr = Structs.MBR()
                (mbr.mbr_tamano, mbr.mbr_fecha_creacion, mbr.mbr_disk_signature, disk_fit, *_) = struct.unpack(mbr_format, mbr_data)
                mbr.disk_fit = chr(disk_fit % 128) 

            print("\tMBR tamaño:", mbr.mbr_tamano)
            print("\tMBR fecha creación:", mbr.mbr_fecha_creacion)
            print("\tDisco fit:", mbr.disk_fit)
            print("\tMBR disk signature:", mbr.mbr_disk_signature)

        except Exception as e:
            print("\tERROR: No se pudo leer el disco en la ruta: " + path+", debido a: "+str(e))

    @staticmethod
    def fdisk(tokens):
        eliminar = False
        for current in tokens:
            id = (current[:current.find('=')]).lower()
            current = current[current.find('=') + 1:]
            if current[:1] == "\"":
                current = current[1:-1]
            if main.Scanner.comparar(id, "delete"):
                eliminar = True

        if not eliminar:
            required = ["size", "path", "name"]
            size = ""
            unit = "k"
            path = ""
            type = "P"
            fit = "WF"
            name = ""
            add = ""

            for current in tokens:
                id = (current[:current.find('=')]).lower()
                current = current[current.find('=') + 1:]
                if current[:1] == "\"":
                    current = current[1:-1]

                if main.Scanner.comparar(id, "size"):
                    if id in required:
                        required.remove(id)
                        size = current
                elif main.Scanner.comparar(id, "unit"):
                    unit = current
                elif main.Scanner.comparar(id, "path"):
                    if id in required:
                        required.remove(id)
                        path = current
                elif main.Scanner.comparar(id, "type"):
                    type = current
                elif main.Scanner.comparar(id, "fit"):
                    fit = current
                elif main.Scanner.comparar(id, "name"):
                    if id in required:
                        required.remove(id)
                        name = current
                elif main.Scanner.comparar(id, "add"):
                    add = current
                    if "size" in required:
                        required.remove("size")
                        size = current

            if required:
                print("\tERROR: Faltan parámetros obligatorios para el comando FDISK") 
                return
            if not add:
                Disk.generarParticion(size, unit, path, type, fit, name, add)
            else:
                print("SE AGREGARA ESPACIO A LA PARTICION")
                #agregarParticion(add, unit, name, path)
        else:
            required = ["path", "name", "delete"]
            elimi = ""
            path = ""
            name = ""

            for current in tokens:
                id = (current[:current.find('=')]).lower()
                current = current[id.length() + 1:]
                if current[:1] == "\"":
                    current = current[1:-1]

                if main.Scanner.comparar(id, "path"):
                    if id in required:
                        required.remove(id)
                        path = current
                elif main.Scanner.comparar(id, "name"):
                    if id in required:
                        required.remove(id)
                        name = current
                elif main.Scanner.comparar(id, "delete"):
                    if id in required:
                        required.remove(id)
                        elimi = current

            if required:
                print("\tERROR: Faltan parámetros obligatorios para el comando FDISK junto con el parámetro DELETE") 
                return
            print("SE ELIMINARA LA PARTICION")
            #eliminarParticion(elimi, path, name)

    @staticmethod
    def generarParticion(s, u, p, t, f, n, a):
        try:
            i = int(s)
            if i <= 0:
                raise RuntimeError("-size debe de ser mayor que 0")
            
            if u.lower() in ["b", "k", "m"]:
                if u.lower() != "b":
                    if u.lower() == "k":
                        i *= 1024
                    else:
                        i *= 1024 * 1024
            else:
                raise RuntimeError("-unit no contiene los valores esperados...")
            
            if p[:1] == "\"":
                p = p[1:-1]
            
            if t.lower() not in ["p", "e", "l"]:
                raise RuntimeError("-type no contiene los valores esperados...")
            
            if f.lower() not in ["bf", "ff", "wf"]:
                raise RuntimeError("-fit no contiene los valores esperados...")
            
            try:
                mbr = Structs.MBR()
                with open(p, "rb") as file:
                    mbr_data = file.read()
                    mbr.mbr_tamano = struct.unpack("<i", mbr_data[:4])[0]
                    mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
                    mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
                    mbr.disk_fit = mbr_data[12:14].decode('utf-8')

                    partition_size = struct.calcsize("<iii16s")
                    partition_data = mbr_data[14:14 + partition_size]
                    mbr.mbr_Partition_1.__setstate__(partition_data)
                     
                    partition_data = mbr_data[13 + partition_size:14 + 2 * partition_size]
                    mbr.mbr_Partition_2.__setstate__(partition_data)
                    
                    partition_data = mbr_data[12 + 2 * partition_size:14 + 3 * partition_size]
                    mbr.mbr_Partition_3.__setstate__(partition_data)
                    
                    partition_data = mbr_data[11 + 3 * partition_size:14 + 4 * partition_size]
                    mbr.mbr_Partition_4.__setstate__(partition_data)

            except Exception as e:
                print(e)

            
            partitions = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
            between = []
            used = 0
            ext = 0
            c = 1
            base = sys.getsizeof(mbr) 
            extended = Structs.Particion()
            for prttn in partitions:
                if prttn.part_status == '1':
                    trn = Structs.Transition()
                    trn.partition = c
                    trn.start = prttn.part_start
                    trn.end = prttn.part_start + prttn.part_size
                    trn.before = trn.start - base
                    base = trn.end
                    if used != 0:
                        between[used - 1].after = trn.start - (between[used - 1].end)
                    between.append(trn)
                    used += 1

                    if prttn.part_type.lower() == 'e':
                        ext += 1
                        extended = prttn
                else: 
                    partitions[c - 1] = Structs.Particion()

                if used == 4 and t.lower() != "l":
                    raise RuntimeError("Limite de particiones alcanzado")
                elif ext == 1 and t.lower() == "e":
                    raise RuntimeError("Solo se puede crear una particion Extendida.")

                mbr.mbr_Partition_1 = partitions[0]
                mbr.mbr_Partition_2 = partitions[1]
                mbr.mbr_Partition_3 = partitions[2]
                mbr.mbr_Partition_4 = partitions[3]
                
                c += 1
            
            if ext == 0 and t.lower() == "l":
                raise RuntimeError("No existe particion Extendida para crear la Logica")
            
            if used != 0:
                between[-1].after = mbr.mbr_tamano - between[-1].end
            
            try:
                Disk.buscarParticiones(mbr, n, p)
                print("FDISK", "El nombre: "+n+" ya existe en el disco")
                return
            except Exception as e:
                print(e)
            
            temporal = Structs.Particion()
            temporal.part_status = '1'
            temporal.part_size = i
            temporal.part_type = t[0].upper()
            temporal.part_fit = f[0].upper()
            temporal.part_name = n
            
            if t.lower() == "l": 
                Disk.logica(temporal, extended, p)
                return
            
            mbr = Disk.ajustar(mbr, temporal, between, partitions, used)
            with open(p, "rb+") as bfile:
                bfile.write(mbr.__bytes__())
                if t.lower() == "e":
                    ebr = Structs.EBR()
                    ebr.part_start = startValue 
                    bfile.seek(startValue, 0)
                    bfile.write(ebr.__bytes__())
                    print("FDISK", "partición extendida:", n, "creada correctamente")
                    return
                print("FDISK", "partición primaria:", n, "creada correctamente")
        except ValueError as e: 
            print("FDISK", "-size debe ser un entero")
        except Exception as e: 
            print("FDISK", str(e))

    @staticmethod
    def get_particiones(disco):
        particiones = []
        particiones.append(disco.mbr_Partition_1)
        particiones.append(disco.mbr_Partition_2)
        particiones.append(disco.mbr_Partition_3)
        particiones.append(disco.mbr_Partition_4)
        return particiones

    @staticmethod
    def get_logicas(partition, p):
        ebrs = []

        with open(p, "rb+") as file:
            start_position = partition.part_start -1
            if start_position < 0:
                start_position = 0
                
            file.seek(start_position, 0)
            tmp_data = file.read(struct.calcsize("c2s3i3i16s"))

            while len(tmp_data) == struct.calcsize("c2s3i3i16s"):
                tmp = Structs.EBR()
                tmp.__setstate__(tmp_data)
                if tmp.part_next != -1 :
                    ebrs.append(tmp)
                    file.seek(tmp.part_next-1, 0)
                    tmp_data = file.read(struct.calcsize("c2s3i3i16s"))
                else:
                    break

        return ebrs

    @staticmethod
    def logica(partition, ep, p):
        nlogic = Structs.EBR()
        nlogic.part_status = '1'
        nlogic.part_fit = partition.part_fit
        nlogic.part_size = partition.part_size
        nlogic.part_next = -1
        nlogic.part_name = partition.part_name

        with open(p, "rb+") as file:
            file.seek(0)
            tmp = Structs.EBR()
            file.seek(ep.part_start -1)
            tmp_data = file.read(struct.calcsize("c2s3i3i16s"))
            tmp.__setstate__(tmp_data)
            size = 0
            while True:
                size += struct.calcsize("c2s3i3i16s") + tmp.part_size
                if (tmp.part_status == '0' or tmp.part_status == '\x00') and tmp.part_next == -1:
                    nlogic.part_start = tmp.part_start
                    nlogic.part_next = nlogic.part_start + nlogic.part_size + struct.calcsize("c2s3i3i16s")
                    if (ep.part_size - size) <= nlogic.part_size:
                        raise RuntimeError("no hay espacio para más particiones lógicas")
                    file.seek(nlogic.part_start-1) 
                    file.write(nlogic.__bytes__())
                    file.seek(nlogic.part_next)
                    addLogic = Structs.EBR()
                    addLogic.part_status = '0'
                    addLogic.part_next = -1
                    addLogic.part_start = nlogic.part_next
                    file.seek(addLogic.part_start)
                    file.write(addLogic.__bytes__())
                    name = nlogic.part_name
                    print(f"partición lógica: {name}, creada correctamente.")
                    return
                file.seek(tmp.part_next-1)
                tmp_data = file.read(struct.calcsize("c2s3i3i16s"))
                tmp.__setstate__(tmp_data)
    
    @staticmethod
    def ajustar(mbr, p, t, ps, u):
        if u == 0:
            p.part_start = sys.getsizeof(mbr)
            startValue = p.part_start
            update_start_value(p.part_start)
            mbr.mbr_Partition_1 = p
            return mbr
        else:
            usar = Structs.Transition()
            c = 0
            for tr in t:
                if c == 0:
                    usar = tr
                    c += 1
                    continue

                if mbr.disk_fit[0].upper() == 'F':
                    if usar.before >= p.part_size or usar.after >= p.part_size:
                        break
                    usar = tr
                elif mbr.disk_fit[0].upper() == 'B':
                    if usar.before < p.part_size or usar.after < p.part_size:
                        usar = tr
                    else:
                        if tr.before >= p.part_size or tr.after >= p.part_size:
                            b1 = usar.before - p.part_size
                            a1 = usar.after - p.part_size
                            b2 = tr.before - p.part_size
                            a2 = tr.after - p.part_size

                            if (b1 < b2 and b1 < a2) or (a1 < b2 and a1 < a2):
                                c += 1
                                continue
                            usar = tr
                elif mbr.disk_fit[0].upper() == 'W':
                    if usar.before < p.part_size or usar.after < p.part_size:
                        usar = tr
                    else:
                        if tr.before >= p.part_size or tr.after >= p.part_size:
                            b1 = usar.before - p.part_size
                            a1 = usar.after - p.part_size
                            b2 = tr.before - p.part_size
                            a2 = tr.after - p.part_size
                            if (b1 > b2 and b1 > a2) or (a1 > b2 and a1 > a2):
                                c += 1
                                continue
                            usar = tr
                c += 1

            if usar.before >= p.part_size or usar.after >= p.part_size:
                if mbr.disk_fit[0].upper() == 'F':
                    if usar.before >= p.part_size:
                        p.part_start = (usar.start - usar.before)
                        startValue = p.part_start
                        update_start_value(p.part_start)
                    else:
                        p.part_start = usar.end
                        startValue = p.part_start
                        update_start_value(p.part_start)
                elif mbr.disk_fit[0].upper() == 'B':
                    b1 = usar.before - p.part_size
                    a1 = usar.after - p.part_size

                    if (usar.before >= p.part_size and b1 < a1) or usar.after < p.part_start:
                        p.part_start = (usar.start - usar.before)
                        startValue = p.part_start
                        update_start_value(p.part_start)
                    else:
                        p.part_start = usar.end
                        startValue = p.part_start
                        update_start_value(p.part_start)
                elif mbr.disk_fit[0].upper() == 'W':
                    b1 = usar.before - p.part_size
                    a1 = usar.after - p.part_size

                    if (usar.before >= p.part_size and b1 > a1) or usar.after < p.part_start:
                        p.part_start = (usar.start - usar.before)
                        startValue = p.part_start
                        update_start_value(p.part_start)
                    else:
                        p.part_start = usar.end
                        startValue = p.part_start
                        update_start_value(p.part_start)

                partitions = [Structs.Particion() for _ in range(4)]

                for i in range(len(ps)):
                    partitions[i] = ps[i]
                
                for i in range(len(partitions)):
                    if partitions[i].part_status == '0':
                        partitions[i] = p
                        break
                mbr.mbr_Partition_1 = partitions[0]
                mbr.mbr_Partition_2 = partitions[1]
                mbr.mbr_Partition_3 = partitions[2]
                mbr.mbr_Partition_4 = partitions[3]
                return mbr
            else:
                raise RuntimeError("no hay espacio suficiente")
    
    @staticmethod
    def buscarParticiones(mbr, name, path):
            partitions = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
            ext = False
            extended = Structs.Particion()

            for partition in partitions:
                if partition.part_status == '1':
                    if partition.part_name == name:
                        return partition
                    elif partition.part_type == 'E':
                        ext = True
                        extended = partition

            if ext:
                ebrs = Disk.get_logicas(extended, path)
                for ebr in ebrs:
                    if ebr.part_status == '1':
                        if ebr.part_name == name:
                            tmp = Structs.Particion()
                            tmp.part_status = '1'
                            tmp.part_type = 'L'
                            tmp.part_fit = ebr.part_fit
                            tmp.part_start = ebr.part_start
                            tmp.part_size = ebr.part_size
                            tmp.part_name = ebr.part_name
                            return tmp
            raise RuntimeError("Creando la partición: " + name + "...")


def update_start_value(new_value):
    global startValue
    startValue = new_value
    