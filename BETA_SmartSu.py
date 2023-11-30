# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 15:38:58 2023

@author: Matías
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.pdfgen import canvas
import os
import matplotlib.font_manager as fm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.dates as mdates
from datetime import datetime
import locale
from reportlab.platypus import Table, TableStyle
from PIL import Image, ImageTk
import subprocess
from reportlab.lib.pagesizes import A4
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

locale.setlocale(locale.LC_TIME, 'es_CL.UTF-8')

# Carpeta hogares
ID = 'ID' 
# Función para cargar un dataframe hogares
def cargar_data_frame(hogar_id):
    csv_file = os.path.join(ID, f'{hogar_id}.csv')
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        return None

# Carpeta datos hogares
folder = 'datos' 

# Función para cargar dataframe datos
def cargar_data_frame_datos(hogar_datos):
    csv_file = os.path.join(folder, f'{hogar_datos}.csv')
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        return None

# Generar los gráficos e informe
def generar_graficos_informe():
    hogar_input = entry_hogar.get()
    mes = month_combobox.current() + 1
    año = int(entry_año.get())

    # Cargar datos
    df_hogar = cargar_data_frame(hogar_input)
    df_datos = cargar_data_frame_datos(hogar_input)
    
    #COLORES 
    color_3 = '000000' #negro
    color_4 = '#FFFFFF' #blanco
    color_5 = '#006D4D' #título
    color_6 = '#E6FFFA' #fondo

    # Fuentes
    pdfmetrics.registerFont(TTFont('robotoitalic', 'Roboto-Italic.ttf'))
    pdfmetrics.registerFont(TTFont('robotoregular', 'Roboto-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('robotolight', 'Roboto-Light.ttf'))
    pdfmetrics.registerFont(TTFont('robotobold', 'Roboto-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('robotomedium', 'Roboto-Medium.ttf'))

    # Cargar fuente personalizada
    ruta_fuente = 'Roboto-Light.ttf'
    roboto = fm.FontProperties(fname=ruta_fuente, size=25)
    robotoy = fm.FontProperties(fname=ruta_fuente, size=20)

    if df_hogar is not None:
        df_hogar['day'] = pd.to_datetime(df_hogar['day'], format='%Y-%m-%d')
        df_filtrado = df_hogar[(df_hogar['day'].dt.month == mes) & (df_hogar['day'].dt.year == año)]
        df_filtradototal = df_hogar.copy()
        # Crear una nueva ventana para mostrar los gráficos
        """graficos_ventana = tk.Toplevel(window)
        graficos_ventana.title("Gráficos")
        graficos_ventana.geometry('900x650')"""

        # Crear pestañas
        style = ttk.Style()        
        # Estilo de las pestañas
        style.configure("Custom.TNotebook.Tab", font=('Helvetica', '12', ))        
        # Aplicar estilo
        notebook = ttk.Notebook(window, style="Custom.TNotebook")
        notebook.pack(fill='both', expand=True)        

        if not df_filtrado.empty:
            # Crear el dataframe para la tabla
            df_tabla = df_filtrado[['day', 'energy_sum']].copy()
            df_tabla['energy_sum'] = df_tabla['energy_sum'] * 191.12
            # Filtra el dataframe para incluir solo las filas del mes y año seleccionados
            df_mes_seleccionado = df_hogar[(df_hogar['day'].dt.month == mes) & (df_hogar['day'].dt.year == año)]
            #energía total gastada en el mes
            energia_total_mes = df_mes_seleccionado['energy_sum'].sum()

            # Crear gráfico de la tabla
            fig_tabla = plt.Figure(figsize=(12, 6))
            ax_tabla = fig_tabla.add_subplot(111)
            sns.lineplot(x=df_tabla['day'], y=df_tabla['energy_sum'], color=color_5,  linewidth=4, ax=ax_tabla)
            ax_tabla.set_xlabel('Fecha', fontsize=12)
            ax_tabla.set_ylabel('Energía (multiplicada por 191.12)', fontsize=12)
            ax_tabla.set_title('Energía  por día', fontproperties=roboto)
            ax_tabla.tick_params(axis='y', labelsize=12)
            date_format = mdates.DateFormatter("%d-%m-%Y")
            ax_tabla.xaxis.set_major_formatter(date_format)           
            ax_tabla.tick_params(axis='x', rotation=35, labelsize=12)
            ax_tabla.grid(True, linestyle='', linewidth=2)
            fig_tabla.patch.set_facecolor(color_6)
            ax_tabla.set_facecolor(color_6)
            # Filtrar el máximo y mínimo consumo para el gráfico de la tabla
            max_consumo_tabla = df_tabla['energy_sum'].max()
            min_consumo_tabla = df_tabla['energy_sum'].min()
            dia_max_consumo_tabla = df_tabla.loc[df_tabla['energy_sum'].idxmax(), 'day']
            dia_min_consumo_tabla = df_tabla.loc[df_tabla['energy_sum'].idxmin(), 'day']
            
            ax_tabla.plot(dia_max_consumo_tabla, max_consumo_tabla, 'ro', markersize=7, label='Máximo')
            ax_tabla.plot(dia_min_consumo_tabla, min_consumo_tabla, 'bo', markersize=7, label='Mínimo')
            ax_tabla.legend()

            # Gráfico consumo mensual
            fig_consumo_dia = plt.Figure(figsize=(14, 6))            
            ax1 = fig_consumo_dia.add_subplot(111)
            sns.lineplot(x=df_filtrado['day'], y=df_filtrado['energy_sum'], color=color_5, linewidth=4, ax=ax1)
            ax1.set_xlabel('Fecha', fontproperties=robotoy)
            ax1.set_ylabel('Consumo de energía [kWh] \n', fontproperties=robotoy)
            #ax1.set_title('Consumo de energía mensual\n', fontproperties=roboto)
            ax1.tick_params(axis='y', labelsize=12)        
            date_format = mdates.DateFormatter("%d-%m-%Y")
            ax1.xaxis.set_major_formatter(date_format)           
            ax1.tick_params(axis='x', rotation=35, labelsize=12)
            ax1.grid(True, linestyle='--', linewidth=0.5)   
            fig_consumo_dia.patch.set_facecolor(color_6)
            ax1.set_facecolor(color_6)
            max_consumo = df_filtrado['energy_sum'].max()
            dia_max_consumo = df_filtrado.loc[df_filtrado['energy_sum'].idxmax(), 'day']
            ax1.plot(dia_max_consumo, max_consumo, 'ro', markersize=7, label='Máximo')                      
            min_consumo = df_filtrado['energy_sum'].min()
            dia_min_consumo = df_filtrado.loc[df_filtrado['energy_sum'].idxmin(), 'day']
            ax1.plot(dia_min_consumo, min_consumo, 'bo', markersize=7, label='Mínimo')
            ax1.legend()
            # Pestaña para el gráfico de consumo diario
            ax1 = ttk.Frame(notebook)
            notebook.add(ax1, text=' Consumo Diario ')
            canvas_consumo_dia = FigureCanvasTkAgg(fig_consumo_dia, master=ax1)
            canvas_consumo_dia.draw()
            canvas_consumo_dia.get_tk_widget().pack(fill='both', expand=True)
            # Filtrar datos de la última semana del mes
            ultimo_dia_mes = df_filtrado['day'].max()
            inicio_ultima_semana = ultimo_dia_mes - pd.DateOffset(days=7)         
            df_ultima_semana = df_filtrado[(df_filtrado['day'] >= inicio_ultima_semana) & (df_filtrado['day'] <= ultimo_dia_mes)]
            
            # Crear el gráfico para el consumo máximo de la última semana del mes
            fig_ultima_semana = plt.Figure(figsize=(12, 6))
            ax4 = fig_ultima_semana.add_subplot(111)
            sns.lineplot(x=df_ultima_semana['day'], y=df_ultima_semana['energy_sum'], color=color_5, linewidth=4, ax=ax4)
            ax4.set_xlabel('fecha', fontsize=12)
            ax4.set_ylabel('Consumo máximo de energía [kWh]', fontsize=12)
            #ax4.set_title('Consumo máximo de energía de la última semana del mes', fontsize=14)
            ax4.tick_params(axis='y',  labelsize=12)
            
            # Formatear el eje x
            date_format = mdates.DateFormatter("%d-%m-%Y")
            ax4.xaxis.set_major_formatter(date_format)          
            ax4.tick_params(axis='x', rotation=35, labelsize=12)
            ax4.grid(True, linestyle='-', linewidth=1)
            fig_ultima_semana.patch.set_facecolor(color_6)
            ax4.set_facecolor(color_6)
            # Filtrar el máximo y mínimo consumo para el gráfico de la última Semana
            max_consumo_semana = df_ultima_semana['energy_sum'].max()
            min_consumo_semana = df_ultima_semana['energy_sum'].min()
            dia_max_consumo_semana = df_ultima_semana.loc[df_ultima_semana['energy_sum'].idxmax(), 'day']
            dia_min_consumo_semana = df_ultima_semana.loc[df_ultima_semana['energy_sum'].idxmin(), 'day']
            
            # Para el máximo consumo (círculo)
            ax4.plot(dia_max_consumo_semana, max_consumo_semana, 'ro', markersize=7, label=f'Máximo: {max_consumo_semana:.2f}')
            # Para el mínimo consumo (cuadrado)
            ax4.plot(dia_min_consumo_semana, min_consumo_semana, 'bo', markersize=7, label=f'Mínimo: {min_consumo_semana:.2f}')
            ax4.legend()
            # Pestaña para el gráfico de consumo de la última semana
            tab3 = ttk.Frame(notebook)
            notebook.add(tab3, text='Última Semana')
            canvas_ultima_semana = FigureCanvasTkAgg(fig_ultima_semana, master=tab3)
            canvas_ultima_semana.draw()
            canvas_ultima_semana.get_tk_widget().pack(fill='both', expand=True)
            # Filtrar el dataframe para obtener los datos de los últimos 12 meses
            fecha_actual = df_filtrado['day'].max()
            fecha_inicio = fecha_actual - pd.DateOffset(months=12)
            
            df_ultimos_12_meses = df_filtradototal[(df_filtradototal['day'] >= fecha_inicio) & (df_filtradototal['day'] <= fecha_actual)]
            
            # Crear el gráfico de línea para el consumo durante los últimos 12 meses
            fig_ultimos_12_meses = plt.Figure(figsize=(12, 6))
            ax5 = fig_ultimos_12_meses.add_subplot(111)
            sns.lineplot(x=df_ultimos_12_meses['day'], y=df_ultimos_12_meses['energy_sum'], color=color_5, linewidth=2, ax=ax5)
            ax5.set_xlabel('Fecha', fontsize=12)
            ax5.set_ylabel('Consumo de energía [kWh]', fontsize=12)
            #ax5.set_title('Consumo de energía durante los últimos 12 meses\n', fontsize=14)
            
            # Eje x ax5
            date_format = mdates.DateFormatter("%d-%m-%Y")
            ax5.xaxis.set_major_formatter(date_format)
            ax5.tick_params(axis='x', rotation=35, labelsize=12)
            ax5.grid(True, linestyle='--', linewidth=0.5)
            fig_ultimos_12_meses.patch.set_facecolor(color_6)
            ax5.set_facecolor(color_6)
            # Filtrar el máximo y mínimo consumo para el gráfico de los Últimos 12 Meses
            max_consumo_ultimos_12_meses = df_ultimos_12_meses['energy_sum'].max()
            min_consumo_ultimos_12_meses = df_ultimos_12_meses['energy_sum'].min()
            dia_max_consumo_ultimos_12_meses = df_ultimos_12_meses.loc[df_ultimos_12_meses['energy_sum'].idxmax(), 'day']
            dia_min_consumo_ultimos_12_meses = df_ultimos_12_meses.loc[df_ultimos_12_meses['energy_sum'].idxmin(), 'day']     
            # máximo consumo
            ax5.plot(dia_max_consumo_ultimos_12_meses, max_consumo_ultimos_12_meses, 'ro', markersize=7, label='Máximo')
            # mínimo consumo
            ax5.plot(dia_min_consumo_ultimos_12_meses, min_consumo_ultimos_12_meses, 'bo', markersize=7, label='Mínimo')
            ax5.legend()
            ax5.tick_params(axis='y', labelsize=12)
            # Pestaña para el gráfico de consumo de los últimos 12 meses
            tab4 = ttk.Frame(notebook)
            notebook.add(tab4, text='Últimos 12 Meses')
            canvas_ultimos_12_meses = FigureCanvasTkAgg(fig_ultimos_12_meses, master=tab4)
            canvas_ultimos_12_meses.draw()
            canvas_ultimos_12_meses.get_tk_widget().pack(fill='both', expand=True)
            
            # Heatmap calendario          
            heatmap_data = df_filtrado.pivot_table(values='energy_sum', index=df_filtrado['day'].dt.week, columns=df_filtrado['day'].dt.weekday)  
            fig_heatmap = plt.Figure(figsize=(8, 6))
            ax_heatmap = fig_heatmap.add_subplot(111)            
            # Días de la semana
            dias_semana = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
            # Número de días en el mes
            num_dias = df_filtrado['day'].dt.days_in_month.iloc[0]  # Suponiendo que todos los días pertenecen al mismo mes         
            # Primer día del mes
            primer_dia_del_mes = df_filtrado['day'].iloc[0]
            dia_de_semana_primer_dia = primer_dia_del_mes.weekday()            
            # HEATMAP
            sns.heatmap(heatmap_data, cmap='GnBu', ax=ax_heatmap, xticklabels=dias_semana)
            ax_heatmap.xaxis.set_ticks_position('top')
            ax_heatmap.set_xticklabels(ax_heatmap.get_xticklabels(), fontsize=16, fontname='verdana')
            ax_heatmap.set_yticklabels([])
            ax_heatmap.tick_params(axis='y', length=0)
            ax_heatmap.tick_params(axis='x', length=0, pad=15)
            cbar = ax_heatmap.collections[0].colorbar
            cbar.set_label('        [kWh]',fontsize=17, fontname='verdana', rotation=0)
            ax_heatmap.set_xlabel('', fontsize=12)
            ax_heatmap.set_ylabel('', fontsize=12)     
            ax_heatmap.set_facecolor(color_6)
            fig_heatmap.patch.set_facecolor(color_6)
            
            for i in range(heatmap_data.shape[0]):
                for j in range(heatmap_data.shape[1]):
                    dia = i * heatmap_data.shape[1] + j - dia_de_semana_primer_dia + 1
                    if 1 <= dia <= num_dias:
                        ax_heatmap.text(j + 0.3, i + 0.8, str(dia), ha='center', va='center', fontsize=13, fontname='georgia', color='black')

            fig_heatmap.set_size_inches(7, 6)  
            # Pestaña para el gráfico heatmap
            tab5 = ttk.Frame(notebook)
            notebook.add(tab5, text='Heatmap')
            canvas_heatmap = FigureCanvasTkAgg(fig_heatmap, master=tab5)
            canvas_heatmap.draw()
            canvas_heatmap.get_tk_widget().pack(fill='both', expand=True)
            
            # Día con mayor consumo en el mes
            dia_con_mas_consumo_mes_datetime = df_filtrado.loc[df_filtrado['energy_sum'].idxmax(), 'day']
            dia_con_mas_consumo_mes = dia_con_mas_consumo_mes_datetime.strftime('%A %d')          
            # Día con mayor consumo en la última semana del mes
            dia_con_mas_consumo_ultima_semana_datetime = df_ultima_semana.loc[df_ultima_semana['energy_sum'].idxmax(), 'day']
            dia_con_mas_consumo_ultima_semana = dia_con_mas_consumo_ultima_semana_datetime.strftime('%A %d')   
            # Mes con mayor consumo en los últimos 12 meses
            mes_con_mas_consumo_ultimos_12_meses = df_ultimos_12_meses.groupby(df_ultimos_12_meses['day'].dt.month)['energy_sum'].sum().idxmax()
            nombre_mes_con_mas_consumo_ultimos_12_meses = datetime(2000, mes_con_mas_consumo_ultimos_12_meses, 1).strftime('%B')
            dia_con_mas_consumo_ultimos_12_meses = dia_con_mas_consumo_mes_datetime.strftime('%A %d de') + nombre_mes_con_mas_consumo_ultimos_12_meses
            # Día con menor consumo en el mes
            dia_con_menor_consumo_mes_datetime = df_filtrado.loc[df_filtrado['energy_sum'].idxmin(), 'day']
            dia_con_menor_consumo_mes = dia_con_menor_consumo_mes_datetime.strftime('%A %d')            
            # Día con menor consumo en la última semana del mes
            dia_con_menor_consumo_ultima_semana_datetime = df_ultima_semana.loc[df_ultima_semana['energy_sum'].idxmin(), 'day']
            dia_con_menor_consumo_ultima_semana = dia_con_menor_consumo_ultima_semana_datetime.strftime('%A %d')           
            # Mes con menor consumo en los últimos 12 meses
            mes_con_menor_consumo_ultimos_12_meses = df_ultimos_12_meses.groupby(df_ultimos_12_meses['day'].dt.month)['energy_sum'].sum().idxmin()
            nombre_mes_con_menor_consumo_ultimos_12_meses = datetime(2000, mes_con_menor_consumo_ultimos_12_meses, 1).strftime('%B')
            dia_con_menor_consumo_ultimos_12_meses = dia_con_menor_consumo_mes_datetime.strftime('%A %d de') + nombre_mes_con_menor_consumo_ultimos_12_meses
            
            #Tarifa          
            administraciondelservicio=1324
            matriz = [
    [146.557, 146.561, 146.563, 146.566, 146.569, 146.572],
    [147.368, 147.372, 147.374, 147.377, 147.38, 147.383],
    [148.382, 148.386, 148.388, 148.391, 148.394, 148.397],
    [149.092, 149.096, 149.098, 149.101, 149.104, 149.107],
    [149.396, 149.4, 149.402, 149.405, 149.408, 149.411]
]
            #obtener stxc y tramo
            numero_stxc = int(re.search(r'Stxc-(\d+)', df_datos['sector_tarifario'].iloc[0]).group(1))
            numero_tramo = int(re.search(r'Tramo: (\d+)', df_datos['sector_tarifario'].iloc[0]).group(1))
            
            indice_fila = int(numero_stxc) - 1
            indice_columna = int(numero_tramo) - 1
            
            #Valores de la matriz
            valor_matriz = matriz[indice_fila][indice_columna]            
            electricidadconsumida= int(energia_total_mes*valor_matriz)
            transportedeelectricidad=(4.171*energia_total_mes)
            gasto_total=int(administraciondelservicio+transportedeelectricidad+electricidadconsumida)
        nombre = "SmartSu.pdf"
        file_path = filedialog.asksaveasfilename(defaultextension='.pdf', initialfile=nombre, filetypes=[('Archivos PDF', '*.pdf')])
    
        if file_path:
                    # Crear  PDF
                    c = canvas.Canvas(file_path)                  

                    #PORTADA
                    c.drawImage("fondoportada2.png", 0,0, width=595.275590551181, height=841.8897637795275)
                    mes_numero = month_combobox.current()
                    # Meses
                    nombres_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                    # Nombre del mes 
                    meses = nombres_meses[mes_numero]                    
                    c.setFont("robotolight", 20)
                    c.drawString(140, 670, f"{meses}")
                    c.setFont("robotolight", 15)
                    c.drawString(90, 575, f"N° de cliente: {hogar_input}")                
                    # Información del cliente
                    direccion_suministro = df_datos.loc[0, 'direccion_de_suministro']
                    subestacion_cliente = df_datos.loc[0, 'subestacion']
                    sector_tarifario = df_datos.loc[0, 'sector_tarifario']
                    #potencia_conectada = df_datos.loc[0, 'Potencia_Conectada']
                    fecha_termino = df_datos.loc[0, 'Fecha_termino_de_tarifa']
                    fecha_limite = df_datos.loc[0, 'Fecha_limite_para_cambio_de_tarifa']
                    tipo_tarifa = df_datos.loc[0, 'Tipo_de_tarifa_contratada']                    
                    c.drawString(90, 555, f"Dirección Suministro: {direccion_suministro}")
                    c.drawString(90, 535, f"Subestación: {subestacion_cliente}")
                    c.drawString(90, 515, f"Sector Tarifario: {sector_tarifario}")
                    c.drawString(90, 495, f"Potencia Conectada: {5.5}")
                    c.drawString(90, 475, f"Fecha término de tarifa: {fecha_termino}")
                    c.drawString(90, 455, f"Fecha límite para cambio de tarifa: {fecha_limite}")  
                    c.drawString(90, 435, f"Tipo de tarifa contratada: {tipo_tarifa}")
                    c.setFont("robotobold", 20)
                    c.setFillColor(color_4)
                    c.drawString(322, 331, f"$ {gasto_total}")
                    c.setFont("robotoregular", 15.5)
                    c.setFillColor(color_3)
                    c.drawString(440, 210, f"{administraciondelservicio}")
                    c.drawString(440, 187, f"{transportedeelectricidad}")
                    c.drawString(440, 164, f"{electricidadconsumida}")
                    c.showPage()
                             
                    #PDF GRÁFICO CONSUMO MENSUAL
                    fig_consumo_dia.set_size_inches(12, 6)
                    temp_file_consumo_dia = "temp_fig_consumo_dia.png"
                    fig_consumo_dia.savefig(temp_file_consumo_dia, dpi=150)             
                    c.drawImage('fondograficos.png', 0, 0, width=595.275590551181, height=841.8897637795275)
                    c.drawImage(temp_file_consumo_dia, 40, 460, width=500, height=300)
                    c.setFont("robotolight", 11)
                    c.drawString(110, 400, "Durante el último mes, hemos observado algunas diferencias significativas en") 
                    c.drawString(110, 380, "nuestro consumo de energía eléctrica. El día de máximo consumo fue el ")
                    c.drawString(110, 360, f"{dia_con_mas_consumo_mes} , donde utilizamos más energía que en cualquier otro día. ") 
                    c.drawString(110, 340, "Este pico de consumo podría deberse a múltiples factores, como la operación ")
                    c.drawString(110, 320, "de electrodomésticos de alto consumo o el uso excesivo de la climatización. ")
                    c.drawString(110, 300, "Te recomendamos revisar tus patrones de consumo en este día y considerar")
                    c.drawString(110, 280, "formas de optimizarlos.")
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont("robotolight", 11)
                    c.drawImage('lavadora.png', 175, 150, width=35, height=40)
                    c.drawString(215, 190, "Utilice su lavadora siempre con carga ")
                    c.drawString(215, 170, "completa y de preferencia con agua fría. ")
                    c.drawString(215, 150, "Cuando seque la ropa, prefiera hacerlo")
                    c.drawString(215, 130, "al sol y no en la secadora. ")
                    c.setFillColorRGB(0, 0.353, 0.235)
                    texto = "Consumo de energía mensual"
                    fuente = "robotomedium"
                    tamano_fuente = 17
                    # Calcula la longitud del texto en puntos
                    longitud_texto = c.stringWidth(texto, fuente, tamano_fuente)
                    # Calcula las coordenadas para centrar el texto en la página
                    ancho_pagina = A4[0]
                    x_centro = (ancho_pagina - longitud_texto) / 2
                    # Fuente y el tamaño de la letra
                    c.setFont(fuente, tamano_fuente)
                    # Dibuja el texto centrado en la página
                    c.drawString(x_centro, 740, texto)
                    os.remove(temp_file_consumo_dia)
                    c.showPage()
                                                           
                    #CREAR TABALA CONSUMO (DataFrame de Pandas)
                    data = []
                    data.append(['          Día          ', '      Costo     '])                    
                    for index, row in df_tabla.iterrows():
                        data.append([row['day'].strftime('%d-%m-%Y'), f"${row['energy_sum']:.0f}"])                    
                    table = Table(data)
                    
                    #ESTILO TABLA CONSUMO
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), color_5),  # Fila de encabezado
                        ('TEXTCOLOR', (0, 0), (-1, 0), color_6),  # Color del texto en la fila de encabezado
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinear el texto al centro
                        ('FONTNAME', (0, 0), (-1, 0), 'robotolight'),  # Fuente para la fila de encabezado
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  # Espacio entre la fila de encabezado y las filas de datos
                        ('BACKGROUND', (0, 1), (-1, -1), color_6),  # Fondo de las filas de datos
                        ('GRID', (0, 0), (-1, -1), 1, color_5),  # Líneas de cuadrícula
                        ('FONTNAME', (0, 1), (-1, -1), 'robotoregular'),  # Fuente para las filas de datos
                        ('FONTSIZE', (0, 0), (-1, 0), 15),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinear el texto de las filas de datos al centro
                        ('LEADING', (0, 0), (-1, 0), 15),  # Espacio entre filas para la fila de encabezado
                        ('LEADING', (0, 1), (-1, -1), 14),  # Espacio entre filas para las filas de datos    
                    ]))
                    
                    #PDF TABLA CONSUMO
                    c.drawImage('fondotabla.png', 0, 0, width=595.275590551181, height=841.8897637795275)
                    fuente = "robotomedium"
                    table.wrapOn(c, 0, 0)
                    table.drawOn(c, 90, 50) 
                    c.showPage()

                    #PDF GRÁFICO CONSUMO ÚLTIMA SEMANA
                    c.drawImage('fondograficos.png', 0, 0, width=595.275590551181, height=841.8897637795275)
                    fig_ultima_semana.set_size_inches(8, 6)
                    temp_file_semana = "temp_fig_semana.png"
                    fig_ultima_semana.savefig(temp_file_semana, dpi=150)
                    c.drawImage(temp_file_semana, 40, 460, width=500, height=300)
                    c.setFont("robotolight", 12)
                    c.drawString(110, 390, f"El día con más consumo esta semana fue el {dia_con_mas_consumo_ultima_semana}, mientras que")
                    c.drawString(110, 370, f" el día que más ahorraste energía fue el {dia_con_menor_consumo_ultima_semana}")
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont("robotolight", 11)
                    c.drawImage('lavadora.png', 175, 150, width=35, height=40)
                    c.drawString(215, 190, "Utilice su lavadora siempre con carga ")
                    c.drawString(215, 170, "completa y de preferencia con agua fría. ")
                    c.drawString(215, 150, "Cuando seque la ropa, prefiera hacerlo")
                    c.drawString(215, 130, "al sol y no en la secadora. ")

                    c.setFillColorRGB(0, 0.353, 0.235)
                    texto = "Consumo máximo de energía de la última semana"
                    fuente = "robotomedium"
                    tamano_fuente = 17
                    # Calcula la longitud del texto en puntos
                    longitud_texto = c.stringWidth(texto, fuente, tamano_fuente)
                    # Calcula las coordenadas para centrar el texto en la página
                    ancho_pagina = A4[0]
                    x_centro = (ancho_pagina - longitud_texto) / 2
                    # Establece la fuente y el tamaño de la letra
                    c.setFont(fuente, tamano_fuente)
                    # Dibuja el texto centrado en la página
                    c.drawString(x_centro, 740, texto)   
                    os.remove(temp_file_semana)
                    c.showPage()

                    #PDF GRÁFICO ÚLTIMOS 12 MESES
                    c.drawImage('fondograficos.png', 0, 0, width=595.275590551181, height=841.8897637795275)
                    fig_ultimos_12_meses.set_size_inches(7, 6)
                    temp_ultimos_12_meses = "temp_ultimos_12_meses.png"
                    fig_ultimos_12_meses.savefig(temp_ultimos_12_meses, dpi=150)
                    c.drawImage(temp_ultimos_12_meses, 40, 460, width=500, height=300)
                    c.setFont("robotolight", 12)
                    c.drawString(110, 400, "Durante este período, hemos notado algunas diferencias notables en") 
                    c.drawString(110, 380, f"nuestro consumo mensual. El mes con el mayor consumo fue {nombre_mes_con_mas_consumo_ultimos_12_meses}.")
                    c.drawString(110, 360, "Esto podría estar relacionado con la llegada del verano y el uso más") 
                    c.drawString(110, 340, "frecuente del aire acondicionado o ventiladores,, así como con las")
                    c.drawString(110, 320, "vacaciones escolares o visitas de familiares que pasaron más tiempo ")
                    c.drawString(110, 300, "en casa.")
                    c.drawString(110, 280, "")
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont("robotolight", 11)
                    c.drawImage('lavadora.png', 175, 150, width=35, height=40)
                    c.drawString(215, 190, "Utilice su lavadora siempre con carga ")
                    c.drawString(215, 170, "completa y de preferencia con agua fría. ")
                    c.drawString(215, 150, "Cuando seque la ropa, prefiera hacerlo")
                    c.drawString(215, 130, "al sol y no en la secadora. ")
                    c.setFillColorRGB(0, 0.353, 0.235)
                    texto = "Consumo de los últimos 12 meses"
                    fuente = "robotomedium"
                    tamano_fuente = 17
                    # Calcula la longitud del texto en puntos
                    longitud_texto = c.stringWidth(texto, fuente, tamano_fuente)
                    # Calcula las coordenadas para centrar el texto en la página
                    ancho_pagina = A4[0]
                    x_centro = (ancho_pagina - longitud_texto) / 2
                    # Establece la fuente y el tamaño de la letra
                    c.setFont(fuente, tamano_fuente)
                    # Dibuja el texto centrado en la página
                    c.drawString(x_centro, 740, texto)                 
                    os.remove(temp_ultimos_12_meses)
                    c.showPage()
                                   
                    #PDF CALENDARIO
                    c.drawImage('fondograficos.png', 0, 0, width=595.275590551181, height=841.8897637795275)
                    fig_heatmap.set_size_inches(8, 6)
                    temp_file_heatmap = "temp_heatmap.png"
                    fig_heatmap.savefig(temp_file_heatmap, dpi=150)
                    c.drawImage(temp_file_heatmap, 58, 435, width=500, height=300)
                    c.setFont("robotolight", 12)                   
                    c.drawString(110, 400, "El calendario de consumo de energía, cada día se muestra como un color.") 
                    c.drawString(110, 380, "Los colores más oscuros indican un mayor consumo de energía, mientras")
                    c.drawString(110, 360, "que los colores más claros representan un menor consumo.") 
                    c.drawString(110, 340, "Es esencial ser cauteloso con los días oscuros en el calendario. Tomar ")
                    c.drawString(110, 320, "acciones para reducir el consumo en estos días te permitirá mantener un")
                    c.drawString(110, 300, "control sobre tus costos.")
                    c.drawString(110, 280, "")
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont("robotolight", 11)
                    c.drawImage('refrigerador.png', 175, 140, width=35, height=55)
                    c.drawString(215, 190, "No introduzcas alimentos calientes en")
                    c.drawString(215, 170, "tu refrigerador. Así evitarás que este")
                    c.drawString(215, 150, "consuma electricidad adicional.")
                    c.drawString(215, 130, "")
                    c.setFillColorRGB(0, 0.353, 0.235)
                    longitud_texto = c.stringWidth(f"{meses}", fuente, tamano_fuente)
                    ancho_pagina = A4[0]
                    x_centro = (ancho_pagina - longitud_texto) / 2
                    c.setFont("robotomedium", 17)
                    c.drawString(x_centro, 748, f"{meses}")                 
                    os.remove(temp_file_heatmap)
                                        
                    # Guardar y cerrar el PDF
                    c.save()
                    try:
                        subprocess.Popen([file_path], shell=True)
                    except Exception as e:
                        print(f"No se pudo abrir el archivo PDF: {e}")
                    else:
                        print(f"El archivo PDF se abrió automáticamente: {file_path}")

                    messagebox.showinfo('Informe generado', f'Se ha generado el informe en el archivo:\n{file_path}')
        else:
            messagebox.showwarning('Datos no encontrados', 'No se encontraron datos para la fecha ingresada.')
    else:
        messagebox.showwarning('Hogar no encontrado', 'El hogar ingresado no existe en los archivos CSV.')
     
