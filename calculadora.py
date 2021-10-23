# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 21:20:19 2021

@author: mateuscarvalho
"""
#Importações
import streamlit as st
import pandas as pd
import pickle
from catboost import CatBoostRegressor
import yaml
import psycopg2



@st.cache()
def loader(data_path = "./data/model_input.csv",model_path= "./model/model.cbm", normalize_path="./model/data_pipeline.pkl", config_path="./config/login_bd.yml"):
    model_input = pd.read_csv(data_path)
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    with open(normalize_path, "rb") as f:
        data_pipeline = pickle.load(f)
    
    model = CatBoostRegressor()
    model.load_model(model_path)
    
    return data_pipeline, model, model_input, config


data_pipeline, model, model_input, config = loader()

@st.cache()
def salvar_feedback(config, mensagem):
    #Conectando ao banco de dados
    conn = psycopg2.connect(dbname = config["Credencial"]["Database"], 
                        user = config["Credencial"]["User"], 
                        password = config["Credencial"]["Password"], 
                        host = config["Credencial"]["Host"])

    cur = conn.cursor()

    #cur.execute("CREATE TABLE feedback (mensagem VARCHAR(30));")

    cur.execute("INSERT INTO feedback (mensagem) VALUES(%s)", (mensagem,)) 
    #Confirmnando a inclusão
    conn.commit()
    
    #Consultar registros
    #cur.execute("select * from feedback;")
    #print(cur.fetchall())
    
    #Fechar conexões
    cur.close()
    conn.close()

st.write("Calculadora de imóveis")

st.sidebar.title("Entre com os as características do apartamento")
area = st.sidebar.number_input("Área", min_value=10, max_value=400, step=25, value=70)
bairro = st.sidebar.selectbox("Bairro", options=model_input["bairro"].unique())
garages = st.sidebar.slider("Garagens", min_value=0, max_value=5)
bathrooms = st.sidebar.slider("Banheiros", min_value=1, max_value=5)
rooms = st.sidebar.slider("Quartos", min_value=1, max_value=5)

novo_apto = pd.DataFrame([[area, rooms, bathrooms, garages, bairro]], 
                         columns=["area", "rooms","bathrooms", "garages","bairro"])

novo_apto_normalizado = pd.DataFrame(data_pipeline.transform(novo_apto), columns=novo_apto.columns)



prediction = model.predict(novo_apto_normalizado)[0]

st.write(f"Preço previsto: R$ {prediction:,.2f}")

mensagem = st.text_input("Envie seu feedback")

if len(mensagem)> 0:
    salvar_feedback(config, mensagem)
else:
    pass
    
    



