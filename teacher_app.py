import calendar
from datetime import date, datetime
import re
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
                    user_unique_key = str(user_data["id"])

                    edit_teacher_name = st.text_input(
                        "الاسم الظاهر / الكرتي الجديد:",
                        value=user_data.get("teacher_name", ""),
                        key=f"edit_t_name_{user_unique_key}",
                    )
                    edit_username = st.text_input(
                        "اسم المستخدم الجديد للدخول:",
                        value=user_data.get("username", ""),
                        key=f"edit_u_name_{user_unique_key}",
                    )

                    if st.button("💾 حفظ البيانات المعدلة", use_container_width=True):
                        if edit_teacher_name.strip() and edit_username.strip():
                            target_user_id = int(user_data["id"])

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
                                    f"⚠️ اسم المستخدم '{new_user.strip()}' مأخوذ بالفعل!"
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
                                        "parent_teacher_id": parent_teacher_id if account_type == "مساعد للمعلم" else None,
                                    }).execute()
                                    st.success(f"تم إنشاء حساب '{new_teacher}' بنجاح! ✅")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"حدث خطأ أثناء الإنشاء: {e}")
                    else:
                        st.warning("يرجى استكمال جميع البيانات المطلوبة.")

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
    parent_res = (
        supabase.table("users")
        .select("teacher_name")
        .eq("id", current_user_id)
        .execute()
    )
    main_teacher_name = (
        parent_res.data[0]["teacher_name"] if parent_res.data else ""
    )
    sender_name = st.session_state.user["teacher_name"]
else:
    current_user_id = st.session_state.user["id"]
    is_assistant = False
    main_teacher_name = st.session_state.user["teacher_name"]
    sender_name = st.session_state.user["teacher_name"]

teacher_display_name = st.session_state.user["teacher_name"]

# ---------------------------------------------------------
# 6. القائمة الجانبية
# ---------------------------------------------------------
role_label = "مساعد معلم 🛠️" if is_assistant else "معلم 👤"
st.sidebar.title(f"{role_label}: {teacher_display_name}")

if st.sidebar.button("تسجيل الخروج 🚪", use_container_width=True):
    st.session_state.user = None
    st.rerun()

st.sidebar.markdown("---")

menu_options = [
    "1️⃣ تكويد وإدارة المجموعات والطلاب",
    "2️⃣ تسجيل الحضور والدرجات",
]

if not is_assistant:
    menu_options.append("💵 تسجيل التحصيل المالي")

menu_options.extend([
    "3️⃣ كشف حساب طالب / مجموعة",
    "4️⃣ تقرير موقف الدفع والغياب",
    "5️⃣ تقرير النتائج الأكاديمية",
])

if not is_assistant:
    menu_options.append("6️⃣ تقرير الإيرادات والتحصيلات")
    menu_options.append("🔐 تغيير كلمة مرور المساعد")

menu_options.append("🔑 تغيير كلمة المرور الخاصة بي")

menu = st.sidebar.radio("انتقل إلى:", menu_options)

