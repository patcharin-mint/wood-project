from website import create_app

app = create_app()

# สั่งรัน project / web server
if __name__ =='__main__':
	app.run(debug = True)
	