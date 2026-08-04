from supabase import create_client, Client
import pandas as pd
import streamlit as st
from datetime import date

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="Teacher application",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🌐 تطبيق الاتجاه من اليمين إلى اليسار (RTL) وتنسيق الهيدر والفوتر
st.markdown(
    """
    <style>
        /* اتجاه الصفحة بالكامل من اليمين إلى اليسار */
        html, body, [class*="css"] {
            direction: rtl;
            text-align: right;
        }
        /* القائمة الجانبية */
        section[data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }
        /* المدخلات والقوائم */
        .stTextInput, .stSelectbox, .stNumberInput, .stDateInput {
            direction: rtl;
            text-align: right;
        }
        /* تنسيق الهيدر للشعار مع النص */
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
            color: #0088cc; /* لون أزرق فاتح */
            font-family: Arial, sans-serif;
        }
        /* تنسيق العنوان الرئيسي ليكون في المنتصف تماماً */
        .app-title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin-top: 5px;
            margin-bottom: 20px;
            color: #333333;
        }
        /* تنسيق الفوتر لأسفل الصفحة */
        .footer-container {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e6e6e6;
            text-align: center;
            font-size: 14px;
            color: #666666;
            direction: ltr; /* اتجاه إنجليزي لضمان تنسيق الإيميل والحقوق */
        }
        .footer-container a {
            color: #0088cc;
            text-decoration: none;
            font-weight: bold;
        }
        .footer-container a:hover {
            text-decoration: underline;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# دالة طباعة الفوتر في نهاية الصفحة
# ---------------------------------------------------------
def render_footer():
    st.markdown(
        """
        <div class="footer-container">
            <p style="margin-bottom: 5px;">© tech-builder</p>
            <p><a href="mailto:support@tech-builder.uk">support@tech-builder.uk</a></p>
        </div>
        """,
        unsafe_allow_html=True
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

# 🔑 كلمة مرور لوحة الإدارة (الأدمن)
ADMIN_PASSWORD = "admin_tech_builder_2026"

# 🖼️ رابط الصورة من ImgBB
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
        # عرض الشعار وبجانبه اسم Tech Builder
        st.markdown(
            f"""
            <div class="logo-header">
                <img src="{LOGO_URL}" width="70" style="vertical-align: middle;">
                <span class="logo-text">Tech Builder</span>
            </div>
            """,
            unsafe_allow_html=True
        )
            
        # عرض العنوان Teacher application بدون قفل وفي منتصف الصفحة تماماً
        st.markdown('<div class="app-title">Teacher application</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        tab_login, tab_admin = st.tabs(["دخول المعلمين 👤", "لوحة الإدارة 🛠️"])
        
        # --- تبويب دخول العملاء ---
        with tab_login:
            st.markdown("##### تسجيل الدخول للحساب")
            username = st.text_input("اسم المستخدم:")
            password = st.text_input("كلمة المرور:", type="password")
            
            if st.button("دخول 🚪", use_container_width=True):
                if username and password:
                    res = supabase.table("users").select("*").eq("username", username.strip()).eq("password_hash", password.strip()).execute()
                    if res.data:
                        st.session_state.user = res.data[0]
                        st.success(f"مرحباً بك أستاذ {res.data[0]['teacher_name']}!")
                        st.rerun()
                    else:
                        st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
                else:
                    st.warning("يرجى إدخال اسم المستخدم وكلمة المرور.")
                    
        # --- تبويب لوحة الأدمن (إنشاء وحذف الحسابات) ---
        with tab_admin:
            st.markdown("##### إدارة حسابات المعلمين (خاص بالجهة المنفذة)")
            admin_pass = st.text_input("كلمة مرور الأدمن:", type="password", key="admin_pass_key")
            
            if admin_pass == ADMIN_PASSWORD:
                st.success("تم التحقق من هويّة الأدمن ✅")
                
                # --- إضافة حساب جديد ---
                st.markdown("###### ➕ إضافة معلم جديد")
                new_teacher = st.text_input("اسم المعلم الكامل (اللقب):")
                new_user = st.text_input("اسم المستخدم الجديد للعميل:")
                new_pass = st.text_input("كلمة المرور للعميل:", type="password", key="new_user_pass_key")
                
                if st.button("➕ إنشاء حساب للعميل", use_container_width=True):
                    if new_teacher and new_user and new_pass:
                        try:
                            supabase.table("users").insert({
                                "username": new_user.strip(),
                                "password_hash": new_pass.strip(),
                                "teacher_name": new_teacher.strip()
                            }).execute()
                            st.success(f"تم إنشاء حساب المعلم '{new_teacher}' بنجاح!")
                            st.rerun()
                        except Exception as e:
                            st.error("حدث خطأ: اسم المستخدم مُسجل بالفعل أو هناك مشكلة بالنظام.")
                    else:
                        st.warning("يرجى استكمال جميع البيانات المطلوبة.")
                
                # --- حذف حساب معلم ---
                st.markdown("---")
                st.markdown("###### 🗑️ حذف حساب معلم")
                res_users = supabase.table("users").select("*").execute()
                if res_users.data:
                    df_users = pd.DataFrame(res_users.data)
                    user_to_delete = st.selectbox("اختر المعلم المراد حذفه:", df_users["teacher_name"].tolist(), key="del_user_select")
                    
                    if st.button("❌ حذف المعلم نهائياً", use_container_width=True):
                        user_id_del = int(df_users[df_users["teacher_name"] == user_to_delete]["id"].values[0])
                        
                        # 1. حذف كافة البيانات المرتبطة بهذا المعلم
                        supabase.table("attendance").delete().eq("user_id", user_id_del).execute()
                        supabase.table("students").delete().eq("user_id", user_id_del).execute()
                        supabase.table("groups").delete().eq("user_id", user_id_del).execute()
                        
                        # 2. حذف المعلم من جدول users
                        supabase.table("users").delete().eq("id", user_id_del).execute()
                        
                        st.success(f"تم حذف حساب المعلم '{user_to_delete}' وجميع بياناته بنجاح!")
                        st.rerun()
                else:
                    st.info("لا يوجد مستخدمون حالياً.")
                    
            elif admin_pass:
                st.error("كلمة مرور الأدمن غير صحيحة.")

        # --- التذييل الخاص بالتواصل ---
        st.markdown(
            """
            <br><hr>
            <center>
                <p style='font-size: 15px; margin-bottom: 12px;'>للحصول على حساب جديد أو تجديد الاشتراك، يرجى التواصل <b>(Tech Builder)</b></p>
                <a href='https://wa.me/201218505995' target='_blank' style='text-decoration: none;'>
                    <button style='background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold;'>
                        💬 التواصل عبر واتساب: 01218505995
                    </button>
                </a>
            </center>
            """, 
            unsafe_allow_html=True
        )

    # إضافة الفوتر في صفحة تسجيل الدخول
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
# 6. القائمة الجانبية وزر الخروج
# ---------------------------------------------------------
st.sidebar.title(f"👤 مرحباً: أ/ {teacher_display_name}")
if st.sidebar.button("تسجيل الخروج 🚪"):
    st.session_state.user = None
    st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "انتقل إلى:",
    [
        "1️⃣ تكويد وإدارة المجموعات والطلاب",
        "2️⃣ تسجيل الحضور والدرجات والدفع",
        "3️⃣ كشف حساب طالب (تاريخ/حضور/درجات)",
        "4️⃣ تقرير موقف الدفع للطلاب",
        "5️⃣ تقرير الإيرادات والتحصيلات"
    ]
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
                        "group_name": new_group.strip()
                    }).execute()
                    st.success(f"تمت إضافة المجموعة '{new_group}' بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error("حدث خطأ أثناء إضافة المجموعة.")
            else:
                st.warning("يرجى إدخال اسم المجموعة.")

    with col2:
        st.subheader("➕ إضافة طالب إلى مجموعة")
        res_groups = supabase.table("groups").select("*").eq("user_id", current_user_id).execute()
        df_groups = pd.DataFrame(res_groups.data)
        
        if not df_groups.empty:
            group_selected = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist())
            student_name = st.text_input("اسم الطالب:")
            
            if st.button("حفظ الطالب"):
                if student_name.strip():
                    group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
                    supabase.table("students").insert({
                        "user_id": current_user_id,
                        "group_id": group_id,
                        "student_name": student_name.strip()
                    }).execute()
                    st.success(f"تمت إضافة الطالب '{student_name}' إلى مجموعة '{group_selected}'.")
                    st.rerun()
                else:
                    st.warning("يرجى إدخال اسم الطالب.")
        else:
            st.info("قم بإضافة مجموعة أولاً لتمكين إضافة الطلاب.")

    st.markdown("---")
    
    # قسم الحذف والإدارة
    st.subheader("🗑️ إدارة وحذف البيانات")
    del_tab1, del_tab2 = st.tabs(["حذف طالب", "حذف مجموعة كاملة"])
    
    with del_tab1:
        res_stds = supabase.table("students").select("*").eq("user_id", current_user_id).execute()
        df_all_stds = pd.DataFrame(res_stds.data)
        if not df_all_stds.empty:
            std_to_del = st.selectbox("اختر الطالب للمسح:", df_all_stds["student_name"].tolist(), key="del_std_select")
            if st.button("حذف الطالب المحدد"):
                std_id = int(df_all_stds[df_all_stds["student_name"] == std_to_del]["id"].values[0])
                supabase.table("students").delete().eq("id", std_id).execute()
                st.success(f"تم حذف الطالب '{std_to_del}' بنجاح!")
                st.rerun()
        else:
            st.info("لا يوجد طلاب لحذفهم.")

    with del_tab2:
        if not df_groups.empty:
            grp_to_del = st.selectbox("اختر المجموعة للمسح:", df_groups["group_name"].tolist(), key="del_grp_select")
            if st.button("حذف المجموعة وكل طلابها"):
                grp_id = int(df_groups[df_groups["group_name"] == grp_to_del]["id"].values[0])
                supabase.table("groups").delete().eq("id", grp_id).execute()
                st.success(f"تم حذف المجموعة '{grp_to_del}' بنجاح!")
                st.rerun()
        else:
            st.info("لا توجد مجموعات لحذفها.")

    st.markdown("---")
    st.subheader("📋 قائمة المجموعات والطلاب المسجلين حالياً")
    res_full = supabase.table("students").select("id, student_name, groups(group_name)").eq("user_id", current_user_id).execute()
    if res_full.data:
        formatted_data = []
        for item in res_full.data:
            formatted_data.append({
                "ID الطالب": item["id"],
                "اسم الطالب": item["student_name"],
                "المجموعة": item["groups"]["group_name"] if item.get("groups") else "-"
            })
        st.dataframe(pd.DataFrame(formatted_data), use_container_width=True)
    else:
        st.info("لا يوجد طلاب مسجلون بعد.")

# ---------------------------------------------------------
# الصفحة الثانية: تسجيل الحضور والدرجات والدفع
# ---------------------------------------------------------
elif menu == "2️⃣ تسجيل الحضور والدرجات والدفع":
    st.header("📝 تسجيل الحضور والدرجات والتحصيل")
    
    res_groups = supabase.table("groups").select("*").eq("user_id", current_user_id).execute()
    df_groups = pd.DataFrame(res_groups.data)
    
    if df_groups.empty:
        st.warning("لا توجد مجموعات معرفة. يرجى إضافة مجموعات أولاً.")
    else:
        group_selected = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist())
        group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
        session_date = st.date_input("تاريخ الحصة:", date.today())
        
        res_stds = supabase.table("students").select("id, student_name").eq("group_id", group_id).execute()
        students_in_group = pd.DataFrame(res_stds.data)
        
        if students_in_group.empty:
            st.info("لا يوجد طلاب مسجلون في هذه المجموعة.")
        else:
            st.write(f"### تسجيل بيانات حصة يوم: {session_date}")
            
            with st.form("attendance_form"):
                records = []
                for idx, row in students_in_group.iterrows():
                    st.markdown(f"**👤 الطالب: {row['student_name']}**")
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    res_att = supabase.table("attendance").select("id").eq("student_id", row["id"]).execute()
                    sess_count = len(res_att.data)
                    is_fourth = (sess_count + 1) % 4 == 0
                    
                    with col1:
                        status = st.radio(f"الحالة ({row['student_name']}):", ["حضر", "غائب"], key=f"status_{row['id']}")
                    with col2:
                        score = st.number_input(f"درجة الامتحان:", min_value=0.0, max_value=100.0, value=0.0, key=f"score_{row['id']}")
                    with col3:
                        if is_fourth:
                            st.warning("⚠️ خانة تحصيل (الحصة الرابعة)")
                            paid = st.checkbox("تم سداد المبلغ", key=f"paid_{row['id']}")
                        else:
                            st.write("حصة عادية")
                            paid = st.checkbox("سداد اختياري", key=f"paid_{row['id']}")
                    st.markdown("---")
                    
                    records.append({
                        "user_id": current_user_id,
                        "student_id": int(row["id"]),
                        "group_id": group_id,
                        "session_date": str(session_date),
                        "attended": True if status == "حضر" else False,
                        "paid": 1 if paid else 0
                    })
                
                submit = st.form_submit_button("💾 حفظ بيانات الحصة")
                if submit:
                    supabase.table("attendance").insert(records).execute()
                    st.success("تم حفظ الحضور والدرجات والتحصيلات بنجاح!")

# ---------------------------------------------------------
# الصفحة الثالثة: كشف حساب طالب
# ---------------------------------------------------------
elif menu == "3️⃣ كشف حساب طالب (تاريخ/حضور/درجات)":
    st.header("🔍 كشف حضور ودرجات طالب")
    
    res_groups = supabase.table("groups").select("*").eq("user_id", current_user_id).execute()
    df_groups = pd.DataFrame(res_groups.data)
    
    if not df_groups.empty:
        col1, col2 = st.columns(2)
        with col1:
            group_selected = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist())
            group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
            
        res_stds = supabase.table("students").select("id, student_name").eq("group_id", group_id).execute()
        students_in_group = pd.DataFrame(res_stds.data)
        
        with col2:
            if not students_in_group.empty:
                student_selected = st.selectbox("اختر الطالب:", students_in_group["student_name"].tolist())
                student_id = int(students_in_group[students_in_group["student_name"] == student_selected]["id"].values[0])
            else:
                student_selected = None

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("من تاريخ:", date(2026, 1, 1))
        with col_d2:
            end_date = st.date_input("إلى تاريخ:", date.today())

        if student_selected:
            res_att = supabase.table("attendance").select("*").eq("student_id", student_id).gte("session_date", str(start_date)).lte("session_date", str(end_date)).execute()
            if res_att.data:
                df_rep = pd.DataFrame(res_att.data)
                df_rep["حالة الحضور"] = df_rep["attended"].apply(lambda x: "حضر" if x else "غائب")
                df_rep["حالة الدفع"] = df_rep["paid"].apply(lambda x: "تم الدفع" if x == 1 else "لم يدفع")
                df_display = df_rep[["session_date", "حالة الحضور", "حالة الدفع"]].rename(columns={"session_date": "تاريخ الحصة"})
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("لا توجد سجلات لهذا الطالب في هذه الفترة.")

# ---------------------------------------------------------
# الصفحة الرابعة: تقرير موقف الدفع للطلاب
# ---------------------------------------------------------
elif menu == "4️⃣ تقرير موقف الدفع للطلاب":
    st.header("📊 تقرير سداد المصروفات حسب المجموعة")
    
    res_groups = supabase.table("groups").select("*").eq("user_id", current_user_id).execute()
    df_groups = pd.DataFrame(res_groups.data)
    
    if not df_groups.empty:
        group_selected = st.selectbox("اختر المجموعة للتقرير:", df_groups["group_name"].tolist())
        group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
        
        res_stds = supabase.table("students").select("id, student_name").eq("group_id", group_id).execute()
        df_stds = pd.DataFrame(res_stds.data)
        
        if not df_stds.empty:
            report_list = []
            for _, std in df_stds.iterrows():
                res_att = supabase.table("attendance").select("paid").eq("student_id", std["id"]).execute()
                paid_count = sum([1 for item in res_att.data if item.get("paid") == 1])
                report_list.append({
                    "اسم الطالب": std["student_name"],
                    "إجمالي الحصص المسجلة": len(res_att.data),
                    "عدد مرات السداد": paid_count,
                    "موقف الدفع": "مسدد ✅" if paid_count > 0 else "غير مسدد ❌"
                })
            st.dataframe(pd.DataFrame(report_list), use_container_width=True)

# ---------------------------------------------------------
# الصفحة الخامسة: تقرير الإيرادات والتحصيلات
# ---------------------------------------------------------
elif menu == "5️⃣ تقرير الإيرادات والتحصيلات":
    st.header("💰 تقرير المتحصلات المالية للمجموعات")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ:", date(2026, 1, 1), key="rev_start")
    with col2:
        end_date = st.date_input("إلى تاريخ:", date.today(), key="rev_end")
        
    session_price = st.number_input("سعر الاشتراك / الحصة الرابعة (جنيه):", min_value=0, value=200)

    res_att = supabase.table("attendance").select("paid, groups(group_name)").eq("user_id", current_user_id).gte("session_date", str(start_date)).lte("session_date", str(end_date)).execute()
    
    if res_att.data:
        paid_records = [r for r in res_att.data if r.get("paid") == 1]
        if paid_records:
            df_rev = pd.DataFrame(paid_records)
            df_rev["المجموعة"] = df_rev["groups"].apply(lambda x: x["group_name"] if x else "غير محدد")
            summary = df_rev.groupby("المجموعة").size().reset_index(name="عدد المدفوعات")
            summary["إجمالي المبلغ المحصل"] = summary["عدد المدفوعات"] * session_price
            
            st.dataframe(summary, use_container_width=True)
            st.metric("إجمالي التحصيلات الكلية", f"{summary['إجمالي المبلغ المحصل'].sum()} جنيه")
        else:
            st.info("لا توجد تحصيلات مالية في هذه الفترة.")
    else:
        st.info("لا توجد تحصيلات مالية في هذه الفترة.")

# ---------------------------------------------------------
# عرض الفوتر الكودي المنفصل أسفل صفحات التطبيق الرئيسية
# ---------------------------------------------------------
render_footer()