# ---------------------------------------------------------
# 1️⃣ تكويد وإدارة المجموعات والطلاب
# ---------------------------------------------------------
if menu == "1️⃣ تكويد وإدارة المجموعات والطلاب":
    st.header("⚙️ تكويد وإدارة المجموعات والطلاب")

    tab_add, tab_edit_std, tab_edit_grp = st.tabs([
        "➕ إضافة جديدة",
        "✏️ تعديل / حذف طالب",
        "📁 إدارة المجموعات (تعديل/حذف)",
    ])

    with tab_add:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ إضافة مجموعة جديدة")
            new_group = st.text_input("اسم المجموعة:")
            if st.button("حفظ المجموعة", use_container_width=True):
                if new_group.strip():
                    supabase.table("groups").insert({
                        "user_id": current_user_id,
                        "group_name": new_group.strip(),
                    }).execute()
                    st.success(f"تمت إضافة المجموعة '{new_group}' بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى كتابة اسم المجموعة.")

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
                    "اختر المجموعة:", df_groups["group_name"].tolist(), key="add_std_grp"
                )
                student_name = st.text_input("اسم الطالب:")
                payment_type = st.selectbox(
                    "طريقة السداد:", ["بالحصة", "شهري"], key="add_std_pay"
                )
                student_phone = st.text_input("تليفون الطالب:")
                parent_phone = st.text_input("تليفون ولي الأمر:")

                if st.button("حفظ الطالب", use_container_width=True):
                    if student_name.strip():
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
                    else:
                        st.warning("يرجى إدخال اسم الطالب.")
            else:
                st.info("قم بإضافة مجموعة أولاً لتتمكن من إضافة طلاب.")

    with tab_edit_std:
        res_groups = (
            supabase.table("groups")
            .select("*")
            .eq("user_id", current_user_id)
            .execute()
        )
        df_groups = pd.DataFrame(res_groups.data or [])

        if not df_groups.empty:
            col_g, col_s = st.columns(2)
            with col_g:
                filter_grp = st.selectbox(
                    "اختر المجموعة لتصفية الطلاب:",
                    df_groups["group_name"].tolist(),
                    key="edit_filter_grp",
                )
                selected_grp_id = int(
                    df_groups[df_groups["group_name"] == filter_grp]["id"].values[0]
                )

            res_stds = (
                supabase.table("students")
                .select("*")
                .eq("group_id", selected_grp_id)
                .execute()
            )
            df_stds = pd.DataFrame(res_stds.data or [])

            if not df_stds.empty:
                with col_s:
                    selected_std_name = st.selectbox(
                        "اختر الطالب المراد تعديله / حذفه:",
                        df_stds["student_name"].tolist(),
                        key="edit_std_select",
                    )

                std_data = df_stds[
                    df_stds["student_name"] == selected_std_name
                ].iloc[0]
                std_id = int(std_data["id"])

                st.markdown("---")
                col_edit, col_del = st.columns([2, 1])

                with col_edit:
                    st.subheader(f"✏️ تعديل بيانات الطالب: {selected_std_name}")
                    up_name = st.text_input(
                        "اسم الطالب المعدل:",
                        value=std_data["student_name"],
                        key=f"up_name_{std_id}",
                    )

                    curr_grp_idx = int(
                        df_groups[df_groups["id"] == std_data["group_id"]].index[0]
                    )
                    up_grp_name = st.selectbox(
                        "نقل إلى مجموعة أخرى:",
                        df_groups["group_name"].tolist(),
                        index=curr_grp_idx,
                        key=f"up_grp_{std_id}",
                    )
                    up_grp_id = int(
                        df_groups[df_groups["group_name"] == up_grp_name]["id"].values[0]
                    )

                    pay_opts = ["بالحصة", "شهري"]
                    curr_pay_idx = (
                        pay_opts.index(std_data["payment_type"])
                        if std_data["payment_type"] in pay_opts
                        else 0
                    )
                    up_pay_type = st.selectbox(
                        "طريقة السداد:",
                        pay_opts,
                        index=curr_pay_idx,
                        key=f"up_pay_{std_id}",
                    )

                    up_phone = st.text_input(
                        "تليفون الطالب:",
                        value=std_data.get("student_phone") or "",
                        key=f"up_p_{std_id}",
                    )
                    up_parent_phone = st.text_input(
                        "تليفون ولي الأمر:",
                        value=std_data.get("parent_phone") or "",
                        key=f"up_pp_{std_id}",
                    )

                    if st.button("💾 حفظ تعديلات الطالب", use_container_width=True):
                        if up_name.strip():
                            supabase.table("students").update({
                                "student_name": up_name.strip(),
                                "group_id": up_grp_id,
                                "payment_type": up_pay_type,
                                "student_phone": up_phone.strip(),
                                "parent_phone": up_parent_phone.strip(),
                            }).eq("id", std_id).execute()
                            st.success(f"تم تعديل بيانات الطالب '{up_name}' بنجاح! ✅")
                            st.rerun()

                with col_del:
                    st.subheader("🗑️ حذف الطالب")
                    st.warning(
                        "⚠️ تندرج هذه الخطوة تحت حذف كامل سجل الطالب المالي والأكاديمي."
                    )
                    if st.button(
                        "❌ حذف الطالب نهائياً", type="primary", use_container_width=True
                    ):
                        supabase.table("attendance").delete().eq(
                            "student_id", std_id
                        ).execute()
                        supabase.table("students").delete().eq("id", std_id).execute()
                        st.success(f"تم حذف الطالب '{selected_std_name}' بنجاح.")
                        st.rerun()
            else:
                st.info("لا يوجد طلاب مسجلين في هذه المجموعة.")
        else:
            st.info("لا توجد مجموعات مسجلة.")

    with tab_edit_grp:
        res_groups = (
            supabase.table("groups")
            .select("*")
            .eq("user_id", current_user_id)
            .execute()
        )
        df_groups = pd.DataFrame(res_groups.data or [])

        if not df_groups.empty:
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                st.subheader("✏️ تعديل اسم المجموعة")
                sel_grp_rename = st.selectbox(
                    "اختر المجموعة المراد تعديل اسمها:",
                    df_groups["group_name"].tolist(),
                    key="rename_grp_sel",
                )
                grp_data_rename = df_groups[
                    df_groups["group_name"] == sel_grp_rename
                ].iloc[0]
                new_grp_name_input = st.text_input(
                    "الاسم الجديد للمجموعة:",
                    value=grp_data_rename["group_name"],
                    key="rename_grp_val",
                )

                if st.button("💾 حفظ الاسم الجديد للمجموعة", use_container_width=True):
                    if new_grp_name_input.strip():
                        supabase.table("groups").update(
                            {"group_name": new_grp_name_input.strip()}
                        ).eq("id", int(grp_data_rename["id"])).execute()
                        st.success("تم تغيير اسم المجموعة بنجاح! ✅")
                        st.rerun()

            with c_g2:
                st.subheader("🗑️ حذف مجموعة")
                sel_grp_del = st.selectbox(
                    "اختر المجموعة المراد حذفها:",
                    df_groups["group_name"].tolist(),
                    key="del_grp_sel",
                )
                grp_data_del = df_groups[df_groups["group_name"] == sel_grp_del].iloc[
                    0
                ]

                if st.button(
                    "❌ حذف المجموعة", type="primary", use_container_width=True
                ):
                    g_id = int(grp_data_del["id"])
                    supabase.table("attendance").delete().eq("group_id", g_id).execute()
                    supabase.table("students").delete().eq("group_id", g_id).execute()
                    supabase.table("groups").delete().eq("id", g_id).execute()
                    st.success(f"تم حذف مجموعة '{sel_grp_del}' بكافة بياناتها بنجاح!")
                    st.rerun()

