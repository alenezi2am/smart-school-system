from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'school_secret_key_123'

def init_db():
    conn = sqlite3.connect('school_v2.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            stage TEXT DEFAULT 'المرحلة المتوسطة',
            class_name TEXT DEFAULT '3 / 1',
            subject TEXT DEFAULT 'عام'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT UNIQUE NOT NULL,
            stage TEXT DEFAULT 'المرحلة المتوسطة',
            class_name TEXT DEFAULT '3 / 1',
            status TEXT DEFAULT 'حاضر'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subject_grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            teacher_name TEXT NOT NULL,
            hw_grade INTEGER DEFAULT 0,
            exam1_grade INTEGER DEFAULT 0,
            exam2_grade INTEGER DEFAULT 0,
            behavior_grade INTEGER DEFAULT 0,
            final_grade INTEGER DEFAULT 0,
            total_grade INTEGER DEFAULT 0,
            attendance TEXT DEFAULT 'حاضر'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            class_name TEXT DEFAULT '3 / 1'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canteen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            price TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'متوفر'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canteen_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price TEXT NOT NULL,
            status TEXT DEFAULT 'قيد التجهيز',
            cancel_reason TEXT DEFAULT ''
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS school_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            day_name TEXT NOT NULL,
            p1 TEXT, p2 TEXT, p3 TEXT, p4 TEXT, p5 TEXT, p6 TEXT, p7 TEXT
        )
    ''')
    
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, stage, class_name, subject) VALUES ('admin', 'admin123', 'admin', 'الإدارة', 'الكل', 'إدارة النظام')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, stage, class_name, subject) VALUES ('canteen', 'canteen123', 'canteen', 'المقصف', 'الكل', 'إدارة المقصف')")

    cursor.execute("SELECT COUNT(*) FROM school_schedules")
    if cursor.fetchone()[0] == 0:
        schedules_data = [
            ('3 / 1', 'الأحد', 'انجلز', 'فنية', 'لغتي', 'علوم', 'رياضيا', 'انجلز', 'علوم'),
            ('3 / 1', 'الإثنين', 'بدنية', 'رياضيا', 'لغتي', 'علوم', 'رياضيا', 'اسلامية', 'انجلز'),
            ('3 / 1', 'الثلاثاء', 'رقمية', 'علوم', 'اسلامية', 'انجلز', 'رياضيا', 'لغتي', '-'),
            ('3 / 1', 'الأربعاء', 'حياتية', 'اسلامية', 'رياضيا', 'اجتماع', 'لغتي', 'علوم', '-'),
            ('3 / 1', 'الخميس', 'رقمية', 'اسلامية', 'اجتماع', 'رياضيا', 'اسلامية', 'انجلز', 'تفكير'),
            ('3 / 2', 'الأحد', 'رياضيا', 'رياضيا', 'لغتي', 'علوم', 'بدنية', 'اسلامية', 'اجتماع'),
            ('3 / 2', 'الإثنين', 'فنية', 'لغتي', 'اسلامية', 'علوم', 'حياتية', 'رياضيا', 'انجلز'),
            ('3 / 2', 'الثلاثاء', 'اسلامية', 'انجلز', 'علوم', 'لغتي', 'رياضيا', 'انجلز', 'بدنية'),
            ('3 / 2', 'الأربعاء', 'رقمية', 'انجلز', 'رياضيا', 'علوم', 'لغتي', 'انجلز', 'اجتماع'),
            ('3 / 2', 'الخميس', 'رياضيا', 'اسلامية', 'لغتي', 'رقومية', 'تفكير', 'اجتماع', '-'),
            ('3 / 3', 'الأحد', 'علوم', 'بدنية', 'اسلامية', 'اجتماع', 'رياضيا', 'انجلز', 'اسلامية'),
            ('3 / 3', 'الإثنين', 'لغتي', 'انجلز', 'علوم', 'رياضيا', 'اسلامية', 'رياضيا', 'انجلز'),
            ('3 / 3', 'الثلاثاء', 'بدنية', 'رياضيا', 'تفكير', 'رياضيا', 'انجلز', 'اسلامية', '-'),
            ('3 / 3', 'الأربعاء', 'اسلامية', 'انجلز', 'رقومية', 'رياضيا', 'اسلامية', 'انجلز', 'رقومية'),
            ('3 / 3', 'الخميس', 'اسلامية', 'رياضيا', 'علوم', 'لغتي', 'رياضيا', 'لغتي', '-'),
            ('3 / 4', 'الأحد', 'تفكير', 'علوم', 'اجتماع', 'رياضيا', 'اسلامية', 'بدنية', 'انجلز'),
            ('3 / 4', 'الإثنين', 'علوم', 'اسلامية', 'رياضيا', 'رقمية', 'لغتي', 'انجلز', 'رياضيا'),
            ('3 / 4', 'الثلاثاء', 'بدنية', 'رياضيا', 'انجلز', 'رياضيا', 'اسلامية', 'لغتي', 'اسلامية'),
            ('3 / 4', 'الأربعاء', 'علوم', 'لغتي', 'اسلامية', 'رياضيا', 'انجلز', 'رقمية', 'انجلز'),
            ('3 / 4', 'الخميس', 'اسلامية', 'رياضيا', 'حياتية', 'لغتي', 'اجتماع', 'تفكير', '-'),
            ('3 / 5', 'الأحد', 'انجلز', 'اجتماع', 'رياضيا', 'علوم', 'بدنية', 'اسلامية', 'لغتي'),
            ('3 / 5', 'الإثنين', 'فنية', 'رياضيا', 'اسلامية', 'علوم', 'حياتية', 'انجلز', 'اسلامية'),
            ('3 / 5', 'الثلاثاء', 'اسلامية', 'انجلز', 'علوم', 'لغتي', 'رياضيا', 'انجلز', 'بدنية'),
            ('3 / 5', 'الأربعاء', 'رقمية', 'انجلز', 'رياضيا', 'علوم', 'لغتي', 'انجلز', 'اجتماع'),
            ('3 / 5', 'الخميس', 'رياضيا', 'اسلامية', 'لغتي', 'رقومية', 'تفكير', 'اجتماع', '-'),
            ('3 / 6', 'الأحد', 'علوم', 'بدنية', 'اسلامية', 'اجتماع', 'رياضيا', 'انجلز', 'لغتي'),
            ('3 / 6', 'الإثنين', 'لغتي', 'انجلز', 'علوم', 'رياضيا', 'اسلامية', 'رياضيا', 'تفكير'),
            ('3 / 6', 'الثلاثاء', 'رياضيا', 'اسلامية', 'بدنية', 'تفكير', 'انجلز', 'علوم', 'انجلز'),
            ('3 / 6', 'الأربعاء', 'اسلامية', 'انجلز', 'لغتي', 'رياضيا', 'اجتماع', 'اسلامية', 'رياضيا'),
            ('3 / 6', 'الخميس', 'علوم', 'رياضيا', 'لغتي', 'اسلامية', 'بدنية', 'فنية', '-'),
            ('3 / 7', 'الأحد', 'علوم', 'اجتماع', 'اسلامية', 'رياضيا', 'انجلز', 'حياتية', '-'),
            ('3 / 7', 'الإثنين', 'رياضيا', 'بدنية', 'اسلامية', 'اجتماع', 'انجلز', 'انجلز', 'لغتي'),
            ('3 / 7', 'الثلاثاء', 'اسلامية', 'رياضيا', 'علوم', 'رقمية', 'رياضيا', 'تفكير', '-'),
            ('3 / 7', 'الأربعاء', 'رياضيا', 'علوم', 'فنية', 'علوم', 'اسلامية', 'لغتي', '-'),
            ('3 / 7', 'الخميس', 'بدنية', 'اسلامية', 'انجلز', 'علوم', 'لغتي', 'رياضيا', '-'),
            ('3 / 8', 'الأحد', 'انجلز', 'علوم', 'رياضيا', 'تفكير', 'رقمية', 'لغتي', 'حياتية'),
            ('3 / 8', 'الإثنين', 'اسلامية', 'رياضيا', 'علوم', 'فنية', 'لغتي', 'انجلز', 'اسلامية'),
            ('3 / 8', 'الثلاثاء', 'رياضيا', 'علوم', 'بدنية', 'اسلامية', 'رقمية', 'انجلز', '-'),
            ('3 / 8', 'الأربعاء', 'رياضيا', 'علوم', 'اجتماع', 'انجلز', 'اسلامية', 'رياضيا', 'اسلامية'),
            ('3 / 8', 'الخميس', 'بدنية', 'اسلامية', 'لغتي', 'انجلز', 'علوم', 'علوم', '-')
        ]
        cursor.executemany("INSERT INTO school_schedules (class_name, day_name, p1, p2, p3, p4, p5, p6, p7) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", schedules_data)

    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            session['stage'] = user[4]
            session['class_name'] = user[5]
            session['subject'] = user[6]
            
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[3] == 'canteen':
                return redirect(url_for('canteen_dashboard'))
            elif user[3] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return render_template('login.html', error='اسم المستخدم أو كلمة المرور غير صحيحة')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        stage = request.form['stage']
        subject = request.form.get('subject', 'عام') if role == 'teacher' else 'عام'
        class_num = request.form.get('class_num', '1')
        class_name = f"3 / {class_num}" if role == 'student' else 'جميع الفصول'
        
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        
        if role == 'teacher':
            cursor.execute("SELECT * FROM users WHERE role = 'teacher' AND subject = ?", (subject,))
            if cursor.fetchone():
                conn.close()
                return render_template('register.html', error=f'عذراً، مادة ({subject}) مسجلة مسبقاً لمعلم آخر!')
        
        try:
            cursor.execute("INSERT INTO users (username, password, role, stage, class_name, subject) VALUES (?, ?, ?, ?, ?, ?)", 
                           (username, password, role, stage, class_name, subject))
            
            if role == 'student':
                cursor.execute("INSERT INTO students_list (student_name, stage, class_name, status) VALUES (?, ?, ?, 'حاضر')", (username, stage, class_name))
                
                cursor.execute("SELECT username, subject FROM users WHERE role = 'teacher'")
                teachers = cursor.fetchall()
                for t in teachers:
                    cursor.execute("""
                        INSERT INTO subject_grades (student_name, subject_name, teacher_name, hw_grade, exam1_grade, exam2_grade, behavior_grade, final_grade, total_grade, attendance)
                        VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 'حاضر')
                    """, (username, t[1], t[0]))
                               
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            error = 'اسم المستخدم موجود مسبقاً، اختر اسماً آخر!'
            
    return render_template('register.html', error=error)

@app.route('/teacher', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
        
    teacher_subject = session.get('subject')
    selected_class = request.args.get('class_filter', '3 / 1')
    
    conn = sqlite3.connect('school_v2.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, s.student_name, s.stage, s.class_name, s.status, 
               COALESCE(g.hw_grade, 0), COALESCE(g.exam1_grade, 0), COALESCE(g.exam2_grade, 0), 
               COALESCE(g.behavior_grade, 0), COALESCE(g.final_grade, 0), COALESCE(g.total_grade, 0), 
               COALESCE(g.attendance, 'حاضر'), COALESCE(g.id, 0)
        FROM students_list s
        LEFT JOIN subject_grades g ON s.student_name = g.student_name AND g.subject_name = ?
        WHERE s.class_name = ?
        ORDER BY s.student_name ASC
    """, (teacher_subject, selected_class))
        
    students = cursor.fetchall()
    
    # حساب إحصائيات سريعة للمعلم (متوسط الدرجات وإجمالي الطلاب)
    total_stu_count = len(students)
    avg_total_grade = 0
    if total_stu_count > 0:
        sum_grades = sum(stu[10] for stu in students)
        avg_total_grade = round(sum_grades / total_stu_count, 1)

    cursor.execute("SELECT * FROM homework")
    homeworks = cursor.fetchall()

    cursor.execute("SELECT day_name, p1, p2, p3, p4, p5, p6, p7 FROM school_schedules WHERE class_name = ?", (selected_class,))
    schedule_rows = cursor.fetchall()
    
    conn.close()
    
    return render_template('teacher.html', students=students, homeworks=homeworks, teacher_subject=teacher_subject, 
                           selected_class=selected_class, schedule_rows=schedule_rows, total_stu_count=total_stu_count, avg_total_grade=avg_total_grade)

@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    if 'role' in session and session['role'] == 'teacher':
        hw = int(request.form['hw_grade'])
        exam1 = int(request.form['exam1_grade'])
        exam2 = int(request.form['exam2_grade'])
        behavior = int(request.form['behavior_grade'])
        final = int(request.form['final_grade'])
        attendance = request.form.get('attendance', 'حاضر')
        
        total_grade = hw + exam1 + exam2 + behavior + final
        subject_name = session.get('subject')
        teacher_name = session.get('username')
        
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT student_name FROM students_list WHERE id = ?", (student_id,))
        stu = cursor.fetchone()
        
        if stu:
            student_name = stu[0]
            cursor.execute("SELECT id FROM subject_grades WHERE student_name = ? AND subject_name = ?", (student_name, subject_name))
            g_row = cursor.fetchone()
            
            if not g_row:
                cursor.execute("""
                    INSERT INTO subject_grades (student_name, subject_name, teacher_name, hw_grade, exam1_grade, exam2_grade, behavior_grade, final_grade, total_grade, attendance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_name, subject_name, teacher_name, hw, exam1, exam2, behavior, final, total_grade, attendance))
            else:
                cursor.execute("""
                    UPDATE subject_grades 
                    SET hw_grade = ?, exam1_grade = ?, exam2_grade = ?, behavior_grade = ?, final_grade = ?, total_grade = ?, attendance = ? 
                    WHERE student_name = ? AND subject_name = ?
                """, (hw, exam1, exam2, behavior, final, total_grade, attendance, student_name, subject_name))
                
            conn.commit()
        conn.close()
    return redirect(url_for('teacher_dashboard'))

@app.route('/add_homework', methods=['POST'])
def add_homework():
    if 'role' in session and session['role'] == 'teacher':
        teacher_name = session['username']
        subject = session.get('subject', 'المادة')
        title = request.form['title']
        content = request.form['content']
        class_name = request.form['class_name']
        
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO homework (teacher_name, subject, title, content, class_name) VALUES (?, ?, ?, ?, ?)",
                       (teacher_name, subject, title, content, class_name))
        conn.commit()
        conn.close()
    return redirect(url_for('teacher_dashboard'))

@app.route('/student')
def student_dashboard():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('school_v2.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students_list WHERE student_name = ?", (session['username'],))
    student_info = cursor.fetchone()
    
    student_class = student_info[3] if student_info else '3 / 1'

    cursor.execute("""
        SELECT g.subject_name, g.teacher_name, g.hw_grade, g.exam1_grade, g.exam2_grade, g.behavior_grade, g.final_grade, g.total_grade, g.attendance
        FROM subject_grades g
        WHERE g.student_name = ?
    """, (session['username'],))
    grades_data = cursor.fetchall()
    
    cursor.execute("SELECT * FROM homework WHERE class_name = ? OR class_name = 'الكل'", (student_class,))
    homeworks = cursor.fetchall()

    cursor.execute("SELECT * FROM canteen")
    canteen_items = cursor.fetchall()
    
    cursor.execute("SELECT id, item_name, quantity, total_price, status, cancel_reason FROM canteen_orders WHERE student_name = ? AND status != 'تم التسليم'", (session['username'],))
    my_orders = cursor.fetchall()
    
    cursor.execute("SELECT username, subject, stage FROM users WHERE role = 'teacher'")
    real_teachers = cursor.fetchall()

    cursor.execute("SELECT day_name, p1, p2, p3, p4, p5, p6, p7 FROM school_schedules WHERE class_name = ?", (student_class,))
    schedule_rows = cursor.fetchall()
    
    conn.close()
    return render_template('student.html', student_info=student_info, grades_data=grades_data, homeworks=homeworks, canteen_items=canteen_items, my_orders=my_orders, real_teachers=real_teachers, schedule_rows=schedule_rows)

@app.route('/order_canteen', methods=['POST'])
def order_canteen():
    if 'role' in session and session['role'] == 'student':
        student_name = session['username']
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        price_str = request.form['price']
        
        try:
            unit_price = float(price_str.replace('ريال', '').strip())
        except:
            unit_price = 3.00
            
        total_price = f"{unit_price * quantity:.2f} ريال"
        
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO canteen_orders (student_name, item_name, quantity, total_price, status, cancel_reason) VALUES (?, ?, ?, ?, 'قيد التجهيز', '')",
                       (student_name, item_name, quantity, total_price))
        conn.commit()
        conn.close()
    return redirect(url_for('student_dashboard'))

@app.route('/cancel_order_student/<int:order_id>', methods=['POST'])
def cancel_order_student(order_id):
    if 'role' in session and session['role'] == 'student':
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE canteen_orders SET status = 'ملغي من الطالب' WHERE id = ? AND student_name = ?", (order_id, session['username']))
        conn.commit()
        conn.close()
    return redirect(url_for('student_dashboard'))

@app.route('/print_certificate')
def print_certificate():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('school_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students_list WHERE student_name = ?", (session['username'],))
    student_info = cursor.fetchone()
    
    cursor.execute("""
        SELECT g.subject_name, g.teacher_name, g.hw_grade, g.exam1_grade, g.exam2_grade, g.behavior_grade, g.final_grade, g.total_grade, g.attendance
        FROM subject_grades g
        WHERE g.student_name = ?
    """, (session['username'],))
    grades_data = cursor.fetchall()
    conn.close()
    
    return render_template('certificate.html', student_info=student_info, grades_data=grades_data)

@app.route('/canteen_dashboard')
def canteen_dashboard():
    if 'role' not in session or session['role'] != 'canteen':
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('school_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM canteen")
    canteen_items = cursor.fetchall()
    
    cursor.execute("SELECT id, student_name, item_name, quantity, total_price, status, cancel_reason FROM canteen_orders WHERE status != 'تم التسليم'")
    canteen_orders = cursor.fetchall()
    conn.close()
    
    return render_template('canteen.html', canteen_items=canteen_items, canteen_orders=canteen_orders)

@app.route('/add_canteen_item', methods=['POST'])
def add_canteen_item():
    if 'role' in session and session['role'] == 'canteen':
        item_name = request.form['item_name']
        price = request.form['price']
        category = request.form['category']
        
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO canteen (item_name, price, category, status) VALUES (?, ?, ?, 'متوفر')", (item_name, price, category))
        conn.commit()
        conn.close()
    return redirect(url_for('canteen_dashboard'))

@app.route('/edit_canteen_item/<int:item_id>', methods=['POST'])
def edit_canteen_item(item_id):
    if 'role' in session and session['role'] == 'canteen':
        item_name = request.form['item_name']
        price = request.form['price']
        category = request.form['category']
        
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE canteen SET item_name = ?, price = ?, category = ? WHERE id = ?", (item_name, price, category, item_id))
        conn.commit()
        conn.close()
    return redirect(url_for('canteen_dashboard'))

@app.route('/delete_canteen_item/<int:item_id>', methods=['POST'])
def delete_canteen_item(item_id):
    if 'role' in session and session['role'] == 'canteen':
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM canteen WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('canteen_dashboard'))

@app.route('/reject_order/<int:order_id>', methods=['POST'])
def reject_order(order_id):
    if 'role' in session and session['role'] == 'canteen':
        reason = request.form['cancel_reason']
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE canteen_orders SET status = 'مرفوض من المقصف', cancel_reason = ? WHERE id = ?", (reason, order_id))
        conn.commit()
        conn.close()
    return redirect(url_for('canteen_dashboard'))

@app.route('/deliver_order/<int:order_id>', methods=['POST'])
def deliver_order(order_id):
    if 'role' in session and session['role'] == 'canteen':
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE canteen_orders SET status = 'تم التسليم' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('canteen_dashboard'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
        
    class_filter = request.args.get('class_filter', '3 / 1')
    
    conn = sqlite3.connect('school_v2.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password, subject, stage FROM users WHERE role = 'teacher'")
    teachers_accounts = cursor.fetchall()
    
    cursor.execute("SELECT id, username, password, stage, class_name FROM users WHERE role = 'student'")
    students_accounts = cursor.fetchall()
    
    cursor.execute("SELECT * FROM students_list WHERE class_name = ?", (class_filter,))
    students = cursor.fetchall()
    
    cursor.execute("SELECT * FROM canteen")
    canteen_items = cursor.fetchall()

    cursor.execute("SELECT id, day_name, p1, p2, p3, p4, p5, p6, p7 FROM school_schedules WHERE class_name = ?", (class_filter,))
    schedule_rows = cursor.fetchall()
    
    conn.close()
    
    return render_template('vice_principal.html', teachers_accounts=teachers_accounts, students_accounts=students_accounts, 
                           students=students, canteen_items=canteen_items, total_students=len(students_accounts), 
                           total_teachers=len(teachers_accounts), class_filter=class_filter, schedule_rows=schedule_rows)

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    if 'role' in session and session['role'] == 'admin':
        sched_id = request.form['sched_id']
        p1 = request.form['p1']
        p2 = request.form['p2']
        p3 = request.form['p3']
        p4 = request.form['p4']
        p5 = request.form['p5']
        p6 = request.form['p6']
        p7 = request.form['p7']
        class_target = request.form['class_target']

        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE school_schedules 
            SET p1 = ?, p2 = ?, p3 = ?, p4 = ?, p5 = ?, p6 = ?, p7 = ?
            WHERE id = ?
        """, (p1, p2, p3, p4, p5, p6, p7, sched_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard', class_filter=class_target))
    return redirect(url_for('login'))

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT student_name FROM students_list WHERE id = ?", (student_id,))
        stu = cursor.fetchone()
        
        if stu:
            student_name = stu[0]
            cursor.execute("DELETE FROM students_list WHERE id = ?", (student_id,))
            cursor.execute("DELETE FROM users WHERE username = ? AND role = 'student'", (student_name,))
            cursor.execute("DELETE FROM subject_grades WHERE student_name = ?", (student_name,))
            conn.commit()
            
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect('school_v2.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        target_user = cursor.fetchone()
        if target_user and target_user[0] != 'admin':
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)