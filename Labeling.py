# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 11:12:16 2019

@author: ehoyos
"""

#Autor Eduardo Hoyos 
# Funciones de etiquetado para la variable Y

#Importar paquetes:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt


#1. Funcion de etiquetado simple

#Toma una serie de retornos ts , un intervalo de tiempo 
#Detecta el inicio de 5 dias con movimientos iguales o superiores a un
#intervalo establecido
#Equivalentes a v*10000 puntos basicos de retorno

def etiquetado_simple(ts,i,v):
    
   
    ret_plus_one =  pd.DataFrame(ts + 1,index =ts.index)
    signals = pd.DataFrame(index =ts.index)
    ret_ac_1 = ret_plus_one.rolling(window=i).agg(lambda x : x.prod()) -1
    #Longs
    signals['signal_L'] = np.where((ret_ac_1>v),1,0)
    #Shorts
    signals['signal_S'] = np.where((ret_ac_1<-v),-1,0)
    #Label
    for k in range(len(signals['signal_L'])-i):
        signals['signal_L'][k]=signals['signal_L'][k+i]
        signals['signal_S'][k]=signals['signal_S'][k+i]
    
    signals['label'] = signals['signal_L'] + signals['signal_S']
    signals['label'][len(signals['signal_L'])-i:]=0
    
    
    
    
    
    #for k in range(len(signals['signal_L'])-i):
    #    signals['signal_L'][k]=signals['signal_L'][k-i]
    df = pd.concat([ret_plus_one,ret_ac_1,signals],axis=1)
    df.columns = ['Log_ret_plus_one',"{}{}".format(i,' Day_Ret'),'signal_L','signal_S','label']
    
    return df


#2. Funcion de etiquetado por momentum
#Toma una serie de tiempo ts y calcula una señal de momentum de i periodos

def momentum(ts,i):
    
   #calcula retorno diario y suma 1
    ret_plus_one =  pd.DataFrame(ts + 1,index =ts.index)
   #Inicializa dataframe de señales
    signals = pd.DataFrame(index =ts.index)
    
    mom = pd.DataFrame(np.where(ts>0,1,-1), index =ts.index)
    mom_1  =mom.rolling(i).mean()
    
    ret_ac_1 = ret_plus_one.rolling(window=i).agg(lambda x : x.prod()) -1
    
    
    #Longs
    #signals['signal_L'] = np.where((ret_ac_1>0.005),1,0)
    signals['signal_L'] = np.where((mom_1>0),1,0)
    #Shorts
    #signals['signal_S'] = np.where((ret_ac_1<-0.005),-1,0)
    signals['signal_S'] = np.where((mom_1<0),-1,0)
    #Label
    signals['label'] = signals['signal_L'] + signals['signal_S']
    df = pd.concat([ret_plus_one,ret_ac_1,mom_1,signals],axis=1)
    df.columns = ['Log_ret_plus_one',"{}{}".format(i,' Day_Ret'),"{}{}".format(i,' Mom'),'signal_L','signal_S','label']
    return df





def cusum(ts,k,h):
    
    Log_ret =  pd.Series(ts ,index =ts.index)
    
    df = pd.DataFrame()  
    #calcula indicador yi
    df['y_i']  =  (Log_ret-k).fillna(0)
    
    #Inicializa one sided cusum positivo
    c_i = np.zeros(len(df))
     #Inicializa one sided cusum negativo
    c_i_prime = np.zeros(len(df))
    #Inicializa etiquetado
    label = np.zeros(len(df))
    
    # determinar ciclos de inversion 
    for l in range(1,len(df)):
            # Calculo ci y ci'
            c_i[l] = max( c_i[l-1] + df['y_i'][l]  ,0)
            c_i_prime[l] = min( c_i_prime[l-1] + df['y_i'][l],0)
            
            if (c_i[l] >= h)and((c_i[l-1]>=0)or((label[l-1]==1))):
                c_i_prime[l] = 0
                label[l] = 1
            elif (c_i_prime[l]<=-h)and((c_i_prime[l-1]<=0)or((label[l-1]==-1))):
                c_i[l] = 0
                label[l] = -1
            elif ((c_i[l] < h)and(c_i_prime[l]>-h))and(label[l-1]==1):
                label[l] = 1
            elif ((c_i[l] < h)and(c_i_prime[l]>-h))and(label[l-1]==-1):
                label[l] = -1
                       
    df['c_i'] = c_i
    df['c_i_prime']=c_i_prime
    df['label'] = label
    df['L_Ret']= Log_ret
    
    #Calcular retorno de la estrategia
    df['retorno'] =  df['label'].shift(1).fillna(0) * df['L_Ret']
    df['perc_ret'] = (1 + df['retorno']).cumprod() -1
    
    
    return df




