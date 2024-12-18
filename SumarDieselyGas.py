import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
from datetime import datetime


def traducir_mes(fecha):
    meses = {
        "January": "enero", "February": "febrero", "March": "marzo", "April": "abril",
        "May": "mayo", "June": "junio", "July": "julio", "August": "agosto",
        "September": "septiembre", "October": "octubre", "November": "noviembre", "December": "diciembre"
    }
    for ingles, espanol in meses.items():
        fecha = fecha.replace(ingles, espanol)
    return fecha

def verificar_proveedor(file_path):
    """
    Verifica si el archivo pertenece a la gasolinera Colón mediante su nombre.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

        receptor = root.find('.//cfdi:Emisor', namespaces)
        if receptor is not None:
            nombre = receptor.attrib.get('Nombre', '').upper()
            if nombre == "#nombre del proveedor":
                return True
            else:
                messagebox.showwarning("Advertencia", f"La factura no pertenece a la gasolinera Colón.\nnombre del proveedor encontrado: \n{nombre}")
                return False
        else:
            messagebox.showerror("Error", "No se encontró el nodo Receptor en el archivo XML.")
            return False
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar el archivo: {e}")
        return False

def verificar_rfc(file_path):
    """
    Verifica si el archivo pertenece a la gasolinera Colón (RFC: GCO740121MC5).
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

        receptor = root.find('.//cfdi:Receptor', namespaces)
        if receptor is not None:
            rfc = receptor.attrib.get('Rfc', '').upper()
            if rfc == '#Rfc proveedor' or rfc == '#RFC empresa':
                return True
            else:
                messagebox.showwarning("Advertencia", f"La factura no pertenece a la gasolinera Colón.\nRFC encontrado: {rfc}")
                return False
        else:
            messagebox.showerror("Error", "No se encontró el nodo Receptor en el archivo XML.")
            return False
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar el archivo: {e}")
        return False


def sacar_datos(file_path):
    """
    Extrae la fecha y el folio del archivo XML.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
        comprobante = root if root.tag.endswith('Comprobante') else root.find('.//cfdi:Comprobante', namespaces)

        if comprobante is not None:
            fecha_original = comprobante.attrib.get('Fecha', 'Fecha no encontrada')
            folio = comprobante.attrib.get('Folio', 'Folio no encontrado')

            fecha_formateada = (
                datetime.strptime(fecha_original[:10], "%Y-%m-%d").strftime("%d de %B %Y")
                if fecha_original != 'Fecha no encontrada' else "Fecha no encontrada"
            )
        else:
            fecha_formateada = "Fecha no encontrada"
            folio = "Folio no encontrado"

        fecha_formateada = traducir_mes(fecha_formateada)
        return fecha_formateada, folio
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar el archivo: {e}")
        return "Desconocido", "Desconocido"


def extract_fuel_data(file_path):
    """
    Extrae la información de combustibles (litros y precios) del archivo XML.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
        total_diesel_liters = 0
        total_diesel_price = 0
        total_gasoline_price = 0

        for concept in root.findall('.//cfdi:Concepto', namespaces):
            description = concept.attrib.get('Descripcion', '').lower()
            liters = float(concept.attrib.get('Cantidad', 0))
            price = float(concept.attrib.get('Importe', 0))

            if 'diesel' in description:
                total_diesel_liters += liters
                total_diesel_price += price
            elif 'magna' in description or 'premium' in description:
                total_gasoline_price += price

        return total_diesel_liters, total_diesel_price, total_gasoline_price
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar el archivo: {e}")
        return 0, 0, 0


def open_file():
    """
    Abre un archivo XML, verifica su RFC con proveedor y extrae la información si es válida.
    """
    file_path = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml")])
    if file_path:
        if verificar_rfc(file_path) and verificar_proveedor(file_path):
            diesel_liters, diesel_price, gasoline_price = extract_fuel_data(file_path)
            diesel_liters_label.config(text=f"Total de litros de diesel: {diesel_liters:,.3f}")
            diesel_price_label.config(text=f"Total del precio del diésel: ${diesel_price:,.2f}")
            gasoline_price_label.config(text=f"Total del precio de la gasolina: ${gasoline_price:,.2f}")
            fecha, folio = sacar_datos(file_path)
            fecha_label.config(text=f"Fecha de la factura: {fecha}")
            folio_label.config(text=f"Folio de la factura: D{folio}")


# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Sumador de Combustibles desde Facturas XML")

# Encabezado
header_frame = tk.Frame(root, padx=10, pady=10)
header_frame.pack(fill="x")

title_label = tk.Label(header_frame, text="Sumador de Diesel y Gas", font=("Arial", 16, "bold"))
title_label.pack()

fecha_label = tk.Label(header_frame, text="Fecha de la factura: ", font=("Arial", 14))
fecha_label.pack()

folio_label = tk.Label(header_frame, text="Folio de la factura: ", font=("Arial", 14))
folio_label.pack()

# Contenido principal
content_frame = tk.Frame(root, padx=10, pady=10)
content_frame.pack(fill="both", expand=False)

diesel_liters_label = tk.Label(content_frame, text="Total de litros de diésel: 0.00", font=("Arial", 12))
diesel_liters_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

diesel_price_label = tk.Label(content_frame, text="Total del precio del diésel: $0.00", font=("Arial", 12))
diesel_price_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

gasoline_price_label = tk.Label(content_frame, text="Total del precio de la gasolina: $0.00", font=("Arial", 12))
gasoline_price_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

# Botones
button_frame = tk.Frame(root, padx=10, pady=10)
button_frame.pack(fill="x")

open_button = tk.Button(button_frame, text="Abrir Archivo XML", command=open_file, font=("Arial", 12))
open_button.grid(row=0, column=0, padx=5)

exit_button = tk.Button(button_frame, text="Salir", command=root.quit, font=("Arial", 12))
exit_button.grid(row=0, column=1, padx=5)

# Ajustar las columnas en los frames
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
content_frame.grid_columnconfigure(0, weight=1)

# Iniciar el bucle principal
root.mainloop()
