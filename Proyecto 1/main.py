import os
import disk 
import mount 
import mkfs 
import users  
 
#exec -path=C:/Users/danie/Desktop/EJEMPLOS_MIA_2S2023/Ejemplo#1 Analizador/auxiliar.script
#exec -path="E:/REPOSITORIOS/MIA_PYTHON/MIA_LAB_2S2023_B/Proyecto 1/auxiliar.script"


mountInstance = mount.Mount() 
logued = False

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
 
    def comando(text):
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

    def separar_tokens(text):
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

    def inicio():
        while True:
            print(">>>>>>>>>>>>>>>>>>>>>>>>> INGRESE UN COMANDO <<<<<<<<<<<<<<<<<<<<<<<<<")
            print("->Si desea terminar con la aplicación ingrese \"exit\"<-")
            #entrada = input("\t>>")
            entrada = "exec -path=\"E:/REPOSITORIOS/MIA_PYTHON/MIA_LAB_2S2023_B/Proyecto 1/auxiliar.script\""
            if entrada.lower() == "exit":
                break
            token = Scanner.comando(entrada)
            entrada = entrada[len(token) + 1:]
            tokens = Scanner.separar_tokens(entrada)
            Scanner.funciones(token, tokens)
            input("\nPresione Enter para continuar....")

    def funciones( token, tks):
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
                Scanner.funcion_excec(tks)
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
            elif token.upper() == "LOGIN":
                print("************** FUNCION LOGIN **************")
                global logued
                if(logued):
                    print("Ya hay una sesión activa")
                else:
                    logued = users.Usuarios().login(tks, mountInstance)
            elif token.upper() == "LOGOUT":
                print("************** FUNCION LOGOUT **************") 
                if(logued):
                    logued = users.Usuarios(mountInstance).logout()
                else:
                    print("No hay una sesión activa")
            elif token.upper() == "MKGRP":
                print("************** FUNCION MKGRP **************")
                if(logued):
                    users.Usuarios(mountInstance).validarDatosGrp(tks, "MK")
                else:
                    print("No hay una sesión activa")
            elif token.upper() == "RMGRP":
                print("************** FUNCION RMGRP **************")
                if(logued):
                    users.Usuarios(mountInstance).validarDatosGrp(tks, "RM")
                else:
                    print("No hay una sesión activa")
            elif token.upper() == "MKUSR":
                print("************** FUNCION MKUSR **************")
                if(logued):
                    users.Usuarios(mountInstance).validarDatosusr(tks, "MK")
                else:
                    print("No hay una sesión activa")
            elif token.upper() == "RMUSR":
                print("************** FUNCION RMUSR **************")
                if(logued):
                    users.Usuarios(mountInstance).validarDatosusr(tks, "RM")
                else:
                    print("No hay una sesión activa")
            elif token.startswith("#"):
                print("************** COMENTARIO **************")
                print(token)
                print("\n")
            else:
                print("\tERROR: No se reconoce el comando: " + token)
 
    def funcion_excec(tokens):
        path = ""
        for token in tokens:
            tk = token[:token.find("=")]
            token = token[len(tk) + 1:]
            if Scanner.comparar(tk, "path"):
                path = token
        if not path:
            print("\tERROR: Se requiere la propiedad path para el comando EXEC") 
            return
        Scanner.excec(path)
 
    def excec(path):
        filename = path
        lines = []
        with open(filename, "r") as input_file:
            for line in input_file:
                lines.append(line.strip())
        for i in lines:
            texto = i
            tk = Scanner.comando(texto)
            if texto:
                if Scanner.comparar(texto, "PAUSE"):
                    print("************** FUNCION PAUSE **************")
                    input("Presione enter para continuar...")
                    continue
                texto = texto[len(tk) + 1:]
                tks = Scanner.separar_tokens(texto)
                Scanner.funciones(tk, tks)

if __name__ == "__main__":
    scanner = Scanner()
    scanner.inicio()
