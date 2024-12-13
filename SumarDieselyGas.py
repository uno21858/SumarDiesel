import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

# Funciones de procesamiento de datos
def sacar_datos(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

        if root.tag.endswith('Comprobante'):
            fecha = root.attrib.get('Fecha', 'Fecha no encontrada')
            folio = root.attrib.get('Folio', 'Folio no encontrado')
        else:
            comprobante = root.find('.//cfdi:Comprobante', namespaces)
            fecha = comprobante.attrib.get('Fecha', 'Fecha no encontrada') if comprobante is not None else 'Fecha no encontrada'
            folio = comprobante.attrib.get('Folio', 'Folio no encontrado') if comprobante is not None else 'Folio no encontrado'

        return fecha, folio
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar el archivo: {e}")
        return "Desconocido"

def extract_fuel_data(file_path):
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

# Función para abrir el archivo y actualizar los valores
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml")])
    if file_path:
        diesel_liters, diesel_price, gasoline_price = extract_fuel_data(file_path)
        diesel_liters_label.config(text=f"Total de litros de diesel: {diesel_liters:,.3f}")
        diesel_price_label.config(text=f"Total del precio del diésel: ${diesel_price:,.2f}")
        gasoline_price_label.config(text=f"Total del precio de la gasolina: ${gasoline_price:,.2f}")
        fecha, folio = sacar_datos(file_path)
        fecha_label.config(text=f"Fecha de la factura: {fecha[:10]}")
        folio_label.config(text=f"Folio de la factura: D{folio}")

# Configuración de la interfaz grafica
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
