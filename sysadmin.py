"""
SYSADMIN ASSISTANT
Sistema Inteligente de Automatización y Monitoreo del Sistema Operativo con Python
Autor: GERALS JOHAN SARMIENTO VASQUEZ
Asignatura: Sistemas Operativos - Séptimo Semestre
Docente: EDGAR MORILLO
"""

import os
import platform
import socket
import shutil
import csv
import threading
import time
from pathlib import Path
from datetime import datetime

import psutil
import schedule

# CONSTANTES GLOBALES


# Procesos críticos que NO deben finalizarse
PROCESOS_CRITICOS = [
    "system", "systemd", "init", "kernel", "svchost",
    "winlogon", "csrss", "lsass", "smss", "services",
    "explorer", "wininit", "dwm", "ntoskrnl"
]

# Clasificación de archivos por categorías
CATEGORIAS = {
    "Documentos/PDF":    [".pdf"],
    "Documentos/WORD":   [".doc", ".docx"],
    "Documentos/EXCEL":  [".xls", ".xlsx"],
    "Documentos/PPTX":   [".ppt", ".pptx"],
    "Imagenes/JPG":      [".jpg", ".jpeg"],
    "Imagenes/PNG":      [".png"],
    "Imagenes/GIF":      [".gif"],
    "Imagenes/WEBP":     [".webp"],
    "Videos/MP4":        [".mp4"],
    "Videos/AVI":        [".avi"],
    "Videos/MKV":        [".mkv"],
    "Videos/MOV":        [".mov"],
    "Audio/MP3":         [".mp3"],
    "Audio/WAV":         [".wav"],
    "Audio/OGG":         [".ogg"],
    "Codigo":            [".py", ".js", ".java", ".cpp", ".c", ".html", ".css", ".sql"],
    "Comprimidos":       [".zip", ".rar", ".7z", ".tar", ".gz"],
}


# UTILIDADES

def limpiar_pantalla():
    """Limpia la consola según el sistema operativo."""
    os.system("cls" if platform.system() == "Windows" else "clear")


def bytes_a_legible(bytes_val):
    """Convierte bytes a formato legible (GB, MB, KB)."""
    for unidad in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unidad}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


def separador(char="=", largo=60):
    """Imprime una línea separadora decorativa."""
    print(char * largo)


def encabezado(titulo):
    """Imprime un encabezado formateado para cada módulo."""
    limpiar_pantalla()
    separador()
    print(f"  SYSADMIN ASSISTANT  |  {titulo}")
    separador()
    print()


def pausar():
    """Pausa la ejecución hasta que el usuario presione Enter."""
    print()
    input("  Presione Enter para continuar...")


# MÓDULO 1 – INFORMACIÓN DEL SISTEMA

def modulo_informacion_sistema():
    """Muestra información completa del equipo y sus recursos."""
    encabezado("INFORMACIÓN DEL SISTEMA")

    # --- Información del equipo ---
    print("  [EQUIPO]")
    print(f"  Nombre del equipo   : {socket.gethostname()}")
    print(f"  Usuario actual      : {os.getlogin()}")
    print(f"  Sistema operativo   : {platform.system()} {platform.release()}")
    print(f"  Versión del SO      : {platform.version()}")
    print(f"  Arquitectura        : {platform.machine()}")
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "No disponible"
    print(f"  Dirección IP        : {ip}")

    separador("-")

   
    print("  [MEMORIA RAM]")
    ram = psutil.virtual_memory()
    print(f"  RAM Total           : {bytes_a_legible(ram.total)}")
    print(f"  RAM Utilizada       : {bytes_a_legible(ram.used)} ({ram.percent}%)")
    print(f"  RAM Libre           : {bytes_a_legible(ram.available)}")

    separador("-")

    
    print("  [PROCESADOR]")
    print(f"  Núcleos físicos     : {psutil.cpu_count(logical=False)}")
    print(f"  Núcleos lógicos     : {psutil.cpu_count(logical=True)}")
    cpu_uso = psutil.cpu_percent(interval=1)
    print(f"  Uso del CPU         : {cpu_uso}%")

    separador("-")

  
    print("  [DISCO DURO]")
    disco = psutil.disk_usage("/")
    print(f"  Espacio total       : {bytes_a_legible(disco.total)}")
    print(f"  Espacio utilizado   : {bytes_a_legible(disco.used)} ({disco.percent}%)")
    print(f"  Espacio libre       : {bytes_a_legible(disco.free)}")

    pausar()


# MÓDULO 2 – MONITOR DE PROCESOS


