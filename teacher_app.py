import calendar
from datetime import date, datetime
import urllib.parse  # لاستخدامها في تشفير النص لرابط الواتساب
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="Teacher application",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🌐 تطبيق الاتجاه من اليمين إلى اليسار (RTL) وتنسيق الهيدر والفوتر
st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            direction: rtl;
            text-align: right;
        }
        section[data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }
        .stTextInput, .stSelectbox, .stNumberInput, .stDateInput {
            direction: rtl;
            text-align: right;
        }
        .logo-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 10px;
        }
        .logo-text {
            font-size: 32px;
            font-weight: bold;
            color: #0088cc;
            font-family: Arial, sans-serif;
        }
        .app-title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin-top: 5px;
            margin-bottom: 20px;
            color: #333333;
        }
        .pay-badge-monthly {
            background-color: #e3f2fd;
            color: #0d47a1;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
        }
        .pay-badge-session {
            background-color: #e8f5e9;
            color: #1b5e20;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
        }
        .footer-container {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e6e6e6;
            text-align: center;
            font-size: 14px;
            color: #666666;
            direction: ltr;
        }
        .footer-container a {
            color: #0088cc;
            text-decoration: none;
            font-weight: bold;
        }
        .footer-container a:hover {
            text-decoration: underline;
        }
        /* تنسيق زر الواتساب */
        .whatsapp-btn {
            background-color: #25D366;
            color: white !important;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
            text-align: center;
        }
        .whatsapp-btn:hover {
            background-color: #1da851;
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_footer():
  st.markdown(
      """
        <div class="footer-container">
            <p style="margin-bottom: 5px;">© tech-builder</p>
            <p><a href="mailto:support@tech-builder.uk">support@tech-builder.uk</a></p>
        </div>
        """,
      unsafe_allow_html=True,
  )


# ---------------------------------------------------------
# 2. إعدادات الاتصال بـ Supabase
# ---------------------------------------------------------
SUPABASE_URL = "https://qzwtydeouokiyzvmwomt.supabase.co"
SUPABASE_KEY = "sb_publishable_ZX1OTDet7YD6-VWa5OiBJg_Jx_Zz4Rm"


@st.cache_resource
def init_supabase():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase: Client = init_supabase()

ADMIN_PASSWORD = "admin_tech_builder_2026"
LOGO_URL = "https://i.ibb.co/Tx4d7kwX/image.png"

# ---------------------------------------------------------
# 3. إدارة الجلسة (Session State)
# ---------------------------------------------------------
if "user" not in st.session_state:
  st.session_state.user = None


# ---------------------------------------------------------
# 4. شاشة تسجيل الدخول + لوحة الأدمن
# ---------------------------------------------------------
def login_screen():
  col1, col2, col3 = st.columns([1, 2, 1])

  with col2:
    st.markdown(
        f"""
            <div class="logo-header">
                <img src="{LOGO_URL}" width="70" style="vertical-align: middle;">
                <span class="logo-text">Tech Builder</span>
            </div>
            """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="app-title">Teacher application</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    tab_login, tab_admin = st.tabs(["دخول المعلمين 👤", "لوحة الإدارة 🛠️"])

    with tab_login:
      st.markdown("##### تسجيل الدخول للحساب")
      username = st.text_input("اسم المستخدم:")
      password = st.text_input("كلمة المرور:", type="password")

      if st.button("دخول 🚪", use_container_width=True):
        if username and password:
          res = (
              supabase.table("users")
              .select("*")
              .eq("username", username.strip())
              .eq("password_hash", password.strip())
              .execute()
          )
          if res.data:
            st.session_state.user = res.data[0]
            st.success(f"مرحباً بك أستاذ {res.data[0]['teacher_name']}!")
            st.rerun()
          else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
        else:
          st.warning("يرجى إدخال اسم المستخدم وكلمة المرور.")

    with tab_admin:
      st.markdown("##### إدارة حسابات المعلمين (خاص بالجهة المنفذة)")
      admin_pass = st.text_input(
          "كلمة مرور الأدمن:", type="password", key="admin_pass_key"
      )

      if admin_pass == ADMIN_PASSWORD:
        st.success("تم التحقق من هويّة الأدمن ✅")

        st.markdown("###### ➕ إضافة معلم جديد")
        new_teacher = st.text_input("اسم المعلم الكامل (اللقب):")
        new_user = st.text_input("اسم المستخدم الجديد للعميل:")
        new_pass = st.text_input(
            "كلمة المرور للعميل:", type="password", key="new_user_pass_key"
        )

        if st.button("➕ إنشاء حساب للعميل", use_container_width=True):
          if new_teacher and new_user and new_pass:
            try:
              supabase.table("users").insert({
                  "username": new_user.strip(),
                  "password_hash": new_pass.strip(),
                  "teacher_name": new_teacher.strip(),
              }).execute()
              st.success(f"تم إنشاء حساب المعلم '{new_teacher}' بنجاح!")
              st.rerun()
            except Exception as e:
              st.error(f"حدث خطأ أثناء الإنشاء: {e}")
          else:
            st.warning("يرجى استكمال جميع البيانات المطلوبة.")

        st.markdown("---")
        st.markdown("###### 🗑️ حذف حساب معلم")
        res_users = supabase.table("users").select("*").execute()
        if res_users.data:
          df_users = pd.DataFrame(res_users.data)
          user_to_delete = st.selectbox(
              "اختر المعلم المراد حذفه:",
              df_users["teacher_name"].tolist(),
              key="del_user_select",
          )

          if st.button("❌ حذف المعلم نهائياً", use_container_width=True):
            user_id_del = int(
                df_users[df_users["teacher_name"] == user_to_delete][
                    "id"
                ].values[0]
            )

            supabase.table("attendance").delete().eq(
                "user_id", user_id_del
            ).execute()
            supabase.table("students").delete().eq(
                "user_id", user_id_del
            ).execute()
            supabase.table("groups").delete().eq(
                "user_id", user_id_del
            ).execute()
            supabase.table("users").delete().eq("id", user_id_del).execute()

            st.success(
                f"تم حذف حساب المعلم '{user_to_delete}' وجميع بياناته بنجاح!"
            )
            st.rerun()
        else:
          st.info("لا يوجد مستخدمون حالياً.")

      elif admin_pass:
        st.error("كلمة مرور الأدمن غير صحيحة.")

    st.markdown(
        """
            <br><hr>
            <center>
                <p style='font-size: 15px; margin-bottom: 8px;'>للحصول على حساب جديد أو تجديد الاشتراك، يرجى التواصل مع <b>(Tech Builder)</b></p>
                <p style='font-size: 17px; font-weight: bold; color: #0088cc; direction: ltr; margin: 0;'>
                    💬 WhatsApp: <span style='color: #25D366;'>+20 121 850 5995</span>
                </p>
            </center>
            """,
        unsafe_allow_html=True,
    )

  render_footer()


if not st.session_state.user:
  login_screen()
  st.stop()

# ---------------------------------------------------------
# 5. البيانات الخاصة بالمعلم الحالي
# ---------------------------------------------------------
current_user_id = st.session_state.user["id"]
teacher_display_name = st.session_state.user["teacher_name"]

# ---------------------------------------------------------
# 6. القائمة الجانبية
# ---------------------------------------------------------
st.sidebar.title(f"👤 مرحباً: أ/ {teacher_display_name}")
if st.sidebar.button("تسجيل الخروج 🚪", use_container_width=True):
  st.session_state.user = None
  st.rerun()

with st.sidebar.expander("🔑 تغيير كلمة المرور"):
  old_pwd = st.text_input(
      "كلمة المرور الحالية:", type="password", key="change_old_pwd"
  )
  new_pwd = st.text_input(
      "كلمة المرور الجديدة:", type="password", key="change_new_pwd"
  )
  confirm_pwd = st.text_input(
      "تأكيد كلمة المرور الجديدة:", type="password", key="change_conf_pwd"
  )

  if st.button("حفظ كلمة المرور الجديدة 💾", use_container_width=True):
    if old_pwd and new_pwd and confirm_pwd:
      if old_pwd != st.session_state.user["password_hash"]:
        st.error("كلمة المرور الحالية غير صحيحة!")
      elif new_pwd != confirm_pwd:
        st.error("كلمة المرور الجديدة غير متطابقة مع التأكيد!")
      elif len(new_pwd.strip()) < 4:
        st.error("يرجى إدخال كلمة مرور تتكون من 4 خانات على الأقل.")
      else:
        try:
          supabase.table("users").update(
              {"password_hash": new_pwd.strip()}
          ).eq("id", current_user_id).execute()
          st.session_state.user["password_hash"] = new_pwd.strip()
          st.success("تم تغيير كلمة المرور بنجاح! ✅")
        except Exception as e:
          st.error(f"حدث خطأ أثناء التحديث: {e}")
    else:
      st.warning("يرجى ملء جميع الحقول المطلوبة.")

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "انتقل إلى:",
    [
        "1️⃣ تكويد وإدارة المجموعات والطلاب",
        "2️⃣ تسجيل الحضور والدرجات والدفع",
        "3️⃣ كشف حساب طالب / مجموعة",
        "4️⃣ تقرير موقف الدفع والغياب",
        "5️⃣ تقرير النتائج الأكاديمية",
        "6️⃣ تقرير الإيرادات والتحصيلات",
    ],
)

# ---------------------------------------------------------
# الصفحة الأولى: تكويد وإدارة المجموعات والطلاب
# ---------------------------------------------------------
if menu == "1️⃣ تكويد وإدارة المجموعات والطلاب":
  st.header("⚙️ تكويد وإدارة المجموعات والطلاب")

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("➕ إضافة مجموعة جديدة")
    new_group = st.text_input("اسم المجموعة:")
    if st.button("حفظ المجموعة"):
      if new_group.strip():
        try:
          supabase.table("groups").insert({
              "user_id": current_user_id,
              "group_name": new_group.strip(),
          }).execute()
          st.success(f"تمت إضافة المجموعة '{new_group}' بنجاح!")
          st.rerun()
        except Exception as e:
          st.error(f"حدث خطأ أثناء إضافة المجموعة: {e}")
      else:
        st.warning("يرجى إدخال اسم المجموعة.")

  with col2:
    st.subheader("➕ إضافة طالب جديد")
    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data)

    if not df_groups.empty:
      group_selected = st.selectbox(
          "اختر المجموعة:", df_groups["group_name"].tolist()
      )
      student_name = st.text_input("اسم الطالب:")
      payment_type = st.selectbox("طريقة السداد:", ["بالحصة", "شهري"])
      student_phone = st.text_input("تليفون الطالب:")
      parent_phone = st.text_input("تليفون ولي الأمر:")

      if st.button("حفظ الطالب"):
        if student_name.strip():
          try:
            group_id = int(
                df_groups[df_groups["group_name"] == group_selected][
                    "id"
                ].values[0]
            )
            supabase.table("students").insert({
                "user_id": current_user_id,
                "group_id": group_id,
                "student_name": student_name.strip(),
                "payment_type": payment_type,
                "student_phone": student_phone.strip(),
                "parent_phone": parent_phone.strip(),
            }).execute()
            st.success(f"تمت إضافة الطالب '{student_name}' بنجاح!")
            st.rerun()
          except Exception as e:
            st.error(f"حدث خطأ أثناء إضافة الطالب: {e}")
        else:
          st.warning("يرجى إدخال اسم الطالب.")
    else:
      st.info("قم بإضافة مجموعة أولاً لتمكين إضافة الطلاب.")

  st.markdown("---")

  st.subheader("🗑️ إدارة وحذف البيانات")
  del_tab1, del_tab2 = st.tabs(["حذف طالب", "حذف مجموعة كاملة"])

  with del_tab1:
    res_stds = (
        supabase.table("students")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_all_stds = pd.DataFrame(res_stds.data)
    if not df_all_stds.empty:
      std_to_del = st.selectbox(
          "اختر الطالب للمسح:",
          df_all_stds["student_name"].tolist(),
          key="del_std_select",
      )
      if st.button("حذف الطالب المحدد"):
        try:
          std_id = int(
              df_all_stds[df_all_stds["student_name"] == std_to_del][
                  "id"
              ].values[0]
          )
          supabase.table("attendance").delete().eq(
              "student_id", std_id
          ).execute()
          supabase.table("students").delete().eq("id", std_id).execute()
          st.success(f"تم حذف الطالب '{std_to_del}' بنجاح!")
          st.rerun()
        except Exception as e:
          st.error(f"حدث خطأ أثناء حذف الطالب: {e}")
    else:
      st.info("لا يوجد طلاب لحذفهم.")

  with del_tab2:
    if not df_groups.empty:
      grp_to_del = st.selectbox(
          "اختر المجموعة للمسح:",
          df_groups["group_name"].tolist(),
          key="del_grp_select",
      )
      if st.button("حذف المجموعة وكل طلابها"):
        try:
          grp_id = int(
              df_groups[df_groups["group_name"] == grp_to_del]["id"].values[0]
          )
          supabase.table("attendance").delete().eq("group_id", grp_id).execute()
          supabase.table("students").delete().eq("group_id", grp_id).execute()
          supabase.table("groups").delete().eq("id", grp_id).execute()
          st.success(f"تم حذف المجموعة '{grp_to_del}' بنجاح!")
          st.rerun()
        except Exception as e:
          st.error(f"حدث خطأ أثناء حذف المجموعة: {e}")
    else:
      st.info("لا توجد مجموعات لحذفها.")

  st.markdown("---")
  st.subheader("📋 قائمة المجموعات والطلاب المسجلين حالياً")
  res_full = (
      supabase.table("students")
      .select(
          "id, student_name, payment_type, student_phone, parent_phone,"
          " groups(group_name)"
      )
      .eq("user_id", current_user_id)
      .execute()
  )
  if res_full.data:
    formatted_data = []
    for item in res_full.data:
      formatted_data.append({
          "ID": item.get("id"),
          "اسم الطالب": item.get("student_name"),
          "المجموعة": (
              item["groups"]["group_name"] if item.get("groups") else "-"
          ),
          "طريقة السداد": item.get("payment_type", "بالحصة"),
          "تليفون الطالب": item.get("student_phone", "-"),
          "تليفون ولي الأمر": item.get("parent_phone", "-"),
      })
    st.dataframe(pd.DataFrame(formatted_data), use_container_width=True)
  else:
    st.info("لا يوجد طلاب مسجلون بعد.")

# ---------------------------------------------------------
# الصفحة الثانية: تسجيل الحضور والدرجات والدفع
# ---------------------------------------------------------
elif menu == "2️⃣ تسجيل الحضور والدرجات والدفع":
  st.header("📝 تسجيل الحضور والدرجات والتحصيل")

  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data)

  if df_groups.empty:
    st.warning("لا توجد مجموعات معرفة. يرجى إضافة مجموعات أولاً.")
  else:
    group_selected = st.selectbox(
        "اختر المجموعة:", df_groups["group_name"].tolist()
    )
    group_id = int(
        df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
    )
    session_date = st.date_input("تاريخ الحصة:", date.today())

    res_stds = (
        supabase.table("students").select("*").eq("group_id", group_id).execute()
    )
    students_in_group = pd.DataFrame(res_stds.data)

    if students_in_group.empty:
      st.info("لا يوجد طلاب مسجلون في هذه المجموعة.")
    else:
      st.write(f"### تسجيل بيانات حصة يوم: {session_date}")

      with st.form("attendance_form"):
        records = []
        for idx, row in students_in_group.iterrows():
          pay_type = row.get("payment_type", "بالحصة")
          badge_class = (
              "pay-badge-monthly"
              if pay_type == "شهري"
              else "pay-badge-session"
          )

          st.markdown(
              f"**👤 الطالب: {row['student_name']}** &nbsp; <span"
              f" class='{badge_class}'>طريقة السداد: {pay_type}</span>",
              unsafe_allow_html=True,
          )

          c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 2])

          with c1:
            status = st.radio(
                "الحضور:", ["حضر", "غائب"], key=f"status_{row['id']}"
            )
          with c2:
            score = st.number_input(
                "درجة الطالب:",
                min_value=0.0,
                max_value=500.0,
                value=0.0,
                key=f"score_{row['id']}",
            )
          with c3:
            max_score = st.number_input(
                "الدرجة العظمى:",
                min_value=1.0,
                max_value=500.0,
                value=100.0,
                key=f"max_{row['id']}",
            )
          with c4:
            pct_calc = (score / max_score * 100) if max_score > 0 else 0
            st.markdown(
                "**النسبة:** <br><span style='font-size:18px;"
                f" color:#0088cc;'>{pct_calc:.1f}%</span>",
                unsafe_allow_html=True,
            )
          with c5:
            paid_amount = st.number_input(
                "المبلغ المسدد (جنيه):",
                min_value=0.0,
                value=0.0,
                step=10.0,
                key=f"paid_{row['id']}",
            )

          st.markdown("---")

          records.append({
              "user_id": current_user_id,
              "student_id": int(row["id"]),
              "group_id": group_id,
              "session_date": str(session_date),
              "attended": True if status == "حضر" else False,
              "score": score,
              "max_score": max_score,
              "paid": 1 if paid_amount > 0 else 0,
              "paid_amount": paid_amount,
          })

        submit = st.form_submit_button("💾 حفظ بيانات الحصة بالكامل")
        if submit:
          try:
            supabase.table("attendance").insert(records).execute()
            st.success("تم حفظ الحضور والدرجات والتحصيلات بنجاح!")
          except Exception as e:
            st.error(f"حدث خطأ أثناء حفظ الحضور: {e}")

