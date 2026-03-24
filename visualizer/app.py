import os
import json
import redis
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Miner Visualizer", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def conectar_redis():
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    return redis.Redis(host=host, port=port, decode_responses=True)

db = conectar_redis()

def consumir_cola():
    mensajes_procesados = 0
    
    while True:
        mensaje_crudo = db.rpop("word_queue")
        
        if not mensaje_crudo:
            break 
            
        try:
            datos = json.loads(mensaje_crudo)
            palabra = datos.get("word")
            lenguaje = datos.get("language")
            
            if not palabra:
                continue
                
            diccionario_lenguaje = f"ranking:{lenguaje}"
            db.hincrby(diccionario_lenguaje, palabra, 1)
            
            mensajes_procesados += 1
        except json.JSONDecodeError:
            pass 
            
    return mensajes_procesados

def obtener_top_10(lenguaje):
    diccionario_lenguaje = f"ranking:{lenguaje}"
    
    todos_los_datos = db.hgetall(diccionario_lenguaje)
    
    if not todos_los_datos:
        return pd.DataFrame(columns=["Palabra", "Frecuencia"]).set_index("Palabra")
        
    datos_numericos = {palabra: int(cantidad) for palabra, cantidad in todos_los_datos.items()}
    
    top_10 = sorted(datos_numericos.items(), key=lambda x: x[1], reverse=True)[:10]
    
    df = pd.DataFrame(top_10, columns=["Palabra", "Frecuencia"])
    df.set_index("Palabra", inplace=True) 
    return df



st.title("Ranking de Convenciones")

if st.button("Actualizar Datos", use_container_width=True):
    con_spinner = st.spinner("Actualizando Datos")
    with con_spinner:
        procesados = consumir_cola()
        if procesados > 0:
            st.success(f"Se sacaron {procesados} palabras de la cola y se contaron")
        else:
            st.info("La cola está vacía por ahora")

col_python, col_java = st.columns(2)

with col_python:
    st.subheader("Top 10 Python")
    df_py = obtener_top_10("python")
    if not df_py.empty:
        st.bar_chart(df_py, color="#FFD43B") 
    else:
        st.write("Aún no hay datos de Python en la base de datos")

with col_java:
    st.subheader("Top 10 Java")
    df_java = obtener_top_10("java")
    if not df_java.empty:
        st.bar_chart(df_java, color="#f89820") 
    else:
        st.write("Aún no hay datos de Java en la base de datos")