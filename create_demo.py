from website import create_app, db
from website.models import User, Role, Source, Wood
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # สร้าง Role
    roles = [
        'นักวิจัย', 'นักเรียน/นักศึกษา', 'บุคคลทั่วไป', 'เจ้าหน้าที่ป่าไม้', 'ผู้ซื้อไม้', 'ผู้ค้าไม้'
    ]
    for name in roles:
        role = Role.query.filter_by(role_name=name).first()
        if not role:
            role = Role(role_name=name)
            db.session.add(role)
    
    db.session.commit()

    # ตรวจสอบและเพิ่มผู้ใช้ admin
    admin_role = Role.query.filter_by(role_name='Admin').first()
    if admin_role:
        new_admin = User(
            email='admin@gmail.com',
            first_name='admin',
            last_name='admin',
            user_name='admin1',
            password=generate_password_hash('1234567', method='pbkdf2:sha256'),
            role_id=admin_role.role_id,
            profile_picture=None
        )
        db.session.add(new_admin)

    # สร้าง Source
    sources = ['สวนนานาไม้']
    for name in sources:
        source = Source.query.filter_by(source_name=name).first()
        if not source:
            source = Source(source_name=name)
            db.session.add(source)

    # สร้าง Wood
    woods = [
        ('ชิงชัน (Dalbergia oliveri Gamble ex Prain)', 'ching'),
        ('ยูคาลิปตัส (Eucalyptus globulus Labill.)', 'euca'),
        ('กะพี้เขาควาย (Dalbergia cultrata Graham ex Benth.)', 'kapi'),
        ('พะยูง (Dalbergia cochinchinensis Pierre)', 'payung'),
        ('ประดู่ (Pterocarpus macrocarpus Kurz)', 'pradu'),
        ('สัก (Tectona grandis L.f.)', 'sak'),
        ('ตะเคียน (Hopea odorata Roxb.)', 'takian'),
        ('เต็ง (Shorea obtusa Wall. ex Blume)', 'teng'),
        ('ยางนา (Dipterocarpus alatus Roxb.ex G.Don.)', 'yangna'),
        ('ยางพารา (Hevea brasiliensis Muell. Arg.)', 'yangpara')
    ]
    for name, nickname in woods:
        wood = Wood.query.filter_by(wood_name=name).first()
        if not wood:
            wood = Wood(wood_name=name, wood_nickname=nickname)
            db.session.add(wood)

    # Commit ทุกการเปลี่ยนแปลง
    db.session.commit()
    print("Admin user and other records created successfully.")
