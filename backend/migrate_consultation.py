"""
상담 테이블에 student_name과 student_grade 컬럼 추가하는 마이그레이션 스크립트
기존 데이터베이스에 컬럼을 추가합니다.
"""
import sqlite3

DB_PATH = "./bigmama.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # student_name 컬럼이 있는지 확인
        cursor.execute("PRAGMA table_info(consultations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'student_name' not in columns:
            print("student_name 컬럼 추가 중...")
            cursor.execute("ALTER TABLE consultations ADD COLUMN student_name VARCHAR")
            
            # 기존 데이터가 있으면 student_id로부터 학생 정보 복사
            cursor.execute("""
                UPDATE consultations 
                SET student_name = (
                    SELECT name FROM students WHERE students.id = consultations.student_id
                )
                WHERE student_id IS NOT NULL
            """)
            
        if 'student_grade' not in columns:
            print("student_grade 컬럼 추가 중...")
            cursor.execute("ALTER TABLE consultations ADD COLUMN student_grade VARCHAR")
            
            # 기존 데이터가 있으면 student_id로부터 학년 정보 복사
            cursor.execute("""
                UPDATE consultations 
                SET student_grade = (
                    SELECT grade FROM students WHERE students.id = consultations.student_id
                )
                WHERE student_id IS NOT NULL
            """)
        
        # student_id를 nullable로 변경 (SQLite는 ALTER COLUMN을 지원하지 않으므로 새 테이블 생성)
        # 하지만 데이터 손실 위험이 있으므로 일단 건너뜀
        # 기존 데이터는 student_id가 있을 것이고, 새로 추가되는 데이터는 student_name/grade만 있을 수 있음
        
        conn.commit()
        print("마이그레이션 완료!")
        
    except Exception as e:
        conn.rollback()
        print(f"마이그레이션 오류: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