# ---------------------------------------------------------
# الصفحة الثالثة: كشف حساب طالب / مجموعة
# ---------------------------------------------------------
elif menu == "3️⃣ كشف حساب طالب / مجموعة":
  st.header("🔍 كشف حضور ودرجات ودفع الطلاب")

  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data)

  if not df_groups.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
      group_selected = st.selectbox(
          "اختر المجموعة:", df_groups["group_name"].tolist()
      )
      group_id = int(
          df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
      )
    with col2:
      start_date = st.date_input("من تاريخ:", date(2026, 1, 1))
    with col3:
      end_date = st.date_input("إلى تاريخ:", date.today())

    res_att = (
        supabase.table("attendance")
        .select("*, students(student_name, payment_type)")
        .eq("group_id", group_id)
        .gte("session_date", str(start_date))
        .lte("session_date", str(end_date))
        .execute()
    )

    if res_att.data:
      report_rows = []
      for item in res_att.data:
        std_info = item.get("students") or {}
        sc = item.get("score", 0)
        mx = item.get("max_score", 100)
        pct = (sc / mx * 100) if mx and mx > 0 else 0

        report_rows.append({
            "تاريخ الحصة": item.get("session_date"),
            "اسم الطالب": std_info.get("student_name", "-"),
            "طريقة السداد": std_info.get("payment_type", "بالحصة"),
            "حالة الحضور": "حضر ✅" if item.get("attended") else "غائب ❌",
            "الدرجة": f"{sc} / {mx}",
            "النسبة المئوية": f"{pct:.1f}%",
            "حالة الدفع": (
                "تم الدفع ✅"
                if item.get("paid_amount", 0) > 0 or item.get("paid") == 1
                else "لم يدفع ❌"
            ),
            "المبلغ المدفوع": f"{item.get('paid_amount', 0)} جنيه",
        })
      st.dataframe(pd.DataFrame(report_rows), use_container_width=True)
    else:
      st.info("لا توجد سجلات حضور لهذه المجموعة خلال الفترة المحددة.")
  else:
    st.info("لا توجد مجموعات معرفة.")

