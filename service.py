from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

# Flask 애플리케이션 생성
app = Flask(
    __name__,
    static_url_path='',
    static_folder='./',  # 정적 파일 위치 지정
    template_folder='./'  # 템플릿 파일 위치 지정
)

# SQLite 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waitlist.db'
db = SQLAlchemy(app)

# 데이터베이스 모델 정의
class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)  # 전화번호
    table_number = db.Column(db.Integer)  # 선택된 식사 테이블 번호
    wait_table = db.Column(db.Integer)  # 선택된 대기 테이블 번호

    def __repr__(self):
        return f"<대기 리스트: {self.phone_number}, 식사 테이블: {self.table_number}, 대기 테이블: {self.wait_table}>"

# 데이터베이스 테이블 생성
with app.app_context():
    db.create_all()
# 주문 테이블 모델
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    table_number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Order: {self.menu_name}, Quantity: {self.quantity}, Price: {self.price}, Phone: {self.phone_number}, Table: {self.table_number}>"

# 주문 추가 API
@app.route('/api/order', methods=['POST'])
def add_order():
    data = request.json
    new_order = Order(
        menu_name=data['menuName'],
        quantity=data['quantity'],
        price=data['price'],
        phone_number=data['phoneNumber'],
        table_number=data['tableNumber']
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'success': True, 'message': '주문이 추가되었습니다.'})

# 주문 목록 조회 API
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    order_list = []
    for order in orders:
        order_list.append({
            'menuName': order.menu_name,
            'quantity': order.quantity,
            'price': order.price,
            'phoneNumber': order.phone_number,
            'tableNumber': order.table_number
        })
    return jsonify({'orders': order_list})

# 홈 페이지 라우트
@app.route('/')
@app.route('/home')
def kiosk_index():
    return render_template('index.html')

# 대기 테이블 선택 페이지 라우트
@app.route('/wait')
def wait_page():
    return render_template('Wait/wait.html')

# 대기 리스트에 새 항목 추가 API
@app.route('/api/wait', methods=['POST'])
def add_wait():
    phone_number = request.form.get('phoneNumber')  # 폼 데이터에서 전화번호 가져오기
    if phone_number:
        new_waitlist_entry = Waitlist(phone_number=phone_number)
        db.session.add(new_waitlist_entry)
        db.session.commit()
        return jsonify({'success': True, 'count': get_waiting_count()})
    return jsonify({'success': False, 'message': '유효하지 않은 전화번호'}), 400

# 대기 인원 수 조회 API
@app.route('/api/wait/count', methods=['GET'])
def get_wait_count():
    count = Waitlist.query.filter(Waitlist.phone_number != '-').count()
    return jsonify({'count': count})

# 전화번호가 있는 대기 인원 수 조회 API
@app.route('/api/wait/phone_count', methods=['GET'])
def get_phone_count():
    count = Waitlist.query.filter(Waitlist.phone_number != '-').count()
    return jsonify({'count': count})

# 사용 가능한 테이블 수 조회 API
@app.route('/api/tables/available_count', methods=['GET'])
def get_available_table_count():
    total_tables = 6
    selected_count = Waitlist.query.filter(Waitlist.table_number != None).count()
    available_count = total_tables - selected_count
    return jsonify({'availableCount': available_count})

# 전체 대기 인원 수 조회 함수
def get_waiting_count():
    return Waitlist.query.count()

# 식사 테이블 업데이트 API
@app.route('/api/table', methods=['POST'])
def update_table():
    phone_number = request.form.get('phoneNumber')
    table_number = request.form.get('tableNumber')

    if table_number:
        try:
            table_number = int(table_number)  # 문자열로 전송된 테이블 번호를 정수로 변환

            # 전화번호 없이 테이블 번호만 저장하는 새 레코드 생성
            if not phone_number:
                new_waitlist_entry = Waitlist(phone_number='-', table_number=table_number)
                db.session.add(new_waitlist_entry)
                db.session.commit()
                return jsonify({'success': True, 'message': '테이블 선택 완료'})

            # 전화번호가 있는 경우 기존 로직
            waitlist_entry = Waitlist.query.filter_by(phone_number=phone_number).first()
            if waitlist_entry:
                waitlist_entry.table_number = table_number
                db.session.commit()
                return jsonify({'success': True, 'message': '테이블 선택 완료'})
            else:
                return jsonify({'success': False, 'message': '전화번호를 찾을 수 없습니다.'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'오류 발생: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': '테이블 번호를 입력하세요.'}), 400
    
# 대기 테이블 업데이트 API
@app.route('/api/wait_table', methods=['POST'])
def update_wait_table():
    phone_number = request.form.get('phoneNumber')
    wait_table = request.form.get('waitTable')

    if wait_table:
        try:
            wait_table = int(wait_table)  # 문자열로 전송된 대기 테이블 번호를 정수로 변환

            # 전화번호 없이 대기 테이블 번호만 저장하는 새 레코드 생성
            if not phone_number:
                new_waitlist_entry = Waitlist(phone_number='-', wait_table=wait_table)
                db.session.add(new_waitlist_entry)
                db.session.commit()
                return jsonify({'success': True, 'message': '대기 테이블 선택 완료'})

            # 전화번호가 있는 경우 기존 로직
            waitlist_entry = Waitlist.query.filter_by(phone_number=phone_number).first()
            if waitlist_entry:
                waitlist_entry.wait_table = wait_table
                db.session.commit()
                return jsonify({'success': True, 'message': '대기 테이블 선택 완료'})
            else:
                return jsonify({'success': False, 'message': '전화번호를 찾을 수 없습니다.'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'오류 발생: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': '대기 테이블 번호를 입력하세요.'}), 400

# 선택된 식사 테이블 조회 API
@app.route('/api/tables/selected', methods=['GET'])
def get_selected_tables():
    selected_tables = Waitlist.query.with_entities(Waitlist.table_number).filter(Waitlist.table_number != None).all()
    selected_tables = [table[0] for table in selected_tables]
    return jsonify({'selectedTables': selected_tables})

# 선택된 대기 테이블 조회 API
@app.route('/api/wait/selected', methods=['GET'])
def get_selected_wait_tables():
    selected_wait_tables = Waitlist.query.with_entities(Waitlist.wait_table).filter(Waitlist.wait_table != None).all()
    selected_wait_tables = [table[0] for table in selected_wait_tables]
    return jsonify({'selectedWaitTables': selected_wait_tables})

# 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
