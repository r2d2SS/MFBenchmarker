from multiprocessing import context
from numpy import double
import requests
from django.shortcuts import render
import json
import pymysql
from sshtunnel import SSHTunnelForwarder
from datetime import date
import pandas as pd
import os
from .forms import MarginForm
from bs4 import BeautifulSoup


# Create your views here.
# definition of my functions


def get_download_path(file_name):
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
            result = str(location) + '/' + file_name + '.xlsx'
        return result
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads/{}{}'.format(file_name, '.xlsx'))


MySQL_hostname = 'localhost'  # MySQL Host
sql_username = 'remoteAccess'  # Username
sql_password = 'lpf9dmWmi7@kdl'  # os.environ.get('sql_password') #Password
sql_main_database = 'wordpress'  # Database Name
sql_port = 3306
ssh_host = '206.189.3.154'  # SSH Host
ssh_user = 'root'  # SSH Username
ssh_port = 22
ssh_pass = 'we@dflG0QfL32F'


with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_password=ssh_pass,
        ssh_username=ssh_user,
        remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
    conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                           passwd=sql_password, db=sql_main_database,
                           port=tunnel.local_bind_port)
    
    today = date.today()
    cursor = conn.cursor()
                
    def base(request):
        df = pd.read_csv("output.csv")
        df = df.fillna('')
        # parsing the DataFrame in json format.
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, 'main/base.html', context)
        


    def n_export(request):
        df = pd.read_csv("neverSold.csv")

        writer = pd.ExcelWriter(get_download_path('neverSoldBenchmark'), engine='xlsxwriter')
        df.to_excel(writer, index=True, sheet_name='neverSold', index_label='#')

        workbook = writer.book
        worksheet = writer.sheets['neverSold']
        
        # conditional formatting
        number_rows = len(df.index)
        table_range = "B2:G{}".format(number_rows + 1)
        border_format = workbook.add_format({'border': 1, 'align': 'left'})
        f1 = workbook.add_format({'font_size': 11,
                              'align': 'center'})
        
        # setting provisional widths
        worksheet.set_column('B:B', width=50)
        worksheet.set_column('G:G', 15, f1)   
        
        # adding table borders
        worksheet.conditional_format(table_range, {'type': 'no_blanks',
                                               'format': border_format})
        worksheet.conditional_format(table_range, {'type': 'blanks',
                                               'format': border_format})
        
        writer.save()

        df = pd.read_csv("neverSold.csv")
        df = df.fillna('')
        # parsing the DataFrame in json format.
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, 'main/n_export.html', context)

    # funciones auxiliares
    def in_marcas_filter(value):
        return """SELECT * FROM inStock_pivot WHERE marca = '""" + value + """'; """
    
    def out_marcas_filter(value):
        return """SELECT * FROM outOfStock_pivot WHERE marca = '""" + value + """'; """

    def n_marcas_filter(value):
        return """SELECT * FROM notInPM WHERE marca = '""" + value + """'; """
    
    def margin_value(request):
        return render(request, 'cv-form.html', {'form': form})
        

    conn.commit()
    conn.close()
    
def inStock(request):
    with SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_password=ssh_pass,
                ssh_username=ssh_user,
                remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
            conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                                    passwd=sql_password, db=sql_main_database,
                                    port=tunnel.local_bind_port)
            if request.method == "POST":
                filtro = request.POST["marca"]
                query = in_marcas_filter(str(filtro))
                results = pd.read_sql_query(query, conn)
                results.to_csv("filtered.csv", index=False)
                df = pd.read_csv("filtered.csv")
                df = df.fillna('')
            # parsing the DataFrame in json format.
                json_records = df.reset_index().to_json(orient='records')
                data = json.loads(json_records)
                context = {'d': data}
                conn.close()
                return render(request, 'main/in_stock.html', context)
            else:
                query = "SELECT * FROM wordpress.inStock_pivot;"
                results = pd.read_sql_query(query, conn)
                results.to_csv("inStock.csv", index=False)
                df = pd.read_csv("inStock.csv")
                df = df.fillna('')
                # parsing the DataFrame in json format.
                json_records = df.reset_index().to_json(orient='records')
                data = json.loads(json_records)
                context = {'d': data}
                conn.close()
                return render(request, 'main/in_stock.html', context)