# ---------------------------------------------------------
# الصفحة الرابعة: تقرير موقف الدفع والغياب
# ---------------------------------------------------------
elif menu == "4️⃣ تقرير موقف الدفع والغياب":
  st.header("📊 تقرير سداد المصروفات وعدد مرات الغياب")

  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data)

  if not df_groups.empty:
    c1, c2, c3 = st.columns(3)
    with c1:
      group_selected = st.selectbox(
          "اختر المجموعة للتقرير:", df_groups["group_name"].tolist()
      )
      group_id = int(
          df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
      )
    with c2:
      start_date = st.date_input("من تاريخ:", date(2026, 1, 1), key="rep4_start")
    with c3:
      end_date = st.date_input("إلى تاريخ:", date.today(), key="rep4_end")

    res_stds = (
        supabase.table("students")
        .select("*")
        .eq("group_id", group_id)
        .execute()
    )
    df_stds = pd.DataFrame(res_stds.data)

    if not df_stds.empty:
      report_list = []
      for _, std in df_stds.iterrows():
        res_att = (
            supabase.table("attendance")
            .select("*")
            .eq("student_id", std["id"])
            .gte("session_date", str(start_date))
            .lte("session_date", str(end_date))
            .execute()
        )
        att_data = res_att.data or []

        total_sessions = len(att_data)
        absent_count = sum([1 for r in att_data if not r.get("attended")])
        total_paid = sum([r.get("paid_amount", 0) for r in att_data])
        paid_sessions_count = sum([
            1
            for r in att_data
            if r.get("paid_amount", 0) > 0 or r.get("paid") == 1
        ])

        report_list.append({
            "اسم الطالب": std["student_name"],
            "طريقة السداد": std.get("payment_type", "بالحصة"),
            "إجمالي الحصص": total_sessions,
            "عدد مرات الغياب ❌": absent_count,
            "عدد مرات السداد": paid_sessions_count,
            "إجمالي المبالغ المسددة": f"{total_paid} جنيه",
            "موقف الدفع": (
                "مسدد ✅" if paid_sessions_count > 0 else "غير مسدد ❌"
            ),
        })
      st.dataframe(pd.DataFrame(report_list), use_container_width=True)
    else:
      st.info("لا يوجد طلاب في هذه المجموعة.")

