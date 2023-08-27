import time
import Structs
import mount as Mount
import struct
import sys

class MKFS:
    def __init__(self, m = Mount.Mount()):  
        self.mount = m
    
    def mkfs(self, context):
        required = ["id"]
        id = ""
        type = "Full"
        fs = "2fs"
        
        for current in context:
            id_ = current.split('=')[0].lower()
            current = current.split('=')[1]
            if current[0] == "\"":
                current = current[1:-1]
            
            if id_ == "id":
                required.remove(id_)
                id = current
            elif id_ == "type":
                type = current
            elif id_ == "fs":
                fs = current
        
        if required:
            print("MKFS", "requiere ciertos parámetros obligatorios")
            return
        
        self.mkfs2(id, type, fs)
    
    def mkfs2(self, id, t, fs):
        try:
            if t.lower() not in ["fast", "full"]:
                raise ValueError("El comando -type necesita valores específicos.")
            elif fs.lower() not in ["2fs", "3fs"]:
                raise ValueError("El comando -fs necesita valores específicos.")
            
            p = ""
            p , partition = self.mount.getmount(id, p)
            
            n = 0
            tamanioSuperBloque = struct.calcsize("<iiiiiddiiiiiiiiii")
            tamanioInodos = struct.calcsize("<iiiddd15ici")                     #investigar las diferencias de obtener el tamaño de un struct 
            tamanioBloquesArchivos = len(bytes(Structs.BloquesArchivos()))      #con struct.calcsize, sys.getsizeof y len(bytes(struct))
            tamanioJournaling = sys.getsizeof(Structs.Journaling())             #y utilicen el que les parezca más conveniente.
            if fs.lower() == "2fs":
                n = (partition.part_size -  tamanioSuperBloque) // (4 + tamanioInodos + 3 * tamanioBloquesArchivos)
            else:
                n = (partition.part_size - tamanioSuperBloque) // (4 + tamanioInodos + 3 * tamanioBloquesArchivos + tamanioJournaling)
            
            spr = Structs.SuperBloque()
            spr.s_inodes_count = spr.s_free_inodes_count = n
            spr.s_blocks_count = spr.s_free_blocks_count = 3 * n
            spr.s_mtime = int(time.time())
            spr.s_umtime = int(time.time())
            spr.s_mnt_count = 1
            
            if fs.lower() == "2fs":
                spr.s_filesystem_type = 2
                self.ext2(spr, partition, n, p)
                print("MKFS", "Se ha formateado la partición: " + partition.part_name + " con formato EXT2 con éxito")
            else:
                spr.s_filesystem_type = 3
                #self.ext3(spr, partition, n, p) ES IGUAL QUE EL EXT2, ÚNICAMENTE CAMBIA QUE SE LE DEBE AGREGAR EL JOURNALING
                print("MKFS", "Se ha formateado la partición: " + partition.part_name + " con formato EXT3 con éxito")
             
        except Exception as e:
            print("MKFS", e)
    
    def ext2(self, spr, p, n, path):
        tamanioSuperBloque = struct.calcsize("<iiiiiddiiiiiiiiii")
        tamanioInodos = struct.calcsize("<iiiddd15ici")                     #investigar las diferencias de obtener el tamaño de un struct 
        tamanioBloquesCarpetas = len(bytes(Structs.BloquesCarpetas()))      #con struct.calcsize, sys.getsizeof y len(bytes(struct)) 
                                                                            #y utilicen el que les parezca más conveniente.
        
        spr.s_bm_inode_start = p.part_start + tamanioSuperBloque
        spr.s_bm_block_start = spr.s_bm_inode_start + n
        spr.s_inode_start = spr.s_bm_block_start + (3 * n)
        spr.s_block_start = spr.s_bm_inode_start + (n * tamanioInodos)

        try:
            with open(path, "rb+") as bfile:
                bfile.seek(p.part_start-1)
                bfile.write(bytes(spr))
                
                zero = b'0'
                bfile.seek(spr.s_bm_inode_start)
                bfile.write(zero * n)
                
                bfile.seek(spr.s_bm_block_start)
                bfile.write(zero * (3 * n))
                
                inode = Structs.Inodos()
                bfile.seek(spr.s_inode_start)
                for _ in range(n):
                    bfile.write(bytes(inode))
                
                folder = Structs.BloquesCarpetas()
                bfile.seek(spr.s_block_start)
                for _ in range(3 * n):
                    bfile.write(bytes(folder))
        except Exception as e:
            print(e)
        

        try:
            sprTemp = Structs.SuperBloque()  # Crear una instancia de SuperBloque
            bytes_super_bloque = bytes(sprTemp)  # Obtener los bytes de la instancia

            recuperado = bytearray(len(bytes_super_bloque))  # Crear un bytearray del mismo tamaño
            with open(path, "rb") as archivo:
                archivo.seek(p.part_start - 1)
                archivo.readinto(recuperado)
            
            # Desempaquetar los datos del bytearray recuperado
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
        except Exception as e:
            print(e) 

        inode = Structs.Inodos()
        inode.i_uid = 1
        inode.i_gid = 1
        inode.i_size = 0
        inode.i_atime = spr.s_umtime
        inode.i_ctime = spr.s_umtime
        inode.i_mtime = spr.s_umtime
        inode.i_type = 0
        inode.i_perm = 664
        inode.i_block[0] = 0 #porque es una carpeta
        
        fb = Structs.BloquesCarpetas()
        fb.b_content[0].b_name = "."
        fb.b_content[0].b_inodo = 0
        fb.b_content[1].b_name = ".."
        fb.b_content[1].b_inodo = 0
        fb.b_content[2].b_name = "user.txt"
        fb.b_content[2].b_inodo = 1
        
        data = "1,G,root\n1,U,root,root,123\n"
        inodetmp = Structs.Inodos()
        inodetmp.i_uid = 1
        inodetmp.i_gid = 1
        inodetmp.i_size = len(data) + tamanioBloquesCarpetas
        inodetmp.i_atime = spr.s_umtime
        inodetmp.i_ctime = spr.s_umtime
        inodetmp.i_mtime = spr.s_umtime
        inodetmp.i_type = 1
        inodetmp.i_perm = 664
        inodetmp.i_block[0] = 1 #porque es un archivo
        
        inode.i_size = inodetmp.i_size + tamanioBloquesCarpetas + tamanioInodos
        
        fileb = Structs.BloquesArchivos()
        fileb.b_content = data
        
        try:            
            with open(path, "rb+") as bfiles:
                bfiles.seek(spr.s_bm_inode_start)
                bfiles.write(b'1' * 2)
                
                bfiles.seek(spr.s_bm_block_start)
                bfiles.write(b'1' * 2)
                
                bfiles.seek(spr.s_inode_start)
                bfiles.write(bytes(inode))
                bfiles.write(bytes(inodetmp))
                
                bfiles.seek(spr.s_block_start)
                bfiles.write(bytes(fb))
                bfiles.write(bytes(fileb))
        except Exception as e:
            print(e)