# ---------------------------------------------------------
# 2️⃣ تسجيل الحضور والدرجات (تعديل وحذف سجل الحضور)
# ---------------------------------------------------------
elif menu == "2️⃣ تسجيل الحضور والدرجات":
    st.header("📝 تسجيل الحضور والدرجات")

    tab_rec, tab_del_att = st.tabs(["📝 تسجيل حضور جديد", "✏️ تعديل / 🗑️ حذف سجل حضور"])

    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data or [])

    with tab_rec:
        if not df_groups.empty:
            group_selected = st.selectbox(
                "اختر المجموعة:", df_groups["group_name"].tolist(), key="rec_att_grp"
            )
            group_id = int(
                df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
            )
            session_date = st.date_input("تاريخ الحصة:", date.today(), key="rec_att_date")

            res_stds = (
                supabase.table("students").select("*").eq("group_id", group_id).execute()
            )
            students_in_group = pd.DataFrame(res_stds.data or [])

            if not students_in_group.empty:
                with st.form("attendance_form"):
                    records = []
                    for idx, row in students_in_group.iterrows():
                        st.markdown(f"**👤 الطالب: {row['student_name']}**")

                        c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
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

                        st.markdown("---")

                        records.append({
                            "user_id": current_user_id,
                            "student_id": int(row["id"]),
                            "group_id": group_id,
                            "session_date": str(session_date),
                            "attended": True if status == "حضر" else False,
                            "score": score,
                            "max_score": max_score,
                            "paid": 0,
                            "paid_amount": 0.0,
                        })

                    submit = st.form_submit_button("💾 حفظ بيانات الحصة والدرجات")
                    if submit:
                        supabase.table("attendance").insert(records).execute()
                        st.success("تم حفظ الحضور والدرجات بنجاح!")
                        st.rerun()
            else:
                st.info("لا يوجد طلاب مسجلين في هذه المجموعة.")
        else:
            st.info("لا توجد مجموعات مسجلة.")

    with tab_del_att:
        st.subheader("✏️ تعديل أو 🗑️ حذف سجل حضور طالب")
        if not df_groups.empty:
            col_del1, col_del2 = st.columns(2)
            with col_del1:
                del_grp_selected = st.selectbox(
                    "اختر المجموعة:", df_groups["group_name"].tolist(), key="del_att_grp"
                )
                del_group_id = int(
                    df_groups[df_groups["group_name"] == del_grp_selected]["id"].values[0]
                )
            
            res_stds_del = (
                supabase.table("students").select("*").eq("group_id", del_group_id).execute()
            )
            df_stds_del = pd.DataFrame(res_stds_del.data or [])

            if not df_stds_del.empty:
                with col_del2:
                    del_std_selected = st.selectbox(
                        "اختر الطالب:", df_stds_del["student_name"].tolist(), key="del_att_std"
                    )
                    del_std_id = int(
                        df_stds_del[df_stds_del["student_name"] == del_std_selected]["id"].values[0]
                    )

                res_att_records = (
                    supabase.table("attendance")
                    .select("*")
                    .eq("student_id", del_std_id)
                    .order("session_date", desc=True)
                    .execute()
                )
                df_att_records = pd.DataFrame(res_att_records.data or [])

                if not df_att_records.empty:
                    st.markdown("###### السجلات المسجلة للطالب (يمكنك تعديل الحضور/الدرجات أو الحذف):")
                    for idx, att_row in df_att_records.iterrows():
                        att_rec_id = att_row["id"]
                        curr_attended = bool(att_row.get("attended", True))
                        curr_score = float(att_row.get("score", 0.0))
                        curr_max = float(att_row.get("max_score", 100.0))

                        with st.expander(f"📅 تاريخ الحصة: {att_row['session_date']} — ({'حضر ✅' if curr_attended else 'غائب ❌'})"):
                            c_m1, c_m2, c_m3 = st.columns([2, 2, 2])
                            with c_m1:
                                new_status = st.radio(
                                    "حالة الحضور:",
                                    ["حضر", "غائب"],
                                    index=0 if curr_attended else 1,
                                    key=f"edit_att_status_{att_rec_id}"
                                )
                            with c_m2:
                                new_score = st.number_input(
                                    "الدرجة:",
                                    min_value=0.0,
                                    max_value=500.0,
                                    value=curr_score,
                                    key=f"edit_att_score_{att_rec_id}"
                                )
                            with c_m3:
                                new_max = st.number_input(
                                    "الدرجة العظمى:",
                                    min_value=1.0,
                                    max_value=500.0,
                                    value=curr_max,
                                    key=f"edit_att_max_{att_rec_id}"
                                )

                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("💾 حفظ التعديل", key=f"btn_save_att_{att_rec_id}", use_container_width=True):
                                    supabase.table("attendance").update({
                                        "attended": True if new_status == "حضر" else False,
                                        "score": new_score,
                                        "max_score": new_max
                                    }).eq("id", att_rec_id).execute()
                                    st.success("تم تعديل السجل بنجاح! ✅")
                                    st.rerun()
                            with btn_col2:
                                if st.button("❌ حذف هذا السجل", key=f"btn_del_att_{att_rec_id}", type="primary", use_container_width=True):
                                    supabase.table("attendance").delete().eq("id", att_rec_id).execute()
                                    st.success("تم حذف سجل الحضور بنجاح! ✅")
                                    st.rerun()
                else:
                    st.info("لا توجد سجلات حضور مسجلة لهذا الطالب.")
            else:
                st.info("لا يوجد طلاب مسجلين في هذه المجموعة.")

