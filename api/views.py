from multiprocessing import context
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
        # Currency conversions (eur_usd)
        eur_usd = "https://free.currconv.com/api/v7/convert?q=EUR_USD&compact=ultra&apiKey=c9a95883144392549da5"
        res = requests.get(eur_usd).text
        doc = BeautifulSoup(res, "html.parser")
        if doc.string is not None:
            price_usd = doc.string.split(':')[1].split('}')[0]
        else:  # esto para cuando este down el server TODO: EVENTUALLY EITHER CHANGE API OR HAVE TWO FREE APIS IN CASE ONE FAILS
            price_usd = '1.053517'

        # Currency conversions (usd_eur)
        usd_eur = "https://free.currconv.com/api/v7/convert?q=USD_EUR&compact=ultra&apiKey=c9a95883144392549da5"
        res = requests.get(usd_eur).text
        doc = BeautifulSoup(res, "html.parser")
        if doc.string is not None:
            price_eur = doc.string.split(':')[1].split('}')[0]
        else:  # esto para cuando este down el server TODO: EVENTUALLY EITHER CHANGE API OR HAVE TWO FREE APIS IN CASE ONE FAILS
            price_eur = '0.94925'

        if request.method == "POST":
            formOriginal = MarginForm(request.POST)
            if formOriginal.is_valid():
                form = formOriginal['new_margin'].value
                new_margin = formOriginal.cleaned_data['new_margin']

                # new margin
                margin = str(round(float(1 - (int(new_margin) / 100)), 1))

                # update stock y notInPm
                query1 = "drop view outofstock;"
                query2 = "drop view instock;"
                query3 = "drop view notInPM"
                cursor.execute(query1)
                cursor.execute(query2)
                cursor.execute(query3)
                conn.commit()

                query4 = """create view outofstock as (select p.SKU, m.stock_status from product_master p JOIN 
                www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 
                'outofstock');"""
                query5 = """create view instock as (select p.SKU, m.stock_status from product_master p JOIN 
                www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 
                'instock');"""
                query6 = """create view notInPM as (select Product, ProductType, case when s.Competitor = "IH" then $ 
                end as IH, case when s.Competitor = "CH" then $ end as CH, case when s.Competitor = "NT" then $ end as 
                NT, case when s.Competitor = "IH" or s.Competitor = "CH" or s.Competitor = "NT" then CEIL((($*""" + \
                         margin + """)/1+0.05)*""" + price_eur + """) end as PrecioAComprar from scraper s 
                         WHERE s.sku IS NULL AND s.ExtractionDate = ' """ + str(today) + """ ');"""
                cursor.execute(query4)
                cursor.execute(query5)
                cursor.execute(query6)
                conn.commit()

                # update Benchmarkers
                query1 = " drop view outOfStockBenchmark; "
                query2 = " drop view inStockBenchmark; "
                cursor.execute(query1)
                cursor.execute(query2)
                conn.commit()


                query3 = """create view outOfStockBenchmark as (select s.ExtractionDate, s.scraper_id, s.sku, Product, ProductType, p.marca, case when p.proveedor = "TA" then coste_trans_tax end as TA, case when p.proveedor = "CO" then coste_trans_tax end as CO, case when p.proveedor = "DV" then coste_trans_tax end as DV, case when p.proveedor = "GE" then coste_trans_tax end as GE, case when p.proveedor = "LP" then coste_trans_tax end as LP, case when p.proveedor = "RA" then coste_trans_tax end as RA, case when p.proveedor = "LA" then coste_trans_tax end as LA, case when p.proveedor = "CF" then coste_trans_tax end as CF, case when s.Competitor = "IH" then $ end as IH, case when s.Competitor = "CH" then $ end as CH, case when s.Competitor = "NT" then $ end as NT from scraper s JOIN product_master p ON s.sku = p.Simple_SKU JOIN www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci JOIN outofstock i ON p.SKU = i.SKU WHERE s.ExtractionDate = '""" + str(today) + """');"""
                query4 = """create view inStockBenchmark as (select s.ExtractionDate, s.scraper_id, s.sku, Product, ProductType, p.marca, case when p.proveedor = "TA" then coste_trans_tax end as TA, case when p.proveedor = "CO" then coste_trans_tax end as CO, case when p.proveedor = "DV" then coste_trans_tax end as DV, case when p.proveedor = "GE" then coste_trans_tax end as GE, case when p.proveedor = "LP" then coste_trans_tax end as LP, case when p.proveedor = "RA" then coste_trans_tax end as RA, case when p.proveedor = "LA" then coste_trans_tax end as LA, case when p.proveedor = "CF" then coste_trans_tax end as CF, case when s.Competitor = "IH" then $ end as IH, case when s.Competitor = "CH" then $ end as CH, case when s.Competitor = "NT" then $ end as NT from scraper s JOIN product_master p ON s.sku = p.Simple_SKU JOIN www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci JOIN instock i ON p.SKU = i.SKU WHERE s.ExtractionDate = '""" + str(today) + """');"""
                cursor.execute(query3)
                cursor.execute(query4)
                conn.commit()

                # update PIVOTS

                query1 = " drop view outOfStock_pivot; "
                query2 = " drop view inStock_pivot; "
                cursor.execute(query1)
                cursor.execute(query2)
                conn.commit()

                query3 = " create view outOfStock_pivot as (select sku, marca, CEIL(max(TA)/" + margin + "*" + price_usd + ") as TA, CEIL(max(CO)/" + margin + "*" + price_usd + ")  as CO, CEIL(max(DV)/" + margin + "*" + price_usd + ")  as DV, CEIL(max(GE)/" + margin + "*" + price_usd + ")  as GE, CEIL(max(LP)/" + margin + "*" + price_usd + ")  as LP, CEIL(max(RA)/" + margin + "*" + price_usd + ")  as RA, CEIL(max(LA)/" + margin + "*" + price_usd + ")  as LA, CEIL(max(CF)/" + margin + "*" + price_usd + ")  as CF, CEIL(max(IH)) as IH, CEIL(max(CH)) as CH, CEIL(max(NT)) as NT from outOfStockBenchmark group by sku, marca); "
                query4 = " create view inStock_pivot as (select sku, marca, CEIL(max(TA)/" + margin + "*" + price_usd + ") as TA, CEIL(max(CO)/" + margin + "*" + price_usd + ")  as CO, CEIL(max(DV)/" + margin + "*" + price_usd + ")  as DV, CEIL(max(GE)/" + margin + "*" + price_usd + ")  as GE, CEIL(max(LP)/" + margin + "*" + price_usd + ")  as LP, CEIL(max(RA)/" + margin + "*" + price_usd + ")  as RA, CEIL(max(LA)/" + margin + "*" + price_usd + ")  as LA, CEIL(max(CF)/" + margin + "*" + price_usd + ")  as CF, CEIL(max(IH)) as IH, CEIL(max(CH)) as CH, CEIL(max(NT)) as NT from inStockBenchmark group by sku, marca); "
                cursor.execute(query3)
                cursor.execute(query4)
                conn.commit()
                conn.close()
                return render(request, 'main/new_margin.html', {'margin': form})
            else:
                form = formOriginal['new_margin'].value
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

            query3 = """create view outofstock as (select p.SKU, m.stock_status from product_master p JOIN 
            www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 
            'outofstock');"""
            query4 = """create view instock as (select p.SKU, m.stock_status from product_master p JOIN 
            www_wc_product_meta_lookup m ON p.SKU = m.sku collate utf8mb4_0900_ai_ci WHERE m.stock_status = 
            'instock');"""
            cursor.execute(query3)
            cursor.execute(query4)
            conn.commit()

            # update_pivot_tables()
            margin = str(round(float(1 - (int(40) / 100)), 1))

            query1 = " drop view outOfStock_pivot; "
            query2 = " drop view inStock_pivot; "
            cursor.execute(query1)
            cursor.execute(query2)
            conn.commit()

            query3 = " create view outOfStock_pivot as (select sku, marca, CEIL(max(TA)/" + margin + "*" + price_usd + ") as TA, CEIL(max(CO)/" + margin + "*" + price_usd + ")  as CO, CEIL(max(DV)/" + margin + "*" + price_usd + ")  as DV, CEIL(max(GE)/" + margin + "*" + price_usd + ")  as GE, CEIL(max(LP)/" + margin + "*" + price_usd + ")  as LP, CEIL(max(RA)/" + margin + "*" + price_usd + ")  as RA, CEIL(max(LA)/" + margin + "*" + price_usd + ")  as LA, CEIL(max(CF)/" + margin + "*" + price_usd + ")  as CF, CEIL(max(IH)) as IH, CEIL(max(CH)) as CH, CEIL(max(NT)) as NT from outOfStockBenchmark group by sku, marca); "
            query4 = " create view inStock_pivot as (select sku, marca, CEIL(max(TA)/" + margin + "*" + price_usd + ") as TA, CEIL(max(CO)/" + margin + "*" + price_usd + ")  as CO, CEIL(max(DV)/" + margin + "*" + price_usd + ")  as DV, CEIL(max(GE)/" + margin + "*" + price_usd + ")  as GE, CEIL(max(LP)/" + margin + "*" + price_usd + ")  as LP, CEIL(max(RA)/" + margin + "*" + price_usd + ")  as RA, CEIL(max(LA)/" + margin + "*" + price_usd + ")  as LA, CEIL(max(CF)/" + margin + "*" + price_usd + ")  as CF, CEIL(max(IH)) as IH, CEIL(max(CH)) as CH, CEIL(max(NT)) as NT from inStockBenchmark group by sku, marca); "
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

        # setting provisional widths
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
