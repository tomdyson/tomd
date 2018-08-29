local:
	./tomd/manage.py runserver

deploy:
	git push origin master

build:
	./manage.py build
	./netlifyctl -A $$NETLIFY_TOKEN -P $$BUILD_DIR -s $$NETLIFY_SITE_ID deploy