# ---------------------------------------------------------
# 💵 تسجيل التحصيل المالي
# ---------------------------------------------------------
elif menu == "💵 تسجيل التحصيل المالي" and not is_assistant:
    st.header("💵 تسجيل التحصيل المالي للطلاب")

    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        col_g, col_d = st.columns(2)
        with col_g:
            group_selected = st.selectbox(
                "اختر المجموعة:",
                df_groups["group_name"].tolist(),
                key="pay_group_sel",
            )
            group_id = int(
                df_groups[df_groups["group_name"] == group_selected]["id"].values[0]
            )
        with col_d:
            payment_date = st.date_input(
                "اختر تاريخ اليوم/الحصة:", date.today(), key="pay_date_sel"
            )

        res_stds = (
            supabase.table("students")
            .select("*")
            .eq("group_id", group_id)
            .execute()
        )
        df_stds = pd.DataFrame(res_stds.data or [])

        if not df_stds.empty:
            st.markdown("---")
            st.markdown(
                f"##### 📋 جدول تحصيل النقدية لمجموعة (**{group_selected}**) بتاريخ"
                f" **{payment_date}**"
            )

            res_att_today = (
                supabase.table("attendance")
                .select("*")
                .eq("group_id", group_id)
                .eq("session_date", str(payment_date))
                .execute()
            )
            att_dict = {
                item["student_id"]: item for item in (res_att_today.data or [])
            }

            with st.form("payment_collection_form"):
                pay_records = []
                for idx, std in df_stds.iterrows():
                    s_id = int(std["id"])
                    st.markdown(f"**👤 الطالب: {std['student_name']}** (طريقة السداد: {std.get('payment_type', 'بالحصة')})")

                    curr_att = att_dict.get(s_id, {})
                    c1, c2 = st.columns(2)
                    with c1:
                        p_amount = st.number_input(
                            "المبلغ المدفوع:",
                            min_value=0.0,
                            value=float(curr_att.get("paid_amount", 0.0)),
                            key=f"pay_amt_{s_id}",
                        )
                    with c2:
                        p_status = st.checkbox(
                            "تم الدفع",
                            value=bool(curr_att.get("paid", 0)),
                            key=f"pay_chk_{s_id}",
                        )

                    pay_records.append({
                        "student_id": s_id,
                        "amount": p_amount,
                        "paid": 1 if (p_status or p_amount > 0) else 0,
                    })
                    st.markdown("---")

                btn_pay_submit = st.form_submit_button("💾 حفظ التحصيل المالي")
                if btn_pay_submit:
                    for pr in pay_records:
                        chk_exist = (
                            supabase.table("attendance")
                            .select("id")
                            .eq("student_id", pr["student_id"])
                            .eq("session_date", str(payment_date))
                            .execute()
                        )
                        if chk_exist.data:
                            supabase.table("attendance").update({
                                "paid": pr["paid"],
                                "paid_amount": pr["amount"],
                            }).eq("id", chk_exist.data[0]["id"]).execute()
                        else:
                            supabase.table("attendance").insert({
                                "user_id": current_user_id,
                                "student_id": pr["student_id"],
                                "group_id": group_id,
                                "session_date": str(payment_date),
                                "attended": False,
                                "score": 0,
                                "max_score": 100,
                                "paid": pr["paid"],
                                "paid_amount": pr["amount"],
                            }).execute()

                    st.success("تم حفظ البيانات المالية بنجاح! ✅")
                    st.rerun()

