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
                                        "parent_teacher_id": parent_teacher_id,
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
# 6. القائمة الجانبية (تم تحسين وترتيب خيارات القائمة)
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
# 2️⃣ تسجيل الحضور والدرجات
# ---------------------------------------------------------
elif menu == "2️⃣ تسجيل الحضور والدرجات":
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
                    existing_rec = att_dict.get(s_id, {})

                    c_name, c_att, c_paid = st.columns([3, 2, 3])

                    with c_name:
                        st.markdown(
                            f"<div style='padding-top: 10px;'><b>👤 {std['student_name']}</b></div>",
                            unsafe_allow_html=True,
                        )

                    with c_att:
                        is_att_val = existing_rec.get("attended", True)
                        att_status = st.selectbox(
                            "الحضور:",
                            ["حضر", "غائب"],
                            index=0 if is_att_val else 1,
                            key=f"pay_att_{s_id}",
                        )

                    with c_paid:
                        init_paid = float(existing_rec.get("paid_amount", 0.0))
                        paid_val = st.number_input(
                            "المبلغ المحصل (جنيه):",
                            min_value=0.0,
                            value=init_paid,
                            step=10.0,
                            key=f"pay_val_{s_id}",
                        )

                    pay_records.append({
                        "student_id": s_id,
                        "existing_id": existing_rec.get("id"),
                        "attended": True if att_status == "حضر" else False,
                        "paid_amount": paid_val,
                        "score": existing_rec.get("score", 0.0),
                        "max_score": existing_rec.get("max_score", 100.0),
                    })
                    st.markdown(
                        "<hr style='margin: 4px 0; border-color: #222;'>",
                        unsafe_allow_html=True,
                    )

                if st.form_submit_button(
                    "💾 حفظ وتأكيد التحصيلات المالية", use_container_width=True
                ):
                    for rec in pay_records:
                        if rec["existing_id"]:
                            supabase.table("attendance").update({
                                "attended": rec["attended"],
                                "paid_amount": rec["paid_amount"],
                            }).eq("id", rec["existing_id"]).execute()
                        else:
                            supabase.table("attendance").insert({
                                "user_id": current_user_id,
                                "student_id": rec["student_id"],
                                "group_id": group_id,
                                "session_date": str(payment_date),
                                "attended": rec["attended"],
                                "paid_amount": rec["paid_amount"],
                                "score": rec["score"],
                                "max_score": rec["max_score"],
                            }).execute()
                    st.success("تم تحديث وحفظ التحصيلات المالية بنجاح! 💵")
                    st.rerun()

# ---------------------------------------------------------
# 3️⃣ كشف حساب طالب / مجموعة
# ---------------------------------------------------------
elif menu == "3️⃣ كشف حساب طالب / مجموعة":
    st.header("📄 كشف حساب طالب / مجموعة")
    res_groups = supabase.table("groups").select("*").eq("user_id", current_user_id).execute()
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        grp_sel = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist(), key="stmt_grp")
        grp_id = int(df_groups[df_groups["group_name"] == grp_sel]["id"].values[0])

        res_stds = supabase.table("students").select("*").eq("group_id", grp_id).execute()
        df_stds = pd.DataFrame(res_stds.data or [])

        if not df_stds.empty:
            std_sel = st.selectbox("اختر الطالب:", ["عرض كافة المجموعة"] + df_stds["student_name"].tolist())

            if std_sel == "عرض كافة المجموعة":
                res_att = supabase.table("attendance").select("*, students(student_name)").eq("group_id", grp_id).execute()
            else:
                std_id = int(df_stds[df_stds["student_name"] == std_sel]["id"].values[0])
                res_att = supabase.table("attendance").select("*, students(student_name)").eq("student_id", std_id).execute()

            df_att = pd.DataFrame(res_att.data or [])
            if not df_att.empty:
                df_att["اسم الطالب"] = df_att["students"].apply(lambda x: x.get("student_name") if isinstance(x, dict) else "-")
                df_att["الحالة"] = df_att["attended"].apply(lambda x: "حضر ✅" if x else "غائب ❌")
                df_att = df_att.rename(columns={
                    "session_date": "تاريخ الحصة",
                    "score": "الدرجة",
                    "max_score": "الدرجة العظمى",
                    "paid_amount": "المبلغ المدفوع"
                })
                st.dataframe(df_att[["اسم الطالب", "تاريخ الحصة", "الحالة", "الدرجة", "الدرجة العظمى", "المبلغ المدفوع"]], use_container_width=True)
            else:
                st.info("لا توجد سجلات متاحة لهذه التصفية.")
        else:
            st.info("لا يوجد طلاب مسجلين في هذه المجموعة.")

# ---------------------------------------------------------
# 4️⃣ تقرير موقف الدفع والغياب
# ---------------------------------------------------------
elif menu == "4️⃣ تقرير موقف الدفع والغياب":
    st.header("📊 تقرير موقف الدفع والغياب")
    res_groups = supabase.table("groups").select("*").eq("user_id", current_user_id).execute()
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        grp_sel = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist(), key="abs_grp")
        grp_id = int(df_groups[df_groups["group_name"] == grp_sel]["id"].values[0])

        res_att = supabase.table("attendance").select("*, students(student_name)").eq("group_id", grp_id).execute()
        df_att = pd.DataFrame(res_att.data or [])

        if not df_att.empty:
            df_att["student_name"] = df_att["students"].apply(lambda x: x.get("student_name") if isinstance(x, dict) else "-")
            summary = df_att.groupby("student_name").agg(
                مرات_الحضور=("attended", lambda x: sum(x == True)),
                مرات_الغياب=("attended", lambda x: sum(x == False)),
                إجمالي_المدفوع=("paid_amount", "sum")
            ).reset_index()

            st.dataframe(summary, use_container_width=True)
        else:
            st.info("لا توجد سجلات حضور للمجموعة المحددة.")