def outOfStock(request):
    with SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_password=ssh_pass,
                ssh_username=ssh_user,
                remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
            conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                                    passwd=sql_password, db=sql_main_database,
                                    port=tunnel.local_bind_port)
            if request.method == "POST":
                filtro = request.POST["marca"]
                query = out_marcas_filter(str(filtro))
                results = pd.read_sql_query(query, conn)
                results.to_csv("filtered.csv", index=False)
                df = pd.read_csv("filtered.csv")
                df = df.fillna('')
            # parsing the DataFrame in json format.
                json_records = df.reset_index().to_json(orient='records')
                data = json.loads(json_records)
                context = {'d': data}
                conn.close()
                return render(request, 'main/out_of_stock.html', context)
            else:
                query1 = "SELECT * FROM wordpress.outOfStock_pivot;"
                results = pd.read_sql_query(query1, conn)
                results.to_csv("outOfStock.csv", index=False)
                df = pd.read_csv("outOfStock.csv")
                df = df.fillna('')
                # parsing the DataFrame in json format.
                json_records = df.reset_index().to_json(orient='records')
                data = json.loads(json_records)
                context = {'d': data}
                conn.close()
                return render(request, 'main/out_of_stock.html', context)



def neverSold(request):
    with SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_password=ssh_pass,
                ssh_username=ssh_user,
                remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
            conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                                    passwd=sql_password, db=sql_main_database,
                                    port=tunnel.local_bind_port)
            
            query = "SELECT * FROM wordpress.notInPM;"
            results = pd.read_sql_query(query, conn)
            results.to_csv("neverSold.csv", index=False)
            df = pd.read_csv("neverSold.csv")
            df = df.fillna('')
            # parsing the DataFrame in json format.
            json_records = df.reset_index().to_json(orient='records')
            data = json.loads(json_records)
            context = {'d': data}
            conn.close()
            return render(request, 'main/never_sold.html', context)
        
        