# ---------------------------------------------------------
# الصفحة الخامسة: تقرير النتائج الأكاديمية (معدّل ومزود بخاصية إرسال الواتساب)
# ---------------------------------------------------------
elif menu == "5️⃣ تقرير النتائج الأكاديمية":
  st.header("📈 تقرير النتائج الأكاديمية وتقرير ولي الأمر")

  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data)

  if not df_groups.empty:
    c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1.5])
    with c1:
      group_selected = st.selectbox(
          "اختر المجموعة:", df_groups["group_name"].tolist()
      )
      group_id = int(
          df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
      )

    # جلب الطلاب التابعين للمجموعة لإضافتهم في القائمة
    res_stds = (
        supabase.table("students")
        .select("*")
        .eq("group_id", group_id)
        .execute()
    )
    df_stds = pd.DataFrame(res_stds.data)

    with c2:
      student_options = ["الكل"]
      if not df_stds.empty:
        student_options += df_stds["student_name"].tolist()
      selected_student = st.selectbox("اختر الطالب:", student_options)

    with c3:
      start_date = st.date_input("من تاريخ:", date(2026, 1, 1), key="res_start")
    with c4:
      end_date = st.date_input("إلى تاريخ:", date.today(), key="res_end")

    # جلب بيانات الحضور والدرجات
    res_att = (
        supabase.table("attendance")
        .select(
            "session_date, attended, score, max_score, student_id,"
            " students(student_name, parent_phone)"
        )
        .eq("group_id", group_id)
        .gte("session_date", str(start_date))
        .lte("session_date", str(end_date))
        .execute()
    )

    if res_att.data:
      raw_data = []
      for r in res_att.data:
        std_info = r.get("students") or {}
        std_name = std_info.get("student_name", "غير معروف")

        # الفلترة بحسب الطالب في حال لم يكن الخيار "الكل"
        if selected_student != "الكل" and std_name != selected_student:
          continue

        sc = r.get("score", 0)
        mx = r.get("max_score", 100)
        pct = (sc / mx * 100) if mx and mx > 0 else 0

        res_str = (
            f"✅ حضر ({sc}/{mx} - {pct:.0f}%)" if r.get("attended") else "❌ غائب"
        )

        raw_data.append({
            "اسم الطالب": std_name,
            "تاريخ الحصة": r.get("session_date"),
            "النتيجة": res_str,
            "حضر": r.get("attended"),
            "الدرجة": sc,
            "الدرجة العظمى": mx,
        })

      if raw_data:
        df_raw = pd.DataFrame(raw_data)

        # 🟢 إذا كان العرض لجميع الطلاب (جدول شبكي مفصل)
        if selected_student == "الكل":
          pivot_df = df_raw.pivot_table(
              index="اسم الطالب",
              columns="تاريخ الحصة",
              values="النتيجة",
              aggfunc="first",
          ).fillna("غير مسجل")
          st.dataframe(pivot_df, use_container_width=True)

        # 🟢 إذا تم اختيار طالب محدد (تفاصيل الطالب + زر الواتساب)
        else:
          st.markdown("---")
          std_row = df_stds[df_stds["student_name"] == selected_student].iloc[0]
          parent_phone = str(std_row.get("parent_phone", "")).strip()

          col_info1, col_info2 = st.columns(2)
          with col_info1:
            st.subheader(f"👤 تقرير الطالب: {selected_student}")
            st.write(
                f"📱 **تليفون ولي الأمر:** {parent_phone if parent_phone else 'غير مسجل'}"
            )

          # حساب الإحصائيات العامة للطالب
          total_sessions = len(df_raw)
          attended_count = sum(df_raw["حضر"])
          absent_count = total_sessions - attended_count
          total_score = df_raw[df_raw["حضر"]]["الدرجة"].sum()
          total_max = df_raw[df_raw["حضر"]]["الدرجة العظمى"].sum()
          overall_pct = (
              (total_score / total_max * 100) if total_max > 0 else 0
          )

          with col_info2:
            st.metric("عدد الحصص", f"{total_sessions}")
            st.metric("عدد مرات الغياب", f"{absent_count}")
            st.metric("المعدل الأكاديمي", f"{overall_pct:.1f}%")

          st.write("#### 📋 تفاصيل الحصص خلال الفترة:")
          st.dataframe(
              df_raw[["تاريخ الحصة", "النتيجة"]], use_container_width=True
          )

          # 📲 تجهيز رسالة الواتساب وزر الإرسال
          if parent_phone:
            # تنظيف وتنسيق الرقم ليقبل كود الدولة (افتراضياً مصر +20 إذا لم يذكر)
            formatted_phone = parent_phone.replace(" ", "").replace("-", "")
            if formatted_phone.startswith("01"):
              formatted_phone = "20" + formatted_phone[1:]
            elif formatted_phone.startswith("+"):
              formatted_phone = formatted_phone.replace("+", "")

            # تجهيز نص التقرير للرسالة
            msg_text = (
                f"السلام عليكم ورحمة الله وبركاته،\n"
                f"تقرير متابعة الطالب: *{selected_student}*\n"
                f"الفترة من: {start_date} إلى {end_date}\n\n"
                f"📌 *ملخص الأداء:*\n"
                f"• إجمالي الحصص: {total_sessions}\n"
                f"• عدد مرات الحضور: {attended_count}\n"
                f"• عدد مرات الغياب: {absent_count}\n"
                f"• المستوى الأكاديمي العام: {overall_pct:.1f}%\n\n"
                f"مع تحيات الأستاذ: {teacher_display_name}"
            )

            encoded_msg = urllib.parse.quote(msg_text)
            wa_url = (
                f"https://wa.me/{formatted_phone}?text={encoded_msg}"
            )

            st.markdown(
                f"""
                <center>
                    <a href="{wa_url}" target="_blank" class="whatsapp-btn">
                        📲 إرسال هذا التقرير عبر WhatsApp لولي الأمر
                    </a>
                </center>
                """,
                unsafe_allow_html=True,
            )
          else:
            st.warning(
                "⚠️ لم يتم تسجيل رقم هاتف ولي الأمر لهذا الطالب في شاشة"
                " التكويد."
            )

      else:
        st.info("لا توجد سجلات لهذا الطالب في الفترة المحسوبة.")
    else:
      st.info("لا توجد حصص مسجلة لهذه المجموعة في الفترة المحددة.")
  else:
    st.info("لا توجد مجموعات معرفة.")

