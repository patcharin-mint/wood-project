from website import create_app
import sys
import io


# เปลี่ยน sys.stdout เป็น utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = create_app()

# สั่งรัน project / web server
if __name__ =='__main__':
	app.run(debug = True)
	