def margin_set(request):
    context = {}
    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_password=ssh_pass,
            ssh_username=ssh_user,
            remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
                conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                            passwd=sql_password, db=sql_main_database,
                            port=tunnel.local_bind_port)
                cursor = conn.cursor()
                if request.method == "POST":
                    formOriginal = MarginForm(request.POST) 
                    if formOriginal.is_valid():
                        form = formOriginal['new_margin'].value
                        new_margin = formOriginal.cleaned_data['new_margin']

                        # update_stock()
                        query1 = "drop view outofstock;"
                        query2 = "drop view instock;"
                        cursor.execute(query1)
                        cursor.execute(query2)
                        conn.commit()
                    
                        query3 = """create view outofstock as (select p.SKU, m.stock_status from product_master p JOIN www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 'outofstock');"""
                        query4 = """create view instock as (select p.SKU, m.stock_status from product_master p JOIN www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 'instock');"""
                        cursor.execute(query3)
                        cursor.execute(query4)
                        conn.commit()
                    
                        # update_pivot_tables()
                        margin = str(round(float(1 - (int(new_margin)/100)),1))

                        # Currency conversions 
                        eur_usd = "https://free.currconv.com/api/v7/convert?q=EUR_USD&compact=ultra&apiKey=c9a95883144392549da5"
                        res = requests.get(eur_usd).text
                        doc = BeautifulSoup(res, "html.parser")
                        if doc.string is not None:
                            price = doc.string.split(':')[1].split('}')[0]
                        else: #esto para cuando este down el server TODO: EVENTUALLY EITHER CHANGE API OR HAVE TWO FREE APIS IN CASE ONE FAILS
                            price = '1.07'
                        
                        query1 = " drop view outOfStock_pivot; "
                        query2 = " drop view inStock_pivot; "
                        cursor.execute(query1)
                        cursor.execute(query2)
                        conn.commit()
                        
                        query3 = " create view outOfStock_pivot as (select sku, marca, ROUND(max(TA)/" + margin + "*" + price + ", 3) as TA, ROUND(max(CO)/" + margin + "*" + price + ", 3)  as CO, ROUND(max(DV)/" + margin + "*" + price + ", 3)  as DV, ROUND(max(GE)/" + margin + "*" + price + ", 3)  as GE, ROUND(max(LP)/" + margin + "*" + price + ", 3)  as LP, ROUND(max(RA)/" + margin + "*" + price + ", 3)  as RA, ROUND(max(LA)/" + margin + "*" + price + ", 3)  as LA, ROUND(max(CF)/" + margin + "*" + price + ", 3)  as CF, ROUND(max(IH), 3) as IH, ROUND(max(CH), 3) as CH, ROUND(max(NT), 3) as NT from outofStockBenchmark group by sku, marca); "
                        query4 = " create view inStock_pivot as (select sku, marca, ROUND(max(TA)/" + margin + "*" + price + ", 3) as TA, ROUND(max(CO)/" + margin + "*" + price + ", 3)  as CO, ROUND(max(DV)/" + margin + "*" + price + ", 3)  as DV, ROUND(max(GE)/" + margin + "*" + price + ", 3)  as GE, ROUND(max(LP)/" + margin + "*" + price + ", 3)  as LP, ROUND(max(RA)/" + margin + "*" + price + ", 3)  as RA, ROUND(max(LA)/" + margin + "*" + price + ", 3)  as LA, ROUND(max(CF)/" + margin + "*" + price + ", 3)  as CF, ROUND(max(IH), 3) as IH, ROUND(max(CH), 3) as CH, ROUND(max(NT), 3) as NT from inStockBenchmark group by sku, marca); "
                        cursor.execute(query3)
                        cursor.execute(query4)
                        conn.commit()
                        conn.close()
                        return render(request, 'main/new_margin.html', {'margin': form})
                    else:
                        form = form['new_margin'].value
                        conn.close()
                        return render(request, 'main/new_margin_error.html', {'margin': form})
                else: 
                    # default margin of 40
                    # update_stock()
                    query1 = "drop view outofstock;"
                    query2 = "drop view instock;"
                    cursor.execute(query1)
                    cursor.execute(query2)
                    conn.commit()
                
                    query3 = """create view outofstock as (select p.SKU, m.stock_status from product_master p JOIN www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 'outofstock');"""
                    query4 = """create view instock as (select p.SKU, m.stock_status from product_master p JOIN www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 'instock');"""
                    cursor.execute(query3)
                    cursor.execute(query4)
                    conn.commit()
                
                    # update_pivot_tables()
                    margin = str(round(float(1 - (int(40)/100)),1))

                    # Currency conversions 
                    eur_usd = "https://free.currconv.com/api/v7/convert?q=EUR_USD&compact=ultra&apiKey=c9a95883144392549da5"
                    res = requests.get(eur_usd).text
                    doc = BeautifulSoup(res, "html.parser")
                    if doc.string is not None:
                        price = doc.string.split(':')[1].split('}')[0]
                    else: #esto para cuando este down el server TODO: EVENTUALLY EITHER CHANGE API OR HAVE TWO FREE APIS IN CASE ONE FAILS
                        price = '1.07'
                    
                    query1 = " drop view outOfStock_pivot; "
                    query2 = " drop view inStock_pivot; "
                    cursor.execute(query1)
                    cursor.execute(query2)
                    conn.commit()
                    
                    query3 = " create view outOfStock_pivot as (select sku, marca, ROUND(max(TA)/" + margin + "*" + price + ", 3) as TA, ROUND(max(CO)/" + margin + "*" + price + ", 3)  as CO, ROUND(max(DV)/" + margin + "*" + price + ", 3)  as DV, ROUND(max(GE)/" + margin + "*" + price + ", 3)  as GE, ROUND(max(LP)/" + margin + "*" + price + ", 3)  as LP, ROUND(max(RA)/" + margin + "*" + price + ", 3)  as RA, ROUND(max(LA)/" + margin + "*" + price + ", 3)  as LA, ROUND(max(CF)/" + margin + "*" + price + ", 3)  as CF, ROUND(max(IH), 3) as IH, ROUND(max(CH), 3) as CH, ROUND(max(NT), 3) as NT from outofStockBenchmark group by sku, marca); "
                    query4 = " create view inStock_pivot as (select sku, marca, ROUND(max(TA)/" + margin + "*" + price + ", 3) as TA, ROUND(max(CO)/" + margin + "*" + price + ", 3)  as CO, ROUND(max(DV)/" + margin + "*" + price + ", 3)  as DV, ROUND(max(GE)/" + margin + "*" + price + ", 3)  as GE, ROUND(max(LP)/" + margin + "*" + price + ", 3)  as LP, ROUND(max(RA)/" + margin + "*" + price + ", 3)  as RA, ROUND(max(LA)/" + margin + "*" + price + ", 3)  as LA, ROUND(max(CF)/" + margin + "*" + price + ", 3)  as CF, ROUND(max(IH), 3) as IH, ROUND(max(CH), 3) as CH, ROUND(max(NT), 3) as NT from inStockBenchmark group by sku, marca); "
                    cursor.execute(query3)
                    cursor.execute(query4)
                    conn.commit()
                    conn.close()
                    return render(request, 'main/margin_set.html', context)
                
