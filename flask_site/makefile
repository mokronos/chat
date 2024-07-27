css:
	npx tailwindcss -i ./static/css/src/input.css -o ./static/css/output.css --watch

css-prod:
	npx tailwindcss -i ./static/css/src/input.css -o ./static/css/output.css --minify

env:
	@read -p "Enter secret key: " secret; \
	touch .env; \
	echo "export SECRET_KEY=$$secret" > .env

