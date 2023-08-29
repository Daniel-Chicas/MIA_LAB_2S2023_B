import os
import struct
import mount as Mount
import Structs
import main as main

class Sesion:
    def __init__(self):
        self.id_user = 0
        self.id_grp = 0
        self.inicioSuper = 0
        self.inicioJournal = 0
        self.tipo_sistema = 0
        self.direccion = ""
        self.fit = ""

class UsuarioActivo:
    def __init__(self):
        self.user = ""
        self.password = ""
        self.id = ""
        self.uid = 0

actualSesion = Sesion()
logueado = UsuarioActivo()


class Usuarios:
    def __init__(self, m = Mount.Mount()):  
        self.mount = m

    def login(self, context, m):
        self.mount = m
        id = ""
        user = ""
        password = ""

        for current in context:
            id_ = current[:current.find('=')].strip().lower()
            current = current[current.find('=') + 1:]
            
            if current.startswith("\""):
                current = current[1:-1]

            if id_ == "id":
                id = current
            elif id_ == "user":
                user = current
            elif id_ == "pass":
                password = current

        if id == "" or user == "" or password == "":
            print("LOGIN: Necesita parámetros obligatorios")
            return False

        return self.sesion_activa(user, password, id)

    def sesion_activa(self, u, p, id): 
        tamanioBloquesCarpetas = len(bytes(Structs.BloquesCarpetas()))

        try:
            path = ""
            path, partition = self.mount.getmount(id, path)

            sprTemp = Structs.SuperBloque()  # Crear una instancia de SuperBloque
            bytes_super_bloque = bytes(sprTemp)  # Obtener los bytes de la instancia

            recuperado = bytearray(len(bytes_super_bloque))  # Crear un bytearray del mismo tamaño
            with open(path, "rb") as archivo:
                archivo.seek(partition.part_start - 1)
                archivo.readinto(recuperado)

            sprTemp.s_filesystem_type = struct.unpack("<i", recuperado[:4])[0]
            sprTemp.s_inodes_count = struct.unpack("<i", recuperado[4:8])[0]
            sprTemp.s_blocks_count = struct.unpack("<i", recuperado[8:12])[0]
            sprTemp.s_free_blocks_count = struct.unpack("<i", recuperado[12:16])[0]
            sprTemp.s_free_inodes_count = struct.unpack("<i", recuperado[16:20])[0]
            sprTemp.s_mtime = struct.unpack("<d", recuperado[20:28])[0]
            sprTemp.s_umtime = struct.unpack("<d", recuperado[28:36])[0]
            sprTemp.s_mnt_count = struct.unpack("<i", recuperado[36:40])[0]
            sprTemp.s_magic = struct.unpack("<i", recuperado[40:44])[0]
            sprTemp.s_inode_size = struct.unpack("<i", recuperado[44:48])[0]
            sprTemp.s_block_size = struct.unpack("<i", recuperado[48:52])[0]
            sprTemp.s_first_ino = struct.unpack("<i", recuperado[52:56])[0]
            sprTemp.s_first_blo = struct.unpack("<i", recuperado[56:60])[0]
            sprTemp.s_bm_inode_start = struct.unpack("<i", recuperado[60:64])[0]
            sprTemp.s_bm_block_start = struct.unpack("<i", recuperado[64:68])[0]
            sprTemp.s_inode_start = struct.unpack("<i", recuperado[68:72])[0]
            sprTemp.s_block_start = struct.unpack("<i", recuperado[72:76])[0] 

            fb = Structs.BloquesArchivos()
            bytes_bloque_archivo = bytes(fb)
            usuariosTXT = bytearray(len(bytes_bloque_archivo))
            with open(path, "rb") as rfile: 
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.readinto(usuariosTXT) 

            fb.b_content = struct.unpack("<64s", usuariosTXT[:64])[0]

            txt = usuariosTXT.decode('ascii') 
            vctr = self.get_elements(txt, '\n')
            for line in vctr:
                if line[2] == 'U' or line[2] == 'u':
                    in_ = self.get_elements(line, ',')
                    if main.Scanner.comparar(in_[3], u) and main.Scanner.comparar(in_[4], p) and in_[0] != '0': 
                        print("\tUSUARIO", u, "LOGUEADO CORRECTAMENTE")
                        global logueado
                        logueado.id = id
                        logueado.user = u
                        logueado.password = p
                        logueado.uid = int(in_[0])


                        return True
            raise RuntimeError("no hay credenciales similares")
        except Exception as e:
            print(f"LOGIN: {str(e)}")
            return False

    def get_elements(self, txt, c):
        v = []
        line = ""
        if c == ',':
            txt += ','
        for x in txt:
            if x == c:
                v.append(line)
                line = ""
                continue
            line += x

        if not v:
            raise RuntimeError("no hay archivo txt")
        return v

    def logout(self):
        global logueado
        print("Cerrando sesión...")
        print("¡ADIÓS " + logueado.user + ", espero volver a verte!") 
        logueado = UsuarioActivo()
        actualSesion = Sesion()
        return False
     
    def validarDatosGrp(self, context, action):
        name = ""
        for current in context:
            id_ = current[:current.find('=')]
            current = current[current.find('=') + 1:]
            if current[:1] == "\"":
                current = current[1:-1]
            elif main.Scanner.comparar(id_, "name"):
                name = current

        if name == "":
            print(action + "GRP", "No se encontró el parámetro \"-name\"")
            return
        elif main.Scanner.comparar(action, "MK"):
            self.mkgrp(name)
        else:
            self.rmgrp(name)

    def mkgrp(self, n):
        tamanioBloquesCarpetas = len(bytes(Structs.BloquesCarpetas()))
        try:
            global logueado
            if not main.Scanner.comparar(logueado.user, "root"):
                raise RuntimeError("Solo el usuario ROOT puede acceder a estos comandos")

            path = ""
            path, partition = self.mount.getmount(logueado.id, path)
            sprTemp = Structs.SuperBloque()  # Crear una instancia de SuperBloque
            bytes_super_bloque = bytes(sprTemp)  # Obtener los bytes de la instancia

            recuperado = bytearray(len(bytes_super_bloque))  # Crear un bytearray del mismo tamaño
            with open(path, "rb") as archivo:
                archivo.seek(partition.part_start - 1)
                archivo.readinto(recuperado)

            sprTemp.s_filesystem_type = struct.unpack("<i", recuperado[:4])[0]
            sprTemp.s_inodes_count = struct.unpack("<i", recuperado[4:8])[0]
            sprTemp.s_blocks_count = struct.unpack("<i", recuperado[8:12])[0]
            sprTemp.s_free_blocks_count = struct.unpack("<i", recuperado[12:16])[0]
            sprTemp.s_free_inodes_count = struct.unpack("<i", recuperado[16:20])[0]
            sprTemp.s_mtime = struct.unpack("<d", recuperado[20:28])[0]
            sprTemp.s_umtime = struct.unpack("<d", recuperado[28:36])[0]
            sprTemp.s_mnt_count = struct.unpack("<i", recuperado[36:40])[0]
            sprTemp.s_magic = struct.unpack("<i", recuperado[40:44])[0]
            sprTemp.s_inode_size = struct.unpack("<i", recuperado[44:48])[0]
            sprTemp.s_block_size = struct.unpack("<i", recuperado[48:52])[0]
            sprTemp.s_first_ino = struct.unpack("<i", recuperado[52:56])[0]
            sprTemp.s_first_blo = struct.unpack("<i", recuperado[56:60])[0]
            sprTemp.s_bm_inode_start = struct.unpack("<i", recuperado[60:64])[0]
            sprTemp.s_bm_block_start = struct.unpack("<i", recuperado[64:68])[0]
            sprTemp.s_inode_start = struct.unpack("<i", recuperado[68:72])[0]
            sprTemp.s_block_start = struct.unpack("<i", recuperado[72:76])[0] 

            fb = Structs.BloquesArchivos()
            bytes_bloque_archivo = bytes(fb)
            usuariosTXT = bytearray(len(bytes_bloque_archivo))
            with open(path, "rb") as rfile: 
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.readinto(usuariosTXT) 

            fb.b_content = struct.unpack("<64s", usuariosTXT[:64])[0]

            txt = usuariosTXT.decode('ascii') 
            vctr = self.get_elements(txt, '\n')
            c = 0
            txttmp = ""
            for line in vctr:
                if line[2] == 'G' or line[2] == 'g':
                    c += 1
                    in_ = line.split(',')
                    if in_[2] == n:
                        if line[0] == '0':
                            pass
                        else:
                            raise RuntimeError("el grupo ya existe")
                    else:
                        txttmp += line + "\n"
                else:
                    txttmp += line + "\n"
            txttmp += f"{c + 1},G,{n}\n"
            fb.b_content = txttmp

            with open(path, "rb+") as rfile:
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.write(bytes(fb))
                print("MKGRP", "grupo "+n+" creado correctamente")
        except Exception as e:
            print("MKGRP", str(e))

    def rmgrp(self, n):
        tamanioBloquesCarpetas = len(bytes(Structs.BloquesCarpetas()))
        try:
            global logueado
            if not main.Scanner.comparar(logueado.user, "root"):
                raise RuntimeError("Solo el usuario ROOT puede acceder a estos comandos")

            path = ""
            path, partition = self.mount.getmount(logueado.id, path)
            sprTemp = Structs.SuperBloque()  # Crear una instancia de SuperBloque
            bytes_super_bloque = bytes(sprTemp)  # Obtener los bytes de la instancia

            recuperado = bytearray(len(bytes_super_bloque))  # Crear un bytearray del mismo tamaño
            with open(path, "rb") as archivo:
                archivo.seek(partition.part_start - 1)
                archivo.readinto(recuperado)

            sprTemp.s_filesystem_type = struct.unpack("<i", recuperado[:4])[0]
            sprTemp.s_inodes_count = struct.unpack("<i", recuperado[4:8])[0]
            sprTemp.s_blocks_count = struct.unpack("<i", recuperado[8:12])[0]
            sprTemp.s_free_blocks_count = struct.unpack("<i", recuperado[12:16])[0]
            sprTemp.s_free_inodes_count = struct.unpack("<i", recuperado[16:20])[0]
            sprTemp.s_mtime = struct.unpack("<d", recuperado[20:28])[0]
            sprTemp.s_umtime = struct.unpack("<d", recuperado[28:36])[0]
            sprTemp.s_mnt_count = struct.unpack("<i", recuperado[36:40])[0]
            sprTemp.s_magic = struct.unpack("<i", recuperado[40:44])[0]
            sprTemp.s_inode_size = struct.unpack("<i", recuperado[44:48])[0]
            sprTemp.s_block_size = struct.unpack("<i", recuperado[48:52])[0]
            sprTemp.s_first_ino = struct.unpack("<i", recuperado[52:56])[0]
            sprTemp.s_first_blo = struct.unpack("<i", recuperado[56:60])[0]
            sprTemp.s_bm_inode_start = struct.unpack("<i", recuperado[60:64])[0]
            sprTemp.s_bm_block_start = struct.unpack("<i", recuperado[64:68])[0]
            sprTemp.s_inode_start = struct.unpack("<i", recuperado[68:72])[0]
            sprTemp.s_block_start = struct.unpack("<i", recuperado[72:76])[0] 

            fb = Structs.BloquesArchivos()
            bytes_bloque_archivo = bytes(fb)
            usuariosTXT = bytearray(len(bytes_bloque_archivo))
            with open(path, "rb") as rfile: 
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.readinto(usuariosTXT) 

            fb.b_content = struct.unpack("<64s", usuariosTXT[:64])[0]

            txt = usuariosTXT.decode('ascii') 
            vctr = self.get_elements(txt, '\n')
            c = 0
            txttmp = ""
            for line in vctr:
                if (line[2] == 'G' or line[2] == 'g') and line[0] != '0':
                    in_ = line.split(',')
                    if in_[2] == n:
                        exist = True
                        txttmp += f"0,G,{in_[2]}\n"
                        continue
                txttmp += line + "\n"
            if not exist:
                raise RuntimeError("el grupo no existe")
            
            fb.b_content = txttmp
            with open(path, "rb+") as rfile:
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.write(bytes(fb))
                print("RMGRP", "grupo "+n+" eliminado correctamente")
        except Exception as e:
            print("RMGRP", str(e))

    def validarDatosusr(self, context, action):
        usr = ""
        pwd = ""
        grp = ""

        for current in context:
            id_ = current[:current.find('=')]
            current = current[current.find('=') + 1:]
            if current[:1] == "\"":
                current = current[1:-1]

            if main.Scanner.comparar(id_, "user"):
                usr = current
            elif main.Scanner.comparar(id_, "pass"):
                pwd = current
            elif main.Scanner.comparar(id_, "grp"):
                grp = current

        if main.Scanner.comparar(action, "MK"):
            if usr == "" or pwd == "" or grp == "":
                print(action + "GRP", "Necesita parámetros obligatorios")
            else:
                self.mkusr(usr, pwd, grp)
        else:
            if usr == "":
                print(action + "GRP", "Necesita parámetros obligatorios")
            else:
                self.rmusr(usr)

    def mkusr(self, usr, pwd, grp):
        tamanioBloquesCarpetas = len(bytes(Structs.BloquesCarpetas()))
        try:
            global logueado
            if not main.Scanner.comparar(logueado.user, "root"):
                raise RuntimeError("Solo el usuario ROOT puede acceder a estos comandos")

            path = ""
            path, partition = self.mount.getmount(logueado.id, path)
            sprTemp = Structs.SuperBloque()  # Crear una instancia de SuperBloque
            bytes_super_bloque = bytes(sprTemp)  # Obtener los bytes de la instancia

            recuperado = bytearray(len(bytes_super_bloque))  # Crear un bytearray del mismo tamaño
            with open(path, "rb") as archivo:
                archivo.seek(partition.part_start - 1)
                archivo.readinto(recuperado)

            sprTemp.s_filesystem_type = struct.unpack("<i", recuperado[:4])[0]
            sprTemp.s_inodes_count = struct.unpack("<i", recuperado[4:8])[0]
            sprTemp.s_blocks_count = struct.unpack("<i", recuperado[8:12])[0]
            sprTemp.s_free_blocks_count = struct.unpack("<i", recuperado[12:16])[0]
            sprTemp.s_free_inodes_count = struct.unpack("<i", recuperado[16:20])[0]
            sprTemp.s_mtime = struct.unpack("<d", recuperado[20:28])[0]
            sprTemp.s_umtime = struct.unpack("<d", recuperado[28:36])[0]
            sprTemp.s_mnt_count = struct.unpack("<i", recuperado[36:40])[0]
            sprTemp.s_magic = struct.unpack("<i", recuperado[40:44])[0]
            sprTemp.s_inode_size = struct.unpack("<i", recuperado[44:48])[0]
            sprTemp.s_block_size = struct.unpack("<i", recuperado[48:52])[0]
            sprTemp.s_first_ino = struct.unpack("<i", recuperado[52:56])[0]
            sprTemp.s_first_blo = struct.unpack("<i", recuperado[56:60])[0]
            sprTemp.s_bm_inode_start = struct.unpack("<i", recuperado[60:64])[0]
            sprTemp.s_bm_block_start = struct.unpack("<i", recuperado[64:68])[0]
            sprTemp.s_inode_start = struct.unpack("<i", recuperado[68:72])[0]
            sprTemp.s_block_start = struct.unpack("<i", recuperado[72:76])[0] 

            fb = Structs.BloquesArchivos()
            bytes_bloque_archivo = bytes(fb)
            usuariosTXT = bytearray(len(bytes_bloque_archivo))
            with open(path, "rb") as rfile: 
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.readinto(usuariosTXT) 

            fb.b_content = struct.unpack("<64s", usuariosTXT[:64])[0]

            txt = usuariosTXT.decode('ascii') 
            vctr = self.get_elements(txt, '\n')
            c = 0
            txttmp = ""
            for line in vctr:
                if (line[2] == 'U' or line[2] == 'u') and line[0] != '0':
                    c += 1
                    in_ = self.get_elements(line, ',')
                    if in_[3] == usr:
                        raise RuntimeError("el usuario ya existe")
                    else:
                        txttmp += line + "\n"
                else:
                    txttmp += line + "\n"
            txttmp += str(c + 1) + ",U," + grp + "," + usr + "," + pwd + "\n"
            fb.b_content = txttmp

            with open(path, "rb+") as rfile:
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.write(bytes(fb))
                print("MKUSR", "Usuario "+usr+" creado correctamente") 
        except Exception as e:
            print("MKUSR", str(e))

    def rmusr(self, usr):
        tamanioBloquesCarpetas = len(bytes(Structs.BloquesCarpetas()))
        try:
            global logueado
            if not main.Scanner.comparar(logueado.user, "root"):
                raise RuntimeError("Solo el usuario ROOT puede acceder a estos comandos")

            path = ""
            path, partition = self.mount.getmount(logueado.id, path)
            sprTemp = Structs.SuperBloque()  # Crear una instancia de SuperBloque
            bytes_super_bloque = bytes(sprTemp)  # Obtener los bytes de la instancia

            recuperado = bytearray(len(bytes_super_bloque))  # Crear un bytearray del mismo tamaño
            with open(path, "rb") as archivo:
                archivo.seek(partition.part_start - 1)
                archivo.readinto(recuperado)

            sprTemp.s_filesystem_type = struct.unpack("<i", recuperado[:4])[0]
            sprTemp.s_inodes_count = struct.unpack("<i", recuperado[4:8])[0]
            sprTemp.s_blocks_count = struct.unpack("<i", recuperado[8:12])[0]
            sprTemp.s_free_blocks_count = struct.unpack("<i", recuperado[12:16])[0]
            sprTemp.s_free_inodes_count = struct.unpack("<i", recuperado[16:20])[0]
            sprTemp.s_mtime = struct.unpack("<d", recuperado[20:28])[0]
            sprTemp.s_umtime = struct.unpack("<d", recuperado[28:36])[0]
            sprTemp.s_mnt_count = struct.unpack("<i", recuperado[36:40])[0]
            sprTemp.s_magic = struct.unpack("<i", recuperado[40:44])[0]
            sprTemp.s_inode_size = struct.unpack("<i", recuperado[44:48])[0]
            sprTemp.s_block_size = struct.unpack("<i", recuperado[48:52])[0]
            sprTemp.s_first_ino = struct.unpack("<i", recuperado[52:56])[0]
            sprTemp.s_first_blo = struct.unpack("<i", recuperado[56:60])[0]
            sprTemp.s_bm_inode_start = struct.unpack("<i", recuperado[60:64])[0]
            sprTemp.s_bm_block_start = struct.unpack("<i", recuperado[64:68])[0]
            sprTemp.s_inode_start = struct.unpack("<i", recuperado[68:72])[0]
            sprTemp.s_block_start = struct.unpack("<i", recuperado[72:76])[0] 

            fb = Structs.BloquesArchivos()
            bytes_bloque_archivo = bytes(fb)
            usuariosTXT = bytearray(len(bytes_bloque_archivo))
            with open(path, "rb") as rfile: 
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.readinto(usuariosTXT) 

            fb.b_content = struct.unpack("<64s", usuariosTXT[:64])[0]

            txt = usuariosTXT.decode('ascii') 
            vctr = self.get_elements(txt, '\n')
            c = 0
            txttmp = ""
            for line in vctr:
                if (line[2] == 'U' or line[2] == 'u') and line[0] != '0':
                    in_ = self.get_elements(line, ',')
                    if in_[3] == usr:
                        exist = True
                        txttmp += "0,U," + in_[2] + "," + in_[3] + "," + in_[4] + "\n"
                        continue
                txttmp += line + "\n"
            if not exist:
                raise RuntimeError("el usuario no existe")
            fb.b_content = txttmp

            with open(path, "rb+") as rfile:
                rfile.seek(sprTemp.s_block_start + tamanioBloquesCarpetas)
                rfile.write(bytes(fb))
                print("RMUSR", "Usuario "+usr+" eliminado correctamente") 
        except Exception as e:
            print("MKUSR", str(e)) 
        