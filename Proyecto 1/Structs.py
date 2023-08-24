import struct

class Structs:
    def __init__(self):
        pass

class Particion:
    def __init__(self):
        self.part_status = '0'
        self.part_type = 'P'
        self.part_fit = 'BF'
        self.part_start = 0
        self.part_size = 0
        self.part_name = ''

    def __bytes__(self):
        return (self.part_status.encode('utf-8') +
                self.part_type.encode('utf-8') +
                self.part_fit.encode('utf-8') +
                struct.pack("<i", self.part_start) +
                struct.pack("<i", self.part_size) +
                self.part_name.ljust(16, '\0').encode('utf-8'))
    
    def __setstate__(self, data):
        self.part_status = data[:1].decode('utf-8')
        self.part_type = data[1:2].decode('utf-8')
        self.part_fit = data[2:3].decode('utf-8')
        self.part_start = struct.unpack("<i", data[3:7])[0]
        self.part_size = struct.unpack("<i", data[7:11])[0]
        self.part_name = data[11:27].decode('utf-8').rstrip('\0')

class MBR:
    def __init__(self):
        self.mbr_tamano = 0
        self.mbr_fecha_creacion = 0
        self.mbr_disk_signature = 0
        self.disk_fit = 'FF'  # Valor por defecto: First Fit
        self.mbr_Partition_1 = Particion()
        self.mbr_Partition_2 = Particion()
        self.mbr_Partition_3 = Particion()
        self.mbr_Partition_4 = Particion()

    def __bytes__(self):
        return (struct.pack("<i", self.mbr_tamano) +
                struct.pack("<i", self.mbr_fecha_creacion) +
                struct.pack("<i", self.mbr_disk_signature) +
                self.disk_fit.encode('utf-8') +
                bytes(self.mbr_Partition_1) +
                bytes(self.mbr_Partition_2) +
                bytes(self.mbr_Partition_3) +
                bytes(self.mbr_Partition_4))

class Transition:
    def __init__(self):
        self.partition = 0
        self.start = 0
        self.end = 0
        self.before = 0
        self.after = 0

    def __bytes__(self):
        return struct.pack("<5i", self.partition, self.start, self.end, self.before, self.after)


class EBR:
    def __init__(self):
        self.part_status = '0'
        self.part_fit = ''
        self.part_start = 0
        self.part_size = 0
        self.part_next = -1
        self.part_name = ''
    
    def __bytes__(self):
        return (self.part_status.encode('utf-8') +
                self.part_fit.encode('utf-8') +
                struct.pack("<i", self.part_start) +
                struct.pack("<i", self.part_size) +
                struct.pack("<i", self.part_next) +
                self.part_name.encode('utf-8').ljust(16, b'\x00'))

    def __setstate__(self, data):
        self.part_status = data[:1].decode('utf-8')
        self.part_fit = data[1:2].decode('utf-8')
        self.part_start = struct.unpack("<i", data[2:6])[0]
        self.part_size = struct.unpack("<i", data[6:10])[0]
        self.part_next = struct.unpack("<i", data[10:14])[0]
        self.part_name = data[14:30].decode('utf-8').rstrip('\0')

class ParticionMontada:
    def __init__(self):
        self.letra = ''
        self.estado = '0'
        self.nombre = ''

class DiscoMontado:
    def __init__(self):
        self.path = ''
        self.estado = '0'
        self.particiones = [ParticionMontada() for _ in range(26)]

class Inodos:
    def __init__(self):
        self.i_uid = -1
        self.i_gid = -1
        self.i_size = -1
        self.i_atime = 0
        self.i_ctime = 0
        self.i_mtime = 0
        self.i_block = [-1] * 15
        self.i_type = -1
        self.i_perm = -1

    def __bytes__(self):
        return (struct.pack("<i", self.i_uid) +
                struct.pack("<i", self.i_gid) +
                struct.pack("<i", self.i_size) +
                struct.pack("<d", self.i_atime) +
                struct.pack("<d", self.i_ctime) +
                struct.pack("<d", self.i_mtime) +
                struct.pack("<15i", *self.i_block) +
                struct.pack("<c", bytes([self.i_type])) +
                struct.pack("<i", self.i_perm))
    
class SuperBloque:
    def __init__(self):
        self.s_filesystem_type = 0
        self.s_inodes_count = 0
        self.s_blocks_count = 0
        self.s_free_blocks_count = 0
        self.s_free_inodes_count = 0
        self.s_mtime = 0
        self.s_umtime = 0
        self.s_mnt_count = 0
        self.s_magic = 0xEF53
        self.s_inode_size = 0
        self.s_block_size = 0
        self.s_first_ino = 0
        self.s_first_blo = 0
        self.s_bm_inode_start = 0
        self.s_bm_block_start = 0
        self.s_inode_start = 0
        self.s_block_start = 0

    def __bytes__(self):
        return (struct.pack("<i", self.s_filesystem_type) +
                struct.pack("<i", self.s_inodes_count) +
                struct.pack("<i", self.s_blocks_count) +
                struct.pack("<i", self.s_free_blocks_count) +
                struct.pack("<i", self.s_free_inodes_count) +
                struct.pack("<d", self.s_mtime) +
                struct.pack("<d", self.s_umtime) +
                struct.pack("<i", self.s_mnt_count) +
                struct.pack("<i", self.s_magic) +
                struct.pack("<i", self.s_inode_size) +
                struct.pack("<i", self.s_block_size) +
                struct.pack("<i", self.s_first_ino) +
                struct.pack("<i", self.s_first_blo) +
                struct.pack("<i", self.s_bm_inode_start) +
                struct.pack("<i", self.s_bm_block_start) +
                struct.pack("<i", self.s_inode_start) +
                struct.pack("<i", self.s_block_start))
    
class Content:
    def __init__(self):
        self.b_name = ''
        self.b_inodo = -1

    def __bytes__(self):
        return (self.b_name.encode('utf-8').ljust(12, b'\x00') +
                struct.pack("<i", self.b_inodo))
    
class BloquesCarpetas:
    def __init__(self):
        self.b_content = [Content() for _ in range(4)]

    def __bytes__(self):
        return b"".join(bytes(c) for c in self.b_content)

class BloquesArchivos:
    def __init__(self):
        self.b_content = b'\x00' * 64

    def __bytes__(self):
        return self.b_content
    
class BloquesApuntadores:
    def __init__(self):
        self.b_pointers = [-1] * 16

    def __bytes__(self):
        return struct.pack("<16i", *self.b_pointers)
    
class Journaling:
    def __init__(self):
        self.estado = -1
        self.operation = ''
        self.type = -1
        self.path = ''
        self.date = 0
        self.content = ''
        self.id_propietario = ''
        self.size = 0

    def __bytes__(self):
        return (struct.pack("<i", self.estado) +
                self.operation.encode('utf-8').ljust(10, b'\x00') +
                struct.pack("<c", bytes([self.type])) +
                self.path.encode('utf-8').ljust(100, b'\x00') +
                struct.pack("<d", self.date) +
                self.content.encode('utf-8').ljust(60, b'\x00') +
                struct.pack("<c", bytes([self.id_propietario])) +
                struct.pack("<i", self.size))