# ---------------------------------------------------------
# الصفحة السادسة: تقرير الإيرادات والتحصيلات الشهرية
# ---------------------------------------------------------
elif menu == "6️⃣ تقرير الإيرادات والتحصيلات":
  st.header("💰 تقرير الإيرادات الشهرية حسب المجموعات")

  c1, c2 = st.columns(2)
  months_arabic = [
      "يناير",
      "فبراير",
      "مارس",
      "أبريل",
      "مايو",
      "يونيو",
      "يوليو",
      "أغسطس",
      "سبتمبر",
      "أكتوبر",
      "نوفمبر",
      "ديسمبر",
  ]

  with c1:
    selected_month_num = st.selectbox(
        "اختر الشهر:",
        range(1, 13),
        format_func=lambda x: f"{x} - {months_arabic[x-1]}",
    )
  with c2:
    selected_year = st.number_input(
        "اختر السنة:", min_value=2024, max_value=2030, value=2026
    )

  _, last_day = calendar.monthrange(selected_year, selected_month_num)
  start_date_str = f"{selected_year}-{selected_month_num:02d}-01"
  end_date_str = f"{selected_year}-{selected_month_num:02d}-{last_day:02d}"

  res_att = (
      supabase.table("attendance")
      .select("paid_amount, groups(group_name)")
      .eq("user_id", current_user_id)
      .gte("session_date", start_date_str)
      .lte("session_date", end_date_str)
      .execute()
  )

  if res_att.data:
    df_rev = pd.DataFrame(res_att.data)
    df_rev["المجموعة"] = df_rev["groups"].apply(
        lambda x: x["group_name"] if x else "غير محدد"
    )
    df_rev["paid_amount"] = df_rev["paid_amount"].fillna(0)

    summary = (
        df_rev.groupby("المجموعة")["paid_amount"]
        .sum()
        .reset_index(name="إيراد المجموعة (جنيه)")
    )
    total_revenue = summary["إيراد المجموعة (جنيه)"].sum()

    if total_revenue > 0:
      summary["نسبة الإيراد من الإجمالي"] = summary[
          "إيراد المجموعة (جنيه)"
      ].apply(lambda x: f"{(x / total_revenue * 100):.1f}%")

      total_row = pd.DataFrame([{
          "المجموعة": "🔴 الإجمالي الكلي",
          "إيراد المجموعة (جنيه)": total_revenue,
          "نسبة الإيراد من الإجمالي": "100%",
      }])

      summary_final = pd.concat([summary, total_row], ignore_index=True)

      st.dataframe(summary_final, use_container_width=True)
      st.metric("إجمالي التحصيلات لهذا الشهر", f"{total_revenue} جنيه")
    else:
      st.info("لا توجد تحصيلات مالية مدفوعة في هذا الشهر.")
  else:
    st.info("لا توجد تحصيلات مالية مدفوعة في هذا الشهر.")

# ---------------------------------------------------------
# عرض الفوتر أسفل جميع الصفحات
# ---------------------------------------------------------
render_footer()
