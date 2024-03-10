import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from tkinter import filedialog
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

direcciones_pista=list(range(0, 361, 10))
filename = ""
ventana_grafico = None
def df_segmentado(filename):    
    vientos = pd.read_csv(filename, sep=None,engine='python')
    intervalo = combobox_intervalo.get()
    if intervalo:
        intervalo = int(intervalo)
        rangos = np.arange(0, vientos.iloc[:,1].max() +intervalo, intervalo)
        for i in range(len(rangos) - 1):
            inicio = rangos[i]
            fin = rangos[i+1]
            columna = f"{inicio}-{fin}"
            vientos[columna] = ((vientos.iloc[:,1] > inicio) & (vientos.iloc[:,1] <= fin)).astype(int)
    nuevo_df = vientos.drop(vientos.columns[1], axis=1)
    df_final = nuevo_df.groupby(nuevo_df.columns[0]).sum().reset_index()
    #print(df_final)
    #print(df_final.iloc[:,1:].sum().sum())
    return df_final
    
def df_vientos_cruzado(df_final):        
    v_c_list = []  
    for w in direcciones_pista:
        v_c = pd.DataFrame(columns=df_final.columns)
        for direccion in df_final.iloc[:,0]:
            for col in df_final.columns[1:]:
                inicio, fin = map(float, col.split('-'))
                angulo_en_radianes = (direccion - w) * np.pi / 180
                result = np.abs(fin * np.sin(angulo_en_radianes))
                result_dec= round(result,2)
                v_c.loc[direccion, col] = result_dec
        v_c.iloc[:,0] = df_final.iloc[:, 0]
        v_c.reset_index(drop=True, inplace=True)
        v_c_list.append(v_c)
    #print(v_c_list)
    return v_c_list
   
def df_frecuencias_admisibles(v_c_list,df_final): 
    maxim = float('-inf')
    lista=[]
    valor_limite=combobox_limites.get()
    valor_limite=int(valor_limite)    
    for v_c in v_c_list:
        f_ad = pd.DataFrame()
        for index, row in v_c.iloc[:, 1:].iterrows():
            for columna, valor in row.items():        
                if valor < valor_limite:
                    if columna in df_final.columns[1:]:  
                        valor_df_final = df_final.loc[index, columna]
                        f_ad.loc[index, columna] = valor_df_final
                    else:
                        f_ad.loc[index, columna] = 0
                else:
                    f_ad.loc[index,columna] = 0
        
        f_ad = f_ad.astype(int)
        lista.append(f_ad)
        print(f_ad)
        print(f_ad.sum().sum())
  
    for w, f_ad in zip(direcciones_pista, lista):
        if f_ad.sum().sum() > maxim:
            maxim = f_ad.sum().sum()
            maxim_w = w
            ang_supl= (w + 180) % 360
            f_ad_maximo=f_ad.copy()
    #print(df_final)        
    print(f_ad_maximo)   
    print(f_ad_maximo.sum().sum())
    vientosceros = pd.read_csv(filename, sep=None,engine='python')
    viento_calma = int(vientosceros[vientosceros.iloc[:,1]==0].count().iloc[1])
    suma_df_final=df_final.iloc[:,1:].sum().sum()
    cohe=((maxim+viento_calma) / (suma_df_final+viento_calma) * 100).round(2)
    #maxim_w_abrev=maxim_w/10
    #ang_supl_abrev=ang_supl/10
    resultados=f"MAYOR COHEFICIENTE\n\nFrecuencia máxima: {maxim}\nDirección de la pista:{maxim_w} - {ang_supl}\nCoheficiente de utilización:{cohe}%"
    print(suma_df_final)
    print(resultados)
    print(viento_calma)
    return resultados, f_ad_maximo,maxim_w
    
