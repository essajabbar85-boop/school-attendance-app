from datetime import datetime
import io
import os
import urllib.request
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
    layout="centered",
    initial_sidebar_state="collapsed",
)

# تنسيقات CSS لمنع تكديس العناصر ولتحسين العرض على الموبايل
st.markdown(
    """
    <style>
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* منع تكديس الأعمدة بطريقة مشوهة في الهواتف */
    [data-testid="stHorizontalBlock"] {
        align-items: center;
        gap: 0.3rem !important;
    }
    
    /* تحسين حجم الأزرار وتراصفها */
    .stButton > button {
        width: 100%;
        padding: 4px 8px;
        font-size: 13px;
        border-radius: 6px;
    }
    
    /* بطاقة لكل مدرس */
    .teacher-card {
        background-color: #f8f9fa;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-right: 4px solid #4169E1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    [data-testid="column"] {
        text-align: right;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# تنزيل خط عربي صحيح تلقائياً للـ PDF
FONT_PATH = "Amiri-Regular.ttf"
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Regular.ttf"

if not os.path.exists(FONT_PATH):
  try:
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)
  except Exception:
    pass


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

if "attendance" not in st.session_state:
  st.session_state.attendance = {}

# العنوان الرئيسي
st.markdown(
    "<h2 style='text-align: center; color: #1D3557;'>🏫 ثانوية خير الأنام"
    " للبنين</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h4 style='text-align: center; color: #457B9D;'>سجل الحضور والغياب"
    " اليومي</h4>",
    unsafe_allow_html=True,
)
st.write("---")

# عرض القائمة بتصميم بطاقات متجاوب للموبايل
for idx, name in enumerate(teachers_list, 1):
  status_info = st.session_state.attendance.get(name, None)
  status_text = f" | <b>الحالة:</b> {status_info[0]}" if status_info else ""

  st.markdown(
      f"<div class='teacher-card'><b>{idx}. {name}</b>{status_text}</div>",
      unsafe_allow_html=True,
  )

  c1, c2, c3 = st.columns(3)

  if c1.button("✅ حضور", key=f"in_{idx}"):
    st.session_state.attendance[name] = (
        "حضور",
        datetime.now().strftime("%I:%M:%S %p"),
    )
    st.rerun()

  if c2.button("🏃 انصراف", key=f"out_{idx}"):
    st.session_state.attendance[name] = (
        "انصراف",
        datetime.now().strftime("%I:%M:%S %p"),
    )
    st.rerun()

  if c3.button("📝 إجازة", key=f"leave_{idx}"):
    st.session_state.attendance[name] = (
        "إجازة",
        datetime.now().strftime("%I:%M:%S %p"),
    )
    st.rerun()


# دالة إنشاء ملف الـ PDF
def generate_pdf():
  buffer = io.BytesIO()
  now = datetime.now()
  today_str = now.strftime("%Y-%m-%d")

  if os.path.exists(FONT_PATH):
    try:
      pdfmetrics.registerFont(TTFont("ArabicFont", FONT_PATH))
      pdf_font = "ArabicFont"
    except Exception:
      pdf_font = "Helvetica"
  else:
    pdf_font = "Helvetica"

  elements = []

  logo_path = "logo.png"
  if os.path.exists(logo_path):
    img = Image(logo_path, width=42, height=42)
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