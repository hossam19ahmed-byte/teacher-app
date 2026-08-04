import sqlite3
import pandas as pd
import streamlit as st
from datetime import date

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tech Builder - نظام إدارة المدرسين",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. بيانات المستخدمين (اسم المستخدم : كلمة المرور)
# ---------------------------------------------------------
USERS = {
    "hossam": "123456",
    "ahmed": "ahmed1994",
    "teacher": "pass1234"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------------------------------------------------
# 3. شاشة تسجيل الدخول
# ---------------------------------------------------------
def login_screen():
    st.title("🔐 تسجيل الدخول - نظام إدارة المدرسين")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("اسم المستخدم:")
        password = st.text_input("كلمة المرور:", type="password")
        login_btn = st.button("دخول", use_container_width=True)
        
        if login_btn:
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"مرحباً بك {username}! جاري التحميل...")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ---------------------------------------------------------
# 4. قاعدة البيانات (تأتي بعد تسجيل الدخول)
# ---------------------------------------------------------
conn = sqlite3.connect("teacher_data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    group_id INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    group_id INTEGER,
    session_date DATE,
    status TEXT,
    exam_score REAL,
    paid INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
)
""")
conn.commit()

# ---------------------------------------------------------
# 5. القائمة الجانبية وزر الخروج
# ---------------------------------------------------------
st.sidebar.title(f"👤 مرحباً: {st.session_state.username}")
if st.sidebar.button("تسجيل الخروج 🚪"):
    st.session_state.logged_in = False
    st.session_state.username = ""
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
                    cursor.execute("INSERT INTO groups (group_name) VALUES (?)", (new_group.strip(),))
                    conn.commit()
                    st.success(f"تمت إضافة المجموعة '{new_group}' بنجاح!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("هذه المجموعة مضافة بالفعل.")
            else:
                st.warning("يرجى إدخال اسم المجموعة.")

    with col2:
        st.subheader("➕ إضافة طالب إلى مجموعة")
        df_groups = pd.read_sql_query("SELECT * FROM groups", conn)
        
        if not df_groups.empty:
            group_selected = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist())
            student_name = st.text_input("اسم الطالب:")
            
            if st.button("حفظ الطالب"):
                if student_name.strip():
                    group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
                    cursor.execute("INSERT INTO students (student_name, group_id) VALUES (?, ?)", (student_name.strip(), group_id))
                    conn.commit()
                    st.success(f"تمت إضافة الطالب '{student_name}' إلى مجموعة '{group_selected}'.")
                    st.rerun()
                else:
                    st.warning("يرجى إدخال اسم الطالب.")
        else:
            st.info("قم بإضافة مجموعة أولاً لتمكين إضافة الطلاب.")

    st.markdown("---")
    
    # ---------------------------------------------------------
    # قسم حذف وتعديل البيانات
    # ---------------------------------------------------------
    st.subheader("🗑️ إدارة وحذف البيانات (للتجربة والمسح)")
    
    del_tab1, del_tab2, del_tab3 = st.tabs(["حذف طالب", "حذف مجموعة كاملة", "⚠️ مسح قاعدة البيانات بالكامل"])
    
    with del_tab1:
        df_all_stds = pd.read_sql_query("SELECT id, student_name FROM students", conn)
        if not df_all_stds.empty:
            std_to_del = st.selectbox("اختر الطالب للمسح:", df_all_stds["student_name"].tolist(), key="del_std_select")
            if st.button("حذف الطالب المحدد"):
                std_id = int(df_all_stds[df_all_stds["student_name"] == std_to_del]["id"].values[0])
                cursor.execute("DELETE FROM attendance WHERE student_id = ?", (std_id,))
                cursor.execute("DELETE FROM students WHERE id = ?", (std_id,))
                conn.commit()
                st.success(f"تم حذف الطالب '{std_to_del}' وكل سجلاته بنجاح!")
                st.rerun()
        else:
            st.info("لا يوجد طلاب لحذفهم.")

    with del_tab2:
        if not df_groups.empty:
            grp_to_del = st.selectbox("اختر المجموعة للمسح:", df_groups["group_name"].tolist(), key="del_grp_select")
            if st.button("حذف المجموعة وكل طلابها"):
                grp_id = int(df_groups[df_groups["group_name"] == grp_to_del]["id"].values[0])
                cursor.execute("DELETE FROM attendance WHERE group_id = ?", (grp_id,))
                cursor.execute("DELETE FROM students WHERE group_id = ?", (grp_id,))
                cursor.execute("DELETE FROM groups WHERE id = ?", (grp_id,))
                conn.commit()
                st.success(f"تم حذف المجموعة '{grp_to_del}' وجميع طلابها وسجلاتها بنجاح!")
                st.rerun()
        else:
            st.info("لا توجد مجموعات لحذفها.")

    with del_tab3:
        st.error("تنبيه: هذا الخيار سيقوم بمسح جميع المجموعات والطلاب وسجلات الحضور والدفع نهائياً!")
        if st.button("🔥 مسح كافة البيانات وتصفير النظام"):
            cursor.execute("DELETE FROM attendance")
            cursor.execute("DELETE FROM students")
            cursor.execute("DELETE FROM groups")
            conn.commit()
            st.success("تم مسح كافة البيانات بنجاح وأصبح النظام خالياً تماماً!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 قائمة المجموعات والطلاب المسجلين حالياً")
    df_all_students = pd.read_sql_query("""
        SELECT s.id AS 'ID الطالب', s.student_name AS 'اسم الطالب', g.group_name AS 'المجموعة'
        FROM students s
        JOIN groups g ON s.group_id = g.id
    """, conn)
    st.dataframe(df_all_students, use_container_width=True)

# ---------------------------------------------------------
# باقي الصفحات (حضور - كشف حساب - تقارير)
# ---------------------------------------------------------
elif menu == "2️⃣ تسجيل الحضور والدرجات والدفع":
    st.header("📝 تسجيل الحضور والدرجات والتحصيل")
    
    df_groups = pd.read_sql_query("SELECT * FROM groups", conn)
    if df_groups.empty:
        st.warning("لا توجد مجموعات معرفة. يرجى إضافة مجموعات أولاً.")
    else:
        group_selected = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist())
        group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
        
        session_date = st.date_input("تاريخ الحصه:", date.today())
        
        students_in_group = pd.read_sql_query("SELECT id, student_name FROM students WHERE group_id = ?", conn, params=(group_id,))
        
        if students_in_group.empty:
            st.info("لا يوجد طلاب مسجلون في هذه المجموعة.")
        else:
            st.write(f"### تسجيل بيانات حصة يوم: {session_date}")
            
            with st.form("attendance_form"):
                records = []
                for idx, row in students_in_group.iterrows():
                    st.markdown(f"**👤 الطالب: {row['student_name']}**")
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    count_query = "SELECT COUNT(*) FROM attendance WHERE student_id = ?"
                    sess_count = cursor.execute(count_query, (row["id"],)).fetchone()[0]
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
                        "student_id": row["id"],
                        "group_id": group_id,
                        "session_date": str(session_date),
                        "status": status,
                        "exam_score": score,
                        "paid": 1 if paid else 0
                    })
                
                submit = st.form_submit_button("💾 حفظ بيانات الحصة")
                if submit:
                    for rec in records:
                        cursor.execute("""
                            INSERT INTO attendance (student_id, group_id, session_date, status, exam_score, paid)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (rec["student_id"], rec["group_id"], rec["session_date"], rec["status"], rec["exam_score"], rec["paid"]))
                    conn.commit()
                    st.success("تم حفظ الحضور والدرجات والتحصيلات بنجاح!")