def cargar_archivo():
    global filename
    filename = filedialog.askopenfilename(initialdir="/", title="Seleccionar archivo CSV", filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
    if filename:
        print("Archivo seleccionado:", filename)
"""
def resultado():
    global filename
    if not filename:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo antes de generar resultados.")
        return
    # Verificar si se ha seleccionado un valor en combobox_intervalo
    if not combobox_intervalo.get():
        messagebox.showwarning("Advertencia", "Por favor, selecciona un intervalo.")
        return
    # Verificar si se ha seleccionado un valor en combobox_limites
    if not combobox_limites.get():
        messagebox.showwarning("Advertencia", "Por favor, selecciona un límite.")
        return
    ######LLAMADO DE LOS DATAFRAMES###############
    df_final = df_segmentado(filename)
    v_c_list = df_vientos_cruzado(df_final)
    resultados,_,_=df_frecuencias_admisibles(v_c_list,df_final)
    etiqueta.config(text=resultados,justify="left")
"""   
def calculo_grafico():
    global ventana_grafico
    if not filename:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo antes de generar el gráfico.")
        return
    if not combobox_intervalo.get():
        messagebox.showwarning("Advertencia", "Por favor, selecciona un intervalo.")
        return
    if not combobox_limites.get():
        messagebox.showwarning("Advertencia", "Por favor, selecciona un límite.")
        return
    ######LLAMADO DE LOS DATAFRAMES###############     
    df_final=df_segmentado(filename)
    v_c_list = df_vientos_cruzado(df_final)
    resultados, _,maxim_w=df_frecuencias_admisibles(v_c_list,df_final)
    ######CREACION ROSA DE VIENTO###############
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks([d * (2 * np.pi / 360) for d in range(10, 361, 10)])
    ax.tick_params(axis='x', labelsize=7)
    
    #############PISTA DE ATERRIZAJE################
    dir_pista = maxim_w
    dir_pista_rad = np.radians(dir_pista)
    dir_opuesto=(dir_pista + 180) % 360
    dir_opuesto_rad=np.radians(dir_opuesto)
    ax.plot([dir_opuesto_rad,dir_pista_rad], [0, 1000], color='grey', linewidth=50,alpha=0.3)
    ax.plot([dir_pista_rad,dir_opuesto_rad], [0, 1000], color='grey', linewidth=50,alpha=0.3)
    r = 1000  # Radio máximo
    ax.plot([0, dir_pista_rad], [0, r], color='red', linewidth=2, alpha=0.5)
    ax.plot([0,dir_opuesto_rad], [0, r], color='red', linewidth=2, alpha=0.5)
    plt.gca().yaxis.set_tick_params(labelsize=0)
    
    if ventana_grafico is not None:
        ventana_grafico.destroy()
        
    ventana_grafico = tk.Toplevel()
    ventana_grafico.title("Rosa de Vientos")

    # Crear el lienzo para el gráfico
    canvas = FigureCanvasTkAgg(fig, master=ventana_grafico)
    canvas.get_tk_widget().pack()
    frame_etiqueta = tk.Frame(ventana_grafico)
    frame_etiqueta.pack()
    etiqueta_resultados = tk.Label(frame_etiqueta, text=resultados,justify="left")
    etiqueta_resultados.pack()
    # Actualizar el lienzo
    canvas.draw()

def validar_entrada_pista(dir_pista):
    if dir_pista == "":
        return True
    try:
        valor = int(dir_pista)
        if 0 <= valor <= 365:
            return True
        else:
            messagebox.showerror("Error", "Ingresa un número entre 0 y 365")
            return False
    except ValueError:
        messagebox.showerror("Error", "Ingresa un valor numérico válido")
        return False
        
def resultado_personalizado(): 
    global ventana_grafico
    if not filename:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo antes de generar el gráfico.")
        return
    if not combobox_intervalo.get():
        messagebox.showwarning("Advertencia", "Por favor, selecciona un intervalo.")
        return
    if not combobox_limites.get():
        messagebox.showwarning("Advertencia", "Por favor, selecciona un límite.")
        return
        
    df_final=df_segmentado(filename)
    dato = int(entrada_pista.get())
    viento_cruzado = pd.DataFrame(columns=df_final.columns)
    for direccion in df_final.iloc[:,0]:
        for col in df_final.columns[1:]:
            inicio, fin = map(float, col.split('-'))
            angulo_en_radianes = (direccion - dato) * np.pi / 180
            result = np.abs(fin * np.sin(angulo_en_radianes))
            result_dec= round(result,2)
            viento_cruzado.loc[direccion, col] = result_dec
    viento_cruzado.iloc[:,0] = df_final.iloc[:, 0]
    viento_cruzado.reset_index(drop=True, inplace=True)
    print(viento_cruzado)
    ########
    maxim = float('-inf')
    valor_limite=combobox_limites.get()
    valor_limite=int(valor_limite)    
    f_ad = pd.DataFrame()
    for index, row in viento_cruzado.iloc[:, 1:].iterrows():
        for columna, valor in row.items():        
            if valor < valor_limite:
                if columna in df_final.columns[1:]:  
                    valor_df_final = df_final.loc[index, columna]
                    f_ad.loc[index, columna] = valor_df_final
                else:
                    f_ad.loc[index, columna] = 0
            else:
                f_ad.loc[index,columna] = 0        
    f_ad = f_ad.astype(int)
    print(f_ad)
    print(f_ad.sum().sum())  
    maxim = f_ad.sum().sum()
    maxim_w = dato
    ang_supl= (dato + 180) % 360
    #f_ad_maximo=f_ad.copy()
    #print(df_final)        
    vientosceros = pd.read_csv(filename, sep=";")
    viento_calma = int(vientosceros[vientosceros.iloc[:,1]==0].count().iloc[1])
    suma_df_final=df_final.iloc[:,1:].sum().sum()
    cohe=((maxim+viento_calma) / (suma_df_final+viento_calma) * 100).round(2)
    #maxim_w_abrev=maxim_w/10
    #ang_supl_abrev=ang_supl/10
    resultados_perso=f"Frecuencia máxima:{maxim}\nDirección de la pista:{maxim_w} - {ang_supl}\nCoheficiente de utilización:{cohe}%"
    print(resultados_perso)
    #######
    if ventana_grafico is not None:
        ventana_grafico.destroy()
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks([d * (2 * np.pi / 360) for d in range(10, 361, 10)])
    ax.tick_params(axis='x', labelsize=7)
    
    #############PISTA DE ATERRIZAJE################
    dir_pista = maxim_w
    dir_pista_rad = np.radians(dir_pista)
    dir_opuesto=(dir_pista + 180) % 360
    dir_opuesto_rad=np.radians(dir_opuesto)
    ax.plot([dir_opuesto_rad,dir_pista_rad], [0, 1000], color='grey', linewidth=50,alpha=0.3)
    ax.plot([dir_pista_rad,dir_opuesto_rad], [0, 1000], color='grey', linewidth=50,alpha=0.3)
    r = 1000  # Radio máximo
    ax.plot([0, dir_pista_rad], [0, r], color='red', linewidth=2, alpha=0.5)
    ax.plot([0,dir_opuesto_rad], [0, r], color='red', linewidth=2, alpha=0.5)
    plt.gca().yaxis.set_tick_params(labelsize=0)
    ventana_grafico = tk.Toplevel()
    ventana_grafico.title("Rosa de Vientos")

    # Crear el lienzo para el gráfico
    canvas = FigureCanvasTkAgg(fig, master=ventana_grafico)
    canvas.get_tk_widget().pack()
    frame_etiqueta = tk.Frame(ventana_grafico)
    frame_etiqueta.pack()
    etiqueta_resultados = tk.Label(frame_etiqueta, text=resultados_perso)
    etiqueta_resultados.pack()
    # Actualizar el lienzo
    canvas.draw()
    #return viento_cruzado, resultados_perso

####TKINTER#####
root = tk.Tk()
root.title("Wind_Rose_Custom")
root.geometry("330x270")
frame = tk.Frame(root, width=310, height=250,bg="lightblue")
frame.grid(row=0,column=0, padx=10, pady=10)
combobox_intervalo = ttk.Combobox(frame, values=[1,2, 3, 5, 10])
combobox_intervalo.place(x=10, y=60)
combobox_limites = ttk.Combobox(frame, values=[10,13,20])
combobox_limites.place(x=160, y=60)
boton_cargar = ttk.Button(frame, text="Cargar archivo",command=cargar_archivo)
boton_cargar.place(x=10,y=20)
boton_grafico = ttk.Button(frame, text="Mayor Coheficiente", command=calculo_grafico)
boton_grafico.place(x=10,y=100)
titulo_entrada=tk.Label(frame, text="Indicar una dirección para la pista: ",bg="lightblue")
titulo_entrada.place(x=7,y=150)
validate_command = root.register(validar_entrada_pista)
entrada_pista=tk.Entry(frame, validate="key", validatecommand=(validate_command, '%P'))
entrada_pista.place(x=10,y=180)
boton_generar_2 = ttk.Button(frame, text="Resultado",command=resultado_personalizado)
boton_generar_2.place(x=150,y=177)
root.mainloop()
