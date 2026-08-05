import calendar
from datetime import date, datetime
import urllib.parse
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتنسيق RTL
# ---------------------------------------------------------
st.set_page_config(
    page_title="Teacher application",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        html, body, [class*="css"] { direction: rtl; text-align: right; }
        section[data-testid="stSidebar"] { direction: rtl; text-align: right; }
        .stTextInput, .stSelectbox, .stNumberInput, .stDateInput { direction: rtl; text-align: right; }
        .logo-header { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 10px; }
        .logo-text { font-size: 32px; font-weight: bold; color: #0088cc; font-family: Arial, sans-serif; }
        .app-title { text-align: center; font-size: 28px; font-weight: bold; margin-top: 5px; margin-bottom: 20px; color: #ffffff; }
        .footer-container { margin-top: 50px; padding-top: 20px; border-top: 1px solid #333333; text-align: center; font-size: 14px; color: #888888; direction: ltr; }
        .footer-container a { color: #0088cc; text-decoration: none; font-weight: bold; }
        .whatsapp-btn { background-color: #25D366; color: white !important; padding: 6px 14px; font-weight: bold; border-radius: 6px; text-decoration: none; display: inline-block; text-align: center; font-size: 13px; }
        .whatsapp-btn:hover { background-color: #1da851; color: white !important; }
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

    tab_login, tab_admin = st.tabs(["دخول المستخدمين 👤", "لوحة الإدارة 🛠️"])

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
            role_title = (
                "أستاذ"
                if res.data[0].get("role", "teacher") == "teacher"
                else "مساعد أ/"
            )
            st.success(
                f"مرحباً بك {role_title} {res.data[0]['teacher_name']}!"
            )
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

        # عرض كشف بجميع الحسابات المسجلة
        st.markdown("###### 🔑 قائمة الحسابات وكلمات المرور المسجلة:")
        res_all_users = supabase.table("users").select("*").execute()
        if res_all_users.data:
          users_list = []
          for u in res_all_users.data:
            role_str = (
                "معلم رئيسي 👑"
                if u.get("role") == "teacher"
                else "مساعد معلم 🛠️"
            )
            users_list.append({
                "الاسم الظاهر": u.get("teacher_name", "-"),
                "اسم المستخدم": u.get("username", "-"),
                "كلمة المرور 🔑": u.get("password_hash", "-"),
                "نوع الحساب": role_str,
            })
          st.dataframe(pd.DataFrame(users_list), use_container_width=True)
        else:
          st.info("لا توجد حسابات مسجلة حالياً.")

        st.markdown("---")

        # ---------------------------------------------------------
        # ميزة جديدة: تعديل الاسم الظاهر واسم المستخدم لأي حساب
        # ---------------------------------------------------------
        st.markdown(
            "###### ✏️ تعديل بيانات حساب (الاسم الظاهر / اسم المستخدم)"
        )
        if res_all_users.data:
          df_all_users = pd.DataFrame(res_all_users.data)
          selected_user_to_edit = st.selectbox(
              "اختر الحساب المراد تعديل بياناته:",
              df_all_users["teacher_name"].tolist(),
              key="admin_edit_user_select",
          )

          user_data = df_all_users[
              df_all_users["teacher_name"] == selected_user_to_edit
          ].iloc[0]

          edit_teacher_name = st.text_input(
              "الاسم الظاهر / الكرتي الجديد:",
              value=user_data.get("teacher_name", ""),
              key="edit_t_name",
          )
          edit_username = st.text_input(
              "اسم المستخدم الجديد للدخول:",
              value=user_data.get("username", ""),
              key="edit_u_name",
          )

          if st.button("💾 حفظ البيانات المعدلة", use_container_width=True):
            if edit_teacher_name.strip() and edit_username.strip():
              target_user_id = int(user_data["id"])

              # تحقق إذا كان اسم المستخدم الجديد مستخدماً بالفعل في حساب آخر
              if edit_username.strip() != user_data["username"]:
                chk = (
                    supabase.table("users")
                    .select("id")
                    .eq("username", edit_username.strip())
                    .execute()
                )
                if chk.data:
                  st.error(
                      f"⚠️ اسم المستخدم '{edit_username.strip()}' مأخوذ بالفعل"
                      " لحساب آخر!"
                  )
                  st.stop()

              try:
                supabase.table("users").update({
                    "teacher_name": edit_teacher_name.strip(),
                    "username": edit_username.strip(),
                }).eq("id", target_user_id).execute()
                st.success(
                    f"تم تعديل بيانات الحساب '{edit_teacher_name}' بنجاح! ✅"
                )
                st.rerun()
              except Exception as e:
                st.error(f"حدث خطأ أثناء التحديث: {e}")
            else:
              st.warning("يرجى ملء جميع الحقول المطلوب تعديلها.")
        else:
          st.info("لا توجد حسابات لتعديلها.")

        st.markdown("---")

        # ---------------------------------------------------------
        # تغيير كلمة المرور لأي حساب بواسطة الأدمن
        # ---------------------------------------------------------
        st.markdown("###### 🔑 تغيير كلمة المرور لأي حساب")
        if res_all_users.data:
          df_all_users = pd.DataFrame(res_all_users.data)
          selected_user_to_reset = st.selectbox(
              "اختر الحساب المراد تغيير كلمة المرور له:",
              df_all_users["teacher_name"].tolist(),
              key="admin_reset_user_select",
          )
          admin_new_pass = st.text_input(
              "كلمة المرور الجديدة للحساب:",
              type="password",
              key="admin_new_pass_input",
          )

          if st.button("🔄 تحديث كلمة المرور", use_container_width=True):
            if admin_new_pass.strip():
              target_user_row = df_all_users[
                  df_all_users["teacher_name"] == selected_user_to_reset
              ].iloc[0]
              target_user_id = int(target_user_row["id"])

              try:
                supabase.table("users").update(
                    {"password_hash": admin_new_pass.strip()}
                ).eq("id", target_user_id).execute()
                st.success(
                    f"تم تغيير كلمة المرور للحساب '{selected_user_to_reset}'"
                    " بنجاح! ✅"
                )
                st.rerun()
              except Exception as e:
                st.error(f"حدث خطأ أثناء التحديث: {e}")
            else:
              st.warning("يرجى إدخال كلمة المرور الجديدة.")

        st.markdown("---")
        st.markdown("###### ➕ إضافة حساب جديد")
        account_type = st.radio(
            "نوع الحساب المراد إنشاؤه:",
            ["معلم رئيسي", "مساعد للمعلم"],
            horizontal=True,
        )

        res_teachers = (
            supabase.table("users")
            .select("*")
            .eq("role", "teacher")
            .execute()
        )
        teachers_df = pd.DataFrame(res_teachers.data or [])

        parent_teacher_id = None
        if account_type == "مساعد للمعلم":
          if not teachers_df.empty:
            selected_t = st.selectbox(
                "اختر المعلم التابع له هذا المساعد:",
                teachers_df["teacher_name"].tolist(),
            )
            parent_teacher_id = int(
                teachers_df[teachers_df["teacher_name"] == selected_t][
                    "id"
                ].values[0]
            )
          else:
            st.warning("⚠️ يجب إضافة معلم رئيسي أولاً لكي تتمكن من ربط مساعد به.")

        new_teacher = st.text_input("اسم المستخدم الكرتي / الاسم الظاهر:")
        new_user = st.text_input("اسم المستخدم الجديد للدخول:")
        new_pass = st.text_input(
            "كلمة المرور:", type="password", key="new_user_pass_key"
        )

        if st.button("➕ إنشاء الحساب الآن", use_container_width=True):
          if new_teacher and new_user and new_pass:
            if account_type == "مساعد للمعلم" and not parent_teacher_id:
              st.error("يرجى اختيار معلم رئيسي للمساعد.")
            else:
              existing_user = (
                  supabase.table("users")
                  .select("id")
                  .eq("username", new_user.strip())
                  .execute()
              )

              if existing_user.data:
                st.error(
                    f"⚠️ اسم المستخدم '{new_user.strip()}' مأخوذ بالفعل! يرجى"
                    " اختيار اسم مستخدم آخر."
                )
              else:
                try:
                  role_val = (
                      "teacher" if account_type == "معلم رئيسي" else "assistant"
                  )
                  supabase.table("users").insert({
                      "username": new_user.strip(),
                      "password_hash": new_pass.strip(),
                      "teacher_name": new_teacher.strip(),
                      "role": role_val,
                      "parent_teacher_id": parent_teacher_id,
                  }).execute()
                  st.success(f"تم إنشاء حساب '{new_teacher}' بنجاح! ✅")
                  st.rerun()
                except Exception as e:
                  st.error(f"حدث خطأ أثناء الإنشاء: {e}")
          else:
            st.warning("يرجى استكمال جميع البيانات المطلوبة.")

        st.markdown("---")
        st.markdown("###### 🗑️ حذف حساب معلم أو مساعد")
        res_users = supabase.table("users").select("*").execute()
        if res_users.data:
          df_users = pd.DataFrame(res_users.data)
          user_to_delete = st.selectbox(
              "اختر الحساب المراد حذفه:",
              df_users["teacher_name"].tolist(),
              key="del_user_select",
          )

          if st.button("❌ حذف الحساب نهائياً", use_container_width=True):
            user_row = df_users[df_users["teacher_name"] == user_to_delete].iloc[
                0
            ]
            user_id_del = int(user_row["id"])

            if user_row.get("role") == "teacher":
              supabase.table("attendance").delete().eq(
                  "user_id", user_id_del
              ).execute()
              supabase.table("students").delete().eq(
                  "user_id", user_id_del
              ).execute()
              supabase.table("groups").delete().eq(
                  "user_id", user_id_del
              ).execute()
              supabase.table("users").delete().eq(
                  "parent_teacher_id", user_id_del
              ).execute()

            supabase.table("users").delete().eq("id", user_id_del).execute()
            st.success(f"تم حذف الحساب '{user_to_delete}' بنجاح!")
            st.rerun()

      elif admin_pass:
        st.error("كلمة مرور الأدمن غير صحيحة.")

    st.markdown(
        """
            <br><hr>
            <center>
                <p style='font-size: 15px; margin-bottom: 8px;'>ل للحصول على حساب جديد أو تجديد الاشتراك، يرجى التواصل مع <b>(Tech Builder)</b></p>
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
# 5. البيانات والتحكم في الصلاحيات للمستخدم الحالي
# ---------------------------------------------------------
user_role = st.session_state.user.get("role", "teacher")

if user_role == "assistant":
  current_user_id = st.session_state.user.get("parent_teacher_id")
  is_assistant = True
else:
  current_user_id = st.session_state.user["id"]
  is_assistant = False

teacher_display_name = st.session_state.user["teacher_name"]

# ---------------------------------------------------------
# 6. القائمة الجانبية
# ---------------------------------------------------------
role_label = "مساعد معلم 🛠️" if is_assistant else "معلم 👤"
st.sidebar.title(f"{role_label}: {teacher_display_name}")

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
        st.error("كلمة المرور الجديدة غير متطابقة!")
      else:
        supabase.table("users").update(
            {"password_hash": new_pwd.strip()}
        ).eq("id", st.session_state.user["id"]).execute()
        st.session_state.user["password_hash"] = new_pwd.strip()
        st.success("تم تغيير كلمة المرور بنجاح! ✅")

st.sidebar.markdown("---")

menu_options = [
    "1️⃣ تكويد وإدارة المجموعات والطلاب",
    "2️⃣ تسجيل الحضور والدرجات والدفع",
    "3️⃣ كشف حساب طالب / مجموعة",
    "4️⃣ تقرير موقف الدفع والغياب",
    "5️⃣ تقرير النتائج الأكاديمية",
]

if not is_assistant:
  menu_options.append("6️⃣ تقرير الإيرادات والتحصيلات")

menu = st.sidebar.radio("انتقل إلى:", menu_options)

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
        supabase.table("groups").insert({
            "user_id": current_user_id,
            "group_name": new_group.strip(),
        }).execute()
        st.success(f"تمت إضافة المجموعة '{new_group}' بنجاح!")
        st.rerun()

  with col2:
    st.subheader("➕ إضافة طالب جديد")
    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data or [])

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
          group_id = int(
              df_groups[df_groups["group_name"] == group_selected]["id"].values[
                  0
              ]
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

  st.markdown("---")
  st.subheader("📋 قائمة المجموعات والطلاب المسجلين")
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
    formatted_data = [
        {
            "ID": item.get("id"),
            "اسم الطالب": item.get("student_name"),
            "المجموعة": (
                item["groups"]["group_name"] if item.get("groups") else "-"
            ),
            "طريقة السداد": item.get("payment_type", "بالحصة"),
            "تليفون الطالب": item.get("student_phone", "-"),
            "تليفون ولي الأمر": item.get("parent_phone", "-"),
        }
        for item in res_full.data
    ]
    st.dataframe(pd.DataFrame(formatted_data), use_container_width=True)

# ---------------------------------------------------------
# الصفحة الثانية: تسجيل الحضور والدرجات والدفع
# ---------------------------------------------------------
elif menu == "2️⃣ تسجيل الحضور والدرجات والدفع":
  st.header("📝 تسجيل الحضور والدرجات")

  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data or [])

  if not df_groups.empty:
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
    students_in_group = pd.DataFrame(res_stds.data or [])

    if not students_in_group.empty:
      with st.form("attendance_form"):
        records = []
        for idx, row in students_in_group.iterrows():
          st.markdown(f"**👤 الطالب: {row['student_name']}**")

          if is_assistant:
            c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
            paid_amount = 0.0
          else:
            c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 2])

          with c1:
            status = st.radio(
                "الحضور:", ["حضر", "غائب"], key=f"status_{row['id']}"
            )
          with c2:
            score = st.number_input(
                "الدرجة:",
                min_value=0.0,
                max_value=500.0,
                value=0.0,
                key=f"score_{row['id']}",
            )
          with c3:
            max_score = st.number_input(
                "العظمى:",
                min_value=1.0,
                max_value=500.0,
                value=100.0,
                key=f"max_{row['id']}",
            )
          with c4:
            pct_calc = (score / max_score * 100) if max_score > 0 else 0
            st.markdown(f"**النسبة:** {pct_calc:.1f}%")

          if not is_assistant:
            with c5:
              paid_amount = st.number_input(
                  "المبلغ المسدد:",
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

        submit = st.form_submit_button("💾 حفظ بيانات الحصة")
        if submit:
          supabase.table("attendance").insert(records).execute()
          st.success("تم الحفظ بنجاح!")

# ---------------------------------------------------------
# الصفحة الثالثة: كشف حساب طالب / مجموعة
# ---------------------------------------------------------
elif menu == "3️⃣ كشف حساب طالب / مجموعة":
  st.header("🔍 كشف حضور ودرجات الطلاب")
  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data or [])

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
        sc, mx = item.get("score", 0), item.get("max_score", 100)
        pct = (sc / mx * 100) if mx > 0 else 0

        row_dict = {
            "تاريخ الحصة": item.get("session_date"),
            "اسم الطالب": std_info.get("student_name", "-"),
            "طريقة السداد": std_info.get("payment_type", "بالحصة"),
            "حالة الحضور": "حضر ✅" if item.get("attended") else "غائب ❌",
            "الدرجة": f"{sc} / {mx}",
            "النسبة": f"{pct:.1f}%",
        }

        if not is_assistant:
          row_dict["المبلغ المدفوع"] = f"{item.get('paid_amount', 0)} جنيه"

        report_rows.append(row_dict)
      st.dataframe(pd.DataFrame(report_rows), use_container_width=True)

# ---------------------------------------------------------
# الصفحة الرابعة: تقرير موقف الدفع والغياب
# ---------------------------------------------------------
elif menu == "4️⃣ تقرير موقف الدفع والغياب":
  st.header(
      "📊 تقرير الغياب" if is_assistant else "📊 تقرير سداد المصروفات والغياب"
  )
  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data or [])

  if not df_groups.empty:
    c1, c2, c3 = st.columns(3)
    with c1:
      group_selected = st.selectbox(
          "اختر المجموعة:", df_groups["group_name"].tolist()
      )
      group_id = int(
          df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
      )
    with c2:
      start_date = st.date_input("من تاريخ:", date(2026, 1, 1), key="rep4_s")
    with c3:
      end_date = st.date_input("إلى تاريخ:", date.today(), key="rep4_e")

    res_stds = (
        supabase.table("students")
        .select("*")
        .eq("group_id", group_id)
        .execute()
    )
    df_stds = pd.DataFrame(res_stds.data or [])

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

        rep_item = {
            "اسم الطالب": std["student_name"],
            "إجمالي الحصص": len(att_data),
            "عدد مرات الغياب ❌": sum(
                [1 for r in att_data if not r.get("attended")]
            ),
        }

        if not is_assistant:
          total_paid = sum([r.get("paid_amount", 0) for r in att_data])
          rep_item["إجمالي المبالغ المسددة"] = f"{total_paid} جنيه"

        report_list.append(rep_item)
      st.dataframe(pd.DataFrame(report_list), use_container_width=True)

# ---------------------------------------------------------
# الصفحة الخامسة: تقرير النتائج الأكاديمية
# ---------------------------------------------------------
elif menu == "5️⃣ تقرير النتائج الأكاديمية":
  st.header("📈 تقرير النتائج الأكاديمية وتعديل نتائج ولي الأمر")

  res_groups = (
      supabase.table("groups")
      .select("*")
      .eq("user_id", current_user_id)
      .execute()
  )
  df_groups = pd.DataFrame(res_groups.data or [])

  if not df_groups.empty:
    c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1.5])
    with c1:
      group_selected = st.selectbox(
          "اختر المجموعة:", df_groups["group_name"].tolist()
      )
      group_id = int(
          df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
      )

    res_stds = (
        supabase.table("students")
        .select("*")
        .eq("group_id", group_id)
        .execute()
    )
    df_stds = pd.DataFrame(res_stds.data or [])

    with c2:
      student_options = ["الكل"]
      if not df_stds.empty:
        student_options += df_stds["student_name"].tolist()
      selected_student = st.selectbox("اختر الطالب:", student_options)

    with c3:
      start_date = st.date_input("من تاريخ:", date(2026, 1, 1), key="res_s")
    with c4:
      end_date = st.date_input("إلى تاريخ:", date.today(), key="res_e")

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
      st.markdown("---")
      st.subheader("📋 سجل النتائج والحصص:")

      for r in res_att.data:
        std_info = r.get("students") or {}
        std_name = std_info.get("student_name", "غير معروف")

        if selected_student != "الكل" and std_name != selected_student:
          continue

        parent_phone = str(std_info.get("parent_phone", "")).strip()
        sc = r.get("score", 0)
        mx = r.get("max_score", 100)
        pct = (sc / mx * 100) if mx > 0 else 0
        attended = r.get("attended")
        session_dt = r.get("session_date")

        col_name, col_date, col_res, col_wa = st.columns([2.5, 2, 4, 2])

        with col_name:
          st.markdown(
              f"<div style='padding-top:8px;'>👤 <b>{std_name}</b></div>",
              unsafe_allow_html=True,
          )

        with col_date:
          st.markdown(
              f"<div style='padding-top:8px;'>📅 {session_dt}</div>",
              unsafe_allow_html=True,
          )

        with col_res:
          if attended:
            st.markdown(
                f"""
                            <div style='background-color: #1e4620; color: #85e89d; border-radius: 8px; padding: 6px 12px; text-align: center; font-weight: bold;'>
                                حضر ✅ ({sc}/{mx} - %{pct:.0f})
                            </div>
                            """,
                unsafe_allow_html=True,
            )
          else:
            st.markdown(
                """
                            <div style='background-color: #4a1e1e; color: #ff8585; border-radius: 8px; padding: 6px 12px; text-align: center; font-weight: bold;'>
                                غائب ❌
                            </div>
                            """,
                unsafe_allow_html=True,
            )

        with col_wa:
          if parent_phone:
            formatted_phone = parent_phone.replace(" ", "").replace("-", "")
            if formatted_phone.startswith("01"):
              formatted_phone = "20" + formatted_phone[1:]
            elif formatted_phone.startswith("+"):
              formatted_phone = formatted_phone.replace("+", "")

            status_txt = (
                f"حضر وحصل على درجة ({sc} من {mx}) بنسبة %{pct:.0f}"
                if attended
                else "غائب عن الحصة"
            )
            single_msg = (
                f"السلام عليكم،\nتقرير حصة يوم {session_dt} للطالب:"
                f" *{std_name}*\nالحالة: {status_txt}\nمع تحيات الأستاذ:"
                f" {teacher_display_name}"
            )

            encoded_msg = urllib.parse.quote(single_msg)
            wa_url = f"https://wa.me/{formatted_phone}?text={encoded_msg}"

            st.markdown(
                f"""
                            <div style='text-align: left;'>
                                <a href="{wa_url}" target="_blank" class="whatsapp-btn">📲 إرسال إشعار الحصة</a>
                            </div>
                            """,
                unsafe_allow_html=True,
            )
          else:
            st.markdown(
                "<div style='text-align: left; color:#888; padding-top:8px;'><small>بدون"
                " رقم</small></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<hr style='margin: 8px 0; border-color: #333;'>",
            unsafe_allow_html=True,
        )
    else:
      st.info("لا توجد حصص مسجلة لهذه المجموعة.")

# ---------------------------------------------------------
# الصفحة السادسة: تقرير الإيرادات والتحصيلات
# ---------------------------------------------------------
elif menu == "6️⃣ تقرير الإيرادات والتحصيلات" and not is_assistant:
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
      st.dataframe(summary, use_container_width=True)
      st.metric("إجمالي التحصيلات لهذا الشهر", f"{total_revenue} جنيه")
    else:
      st.info("لا توجد تحصيلات مالية مدفوعة في هذا الشهر.")
  else:
    st.info("لا توجد تحصيلات مالية مدفوعة في هذا الشهر.")

render_footer()