elif menu == "3️⃣ كشف حساب طالب (تاريخ/حضور/درجات)":
    st.header("🔍 كشف حضور ودرجات طالب")
    
    df_groups = pd.read_sql_query("SELECT * FROM groups", conn)
    if not df_groups.empty:
        col1, col2 = st.columns(2)
        with col1:
            group_selected = st.selectbox("اختر المجموعة:", df_groups["group_name"].tolist())
            group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
            
        students_in_group = pd.read_sql_query("SELECT id, student_name FROM students WHERE group_id = ?", conn, params=(group_id,))
        
        with col2:
            if not students_in_group.empty:
                student_selected = st.selectbox("اختر الطالب:", students_in_group["student_name"].tolist())
                student_id = int(students_in_group[students_in_group["student_name"] == student_selected]["id"].values[0])
            else:
                student_selected = None

        st.subheader("فلترة بالتاريخ:")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("من تاريخ:", date(2026, 1, 1))
        with col_d2:
            end_date = st.date_input("إلى تاريخ:", date.today())

        if student_selected:
            query = """
                SELECT session_date AS 'تاريخ الحصة', status AS 'حالة الحضور', exam_score AS 'درجة الامتحان',
                       CASE WHEN paid = 1 THEN 'تم الدفع' ELSE 'لم يدفع' END AS 'حالة الدفع'
                FROM attendance
                WHERE student_id = ? AND session_date BETWEEN ? AND ?
                ORDER BY session_date DESC
            """
            df_student_report = pd.read_sql_query(query, conn, params=(student_id, str(start_date), str(end_date)))
            st.dataframe(df_student_report, use_container_width=True)