# ---------------------------------------------------------
# 5️⃣ تقرير النتائج الأكاديمية
# ---------------------------------------------------------
elif menu == "5️⃣ تقرير النتائج الأكاديمية":
    st.header("🏆 تقرير النتائج الأكاديمية")
    res_groups = supabase.table("groups").select("*").eq("user_id", current_user_id).execute()
    df_groups = pd.DataFrame(res_groups.data or [])

    if not df_groups.empty:
        grp_sel = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist(), key="acad_grp")
        grp_id = int(df_groups[df_groups["group_name"] == grp_sel]["id"].values[0])

        res_att = supabase.table("attendance").select("*, students(student_name)").eq("group_id", grp_id).execute()
        df_att = pd.DataFrame(res_att.data or [])

        if not df_att.empty:
            df_att["student_name"] = df_att["students"].apply(lambda x: x.get("student_name") if isinstance(x, dict) else "-")
            summary = df_att.groupby("student_name").agg(
                مجموع_الدرجات=("score", "sum"),
                المجموع_الأقصى=("max_score", "sum")
            ).reset_index()

            summary["النسبة المئوية %"] = (summary["مجموع_الدرجات"] / summary["المجموع_الأقصى"] * 100).round(1)
            summary = summary.sort_values(by="النسبة المئوية %", ascending=False)

            st.dataframe(summary, use_container_width=True)
        else:
            st.info("لا توجد سجلات درجات للمجموعة المحددة.")

# ---------------------------------------------------------
# 6️⃣ تقرير الإيرادات والتحصيلات
# ---------------------------------------------------------
elif menu == "6️⃣ تقرير الإيرادات والتحصيلات" and not is_assistant:
    st.header("💰 تقرير الإيرادات والتحصيلات")
    res_att = supabase.table("attendance").select("*").eq("user_id", current_user_id).execute()
    df_att = pd.DataFrame(res_att.data or [])

    if not df_att.empty:
        total_rev = df_att["paid_amount"].sum()
        st.metric(label="إجمالي التحصيلات المالية (جنيه)", value=f"{total_rev:,.2f}")

        st.markdown("---")
        st.subheader("تفاصيل التحصيلات حسب التاريخ")
        daily_rev = df_att.groupby("session_date")["paid_amount"].sum().reset_index()
        daily_rev.columns = ["التاريخ", "الإيراد (جنيه)"]
        st.dataframe(daily_rev, use_container_width=True)
    else:
        st.info("لا توجد تحصيلات مالية مسجلة بعد.")

# ---------------------------------------------------------
# 🔐 تغيير كلمة مرور المساعد
# ---------------------------------------------------------
elif menu == "🔐 تغيير كلمة مرور المساعد" and not is_assistant:
    st.header("🔐 تغيير كلمة مرور المساعد")
    res_asst = supabase.table("users").select("*").eq("parent_teacher_id", current_user_id).eq("role", "assistant").execute()
    df_asst = pd.DataFrame(res_asst.data or [])

    if not df_asst.empty:
        sel_asst_name = st.selectbox("اختر المساعد:", df_asst["teacher_name"].tolist())
        asst_id = int(df_asst[df_asst["teacher_name"] == sel_asst_name]["id"].values[0])
        new_pass_asst = st.text_input("كلمة المرور الجديدة للمساعد:", type="password")

        if st.button("تحديث كلمة المرور", use_container_width=True):
            if new_pass_asst.strip():
                supabase.table("users").update({"password_hash": new_pass_asst.strip()}).eq("id", asst_id).execute()
                st.success(f"تم تغيير كلمة مرور المساعد '{sel_asst_name}' بنجاح! ✅")
            else:
                st.warning("يرجى إدخال كلمة المرور الجديدة.")
    else:
        st.info("لا يوجد مساعدون مرتبطون بحسابك حالياً.")

# ---------------------------------------------------------
# 🔑 تغيير كلمة المرور الخاصة بي
# ---------------------------------------------------------
elif menu == "🔑 تغيير كلمة المرور الخاصة بي":
    st.header("🔑 تغيير كلمة المرور الخاصة بي")
    curr_pass = st.text_input("كلمة المرور الحالية:", type="password")
    new_pass = st.text_input("كلمة المرور الجديدة:", type="password")
    confirm_pass = st.text_input("تأكيد كلمة المرور الجديدة:", type="password")

    if st.button("حفظ كلمة المرور الجديدة", use_container_width=True):
        if curr_pass == st.session_state.user["password_hash"]:
            if new_pass.strip() and new_pass == confirm_pass:
                u_id = int(st.session_state.user["id"])
                supabase.table("users").update({"password_hash": new_pass.strip()}).eq("id", u_id).execute()
                st.session_state.user["password_hash"] = new_pass.strip()
                st.success("تم تحديث كلمة المرور الخاصة بك بنجاح! 🔑")
            else:
                st.error("كلمتا المرور غير متطابقتين أو فارغتين.")
        else:
            st.error("كلمة المرور الحالية غير صحيحة.")

render_footer()
