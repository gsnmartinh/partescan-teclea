"""PartesTeclea: escribe en la pantalla «Procesos 2DO. JUZGADO» los datos de los partes revisados en ParteScan.
Sigue el orden del tabulador de la pantalla. Nunca pulsa «Aceptar»: eso lo haces tú después de revisar cada causa.

Uso:  doble clic (usa partes-para-tecleo.json de la misma carpeta) o por línea de comandos:
      PartesTeclea.exe partes-para-tecleo.json            (paso a paso: espera F9 en cada campo)
      PartesTeclea.exe partes-para-tecleo.json --rapido   (escribe la causa completa y se detiene al terminar)
      PartesTeclea.exe partes-para-tecleo.json --simular  (solo muestra qué escribiría, sin tocar nada)
"""
import json
import re
import sys
import time
import unicodedata

TITULO = r"Procesos 2DO\. JUZGADO"
PAUSA = 0.25          # segundos entre campos en modo rápido


def sin_tildes(v):
    v = unicodedata.normalize("NFD", str(v or ""))
    return "".join(c for c in v if unicodedata.category(c) != "Mn")


def escapar(t):
    """send_keys interpreta + ^ % ~ ( ) { } como teclas especiales: se escriben entre llaves."""
    return "".join("{%s}" % c if c in "+^%~(){}[]" else c for c in sin_tildes(t))


def hora4(h):
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})", h or "")
    return "%02d%s" % (int(m.group(1)), m.group(2)) if m else ""


def plan(p):
    """Lista de (etiqueta, texto) en el orden del tabulador (los números son los pasos de la pantalla)."""
    inf = " ".join(p.get("infracciones") or [])
    return [
        ("1 Rol (se pulsa ENTER: el sistema pone el número)", None),
        ("2 Oficina emisora", p.get("oficina", "")),
        ("3 Fecha ingreso", p.get("fecha_ingreso", "")),
        ("4a Nº Parte", p.get("n_parte", "")),
        ("4b Fecha parte", p.get("fecha_parte", "")),
        ("5 Bol/N.Parte", p.get("boleta", "")),
        ("6 Fecha de la boleta", p.get("fecha_parte", "")),
        ("7 Descripción de la causa", p.get("descripcion", "")),
        ("8 Actuario (hazlo tú: depende del rol)", ""),
        ("9 Citación", p.get("fecha_citacion", "")),
        ("10 Lugar", p.get("lugar", "")),
        ("11 Hora de la infracción", hora4(p.get("hora", ""))),
        ("12 RUT (SR si no tiene)", p.get("rut", "") or "SR"),
        ("13 Nombres", p.get("nombre", "")),
        ("14 Dirección", p.get("direccion", "")),
        ("15 Comuna", p.get("comuna", "")),
        ("16 Placa", p.get("placa", "")),
        ("17 Tipo de vehículo", p.get("tipo_vehiculo", "")),
        ("18 Marca", p.get("marca", "")),
        ("19 Fecha de la infracción", p.get("fecha_parte", "")),
        ("20 Infracción (códigos: %s)" % (inf or "sin código"), inf.split()[0] if inf else ""),
    ]


def esperar_tecla(vk=0x78, abortar=0x1B):
    """Espera F9 (siguiente) sin quitarle el foco al sistema; ESC aborta. Solo Windows."""
    import ctypes
    u = ctypes.windll.user32
    while u.GetAsyncKeyState(vk) & 0x8000:      # suelta primero la tecla anterior
        time.sleep(0.02)
    while True:
        if u.GetAsyncKeyState(vk) & 0x8000:
            return True
        if u.GetAsyncKeyState(abortar) & 0x8000:
            raise KeyboardInterrupt
        time.sleep(0.03)


def resumen(i, p):
    return "[%d] boleta %s · N° parte %s · %s · %s" % (i, p.get("boleta"), p.get("n_parte"),
                                                         p.get("rut") or "SR", p.get("nombre") or p.get("placa"))


def buscar_json(argv):
    """Con doble clic no hay argumentos: se usa el primer .json de la carpeta o el que se escriba/arrastre."""
    import glob
    import os
    if len(argv) > 1 and not argv[1].startswith("--"):
        return argv[1]
    base = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    hallados = sorted(glob.glob(os.path.join(base, "partes-para-tecleo*.json")) + glob.glob("partes-para-tecleo*.json"))
    if hallados:
        print("Usando", hallados[-1]); return hallados[-1]
    ruta = input("No encontré partes-para-tecleo.json en esta carpeta.\nArrastra aquí el archivo y pulsa ENTER: ")
    return ruta.strip().strip('"')


def main(argv):
    ruta = buscar_json(argv)
    if not ruta:
        print(__doc__); return 1
    datos = json.load(open(ruta, encoding="utf-8"))["partes"]
    simular, rapido = "--simular" in argv, "--rapido" in argv
    if simular:
        for i, p in enumerate(datos, 1):
            print(resumen(i, p))
            for etq, t in plan(p):
                print("    %-48s %s" % (etq, "" if t is None else t))
        return 0
    from pywinauto import Desktop
    from pywinauto.keyboard import send_keys

    def ventanas():
        return {w.handle: w.window_text() for w in Desktop(backend="win32").windows() if w.is_visible()}

    for i, p in enumerate(datos, 1):
        print("\n" + resumen(i, p))
        input("Abre una causa NUEVA (pantalla vacía, cursor en el Rol) y pulsa ENTER aquí… ")
        # la causa es una ventana interna del sistema (MDI): no se busca por título. Tienes unos segundos para
        # hacer clic en el campo Rol del sistema; el programa escribe en lo que tenga el foco.
        for n in range(5, 0, -1):
            print("  Haz clic en el campo Rol del sistema… empiezo en %d" % n, end="\r")
            time.sleep(1)
        print(" " * 60)
        base = ventanas()
        for etq, t in plan(p):
            if not rapido:
                print("  -> %s : «%s»   (F9 = escribir y seguir · ESC = parar)" % (etq, t if t else ""))
                esperar_tecla()
            if t is None:
                send_keys("{ENTER}")
            elif t:
                send_keys(escapar(t), with_spaces=True, pause=0.02)
            if t is not None:
                send_keys("{TAB}")
            time.sleep(PAUSA if rapido else 0.1)
            nuevas = {h: n for h, n in ventanas().items() if h not in base}
            if nuevas:
                print("  !! Apareció una ventana:", list(nuevas.values()),
                      "\n     Respóndela tú. Luego pulsa F9 para seguir con el siguiente campo.")
                esperar_tecla()
                base = ventanas()
        print("Listo: revisa la causa y pulsa «Aceptar» tú mismo.")
    return 0


if __name__ == "__main__":
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")     # la consola de Windows no siempre muestra tildes ni «…»
        except Exception:
            pass
    try:
        codigo = main(sys.argv)
    except Exception:
        import traceback
        traceback.print_exc()
        codigo = 1
    input("\nPulsa ENTER para cerrar esta ventana… ")
    sys.exit(codigo)
