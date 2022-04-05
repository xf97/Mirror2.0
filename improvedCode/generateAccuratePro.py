#!/usr/bin/python3

'''
此文件用于处理eps均值和方差，以生成更准确的购买概率
'''

#导入库
import os
import random
import openpyxl	#操作ecxel文件
import math
import numpy
#导入已有的读写类
import sys
from excel2Dict import *
from dict2Excel import *

#定义常量
#输入
EPS_INPUT_FILE_PATH = "..\\improvedData\\epsInput.xlsx"
#输出
EPS_OUTPUT_FILE_PATH = "..\\improvedData\\epsOutput.xlsx"
#均值
AVERAGE_FLAG = "average"
#标准差
STANDARD_FLAG = "standard"
#年份偏移值
OFFSET_VALUE = 2005
#持续年份
LAST_YEAR = 14
#一年有几个月
MONTH_NUM = 12

class generateAccuratePro(object):
	def __init__(self, input_path, output_path):
		self.eps_input_file_path = input_path
		self.eps_output_file_path = output_path
		self.averageEps = self.__get_average_each_year(self.eps_input_file_path)
		self.standardEps = self.__get_standard_each_year(self.eps_input_file_path)

	def __get_average_each_year(self, input_path):
		excelFile = ExcelToDict(input_path)
		excelFile.open_object()
		excelFile.read_excel()
		return excelFile.data_dict[AVERAGE_FLAG]

	def __get_standard_each_year(self, input_path):
		excelFile = ExcelToDict(input_path)
		excelFile.open_object()
		excelFile.read_excel()
		return excelFile.data_dict[STANDARD_FLAG]

	'''
	@ stock id - input
	@ year - input
	@ return average and standard
	'''
	def __get_average_and_standard(self, stock_id, year):
		average = 0.0
		standard = 0.0
		# find average
		for aRow in self.averageEps["value_row"].values():
			for key, value in aRow.items():
				if key == None and value == stock_id:
					# find this stock 
					average = aRow[year]
					break
				else:
					continue
		#find standard
		for aRow in self.standardEps["value_row"].values():
			for key, value in aRow.items():
				if key == None and value == stock_id:
					# find this stock 
					standard = aRow[year]
					break
				else:
					continue	
		return (average, standard)	

	def __get_stock_id(self):
		stock_id_list = list()
		for aRow in self.averageEps["value_row"].values():
			for key, value in aRow.items():
				if key == None and type(value) == str:
					stock_id_list.append(value)
					break
				else:
					continue
		assert len(stock_id_list) == 100	#长度检查
		return stock_id_list

	def __get_probility(self, average, standard):
		probility = numpy.random.normal(loc = average, scale = standard)
		return probility
		'''
		while probility <= 0 or probility >= 1:
			probility = numpy.random.normal(loc = average, scale = standard)
		return probility
		'''

	def generate_probility(self):
		year = 0 
		stock_id_list = self.__get_stock_id()
		probility_dict = dict()
		#print(stock_id_list)
		while year < LAST_YEAR:
			#print(year)
			key = year + OFFSET_VALUE
			probility_dict[key] = dict()
			for stock_id in stock_id_list:
				#取值
				average, standard = self.__get_average_and_standard(stock_id, year + OFFSET_VALUE)
				#根据均值和方差生成正态值
				#生成此股票该年每个月的购买概率
				probility_dict[key][stock_id] = list()
				for _ in range(MONTH_NUM):
					probility = self.__get_probility(average, standard)
					probility_dict[key][stock_id].append(probility)
				#print(stock_id, year + OFFSET_VALUE, average, standard, probility)
			year += 1
		print(probility_dict.keys())
		#保存该概率
		dict2Sheet2Excel(probility_dict, self.eps_output_file_path, year - LAST_YEAR + OFFSET_VALUE, year + OFFSET_VALUE - 1)

# test main
if __name__ == "__main__":
	generator = generateAccuratePro(EPS_INPUT_FILE_PATH, EPS_OUTPUT_FILE_PATH)
	generator.generate_probility()