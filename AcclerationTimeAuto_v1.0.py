#import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
import mdfreader
import math
import re
import os
import copy

#打印数据文件中的基本信息
def getMdfInfo(yop):
    print ('MDF File Name: %s'%(yop.fileName))
    print ('Keys in MDF File: %s'%(yop.keys()))
    print ('MDF File Version: %d'%(yop.MDFVersionNumber))
    return

#读取当前文件夹下后缀为dat/mdf/mf4的文件名称
def getFileList():
    file_list = []
    file_dir = os.getcwd()
    list_dir = os.listdir(file_dir)
    for i in list_dir:
        if i.split('.')[-1] == 'dat' or i.split('.')[-1] == 'mdf' or i.split('.')[-1] == 'mf4' or i.split('.')[-1] == 'DAT' or i.split('.')[-1] == 'MDF' or i.split('.')[-1] == 'MF4':
            file_list.append(i)
    return file_list

#保存data_list中的数值到文件中
def saveData(data_list,fname):
    filename = open(fname, 'a')  
    for value in data_list:
        filename.write(str(value)+'\t')
    filename.write('\n')
    filename.close() 

#基本信息：画图函数
def plotBasicInfo(yop,channel_list,file_name):
    plt.rcParams['font.family'] = 'DejaVu Sans' #全局字体设置，例如Times New Roman, SimHei
    plt.rcParams['font.size'] = 12
    plt.rcParams['figure.figsize'] = (50,10) #图片大小设置
    fig_all = len(channel_list) #计算总的需要画图的张数
    fig_count = 0 #画图时的计数器
    for i in channel_list:    
        fig_count += 1
        plt.subplot(fig_all,1,fig_count) #长图，所以为n行1列
        xname = yop.get_channel_master(i) #取当前通道的master通道，即时间通道的名称，例如time_40
        xdata = yop.get_channel_data(xname) #取当前x通道的数据
        ydata = yop.get_channel_data(i) #取当前y通道的数据
        plt.plot(xdata, ydata, linewidth='0.8')
        yLabel = i + ' / ' + yop.get_channel_unit(i) #将坐标名称和坐标单位组合
        plt.xlabel('Time / s')
        plt.ylabel(yLabel)
        plt.grid(True)
    plt.tight_layout(rect=(0,0,1,0.95)) #使子图标题和全局标题与坐标轴不重合
    plt.suptitle(yop.fileName)
    plt.savefig(file_name[:-4] + '.png', dpi = 300) #去除后缀名
    plt.clf()
    return

#在车速序列中识别加速时间，并保存
def saveAccelrationTime(yop,fname):
    xname = yop.get_channel_master('ESP_v_Signal') #取当前通道的master通道，即时间通道的名称，例如time_40
    time = yop.get_channel_data(xname) #取当前x通道的数据
    speed = yop.get_channel_data('ESP_v_Signal') #取当前y通道的数据
    name_list = ['FileName:',yop.fileName] #重新将文件名称组成一个列表
    saveData(name_list,fname) #保存文件名称
    for i in range(len(time)-1):
        if speed[i] == 0 and speed[i+1] > 0 and speed[i+5] > speed[i]: #取在加速阶段的0km/h的点，加速起始点(三个判断条件：a.第i点等于0，b.第i+1点大于0，c.第i点后的0.1s为加速)
            global t1
            t1 = i + 1 #找到即停止，进入第二级循环
        else:
            continue
        for j in range(t1,t1+750,1): #认为加速时间在15s内，若在15s外，则不是同一次0~100km/h的加速
            if speed[j+1] >= 100: #修改此数据，即修改加速结束点（遇到的第一个大于相应车速的点，即认为加速结束）
                global t2
                t2 = j + 1
                delta = time[t2] - time [t1]
                data_list = []
                for d in (time[t1],speed[t1],time[t2],speed[t2],delta):
                    data_list.append(d)
                saveData(data_list,fname)
                break #一旦找到第一个100km/h的值，立即打断循环
            else:
                continue

def main():
    file_list = getFileList() #调用getFileList函数，获取当前文件夹下的所有mdf/dat文件
    channel_list = ['ESP_v_Signal','MO_Kickdown']
    fname = 'AccelerationTime.txt' #需要保存的日志文件名
    for file_name in file_list:
        yop = mdfreader.mdfreader.Mdf(file_name = file_name, channel_list = channel_list) #用mdfreader加载测试数据
        plotBasicInfo(yop,channel_list,file_name) #将channel_list中的通道做图
        saveAccelrationTime(yop,fname) #调用保存加速时间函数
        print (yop.fileName,'done') #单个循环完成，打印处理完成的标志

if __name__ == '__main__':
    main()


