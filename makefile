local:
	./tomd/manage.py runserver

deploy:
	git push origin master

build:
	mkdir -p $$BUILD_DIR
	./manage.py build
	./manage.py netlify -n
	./netlifyctl -A $$NETLIFY_TOKEN -P $$BUILD_DIR -s $$NETLIFY_SITE_ID deploy
