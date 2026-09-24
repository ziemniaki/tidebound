from pathlib import Path
import re
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'design_bible.pdf'
TEXT=(ROOT/'design_bible.md').read_text()
fontroot=Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype')
for name,file in [('Body','LiberationSerif-Regular.ttf'),('Body-Bold','LiberationSerif-Bold.ttf'),
                  ('Body-Italic','LiberationSerif-Italic.ttf'),('Body-BoldItalic','LiberationSerif-BoldItalic.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(fontroot/file)))
for name,file in [('Head','DejaVuSans.ttf'),('Head-Bold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body-Italic',boldItalic='Body-BoldItalic')
pdfmetrics.registerFontFamily('Head',normal='Head',bold='Head-Bold',italic='Head',boldItalic='Head-Bold')
navy=colors.HexColor('#142C37'); teal=colors.HexColor('#306565'); grey=colors.HexColor('#657477')
styles={
 'body':ParagraphStyle('Body',fontName='Body',fontSize=11,leading=15.4,spaceAfter=8,textColor=navy,allowWidows=0,allowOrphans=0),
 'h1':ParagraphStyle('Chapter',fontName='Head-Bold',fontSize=21,leading=26,spaceAfter=18,textColor=navy,keepWithNext=True),
 'h2':ParagraphStyle('Subsection',fontName='Head-Bold',fontSize=12,leading=17,spaceBefore=13,spaceAfter=8,textColor=teal,keepWithNext=True),
 'small':ParagraphStyle('Small',fontName='Head',fontSize=9,leading=13,spaceAfter=9,textColor=grey),
 'bullet':ParagraphStyle('Bullet',fontName='Body',fontSize=11,leading=15.4,leftIndent=14,firstLineIndent=0,bulletIndent=0,spaceAfter=6,textColor=navy,allowWidows=0,allowOrphans=0),
}
def inline(s):
    s=s.replace('\u2014',' - ').replace('\u2013','-').replace('\u2011','-')
    s=escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Head">\1</font>',s)
    return s

class BibleDoc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if getattr(flowable,'chapter',None):
            title=flowable.chapter; key='c'+str(self.seq.nextf('chapter'))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title,key,level=0)
            self.notify('TOCEntry',(0,title,self.page,key))

def cover(canvas,doc):
    w,h=A4
    canvas.saveState();canvas.setFillColor(navy);canvas.rect(0,0,w,h,fill=1,stroke=0)
    canvas.setFillColor(colors.HexColor('#95C2B5'));canvas.setFont('Head',11)
    canvas.drawString(55,h-95,'A POKÉMON FANGAME / CREATIVE RECORD')
    canvas.setFillColor(colors.white);canvas.setFont('Head-Bold',45)
    canvas.drawString(52,h-200,'TIDEBOUND')
    canvas.setFont('Body',23);canvas.drawString(55,h-238,'Game bible')
    canvas.setStrokeColor(colors.HexColor('#95C2B5'));canvas.setLineWidth(1)
    canvas.line(55,h-276,w-55,h-276)
    y=h-327
    for line in ['A solitary journey through a wounded coastal land,',
                 'where the sea keeps the dead and love can become',
                 'an excuse to refuse their absence.']:
        canvas.setFont('Body',12);canvas.drawString(55,y,line);y-=20
    canvas.setFillColor(colors.HexColor('#C1D6D4'));canvas.setFont('Head',10)
    for i,line in enumerate(['Creative direction: Wojciech Krzyżanowski','Version 1.27 / 23 September 2026',
                             'Working title / Full story spoilers',
                             'Confirmed decisions, proposals, and intentional mysteries']):
        canvas.drawString(55,155-i*20,line)
    canvas.restoreState()

def bodypage(canvas,doc):
    w,h=A4;canvas.saveState();canvas.setFillColor(grey);canvas.setFont('Head',8)
    canvas.drawString(52,h-32,'TIDEBOUND  /  GAME BIBLE')
    canvas.setStrokeColor(colors.HexColor('#CED8D5'));canvas.setLineWidth(.5)
    canvas.line(52,h-41,w-52,h-41)
    canvas.drawString(52,29,'Version 1.27  /  23 September 2026  /  Full story spoilers')
    canvas.drawRightString(w-52,29,str(doc.page));canvas.restoreState()

doc=BibleDoc(str(OUT),pagesize=A4,rightMargin=52,leftMargin=52,topMargin=63,bottomMargin=52,
            title='Tidebound - Game bible',author='Wojciech Krzyżanowski',
            subject='Consolidated worldbuilding, story outline, and continuity record')
story=[Spacer(1,20),PageBreak(),Paragraph('How to use this bible',styles['h1'])]
# Front matter starts after the author block; cover already contains the logline.
front=TEXT.split('This is the consolidated',1)[1].split('### Contents',1)[0]
front='This is the consolidated'+front
for block in front.strip().split('\n\n'):
    if block.startswith('### '):continue
    story.append(Paragraph(inline(block.replace('\n',' ')),styles['body']))
story += [Spacer(1,9),Paragraph('Contents',styles['h2'])]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('TOC',fontName='Head',fontSize=9.2,leading=13.5,
    leftIndent=0,firstLineIndent=0,rightIndent=20,spaceBefore=3,textColor=navy)]
story.append(toc)
content='## 1. '+TEXT.split('## 1. ',1)[1]
for block in content.split('\n\n'):
    block=block.strip()
    if not block:continue
    if block.startswith('## '):
        title=block[3:]
        if title.startswith(('1. ', '27. ', '29. ')):
            story.append(PageBreak())
        else:
            story.extend([CondPageBreak(190),Spacer(1,23)])
        p=Paragraph(inline(title),styles['h1']);p.chapter=title;story.append(p)
    elif block.startswith('### '):
        story.append(Paragraph(inline(block[4:]),styles['h2']))
    elif block.startswith('- '):
        for line in block.splitlines():
            assert line.startswith('- '),line
            story.append(Paragraph(inline(line[2:]),styles['bullet'],bulletText='•'))
    elif re.match(r'^\d+\. ',block):
        for line in block.splitlines():
            n,text=line.split('. ',1)
            story.append(Paragraph(inline(text),styles['bullet'],bulletText=n+'.'))
    else:
        story.append(Paragraph(inline(block.replace('\n',' ')),styles['body']))
doc.multiBuild(story,onFirstPage=cover,onLaterPages=bodypage)
print(OUT)
