import os
import tkinter as tk 
from tkinter import filedialog, messagebox
from tkinter import font as tkFont # Importar tkFont para manejar fuentes

# --- COLORES DE VALLESALUD (Propuesta) ---
COLOR_PRIMARY_BLUE = "#2196F3"    # Azul vibrante para elementos principales
COLOR_DARK_BLUE = "#1976D2"       # Azul oscuro para estados activos o texto de encabezado
COLOR_LIGHT_BLUE = "#E3F2FD"      # Azul muy claro para fondos de secciones
COLOR_ACCENT_GREEN = "#4CAF50"    # Verde para acciones de éxito o confirmación
COLOR_TEXT_DARK = "#212121"       # Gris oscuro para texto general
COLOR_TEXT_LIGHT = "#FFFFFF"      # Blanco para texto en botones o fondos oscuros
COLOR_BACKGROUND_APP = "#F5F5F5"  # Gris claro para el fondo general de la aplicación
COLOR_BORDER_GRAY = "#DEDEDE"     # Gris para bordes sutiles
COLOR_DELETE_RED = "#E53935"      # Rojo para el botón de eliminar

DIC_TIPOGRAFICO = {
    "DFU" : "FEV_900847382_T",
    "FAC" : "CRC_900847382_T",
    "HCE" : "HEV_900847382_T",
    "LAB" : "PDX_900847382_T",
    "AYD" : "PDX_900847382_T",
    "NCD" : "PDE_900847382_T"
}

ruta_principal= "" # Almacena la ruta de la carpeta
num_entradas = [] # Almacena los diccionarios de entrada para OPS, T y el frame asociado

def seleccion_principal():
    """
    Función que abrirá cuadro de diálogo para seleccionar la carpeta principal 
    """
    global ruta_principal
    ruta_principal = filedialog.askdirectory()
    if ruta_principal:
        # Esta variable esta en al función de tkinter que es el texto que se actualiza para mostrar al usuario
        label_estado.config(text=f"Carpeta seleccionada: {ruta_principal}", fg=COLOR_DARK_BLUE)
    else:
        label_estado.config(text="Carpeta no seleccionada", fg=COLOR_TEXT_DARK)


def filas_entrada():
    """
    Función que servirá para agregar una nueva fila de campos para la entrada de datos para la OPS y la T
    """
    # Usamos un Frame para cada par de entradas para organizarlos mejor
    fr_entrada = tk.Frame(frame_campos, bg=COLOR_LIGHT_BLUE, bd=1, relief=tk.FLAT, padx=5, pady=5)
    fr_entrada.pack(pady=5, fill=tk.X)

    label_ops = tk.Label(fr_entrada, text="Número de OPS:", bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_DARK, font=small_font)
    label_ops.pack(side=tk.LEFT, padx=5)

    entry_ops = tk.Entry(fr_entrada, width=15, bd=1, relief=tk.SOLID, font=entry_font)
    entry_ops.pack(side=tk.LEFT, padx=5, ipady=2)

    label_t = tk.Label(fr_entrada, text="Número de la T:", bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_DARK, font=small_font)
    label_t.pack(side=tk.LEFT, padx=5)

    entry_t = tk.Entry(fr_entrada, width=15, bd=1, relief=tk.SOLID, font=entry_font)
    entry_t.pack(side=tk.LEFT, padx=5, ipady=2)

    # Botón para eliminar esta fila
    btn_delete_row = tk.Button(fr_entrada, text="🗑️", command=lambda: eliminar_fila(fr_entrada, entry_ops, entry_t),
                               bg=COLOR_DELETE_RED, fg=COLOR_TEXT_LIGHT, font=small_font,
                               activebackground="#C62828", activeforeground=COLOR_TEXT_LIGHT,
                               relief=tk.RAISED, bd=1, padx=5, pady=2, cursor="hand2")
    btn_delete_row.pack(side=tk.RIGHT, padx=5)

    # Almacenar el frame y los entry widgets
    num_entradas.append({"frame": fr_entrada, "ops_entry": entry_ops, "t_entry": entry_t})
    
    # Actualizar la región de desplazamiento del canvas
    canvas_entries.update_idletasks() # Asegura que los widgets se dibujen antes de calcular el scrollregion
    canvas_entries.config(scrollregion=canvas_entries.bbox("all"))


def eliminar_fila(frame_to_destroy, ops_entry_to_remove, t_entry_to_remove):
    """
    Elimina una fila específica de campos de entrada (OPS y T).
    """
    global num_entradas
    # Quitar de la lista num_entradas
    num_entradas = [item for item in num_entradas if not (item["ops_entry"] == ops_entry_to_remove and item["t_entry"] == t_entry_to_remove)]
    
    # Destruir el frame completo de la fila
    frame_to_destroy.destroy()

    # Actualizar la región de desplazamiento del canvas
    canvas_entries.update_idletasks() # Asegura que los widgets se eliminen antes de calcular el scrollregion
    canvas_entries.config(scrollregion=canvas_entries.bbox("all"))


