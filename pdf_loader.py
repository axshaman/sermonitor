from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm, inch, pica
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
import json

from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, Frame, Spacer



# def pdf_report(data):
def pdf_report(data, name):
    
    # Cirycic symbols
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))

    # Content of PDF
    # fileName = 'bot_telegr.pdf'
    fileName = f'bot_telegram/handlers/reports/{name}.pdf'

    # Create PDF Page
    pdf = canvas.Canvas(fileName, pagesize=A4)
    pdf.setLineWidth(2)             # It's doesn't work
    pdf.setFont("FreeSans", 10)      # Font connect
    pdf.line(30, 710, 550, 710)     # Line on a page



    # --------------------------- START JSON file ------------------------

    # Opening JSON file
    # f = open('1.json', encoding='utf-8')        # encoding='cp1251'      
    # data = json.load(f)                         # Create List of Dicts


    # Обращение по ключам словаря по конкретному объекту
    obj = data[0]
    s = ''
    for i in obj['name']:
        s += i                 # Достаем словарь из массива
    name = 'Параметры поиска:    ' + s                # Обращаемся по ключу в данном словаре
    # print(name)
    pdf.drawString(40, 800, name)            # Какой запрос
    pdf.drawString(40, 750, 'Таблица статистики по ключевым показателям и датам')      # Таблица статистики


    # Dicts of all objects in JSON file
    styles = getSampleStyleSheet()              # Styles DOESN'T WORK
    last_index = len(data) + 1                  # Количество словарей в массиве для среза
    # text = pdf.beginText(inch * 1, inch * 5, styles['Normal'])
    # text = pdf.beginText(inch * 1, inch * 9)
    text = pdf.beginText()                      # Сущность для передачи текста в PDF

    yb = 675                                     # Параметр с позицией строки по высоте
    yс = 660
    yd = 645
    for i in data[0:last_index]:                # Проходим по ключам всех словарей
        # textLines = i['url']                  # чтобы получить значения

        pdf.drawString(50, yb, i['url'])         # Рисуем строку по координатам x/y
        pdf.drawString(30, yс, i['snippet'][0:100])
        pdf.drawString(30, yd, i['snippet'][101:])
        # print(i['snippet'][121:])
        # print('-----------')

        yb -= 60                                 # Двигаем строку вниз
        yс -= 60
        yd -= 60 

    documentTitle = name                         # PDF Title
    pdf.setTitle(documentTitle)

    # pdf.drawText(text)
    pdf.drawText(text)                           # Вставляем полученный текст в PDF
    return pdf.save()