def obtener_procesos():
    """Retorna lista de procesos activos ordenados por uso de CPU."""
    procesos = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            procesos.append({
                "pid":    info["pid"],
                "nombre": info["name"],
                "cpu":    round(info["cpu_percent"] or 0, 2),
                "mem":    round(info["memory_percent"] or 0, 2),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(procesos, key=lambda x: x["cpu"], reverse=True)


def modulo_monitor_procesos():
    """Muestra procesos activos y permite buscar/finalizar uno."""
    while True:
        encabezado("MONITOR DE PROCESOS")
        procesos = obtener_procesos()

        # Mostrar los 20 procesos con mayor consumo de CPU
        print(f"  {'PID':<8} {'NOMBRE':<35} {'CPU %':<10} {'MEM %':<10}")
        separador("-")
        for p in procesos[:20]:
            print(f"  {p['pid']:<8} {p['nombre'][:34]:<35} {p['cpu']:<10} {p['mem']:<10}")

        separador()
        print("  [1] Buscar/Finalizar proceso")
        print("  [0] Volver al menú principal")
        separador("-")
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            nombre_buscado = input("  Ingrese nombre del proceso a buscar: ").strip().lower()
            encontrados = [p for p in procesos if nombre_buscado in p["nombre"].lower()]

            if not encontrados:
                print("  No se encontraron procesos con ese nombre.")
                pausar()
                continue

            print()
            print(f"  {'PID':<8} {'NOMBRE':<35} {'CPU %':<10} {'MEM %':<10}")
            separador("-")
            for p in encontrados:
                print(f"  {p['pid']:<8} {p['nombre'][:34]:<35} {p['cpu']:<10} {p['mem']:<10}")

            pid_input = input("\n  Ingrese el PID a finalizar (o Enter para cancelar): ").strip()
            if pid_input:
                try:
                    pid = int(pid_input)
                    proc = psutil.Process(pid)
                    nombre_proc = proc.name().lower()

                    # Validación de proceso crítico
                    if any(critico in nombre_proc for critico in PROCESOS_CRITICOS):
                        print(f"  ERROR: '{proc.name()}' es un proceso crítico del sistema.")
                        print("  No se puede finalizar.")
                    else:
                        confirmar = input(f"  ¿Seguro que desea finalizar '{proc.name()}'? (s/n): ")
                        if confirmar.lower() == "s":
                            proc.terminate()
                            print(f"  Proceso '{proc.name()}' (PID {pid}) finalizado correctamente.")
                        else:
                            print("  Operación cancelada.")
                except ValueError:
                    print("  PID inválido.")
                except psutil.NoSuchProcess:
                    print("  El proceso ya no existe.")
                except psutil.AccessDenied:
                    print("  Acceso denegado: se requieren permisos de administrador.")
                except Exception as e:
                    print(f"  Error: {e}")
                pausar()

        elif opcion == "0":
            break


# MÓDULO 3 – ORGANIZADOR AUTOMÁTICO DE ARCHIVOS

def obtener_categoria(extension):
    """Retorna la subcarpeta correspondiente a la extensión dada."""
    ext = extension.lower()
    for carpeta, extensiones in CATEGORIAS.items():
        if ext in extensiones:
            return carpeta
    return "Otros"


def modulo_organizador_archivos():
    """Organiza automáticamente los archivos de una carpeta por categoría."""
    encabezado("ORGANIZADOR AUTOMÁTICO DE ARCHIVOS")

    ruta_str = input("  Ingrese la ruta de la carpeta a organizar: ").strip()
    carpeta = Path(ruta_str)

    if not carpeta.exists() or not carpeta.is_dir():
        print("  ERROR: La ruta no existe o no es una carpeta válida.")
        pausar()
        return

    archivos = [f for f in carpeta.iterdir() if f.is_file()]
    if not archivos:
        print("  La carpeta está vacía.")
        pausar()
        return

    print(f"\n  Se encontraron {len(archivos)} archivo(s). Organizando...\n")
    movidos = 0
    errores = 0

    for archivo in archivos:
        categoria = obtener_categoria(archivo.suffix)
        destino_dir = carpeta / categoria
        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = destino_dir / archivo.name

        try:
            # Evitar sobreescritura
            if destino.exists():
                base = archivo.stem
                ext = archivo.suffix
                destino = destino_dir / f"{base}_{int(time.time())}{ext}"
            shutil.move(str(archivo), str(destino))
            print(f"  ✔ {archivo.name}  →  {categoria}/")
            movidos += 1
        except Exception as e:
            print(f"  ✘ {archivo.name}: {e}")
            errores += 1

    separador("-")
    print(f"\n  Organización completada: {movidos} movidos, {errores} errores.")
    pausar()



# MÓDULO 4 – SISTEMA DE COPIAS DE SEGURIDAD

def registrar_backup(log_path, origen, destino, copiados, errores):
    """Registra los detalles del backup en un archivo de log."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] Origen: {origen} | Destino: {destino} | "
                f"Copiados: {copiados} | Errores: {errores}\n")


def realizar_backup(origen_str, destino_str, silencioso=False):
    """Realiza una copia de seguridad de la carpeta origen a la destino."""
    origen = Path(origen_str)
    destino = Path(destino_str)

    if not origen.exists():
        if not silencioso:
            print("  ERROR: La carpeta origen no existe.")
        return 0, 1

    destino.mkdir(parents=True, exist_ok=True)
    copiados = 0
    errores = 0

    for archivo in origen.rglob("*"):
        if archivo.is_file():
            ruta_relativa = archivo.relative_to(origen)
            destino_archivo = destino / ruta_relativa
            destino_archivo.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(str(archivo), str(destino_archivo))
                copiados += 1
                if not silencioso:
                    print(f"  ✔ {ruta_relativa}")
            except (PermissionError, OSError) as e:
                errores += 1
                if not silencioso:
                    print(f"  ✘ {ruta_relativa}: {e}")

    log_path = destino / "backup_log.txt"
    registrar_backup(log_path, origen_str, destino_str, copiados, errores)
    return copiados, errores


def modulo_copias_seguridad():
    """Permite configurar y ejecutar una copia de seguridad manual."""
    encabezado("SISTEMA DE COPIAS DE SEGURIDAD")

    origen = input("  Ingrese la carpeta ORIGEN del respaldo: ").strip()
    destino = input("  Ingrese la carpeta DESTINO del respaldo: ").strip()

    print(f"\n  Iniciando backup: {origen}  →  {destino}\n")
    separador("-")

    copiados, errores = realizar_backup(origen, destino)

    separador("-")
    print(f"\n  Backup completado: {copiados} archivo(s) copiado(s), {errores} error(es).")
    print(f"  Log guardado en: {destino}/backup_log.txt")
    pausar()

# MÓDULO 5 – GENERACIÓN DE REPORTES

def recopilar_datos_sistema():
    """Recopila todos los datos del sistema para el reporte."""
    ram = psutil.virtual_memory()
    disco = psutil.disk_usage("/")
    cpu_uso = psutil.cpu_percent(interval=1)
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "No disponible"

    datos = {
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre_equipo":    socket.gethostname(),
        "usuario":          os.getlogin(),
        "sistema_operativo": f"{platform.system()} {platform.release()}",
        "version_so":       platform.version(),
        "arquitectura":     platform.machine(),
        "ip":               ip,
        "ram_total":        bytes_a_legible(ram.total),
        "ram_usada":        bytes_a_legible(ram.used),
        "ram_libre":        bytes_a_legible(ram.available),
        "ram_porcentaje":   f"{ram.percent}%",
        "cpu_uso":          f"{cpu_uso}%",
        "cpu_nucleos":      psutil.cpu_count(logical=True),
        "disco_total":      bytes_a_legible(disco.total),
        "disco_usado":      bytes_a_legible(disco.used),
        "disco_libre":      bytes_a_legible(disco.free),
        "disco_porcentaje": f"{disco.percent}%",
    }
    return datos


def generar_reporte_txt(ruta, datos, procesos):
    """Genera el reporte en formato TXT."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("       REPORTE DEL SISTEMA - SYSADMIN ASSISTANT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Fecha de generación : {datos['fecha_generacion']}\n\n")
        f.write("[INFORMACIÓN DEL EQUIPO]\n")
        for clave in ["nombre_equipo", "usuario", "sistema_operativo",
                      "version_so", "arquitectura", "ip"]:
            f.write(f"  {clave.replace('_', ' ').title()}: {datos[clave]}\n")
        f.write("\n[RECURSOS DEL SISTEMA]\n")
        for clave in ["ram_total", "ram_usada", "ram_libre", "ram_porcentaje",
                      "cpu_uso", "cpu_nucleos", "disco_total", "disco_usado",
                      "disco_libre", "disco_porcentaje"]:
            f.write(f"  {clave.replace('_', ' ').title()}: {datos[clave]}\n")
        f.write("\n[PROCESOS ACTIVOS (Top 15 por CPU)]\n")
        f.write(f"  {'PID':<8} {'NOMBRE':<35} {'CPU%':<8} {'MEM%':<8}\n")
        f.write("  " + "-" * 58 + "\n")
        for p in procesos[:15]:
            f.write(f"  {p['pid']:<8} {p['nombre'][:34]:<35} {p['cpu']:<8} {p['mem']:<8}\n")
        f.write("\n" + "=" * 60 + "\n")


def generar_reporte_csv(ruta, datos, procesos):
    """Genera el reporte en formato CSV."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["CAMPO", "VALOR"])
        for clave, valor in datos.items():
            writer.writerow([clave, valor])
        writer.writerow([])
        writer.writerow(["PID", "NOMBRE", "CPU %", "MEM %"])
        for p in procesos[:15]:
            writer.writerow([p["pid"], p["nombre"], p["cpu"], p["mem"]])


def modulo_generacion_reportes(silencioso=False, carpeta_destino=None):
    """Genera un reporte completo del sistema en TXT o CSV."""
    if not silencioso:
        encabezado("GENERACIÓN DE REPORTES")
        print("  Formatos disponibles:")
        print("  [1] TXT")
        print("  [2] CSV")
        separador("-")
        formato = input("  Seleccione el formato: ").strip()
    else:
        formato = "1"  

    datos = recopilar_datos_sistema()
    procesos = obtener_procesos()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta_base = Path(carpeta_destino) if carpeta_destino else Path.cwd()

    if formato == "2":
        ruta = carpeta_base / f"reporte_{timestamp}.csv"
        generar_reporte_csv(str(ruta), datos, procesos)
    else:
        ruta = carpeta_base / f"reporte_{timestamp}.txt"
        generar_reporte_txt(str(ruta), datos, procesos)

    if not silencioso:
        print(f"\n  Reporte generado exitosamente:\n  {ruta}")
        pausar()
    else:
        print(f"  [Auto] Reporte generado: {ruta}")



# MÓDULO 6 – AUTOMATIZACIÓN PROGRAMADA

# Variable global para controlar el hilo de automatización
hilo_automatizacion = None
automatizacion_activa = False


def iniciar_hilo_schedule():
    """Corre schedule en un hilo secundario sin bloquear la app."""
    global automatizacion_activa
    automatizacion_activa = True
    while automatizacion_activa:
        schedule.run_pending()
        time.sleep(1)


def modulo_automatizacion():
    """Configura tareas automáticas programadas."""
    global hilo_automatizacion, automatizacion_activa

    encabezado("AUTOMATIZACIÓN PROGRAMADA")

    print("  Configurar tarea automática:")
    print("  [1] Generar reporte automáticamente")
    print("  [2] Ejecutar backup automáticamente")
    print("  [0] Volver")
    separador("-")
    opcion = input("  Seleccione: ").strip()

    if opcion == "0":
        return

    intervalo_str = input("  ¿Cada cuántos minutos ejecutar la tarea? ").strip()
    try:
        intervalo = int(intervalo_str)
        if intervalo <= 0:
            raise ValueError
    except ValueError:
        print("  Intervalo inválido.")
        pausar()
        return

    if opcion == "1":
        schedule.every(intervalo).minutes.do(
            modulo_generacion_reportes, silencioso=True
        )
        print(f"\n  Reporte automático configurado cada {intervalo} minuto(s).")

    elif opcion == "2":
        origen = input("  Carpeta ORIGEN para el backup automático: ").strip()
        destino = input("  Carpeta DESTINO para el backup automático: ").strip()
        schedule.every(intervalo).minutes.do(
            realizar_backup, origen_str=origen, destino_str=destino, silencioso=False
        )
        print(f"\n  Backup automático configurado cada {intervalo} minuto(s).")

    # Iniciar hilo si no está corriendo
    if hilo_automatizacion is None or not hilo_automatizacion.is_alive():
        hilo_automatizacion = threading.Thread(
            target=iniciar_hilo_schedule, daemon=True
        )
        hilo_automatizacion.start()
        print("  Motor de automatización iniciado en segundo plano.")

    pausar()


# MENÚ PRINCIPAL

def menu_principal():
    """Muestra el menú principal y gestiona la navegación entre módulos."""
    while True:
        encabezado("MENÚ PRINCIPAL")
        print("  Seleccione un módulo:\n")
        print("  [1]  Información del Sistema")
        print("  [2]  Monitor de Procesos")
        print("  [3]  Organizador Automático de Archivos")
        print("  [4]  Sistema de Copias de Seguridad")
        print("  [5]  Generación de Reportes")
        print("  [6]  Automatización Programada")
        print()
        separador("-")
        print("  [0]  Salir")
        separador()
        opcion = input("  Ingrese su opción: ").strip()

        if opcion == "1":
            modulo_informacion_sistema()
        elif opcion == "2":
            modulo_monitor_procesos()
        elif opcion == "3":
            modulo_organizador_archivos()
        elif opcion == "4":
            modulo_copias_seguridad()
        elif opcion == "5":
            modulo_generacion_reportes()
        elif opcion == "6":
            modulo_automatizacion()
        elif opcion == "0":
            print("\n  Gracias por usar SYSADMIN ASSISTANT. ¡Hasta pronto!\n")
            break
        else:
            print("  Opción inválida. Intente de nuevo.")
            time.sleep(1)


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    menu_principal()