# ---------------------------------------------------------
# 3️⃣ كشف حساب طالب / مجموعة (ربط تلقائي لحالة الدفع)
# ---------------------------------------------------------
elif menu == "3️⃣ كشف حساب طالب / مجموعة":
    st.header("📊 كشف حساب طالب / مجموعة")

    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        col1, col2 = st.columns(2)
        with col1:
            grp_sel = st.selectbox(
                "اختر المجموعة:", df_groups["group_name"].tolist(), key="stmt_grp"
            )
            g_id = int(df_groups[df_groups["group_name"] == grp_sel]["id"].values[0])

        res_stds = (
            supabase.table("students").select("*").eq("group_id", g_id).execute()
        )
        df_stds = pd.DataFrame(res_stds.data or [])

        if not df_stds.empty:
            with col2:
                std_options = ["جميع طلاب المجموعة"] + df_stds["student_name"].tolist()
                std_sel = st.selectbox("اختر الطالب:", std_options, key="stmt_std")

            if std_sel == "جميع طلاب المجموعة":
                res_att = (
                    supabase.table("attendance")
                    .select("*, students(student_name)")
                    .eq("group_id", g_id)
                    .execute()
                )
            else:
                s_id = int(
                    df_stds[df_stds["student_name"] == std_sel]["id"].values[0]
                )
                res_att = (
                    supabase.table("attendance")
                    .select("*, students(student_name)")
                    .eq("student_id", s_id)
                    .execute()
                )

            df_att = pd.DataFrame(res_att.data or [])
            if not df_att.empty:
                df_att["اسم الطالب"] = df_att["students"].apply(
                    lambda x: x["student_name"] if isinstance(x, dict) else "-"
                )
                df_att["الحضور"] = df_att["attended"].apply(
                    lambda x: "حضر ✅" if x else "غائب ❌"
                )
                
                # ربط تلقائي بحالة الدفع بناءً على التسجيل المالي (سواء خانة تم الدفع أو المبلغ)
                df_att["حالة الدفع"] = df_att.apply(
                    lambda row: "تم الدفع 💵" if (row.get("paid") == 1 or float(row.get("paid_amount", 0.0)) > 0) else "لم يدفع ⚠️",
                    axis=1
                )

                disp_df = df_att[[
                    "session_date",
                    "اسم الطالب",
                    "الحضور",
                    "score",
                    "max_score",
                    "حالة الدفع",
                    "paid_amount",
                ]].copy()
                disp_df.columns = [
                    "تاريخ الحصة",
                    "اسم الطالب",
                    "حالة الحضور",
                    "الدرجة",
                    "الدرجة العظمى",
                    "حالة الدفع",
                    "المبلغ المدفوع",
                ]

                st.dataframe(disp_df, use_container_width=True)
            else:
                st.info("لا توجد سجلات مسجلة لعرضها.")
        else:
            st.info("لا يوجد طلاب مسجلين في هذه المجموعة.")
    else:
        st.info("لا توجد مجموعات مسجلة.")

