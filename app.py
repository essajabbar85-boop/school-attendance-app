import csv
from datetime import datetime
import io
import os
import streamlit as st

# مكتبات المعالجة العربية
import arabic_reshaper
from bidi.algorithm import get_display
# مكتبات ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, TableStyle

# إعدادات الصفحة
st.set_page_config(
    page_title="ثانوية خير الأنام للبنين - سجل الحضور",
    layout="centered"
)

# ==========================================
#  تنسيق اتجاه الصفحة والمكونات من اليمين إلى اليسار (RTL)
# ==========================================
st.markdown("""
    <style>
    /* جعل اتجاه الصفحة والنصوص من اليمين إلى اليسار */
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* محاذاة العناوين والأزرار والأعمدة */
    .stButton > button {
        width: 100%;
    }
    
    /* ضبط اتجاه ترتيب أعمدة Streamlit */
    [data-testid="column"] {
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)


def ar(text):
  if not text or text == "-":
    return text
  reshaped = arabic_reshaper.reshape(str(text))
  return get_display(reshaped)


def get_arabic_day_name(day_name_en):
  days_map = {
      "Saturday": "السبت",
      "Sunday": "الأحد",
      "Monday": "الإثنين",
      "Tuesday": "الثلاثاء",
      "Wednesday": "الأربعاء",
      "Thursday": "الخميس",
      "Friday": "الجمعة",
  }
  return days_map.get(day_name_en, day_name_en)


# قائمة المدرسين
teachers_list = [
    "عيسى عبد الجبار إبراهيم",
    "نيزك مهند محمد",
    "ياسين خضير علي",
    "شاكر محمود نصار",
    "مصطفى عبد الستار مولى",
    "علي طه كريم",
    "محمد جواد كاظم",
    "مها خالد غازي",
    "أحمد محسن ساجت",
    "يحيى ثامر محمد",
    "مصطفى ثامر محمد",
    "ثامر حمزة علي",
    "وليد خالد أحمد",
    "مهند سعدون إسماعيل",
    "وسام حكيم شرقي",
    "محمد طارق ناجي",
    "أحمد صاحب محمود",
    "مشعان حاتم علي",
    "مها داود عبيس",
    "مصطفى ماجد محمود",
    "رأفت عدنان إرحيم",
    "حسين عبد الرحمن صبر",
    "هيثم طالب شهاب",
    "أماني باسم علي",
    "حسين عدنان جياد",
    "هيثم جواد كاظم",
    "نور محمد حسن حسين",
    "محمد عبد الفتاح رحيم",
    "أحمد صباح إبراهيم",
    "ياسر محمود مجبل",
    "غيث عبد الخضر عباس",
    "عبد الله حكمت سعدون",
    "أسامة محمود نصار",
    "مروان إبراهيم ماجد",
    "غفران رحمن حسين",
    "دعاء يونس محمود",
    "حيدر عبد الجاسم لفته",
    "زينب عامر سعيد",
]

# تهيئة حالة الحضور
if "attendance" not in st.session_state:
  st.session_state.attendance = {}

st.title("🏫 ثانوية خير الأنام للبنين")
st.subheader("سجل الحضور والغياب اليومي")
st.write("---")

# عرض جدول تسجيل الحضور مرتباً من اليمين إلى اليسار (ت - اسم المدرس - أزرار التسجيل)
for idx, name in enumerate(teachers_list, 1):
  col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 2])
  
  col1.write(f"**{idx}**")
  col2.write(f"**{name}**")

  if col3.button("حضور", key=f"in_{idx}"):
    st.session_state.attendance[name] = (
        "حضور",
        datetime.now().strftime("%I:%M:%S %p"),
    )
    st.success(f"تم تسجيل حضور: {name}")

  if col4.button("انصراف", key=f"out_{idx}"):
    st.session_state.attendance[name] = (
        "انصراف",
        datetime.now().strftime("%I:%M:%S %p"),
    )
    st.warning(f"تم تسجيل انصراف: {name}")

  if col5.button("إجازة", key=f"leave_{idx}"):
    st.session_state.attendance[name] = (
        "إجازة",
        datetime.now().strftime("%I:%M:%S %p"),
    )
    st.info(f"تم تسجيل إجازة: {name}")


# دالة إنشاء الـ PDF
def generate_pdf():
  buffer = io.BytesIO()
  now = datetime.now()
  today_str = now.strftime("%Y-%m-%d")

  # تسجيل الخط العربي المحلي
  font_filename = "arabic_font.ttf"
  if os.path.exists(font_filename):
    pdfmetrics.registerFont(TTFont("CustomArabicFont", font_filename))
    pdf_font = "CustomArabicFont"
  else:
    pdf_font = "Helvetica"

  elements = []
  if os.path.exists("logo.png"):
    img = Image("logo.png", width=42, height=42)
    img.hAlign = "CENTER"
    elements.append(img)

  styles = getSampleStyleSheet()
  style_school = ParagraphStyle(
      "SchoolHeader",
      parent=styles["Normal"],
      fontName=pdf_font,
      fontSize=13,
      leading=15,
      textColor=colors.HexColor("#B8860B"),
      alignment=1,
  )
  style_title = ParagraphStyle(
      "TitleHeader",
      parent=styles["Normal"],
      fontName=pdf_font,
      fontSize=12,
      leading=14,
      textColor=colors.HexColor("#002B66"),
      alignment=1,
  )
  style_date = ParagraphStyle(
      "DateHeader",
      parent=styles["Normal"],
      fontName=pdf_font,
      fontSize=11,
      leading=13,
      textColor=colors.HexColor("#002B66"),
      alignment=1,
  )

  day_ar = get_arabic_day_name(now.strftime("%A"))
  date_formatted = f"{now.year}/{now.month}/{now.day}"

  elements.append(Paragraph(ar("ثانوية خير الأنام للبنين"), style_school))
  elements.append(Paragraph(ar("سجل الحضور"), style_title))
  elements.append(
      Paragraph(ar(f"{day_ar} {date_formatted}"), style_date)
  )

  table_data = [
      [ar("الوقت"), ar("الحالة"), ar("التاريخ"), ar("اسم المدرس"), ar("ت")]
  ]
  style_cmds = [
      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4169E1")),
      ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
      ("ALIGN", (0, 0), (-1, -1), "CENTER"),
      ("FONTNAME", (0, 0), (-1, -1), pdf_font),
      ("FONTSIZE", (0, 0), (-1, -1), 9),
      ("TOPPADDING", (0, 0), (-1, -1), 2.8),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 2.8),
      ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F4F8")),
      ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1D3557")),
  ]

  for idx, name in enumerate(teachers_list, 1):
    if name in st.session_state.attendance:
      status, time_val = st.session_state.attendance[name]
      status_display = ar(status)
    else:
      status_display = ar("غ")
      time_val = "-"
      row_index = len(table_data)
      style_cmds.append(
          ("TEXTCOLOR", (1, row_index), (1, row_index), colors.red)
      )

    table_data.append(
        [ar(time_val), status_display, ar(today_str), ar(name), ar(str(idx))]
    )

  doc = SimpleDocTemplate(
      buffer,
      pagesize=A4,
      rightMargin=15,
      leftMargin=15,
      topMargin=12,
      bottomMargin=12,
  )
  table = Table(table_data, colWidths=[90, 65, 90, 230, 30])
  table.setStyle(TableStyle(style_cmds))
  elements.append(table)

  doc.build(elements)
  buffer.seek(0)
  return buffer


st.write("---")
pdf_file_buffer = generate_pdf()

st.download_button(
    label="📄 تصدير وتحميل تقرير الـ PDF",
    data=pdf_file_buffer,
    file_name=f"تقرير_الحضور_{datetime.now().strftime('%Y-%m-%d')}.pdf",
    mime="application/pdf",
)