def renombramiento():
    """
    Función que realiza el inicio del renombre de los archivos y carpetas que estén escritas incorrectamente
    """
    # Verificamos que la carpeta exista, si no lanzará la advertencia
    if not ruta_principal:
        messagebox.showwarning("ADVERTENCIA", "Por favor, seleccione una carpeta principal antes de ejecutar.")
        return
    
    # Mapeamos los datos que se ingresen por medio de la interfaz de usuario
    data_user = {}
    for entry_data in num_entradas: # Iterar sobre los diccionarios en num_entradas
        try:
            ops_num = entry_data["ops_entry"].get()
            t_num = entry_data["t_entry"].get()
            if ops_num and t_num:
                # Realizaremos una limpieza quitando espacios y cualquier texto ingresado que no sea numérico
                ops_num_clean = ''.join(filter(str.isdigit, ops_num))
                # Aseguramos que el número T también sea solo dígitos si se desea esa limpieza
                t_num_clean = ''.join(filter(str.isdigit, t_num)) 
                if ops_num_clean: # Solo agregamos si el número de OPS es válido después de la limpieza
                    data_user[ops_num_clean] = t_num_clean # Aquí le asignamos el número de la T a una OPS
        except tk.TclError:
            # Si el widget no existe pasamos al siguiente
            continue

    if not data_user:
        messagebox.showwarning("ADVERTENCIA", "Por favor, ingrese al menos un par de números de OPS y T.")
        return
    
    # Lista para almacenar las rutas de las carpetas a renombrar
    folder_process = []

    # Recolección de datos
    try:
        for dirpath, dirnames, filenames in os.walk(ruta_principal):
            for dirname in dirnames:
                if dirname.startswith("OPS"):
                    ops_num = ''.join(filter(str.isdigit, dirname))
                    if ops_num in data_user:
                        t_num = data_user[ops_num]
                        path_subfolder= os.path.join(dirpath, dirname)

                        # Almacenamos la información en tupla
                        folder_process.append((path_subfolder, t_num, dirpath))
        
        # Ejecuta el renombramiento
        files_processed_count = 0
        folders_renamed_count = 0
        warnings_count = 0

        for old_path_subfolder, t_num, parent_path in folder_process:
            # Renombramos los archivos de la subcarpeta
            for filename in os.listdir(old_path_subfolder):
                if filename.lower().endswith(".pdf"): # Asegurar que sea case-insensitive para .pdf
                    base_name, extension = os.path.splitext(filename)

                    for typo_incorrect, prefix_correct in DIC_TIPOGRAFICO.items():
                        if typo_incorrect in base_name:
                            new_name = f"{prefix_correct}{t_num}{extension}"
                            old_path = os.path.join(old_path_subfolder, filename)
                            new_path = os.path.join(old_path_subfolder, new_name)

                            if not os.path.exists(new_path):
                                os.rename(old_path, new_path)
                                files_processed_count += 1
                            else:
                                print(f"Advertencia: El archivo {new_name} ya existe en {old_path_subfolder}. Se omite.")
                                warnings_count += 1
                            break # Una vez que encontramos una coincidencia, pasamos al siguiente archivo
            
            # Renombramos la carpeta después de haber procesado los archivos
            # Asegurarse de que el nuevo nombre de la carpeta sea el número T
            new_folder_name = t_num 
            new_path_subfolder = os.path.join(parent_path, new_folder_name)
            
            # Solo renombrar si la carpeta destino no existe para evitar errores
            if not os.path.exists(new_path_subfolder):
                os.rename(old_path_subfolder, new_path_subfolder)
                folders_renamed_count += 1
            else:
                print(f"Advertencia: La carpeta {new_folder_name} ya existe en {parent_path}. La carpeta original {os.path.basename(old_path_subfolder)} no fue renombrada.")
                warnings_count += 1
        
        messagebox.showinfo(
            "Proceso Completado", 
            f"Proceso finalizado:\n"
            f"- Archivos PDF procesados: {files_processed_count}\n"
            f"- Carpetas renombradas: {folders_renamed_count}\n"
            f"- Advertencias (archivos/carpetas existentes): {warnings_count}"
        )
    
    except Exception as e:
        messagebox.showerror("ERROR", f"Ocurrió un error inesperado durante el renombrado: {e}")


# --- Interacción con el usuario (Interfaz Tkinter) ---
app = tk.Tk()
app.title("Organizador de Archivos Vallesalud")
app.geometry("700x600") # Tamaño inicial de la ventana
app.resizable(True, True) # Permitir redimensionar la ventana
app.config(bg=COLOR_BACKGROUND_APP) # Fondo general de la aplicación

# --- Definición de Fuentes Personalizadas ---
title_font = tkFont.Font(family="Arial", size=18, weight="bold")
header_font = tkFont.Font(family="Arial", size=12, weight="bold")
label_font = tkFont.Font(family="Arial", size=10)
small_font = tkFont.Font(family="Arial", size=9)
button_font = tkFont.Font(family="Arial", size=11, weight="bold")
entry_font = tkFont.Font(family="Arial", size=10)


