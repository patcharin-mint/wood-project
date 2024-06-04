from website import create_app, db
from website.models import User, Role
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin_role = Role.query.filter_by(role_name='Admin').first()
    if not admin_role:
        admin_role = Role(role_name='Admin')
        db.session.add(admin_role)
        db.session.commit()

    new_admin = User(
        email='admin@gmail.com',
        first_name='admin',
        last_name='admin',
        user_name='admin1',
        password=generate_password_hash('1234567', method='pbkdf2:sha256'),
        role_id=admin_role.role_id,
        profile_picture=None 
    )

    # เพิ่มผู้ใช้ใหม่ลงในฐานข้อมูล
    db.session.add(new_admin)
    db.session.commit()
    print("Admin user created successfully.")