# ---------------------------------------------------------
# 4️⃣ تقرير موقف الدفع والغياب
# ---------------------------------------------------------
elif menu == "4️⃣ تقرير موقف الدفع والغياب":
    st.header("📈 تقرير موقف الدفع والغياب")

    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        grp_sel = st.selectbox(
            "اختر المجموعة:", df_groups["group_name"].tolist(), key="rep_grp"
        )
        g_id = int(df_groups[df_groups["group_name"] == grp_sel]["id"].values[0])

        res_stds = (
            supabase.table("students").select("*").eq("group_id", g_id).execute()
        )
        df_stds = pd.DataFrame(res_stds.data or [])

        if not df_stds.empty:
            summary_list = []
            for idx, std in df_stds.iterrows():
                s_id = int(std["id"])
                res_att = (
                    supabase.table("attendance")
                    .select("*")
                    .eq("student_id", s_id)
                    .execute()
                )
                att_data = res_att.data or []

                total_sessions = len(att_data)
                absent_count = sum(1 for a in att_data if not a.get("attended"))
                unpaid_count = sum(1 for a in att_data if not (a.get("paid") == 1 or float(a.get("paid_amount", 0.0)) > 0))
                total_paid = sum(a.get("paid_amount", 0.0) for a in att_data)

                summary_list.append({
                    "اسم الطالب": std["student_name"],
                    "طريقة السداد": std.get("payment_type", "بالحصة"),
                    "إجمالي الحصص المسجلة": total_sessions,
                    "عدد مرات الغياب": absent_count,
                    "حصص غير مدفوعة": unpaid_count,
                    "إجمالي المحصل": total_paid,
                    "تليفون ولي الأمر": std.get("parent_phone", "-"),
                })

            st.dataframe(pd.DataFrame(summary_list), use_container_width=True)
        else:
            st.info("لا يوجد طلاب مسجلين في هذه المجموعة.")
    else:
        st.info("لا توجد مجموعات مسجلة.")

