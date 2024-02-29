import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from tkinter import filedialog

direcciones_pista = list(range(0, 361, 10))
def viento(filename):   
    vientos = pd.read_csv(filename, sep=";")
    vientos.rename(columns={"Kts": "Nodos"}, inplace=True)
    vientos = vientos.set_index('DIRECCION')
    intervalo = combobox_intervalo.get()
    if intervalo:
        intervalo = int(intervalo)
        rangos = np.arange(0, vientos['Nodos'].max() + intervalo, intervalo)

        for i in range(len(rangos) - 1):
            inicio = rangos[i]
            fin = rangos[i+1]
            columna = f"{inicio}-{fin}"
            vientos[columna] = ((vientos['Nodos'] > inicio) & (vientos['Nodos'] <= fin)).astype(int)
        nuevo_df = vientos.drop(columns=['Nodos'])
        df_final = nuevo_df.groupby('DIRECCION').sum().reset_index()
        df_final = df_final.set_index('DIRECCION')
        
    #lista de vientos cruzados
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
        
    ##probando los df de frecuencias admisibles
    maxim = float('-inf')
    maxim_w = None
    valor_limite=combobox_limites.get()
    valor_limite=int(valor_limite)
    for idx, v_c in enumerate(v_c_list):
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
    print(df_final)
    print(df_final.sum().sum())
    print(" ")
    print(maxim_df)
    print(maxim)
    """ 
    print(df_final)
    print("")
    print("suma")
    print(df_final.sum().sum())    
    print("")
    print("Lista de DataFrames de Viento Cruzado:")
    for idx, v_c in enumerate(v_c_list):
        print(f"Viento Cruzado para dirección {direcciones_pista[idx]}:")
        print(v_c)
    """
def abrir_archivo():
    global filename
    filename = filedialog.askopenfilename(initialdir="/", title="Seleccionar archivo CSV", filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
    if filename:
        print("Archivo seleccionado:", filename)        
    
root = tk.Tk()
root.title("Wind_Rose_Custom")
root.geometry("400x200")

frame = tk.Frame(root, bg="lightgrey", width=400, height=300)
frame.place(relx=0.5, rely=0, anchor="n")
boton_cargar = ttk.Button(frame, text="Cargar archivo",command=abrir_archivo)
boton_cargar.place(x=10,y=20)
combobox_intervalo = ttk.Combobox(frame, values=[2, 3, 5, 10])
combobox_intervalo.place(x=10, y=60)
combobox_limites = ttk.Combobox(frame, values=[10,13,20])
combobox_limites.place(x=200, y=60)
boton_generar = ttk.Button(frame, text="Generar", command=lambda: viento(filename))
boton_generar.place(x=10,y=100)
root.mainloop()