def in_export(request):
    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_password=ssh_pass,
            ssh_username=ssh_user,
            remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
                conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                            passwd=sql_password, db=sql_main_database,
                            port=tunnel.local_bind_port)
                cursor = conn.cursor()
                query = "SELECT * FROM wordpress.inStock_pivot;"
                results = pd.read_sql_query(query, conn)
                results.to_csv("inStock.csv", index=False)
                df = pd.read_csv("inStock.csv")

                writer = pd.ExcelWriter(get_download_path('inStockBenchmark'), engine='xlsxwriter')
                df.to_excel(writer, index=True, sheet_name='inStock', index_label='#')

                workbook = writer.book
                worksheet = writer.sheets['inStock']
                # conditional formatting
                number_rows = len(df.index)
                table_range = "B2:N{}".format(number_rows + 1)
                border_format = workbook.add_format({'border': 1, 'align': 'left'})
                
                # setting of widths 
                worksheet.set_column('B:B', width=15)
                worksheet.set_column('C:C', width=20)
                
                # establish the colors to use
                red = workbook.add_format({'bg_color': '#FFC7CE'})
                green = workbook.add_format({'bg_color': '#C6EFCE'})

                for row in range(number_rows + 1):
                    worksheet.conditional_format('D{}'.format(row + 2) + ':N{}'.format(row + 2), {'type': 'average',
                                                                                                    'criteria': 'above',
                                                                                                    'format': red})

                    worksheet.conditional_format('D{}'.format(row + 2) + ':N{}'.format(row + 2), {'type': 'average',
                                                                                                    'criteria': 'below',
                                                                                                    'format': green})
                
                    # adding table borders
                worksheet.conditional_format(table_range, {'type': 'no_blanks',
                                                        'format': border_format})
                worksheet.conditional_format(table_range, {'type': 'blanks',
                                                        'format': border_format})
                
                writer.save()

                df = df.fillna('')
                # parsing the DataFrame in json format.
                json_records = df.reset_index().to_json(orient='records')
                data = json.loads(json_records)
                context = {'d': data}
                return render(request, 'main/in_export.html', context)
            
def out_export(request):
    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_password=ssh_pass,
            ssh_username=ssh_user,
            remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
                conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                            passwd=sql_password, db=sql_main_database,
                            port=tunnel.local_bind_port)
                cursor = conn.cursor()
                query1 = "SELECT * FROM wordpress.outOfStock_pivot;"
                results = pd.read_sql_query(query1, conn)
                results.to_csv("outOfStock.csv", index=False)
                df = pd.read_csv("outOfStock.csv")

                writer = pd.ExcelWriter(get_download_path('outOfStockBenchmark'), engine='xlsxwriter')
                df.to_excel(writer, index=True, sheet_name='outOfStock', index_label='#')

                workbook = writer.book
                worksheet = writer.sheets['outOfStock']
                # conditional formatting
                number_rows = len(df.index)
                table_range = "B2:N{}".format(number_rows + 1)
                border_format = workbook.add_format({'border': 1, 'align': 'left'})
                
                #setting provisional widths
                worksheet.set_column('B:B', width=15)
                worksheet.set_column('C:C', width=20)

                # establish the colors to use
                red = workbook.add_format({'bg_color': '#FFC7CE'})
                green = workbook.add_format({'bg_color': '#C6EFCE'})

                for row in range(number_rows + 1):
                    worksheet.conditional_format('D{}'.format(row + 2) + ':N{}'.format(row + 2), {'type': 'average',
                                                                                                    'criteria': 'above',
                                                                                                    'format': red})

                    worksheet.conditional_format('D{}'.format(row + 2) + ':N{}'.format(row + 2), {'type': 'average',
                                                                                                    'criteria': 'below',
                                                                                                    'format': green})
                
                    # adding table borders
                worksheet.conditional_format(table_range, {'type': 'no_blanks',
                                                        'format': border_format})
                worksheet.conditional_format(table_range, {'type': 'blanks',
                                                        'format': border_format})
                
                writer.save()

                df = df.fillna('')
                # parsing the DataFrame in json format.
                json_records = df.reset_index().to_json(orient='records')
                data = json.loads(json_records)
                context = {'d': data}
                return render(request, 'main/out_export.html', context)