# ---------------------------------------------------------
# 5️⃣ تقرير النتائج الأكاديمية (مع تفعيل إرسال الواتساب)
# ---------------------------------------------------------
elif menu == "5️⃣ تقرير النتائج الأكاديمية":
    st.header("🏆 تقرير النتائج الأكاديمية")

    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            selected_grp_name = st.selectbox(
                "المجموعة:", df_groups["group_name"].tolist(), key="acad_grp"
            )
            selected_grp_id = int(
                df_groups[df_groups["group_name"] == selected_grp_name]["id"].values[0]
            )

        res_stds = (
            supabase.table("students")
            .select("*")
            .eq("group_id", selected_grp_id)
            .execute()
        )
        df_stds = pd.DataFrame(res_stds.data or [])

        if not df_stds.empty:
            with col_f2:
                selected_std_name = st.selectbox(
                    "اسم الطالب:", df_stds["student_name"].tolist(), key="acad_std"
                )
                selected_std_data = df_stds[
                    df_stds["student_name"] == selected_std_name
                ].iloc[0]
                selected_std_id = int(selected_std_data["id"])

            with col_f3:
                start_date = st.date_input("من تاريخ:", date(date.today().year, date.today().month, 1), key="acad_sdate")
            with col_f4:
                end_date = st.date_input("إلى تاريخ:", date.today(), key="acad_edate")

            res_acad = (
                supabase.table("attendance")
                .select("*")
                .eq("student_id", selected_std_id)
                .gte("session_date", str(start_date))
                .lte("session_date", str(end_date))
                .order("session_date", desc=False)
                .execute()
            )
            df_acad = pd.DataFrame(res_acad.data or [])

            if not df_acad.empty:
                df_acad["حالة الحضور"] = df_acad["attended"].apply(
                    lambda x: "حضر ✅" if x else "غائب ❌"
                )
                df_acad["النسبة المئوية"] = (
                    df_acad["score"] / df_acad["max_score"] * 100
                ).round(1).astype(str) + "%"

                disp_acad = df_acad[[
                    "session_date",
                    "حالة الحضور",
                    "score",
                    "max_score",
                    "النسبة المئوية",
                ]].copy()
                disp_acad.columns = [
                    "تاريخ الحصة",
                    "حالة الحضور",
                    "الدرجة",
                    "الدرجة العظمى",
                    "النسبة المئوية",
                ]

                st.markdown("---")
                st.markdown(f"##### 📊 نتائج الطالب: **{selected_std_name}** للفترة من **{start_date}** إلى **{end_date}**")
                st.dataframe(disp_acad, use_container_width=True)

                # صياغة النص المطلوب تماماً
                sessions_text_list = []
                for _, row in df_acad.iterrows():
                    att_status = "حضر" if row["attended"] else "غائب"
                    if row["attended"]:
                        score_str = f"ودرجة الامتحان: {row['score']} من {row['max_score']}"
                    else:
                        score_str = ""
                    sessions_text_list.append(f"- حصة يوم {row['session_date']}: {att_status} {score_str}".strip())

                sessions_text = "\n".join(sessions_text_list)

                if is_assistant:
                    footer_sig = f"مع تحيات المعلم / {main_teacher_name}\nبواسطة المساعد / {sender_name}"
                else:
                    footer_sig = f"مع تحيات استاذ / {main_teacher_name}"

                whatsapp_message = (
                    f"السلام عليكم\n"
                    f"ولي امر الطالب / {selected_std_name}\n\n"
                    f"إليك تقرير الحضور والنتائج الأكاديمية للفترة من {start_date} إلى {end_date}:\n\n"
                    f"{sessions_text}\n\n"
                    f"{footer_sig}"
                )

                raw_phone = str(selected_std_data.get("parent_phone", "")).strip()
                # تنظيف الرقم وإعداده للصيغة الدولية
                clean_phone = re.sub(r"\D", "", raw_phone)
                if clean_phone.startswith("0"):
                    clean_phone = "2" + clean_phone  # إضافة كود مصر بشكل افتراضي في حال إدخال رقم محلي

                st.markdown("---")
                if clean_phone:
                    encoded_msg = urllib.parse.quote(whatsapp_message)
                    # رابط موثوق ومباشر للواتساب
                    whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
                    st.markdown(
                        f'''
                        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #25D366; color: white; border: none; padding: 14px 28px; font-size: 17px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold;">
                                📲 إرسال التقرير عبر واتساب ولي الأمر ({raw_phone})
                            </button>
                        </a>
                        ''',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("⚠️ رقم ولي الأمر غير مسجل لـ هذا الطالب! يمكنك تعديله من شاشة تكويد وإدارة الطلاب.")
            else:
                st.info("لا توجد حصص مسجلة لهذا الطالب في الفترة المحددة.")
        else:
            st.info("لا يوجد طلاب مسجلين في هذه المجموعة.")
    else:
        st.info("لا توجد مجموعات مسجلة.")

# ---------------------------------------------------------
# 6️⃣ تقرير الإيرادات والتحصيلات (فلتر شهر وسنة)
# ---------------------------------------------------------
elif menu == "6️⃣ تقرير الإيرادات والتحصيلات" and not is_assistant:
    st.header("6️⃣ تقرير الإيرادات والتحصيلات")

    col_m, col_y = st.columns(2)
    with col_m:
        months_arabic = [
            "يناير (1)", "فبراير (2)", "مارس (3)", "أبريل (4)",
            "مايو (5)", "يونيو (6)", "يوليو (7)", "أغسطس (8)",
            "سبتمبر (9)", "أكتوبر (10)", "نوفمبر (11)", "ديسمبر (12)"
        ]
        selected_month_idx = st.selectbox("اختر الشهر:", list(range(1, 13)), format_func=lambda x: months_arabic[x-1], index=date.today().month - 1)
    with col_y:
        selected_year = st.number_input("اختر السنة:", min_value=2020, max_value=2035, value=date.today().year)

    res_groups = (
        supabase.table("groups")
        .select("*")
        .eq("user_id", current_user_id)
        .execute()
    )
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        num_days = calendar.monthrange(selected_year, selected_month_idx)[1]
        start_date_str = f"{selected_year}-{selected_month_idx:02d}-01"
        end_date_str = f"{selected_year}-{selected_month_idx:02d}-{num_days:02d}"

        rev_data = []
        total_all_groups = 0.0

        for idx, grp in df_groups.iterrows():
            g_id = int(grp["id"])
            res_rev = (
                supabase.table("attendance")
                .select("paid_amount")
                .eq("group_id", g_id)
                .gte("session_date", start_date_str)
                .lte("session_date", end_date_str)
                .execute()
            )
            group_total = sum(item.get("paid_amount", 0.0) for item in (res_rev.data or []))
            total_all_groups += group_total

            rev_data.append({
                "اسم المجموعة": grp["group_name"],
                "المبلغ المحصل": group_total,
            })

        st.markdown("---")
        st.markdown(f"##### 📊 إجمالي الإيرادات لشهر **{selected_month_idx}/{selected_year}**")
        
        df_rev = pd.DataFrame(rev_data)
        st.dataframe(df_rev, use_container_width=True)

        st.success(f"💰 **إجمالي التحصيلات الكلية لجميع المجموعات:** {total_all_groups:,.2f} ج.م")
    else:
        st.info("لا توجد مجموعات مسجلة.")

# ---------------------------------------------------------
# 🔐 تغيير كلمة مرور المساعد
# ---------------------------------------------------------
elif menu == "🔐 تغيير كلمة مرور المساعد" and not is_assistant:
    st.header("🔐 تغيير كلمة مرور المساعد")

    res_assistants = (
        supabase.table("users")
        .select("*")
        .eq("parent_teacher_id", current_user_id)
        .eq("role", "assistant")
        .execute()
    )
    df_assistants = pd.DataFrame(res_assistants.data or [])

    if not df_assistants.empty:
        sel_assistant = st.selectbox(
            "اختر المساعد المراد تغيير كلمة مروره:",
            df_assistants["teacher_name"].tolist(),
        )
        asst_data = df_assistants[
            df_assistants["teacher_name"] == sel_assistant
        ].iloc[0]

        new_asst_pass = st.text_input("كلمة المرور الجديدة:", type="password")

        if st.button("حفظ كلمة المرور الجديدة للمساعد", use_container_width=True):
            if new_asst_pass.strip():
                supabase.table("users").update({
                    "password_hash": new_asst_pass.strip()
                }).eq("id", int(asst_data["id"])).execute()
                st.success(f"تم تغيير كلمة مرور المساعد '{sel_assistant}' بنجاح! ✅")
            else:
                st.warning("يرجى كتابة كلمة المرور الجديدة.")
    else:
        st.info("لا يوجد مساعدون مرتبطون بحسابك حالياً.")

# ---------------------------------------------------------
# 🔑 تغيير كلمة المرور الخاصة بي
# ---------------------------------------------------------
elif menu == "🔑 تغيير كلمة المرور الخاصة بي":
    st.header("🔑 تغيير كلمة المرور الخاصة بي")

    old_pass = st.text_input("كلمة المرور الحالية:", type="password")
    new_pass1 = st.text_input("كلمة المرور الجديدة:", type="password")
    new_pass2 = st.text_input("تأكيد كلمة المرور الجديدة:", type="password")

    if st.button("تحديث كلمة المرور", use_container_width=True):
        if old_pass and new_pass1 and new_pass2:
            if old_pass == st.session_state.user["password_hash"]:
                if new_pass1 == new_pass2:
                    supabase.table("users").update({
                        "password_hash": new_pass1.strip()
                    }).eq("id", st.session_state.user["id"]).execute()
                    st.session_state.user["password_hash"] = new_pass1.strip()
                    st.success("تم تغيير كلمة المرور بنجاح! ✅")
                else:
                    st.error("كلمتا المرور الجديدتان غير متطابقتين.")
            else:
                st.error("كلمة المرور الحالية غير صحيحة.")
        else:
            st.warning("يرجى ملء جميع الحقول المطلوب تعبئتها.")

render_footer()