elif menu == "4️⃣ تقرير موقف الدفع للطلاب":
    st.header("📊 تقرير سداد المصروفات حسب المجموعة")
    
    df_groups = pd.read_sql_query("SELECT * FROM groups", conn)
    if not df_groups.empty:
        group_selected = st.selectbox("اختر المجموعة للتقرير:", df_groups["group_name"].tolist())
        group_id = int(df_groups[df_groups["group_name"] == group_selected]["id"].values[0])
        
        query = """
            SELECT s.student_name AS 'اسم الطالب',
                   COUNT(a.id) AS 'إجمالي الحضور/الغياب',
                   SUM(a.paid) AS 'عدد مرات السداد'
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id
            WHERE s.group_id = ?
            GROUP BY s.id
        """
        df_pay_report = pd.read_sql_query(query, conn, params=(group_id,))
        df_pay_report["موقف الدفع"] = df_pay_report["عدد مرات السداد"].apply(lambda x: "مسدد ✅" if x and x > 0 else "غير مسدد ❌")
        
        st.dataframe(df_pay_report, use_container_width=True)

elif menu == "5️⃣ تقرير الإيرادات والتحصيلات":
    st.header("💰 تقرير المتحصلات المالية للمجموعات")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ:", date(2026, 1, 1), key="rev_start")
    with col2:
        end_date = st.date_input("إلى تاريخ:", date.today(), key="rev_end")
        
    session_price = st.number_input("سعر الاشتراك / الحصة الرابعة (جنيه):", min_value=0, value=200)

    query = """
        SELECT g.group_name AS 'المجموعة',
               SUM(a.paid) AS 'عدد المدفوعات'
        FROM attendance a
        JOIN groups g ON a.group_id = g.id
        WHERE a.session_date BETWEEN ? AND ?
        GROUP BY g.id
    """
    df_rev = pd.read_sql_query(query, conn, params=(str(start_date), str(end_date)))
    
    if not df_rev.empty:
        df_rev["إجمالي المبلغ المحصل"] = df_rev["عدد المدفوعات"] * session_price
        st.dataframe(df_rev, use_container_width=True)
        st.metric("إجمالي التحصيلات الكلية", f"{df_rev['إجمالي المبلغ المحصل'].sum()} جنيه")
    else:
        st.info("لا توجد تحصيلات مالية في هذه الفترة.")
