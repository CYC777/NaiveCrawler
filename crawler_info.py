#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import threading
import re
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
import pymysql
browserPath = '/Users/yancheng/phantomjs-2.1.1-macosx/bin/phantomjs'

homePage = 'https://mm.taobao.com/search_tstar_model.htm?'
outputDir = 'photo/'
parser = 'html5lib'


def main():
    db = pymysql.connect("localhost","root","","scrawler",charset="utf8" )

# 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS TBmodel")
# 使用预处理语句创建表
    sql = """CREATE TABLE TBmodel (
         name  CHAR(20) NOT NULL,
         city  CHAR(20),
         height CHAR(20),
         weight CHAR(20),
         img VARCHAR(100) )"""

# 使用 execute()  方法执行 SQL 查询
    cursor.execute(sql)



    driver = webdriver.PhantomJS(executable_path=browserPath)
    driver.get(homePage)
    elem = driver.find_element_by_class_name('page-next')#下一页
    elem.click()
    time.sleep(10)
    bsObj = BeautifulSoup(driver.page_source, parser)
    print("[*]OK GET Page")
    girlsList = driver.find_element_by_id('J_GirlsList').text.split(
        '\n')
    #print(girlsList[::3])
    imagesUrl = re.findall('\/\/gtd\.alicdn\.com\/sns_logo.*\.jpg',
                           driver.page_source)
    girlsUrl = bsObj.find_all(
        "a",
        {"href": re.compile("\/\/.*\.htm\?(userId=)\d*")})  #解析model个人主页地址等信息
    # 所有model的名字地点
    girlsNL = girlsList[::3]
    # 所有model身高体重
    girlsHW = girlsList[1::3]
    # 所有model的个人主页地址
    girlsHURL = [('http:' + i['href']) for i in girlsUrl]
    # 所有model的封面图片地址
    girlsPhotoURL = [('https:' + i) for i in imagesUrl]

    girlsInfo = zip(girlsNL, girlsHW, girlsHURL, girlsPhotoURL)
    print (girlsInfo)
    # 姓名地址      girlNL，  身高体重 girlHW
    # 个人主页地址  girlHRUL, 封面图片 URL
    for girlNL, girlHW, girlHURL, girlCover in girlsInfo:
        list1 = girlNL.split()
        list2 = girlHW.split('/')
        print(type(girlCover))

        #存入db
        str = [list1[0],list1[1],list2[0],list2[1],girlCover]
        print(str)
        print(type(list1[0]))


        try:

            cursor.execute("insert into TBmodel values(%s,%s,%s,%s,%s)",str)
            # 提交到数据库执行
            db.commit()
        except:
            # 如果发生错误则回滚
            print("failed")
            db.rollback()


        print("[*]Girl :", girlNL, girlHW)
        # 建立文件夹
        mkdir(outputDir + girlNL)
        print("    [*]saving...")
        # 获取封面图片
        data = urlopen(girlCover).read()
        with open(outputDir + girlNL + '/cover.jpg', 'wb') as f:
            f.write(data)
        print("    [+]Loading Cover... ")
        # 获取个人主页中的图片
        #getImgs(girlHURL, outputDir + girlNL)




    sql = "SELECT * FROM TBmodel"
    try:
   # 执行SQL语句
        cursor.execute(sql)
   # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            fname = row[0]

       # 打印结果
            print ("fname=%s" % \
                (fname))
    except:
        print ("Error: unable to fetch data")
    driver.close()
    # 关闭数据库连接
    db.close()



def mkdir(path):
    # 判断路径是否存在
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print("    [*]新建了文件夹", path)
        # 创建目录操作函数
        os.makedirs(path)
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print('    [+]文件夹', path, '已创建')





if __name__ == '__main__':
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    main()
