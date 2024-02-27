######SEGUNDA VERSION_VERSION FONAL########

import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from tkinter import filedialog

direcciones_pista = list(range(0, 361, 10))
valor_limite = None  # Variable para almacenar el valor seleccionado en el segundo combobox
vientos = None 
def viento_cruzado(direcciones_pista,df_final):
    if df_final is None:
        return None
    v_c_list = []  
    for w in direcciones_pista:
        v_c = pd.DataFrame(index=df_final.index)
        for direccion in df_final.index:
            for col in df_final.columns[0:]:
                inicio, fin = map(float, col.split('-'))
                angulo_en_radianes = (direccion - w) * np.pi / 180
                result = np.abs(fin * np.sin(angulo_en_radianes))
                result_dec= round(result,2)
                v_c.loc[direccion, col] = result_dec
        v_c.columns = df_final.columns
        v_c_list.append(v_c)  
    return v_c_list

def actualizar_intervalo(vientos):
    intervalo = combobox_intervalo.get()  # Obtener el valor seleccionado del combobox
    if intervalo:  # Verificar si se ha seleccionado un valor
        intervalo = int(intervalo)  # Convertir el valor a entero
        #vientos = pd.read_csv(filename, sep=";")
        vientos.rename(columns={"Kts": "Nodos"}, inplace=True)
        direcciones = vientos.index.unique()
        direcciones = direcciones.sort_values()  # Cambia 'sort' por 'sort_values'
        #vientos = vientos.set_index('DIRECCION')
        rangos = np.arange(0, vientos['Nodos'].max() + intervalo, intervalo)

        for i in range(len(rangos) - 1):
            inicio = rangos[i]
            fin = rangos[i+1]
            columna = f"{inicio}-{fin}"
            vientos[columna] = ((vientos['Nodos'] > inicio) & (vientos['Nodos'] <= fin)).astype(int)
        nuevo_df = vientos.drop(columns=['Nodos'])
        df_final = nuevo_df.groupby('DIRECCION').sum().reset_index()
        df_final = df_final.set_index('DIRECCION')

        print(df_final)
        print(df_final.sum().sum())
        v_c_list = viento_cruzado(direcciones_pista, df_final)  # Llamar a viento_cruzado después de actualizar df_final
        return vientos, df_final, v_c_list
    else:
        return None, None

        
def frecuencia_admisible(vientos,v_c_list):
    vientos, df_final, v_c_list= actualizar_intervalo(vientos)
    maxim = float('-inf')
    maxim_w = None
    for idx, w in enumerate(direcciones_pista):
        v_c = v_c_list[idx]  # Obtener el v_c correspondiente a la iteración actual
        f_ad = pd.DataFrame(index=df_final.index)
        for index, row in v_c.iterrows():
            for columna, valor in row.items():        
                if valor_limite is not None and valor < valor_limite:
                    if columna in df_final.columns:  # Verificar si la columna existe en df_final
                        valor_df_final = df_final.loc[index, columna]
                        f_ad.loc[index, columna] = valor_df_final
                    else:
                        f_ad.loc[index, columna] = 0
                else:
                    f_ad.loc[index,columna] = 0
        
        f_ad = f_ad.astype(int)
        
        # Actualizar maxim y maxim_w si se encuentra un nuevo máximo
        if f_ad.sum().sum() > maxim:
            maxim = f_ad.sum().sum()
            maxim_w = w
            maxim_df = f_ad.copy()    
    return maxim_df, maxim, maxim_w

def coheficiente(v_c_list, df_final):
    maxim_df,maxim, maxim_w = frecuencia_admisible(vientos,v_c_list)
    viento_calma = 10853
    suma_total_frec = df_final.sum().sum()
    cohe = ((maxim + viento_calma) / (viento_calma + suma_total_frec) * 100).round(2)
    resultado_texto = f"La pista con dirección {maxim_w} tiene este coeficiente: {cohe}%"
      
    return resultado_texto
        
def mostrar_resultados(vientos,df_final, v_c_list):
    if df_final is not None:
        print("DataFrame Final:")
        print(df_final)
    if v_c_list is not None:
        print("Lista de DataFrames de Viento Cruzado:")
        for idx, v_c in enumerate(v_c_list):
            print(f"Viento Cruzado para dirección {direcciones_pista[idx]}:")
            print(v_c)
    maxim_df, maxim, maxim_w = frecuencia_admisible(vientos,v_c_list)
    
    # Mostrar los resultados
    print("Máximo DataFrame de Frecuencias Admisibles:")
    print(maxim_df)
    print("Máxima Suma de Frecuencias Admisibles:")
    print(maxim)
    print("Dirección correspondiente al máximo:")
    print(maxim_w)
    print(" ")
    print(" ")
    print(coheficiente(v_c_list, df_final))
    resultado_texto = coheficiente(v_c_list, df_final)
    etiqueta_resultado.config(text=resultado_texto)
    

def abrir_archivo():
    global vientos
    filename = filedialog.askopenfilename(initialdir="/", title="Seleccionar archivo CSV", filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
    if filename:
        print("Archivo seleccionado:", filename)
        vientos = pd.read_csv(filename, sep=";")
        vientos.rename(columns={"Kts": "Nodos"}, inplace=True)
        vientos = vientos.set_index('DIRECCION')
        direcciones = vientos.index.unique()
        direcciones = direcciones.sort_values()  # Cambia 'sort' por 'sort_values'
        combobox_intervalo.config(state="readonly")
        return vientos

        
def actualizar_combobox():
   if vientos is not None:
       mostrar_resultados(*actualizar_intervalo(vientos))
       boton_generar.config(state="normal")
       combobox_limites.focus_set()
       
       
def on_combobox_intervalo_select(event):
    # Esta función maneja la selección en el combobox_intervalo
    combobox_limites.config(state="readonly")  # Habilitamos el combobox_limites
    combobox_limites.focus_set()  # Nos aseguramos de que el foco esté en el combobox_limites

def on_combobox_limites_select(event):
    # Esta función maneja la selección en el combobox_limites
    global valor_limite
    valor = combobox_limites.get()
    if valor:
        valor_limite = int(valor)
        boton_generar.config(state="normal")
    else:
        boton_generar.config(state="disabled")

######TKINTER########
root = tk.Tk()
root.title("Wind_Rose_Custom")
root.geometry("400x200") 

frame = tk.Frame(root, bg="lightgrey", width=400, height=300)
frame.place(relx=0.5, rely=0, anchor="n")
boton_actualizar = ttk.Button(frame, text="Cargar archivo",command=abrir_archivo)
boton_actualizar.place(x=10,y=20)

combobox_intervalo = ttk.Combobox(frame, values=[2, 3, 5, 10],state="disabled")
combobox_intervalo.place(x=10, y=60)
combobox_intervalo.bind("<<ComboboxSelected>>", on_combobox_intervalo_select)

combobox_limites = ttk.Combobox(frame, values=[10,13,20], state="disabled")
combobox_limites.place(x=200, y=60)
combobox_limites.bind("<<ComboboxSelected>>", on_combobox_limites_select)

boton_generar = ttk.Button(frame, text="Generar", command=actualizar_combobox, state="disabled")
boton_generar.place(x=10,y=100)
mensaje = tk.Label(frame, text="")
mensaje.place(x=10,y=170)
etiqueta_resultado = tk.Label(frame, text="", wraplength=380)
etiqueta_resultado.place(x=10, y=170)

df_final = None
root.mainloop()