# --- Frame Principal que contiene todos los elementos ---
main_frame = tk.Frame(app, padx=20, pady=20, bg=COLOR_BACKGROUND_APP, bd=2, relief=tk.GROOVE)
main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# --- Título de la Aplicación ---
label_title = tk.Label(main_frame, text="Organizador de Documentos Vallesalud", 
                       font=title_font, fg=COLOR_DARK_BLUE, bg=COLOR_BACKGROUND_APP)
label_title.pack(pady=15)

# --- Sección 1: Selección de Carpeta ---
frame_selection = tk.LabelFrame(main_frame, text="1. Seleccionar Carpeta Principal", 
                                font=header_font, fg=COLOR_PRIMARY_BLUE, bg=COLOR_LIGHT_BLUE,
                                padx=15, pady=15, bd=1, relief=tk.SOLID)
frame_selection.pack(pady=10, fill=tk.X)

label_folder_instruction = tk.Label(frame_selection, text="Haga clic para elegir la carpeta que contiene las carpetas 'OPS'.", 
                                   bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_DARK, font=label_font)
label_folder_instruction.pack(pady=5)

btn_select= tk.Button(frame_selection, text="Seleccionar Carpeta", command=seleccion_principal,
                      bg=COLOR_PRIMARY_BLUE, fg=COLOR_TEXT_LIGHT, font=button_font,
                      activebackground=COLOR_DARK_BLUE, activeforeground=COLOR_TEXT_LIGHT,
                      relief=tk.RAISED, bd=2, padx=10, pady=5, cursor="hand2")
btn_select.pack(pady=10)

label_estado = tk.Label(frame_selection, text="Carpeta no seleccionada", fg=COLOR_TEXT_DARK, 
                        bg=COLOR_LIGHT_BLUE, font=small_font)
label_estado.pack(pady=5)

# --- Sección 2: Entrada de Pares OPS y T ---
frame_entries_section = tk.LabelFrame(main_frame, text="2. Ingresar Pares de OPS y T", 
                                     font=header_font, fg=COLOR_PRIMARY_BLUE, bg=COLOR_BACKGROUND_APP,
                                     padx=15, pady=15, bd=1, relief=tk.SOLID)
frame_entries_section.pack(pady=10, fill=tk.BOTH, expand=True)

label_entry_instruction= tk.Label(frame_entries_section, text="Agregue o elimine filas e ingrese los números correspondientes:", 
                                  bg=COLOR_BACKGROUND_APP, fg=COLOR_TEXT_DARK, font=label_font)
label_entry_instruction.pack(pady=10)

# --- Botón para agregar más filas de entrada (AHORA DENTRO de frame_entries_section y antes del Canvas) ---
btn_add = tk.Button(frame_entries_section, text="✚ Agregar Par OPS/T", command=filas_entrada, 
                    bg=COLOR_PRIMARY_BLUE, fg=COLOR_TEXT_LIGHT, font=button_font,
                    activebackground=COLOR_DARK_BLUE, activeforeground=COLOR_TEXT_LIGHT,
                    relief=tk.RAISED, bd=2, padx=15, pady=7, cursor="hand2")
btn_add.pack(pady=10) 

# Este frame contendrá las entradas dinámicas, usando un Canvas para hacerla scrollable si hay muchas
canvas_entries = tk.Canvas(frame_entries_section, bg=COLOR_BACKGROUND_APP, bd=0, highlightthickness=0)
canvas_entries.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5) 

scrollbar_entries = tk.Scrollbar(frame_entries_section, orient="vertical", command=canvas_entries.yview)
scrollbar_entries.pack(side=tk.RIGHT, fill=tk.Y)

canvas_entries.configure(yscrollcommand=scrollbar_entries.set)
# Añadido de nuevo el bind para que el scrollregion se actualice correctamente al redimensionar la ventana
canvas_entries.bind('<Configure>', lambda e: canvas_entries.configure(scrollregion = canvas_entries.bbox("all")))

frame_campos = tk.Frame(canvas_entries, bg=COLOR_BACKGROUND_APP)
canvas_entries.create_window((0, 0), window=frame_campos, anchor="nw", width=600) # Ancho fijo para las entradas

# --- Botón de Ejecutar ---
btn_execute = tk.Button(main_frame, text="► Ejecutar Renombrado", command=renombramiento,
                        bg=COLOR_ACCENT_GREEN, fg=COLOR_TEXT_LIGHT, font=button_font,
                        activebackground="#388E3C", activeforeground=COLOR_TEXT_LIGHT, 
                        relief=tk.RAISED, bd=2, padx=20, pady=10, cursor="hand2")
btn_execute.pack(pady=20)

# Llama a filas_entrada una vez al inicio para tener una fila por defecto
filas_entrada()

app.mainloop()