# Ventana valores de entrada
window = tk.Tk()
window.title('SmartSu')
window.geometry('800x500')
window.iconbitmap("captura.ico")
window.resizable(0,0)
# Imagen de fondo
background_image = Image.open("fondo3.jpeg")
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(window, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
# Entrada N° Cliente
"""label_hogar = ttk.Label(window, text='N° de cliente:',font = "helvetica 12")
label_hogar.pack()"""
entry_hogar = ttk.Entry(window, width=25)
entry_hogar.pack()
entry_hogar.place(x=330, y=150)
# Entrada MES
"""label_mes = ttk.Label(window, text='Mes:', font = "helvetica 12")
label_mes.pack()"""
month_combobox = ttk.Combobox(window, values=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                                              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'], width=22)
month_combobox.pack()
month_combobox.place(x=330, y=205) 
#Entrada AÑO
"""label_año = ttk.Label(window, text='Año:', font = "helvetica 12")
label_año.pack()"""
entry_año = ttk.Entry(window, width=25)
entry_año.pack()
entry_año.place(x=330, y=255) 
# Botón SmartSu
style = ttk.Style()
style.configure("Custom.TButton", foreground="black", justify="right", background="black", font=("robotoregular", 12))
btn_generar = ttk.Button(window, text='SmartSu', width=20, command=generar_graficos_informe, style="Custom.TButton")
btn_generar.pack()
btn_generar.place(x=310, y=305)

# Ejecutar la ventana principal
window.mainloop()