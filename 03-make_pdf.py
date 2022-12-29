import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import textwrap

path_db_kamir = './data/db/kamir_cardpool.sqlite'
data_img_dir = './data/img/'
data_pdf_dir = './data/pdf/'
path_img_proxy = './resources/no_image.jpg'

def textReshaper(txt):
    if(txt == ''):
        return ''
    txt = txt.replace('  ', '\n')
    tmp = []

    for s in txt.split('\n'):
        for ss in textwrap.wrap(s, 39):
            tmp.append(ss)
        tmp.append('\n')
    else:
        del tmp[len(tmp)-1]

    return '\n'.join(tmp).replace('\n\n', '\n')

def generate_pdf(i): # i means info
    card_info = {'name': i[0], 'mana_value': str(i[1]), 'mana_cost': i[2] or '',
                 'type': i[3], 'power': str(i[4]), 'toughness': str(i[5]),
                 'expansion': i[6], 'text': i[7] or ''}
    card_pdf = canvas.Canvas(data_pdf_dir + '{0}/{1}.pdf'.format(card_info['mana_value'], card_info['name']))
    card_pdf.setPageSize((48.0*mm, 67.0*mm))

    card_pdf.setStrokeColorRGB(0.8, 0.8, 0.8)
    card_pdf.setLineWidth(0.5)
    card_pdf.rect(0.5*mm, 0.5*mm, 47*mm, 66*mm)

    card_pdf.setFont("Courier", 2.5*mm)
    card_pdf.drawRightString(47.5*mm, 64.3*mm, card_info['mana_cost'])
    card_pdf.drawString(0.8*mm, 61.8*mm, card_info['name'])

    img = Image.open(data_img_dir + '{0}/{1}.jpg'.format(card_info['mana_value'], card_info['name']))
    card_pdf.drawInlineImage(img, 1*mm, 34*mm,
                              width=46*mm, height=46*100/171*mm)
    if(len(card_info['type']) > 37):
        card_pdf.setFont("Courier", (77.4 / len(card_info['type']))*mm)
        card_pdf.drawString(0.8*mm, 32*mm, card_info['type'])
    else:
        card_pdf.setFont("Courier", 2.15*mm)
        card_pdf.drawString(0.9*mm, 31.75*mm, card_info['type'])

    card_pdf.line(1*mm, 30.75*mm, 47*mm, 30.75*mm)

    shaped_text = textReshaper(card_info['text'])
    lc = shaped_text.count('\n') + 1 # lines count テキスト部の行数をカウントする　テキストレイアウト調整用
    card_pdf.setFont("Courier", 2.025*mm if lc < 14 else (2.025 - 0.035 * (lc - 13))*mm)
    txt = card_pdf.beginText(1*mm, 29*mm)
    txt.setLeading(2*mm if lc < 14 else (2 - 0.09 * (lc - 13))*mm)
    txt.setCharSpace(-0.03*mm)

    txt.textLines(shaped_text)
    card_pdf.drawText(txt)

    card_pdf.setFont("Courier", 2*mm)
    card_pdf.drawString(1*mm, 1*mm, card_info['expansion'])

    card_pdf.setFont("Courier-Bold", 2.5*mm)
    card_pdf.drawRightString(46.5*mm, 2*mm,
                              card_info['power'] + '/' + card_info['toughness'])

    card_pdf.setFont("Courier", 1.8*mm)
    card_pdf.drawString(6*mm, 1*mm, "#ProjectKamir")

    card_pdf.save()

def make_pdf():
    conn = sqlite3.connect(path_db_kamir)
    cur = conn.cursor()

    cur.execute("SELECT name, mana_value, mana_cost, type, power, toughness, expansion, oracle FROM cards WHERE layout == \"normal\" OR layout == \"adventure\" OR layout == \"transform\" OR layout == \"meld\" OR layout == \"modal_dfc\" ORDER BY mana_value, name")

    cards = cur.fetchall()

    conn.close()

    for c in cards:
        #print(c[0]) # name
        generate_pdf(c)

if __name__ == '__main__':
    make_pdf()