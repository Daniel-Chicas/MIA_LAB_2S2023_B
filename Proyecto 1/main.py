import os
import disk as disk
import mount as mount
import mkfs as mkfs
 
#exec -path=C:/Users/danie/Desktop/EJEMPLOS_MIA_2S2023/Ejemplo#1 Analizador/auxiliar.script
#exec -path="E:/REPOSITORIOS/MIA_PYTHON/MIA_LAB_2S2023_B/Proyecto 1/auxiliar.script"


mountInstance = mount.Mount() 

class Scanner:
    def __init__(self):
        pass

    @staticmethod
    def mayusculas(a):
        return a.upper()

    @staticmethod
    def comparar(a, b):
        return a.upper() == b.upper()
 
    @staticmethod
    def confirmar(mensaje):
        respuesta = input(f"{mensaje} (y/n)\n\t").lower()
        return respuesta == "y"

    def comando(self, text):
        tkn = ""
        terminar = False
        for c in text:
            if terminar:
                if c == ' ' or c == '-':
                    break
                tkn += c
            elif c != ' ' and not terminar:
                if c == '#':
                    tkn = text
                    break
                else:
                    tkn += c
                    terminar = True
        return tkn

    def separar_tokens(self, text):
        tokens = []
        if not text:
            return tokens
        text += ' '
        token = ""
        estado = 0
        for c in text:
            if estado == 0 and c == '-':
                estado = 1
            elif estado == 0 and c == '#':
                continue
            elif estado != 0:
                if estado == 1:
                    if c == '=':
                        estado = 2
                    elif c == ' ':
                        continue
                elif estado == 2:
                    if c == '\"':
                        estado = 3
                        continue
                    else:
                        estado = 4
                elif estado == 3:
                    if c == '\"':
                        estado = 4
                        continue
                elif estado == 4 and c == '\"':
                    tokens.clear()
                    continue
                elif estado == 4 and c == ' ':
                    estado = 0
                    tokens.append(token)
                    token = ""
                    continue
                token += c
        return tokens

    def inicio(self):
        while True:
            print(">>>>>>>>>>>>>>>>>>>>>>>>> INGRESE UN COMANDO <<<<<<<<<<<<<<<<<<<<<<<<<")
            print("->Si desea terminar con la aplicación ingrese \"exit\"<-")
            #entrada = input("\t>>")
            entrada = "exec -path=\"E:/REPOSITORIOS/MIA_PYTHON/MIA_LAB_2S2023_B/Proyecto 1/auxiliar.script\""
            if entrada.lower() == "exit":
                break
            token = self.comando(entrada)
            entrada = entrada[len(token) + 1:]
            tokens = self.separar_tokens(entrada)
            self.funciones(token, tokens)
            input("\nPresione Enter para continuar....")

    def funciones(self, token, tks):
        if token:
            if token.upper() == "MKDISK":
                print("************** FUNCION MKDISK **************")
                disk.Disk.validarDatos(tks)
                print("\n")
            elif token.upper() == "RMDISK":
                print("************** FUNCION RMDISK **************")
                disk.Disk.rmdisk(tks)
                print("\n") 
            elif token.upper() == "FDISK":
                print("************** FUNCION FDISK **************")
                print("\n")
                disk.Disk.fdisk(tks)
            elif token.upper() == "EXEC":
                print("************** FUNCION EXEC **************")
                print("\n")
                self.funcion_excec(tks)
            elif token.upper() == "MOUNT":
                print("************** FUNCION MOUNT **************")
                print("\n") 
                mountInstance.validarDatos(tks)
            elif token.upper() == "UNMOUNT":
                print("************** FUNCION UNMOUNT **************")
                print("\n")
                mountInstance.validarDatosU(tks)
            elif token.upper() == "MKFS": 
                print("************** FUNCION MKFS **************")
                print("\n")
                fileSystem = mkfs.MKFS(mountInstance)
                fileSystem.mkfs(tks) 
            elif token.startswith("#"):
                print("************** COMENTARIO **************")
                print(token)
                print("\n")
            else:
                print("\tERROR: No se reconoce el comando: " + token)

    def funcion_excec(self, tokens):
        path = ""
        for token in tokens:
            tk = token[:token.find("=")]
            token = token[len(tk) + 1:]
            if self.comparar(tk, "path"):
                path = token
        if not path:
            print("\tERROR: Se requiere la propiedad path para el comando EXEC") 
            return
        self.excec(path)

    def excec(self, path):
        filename = path
        lines = []
        with open(filename, "r") as input_file:
            for line in input_file:
                lines.append(line.strip())
        for i in lines:
            texto = i
            tk = self.comando(texto)
            if texto:
                if self.comparar(texto, "PAUSE"):
                    print("************** FUNCION PAUSE **************")
                    input("Presione enter para continuar...")
                    continue
                texto = texto[len(tk) + 1:]
                tks = self.separar_tokens(texto)
                self.funciones(tk, tks)

if __name__ == "__main__":
    scanner = Scanner()
    scanner.inicio()
