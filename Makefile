run:
	uvicorn app.main:app --reload

alembic-up:
	python -m alembic -c app/alembic.ini upgrade head

alembic-dw:
	alembic -c app/alembic.ini downgrade -1

alembic-gen:
	alembic -c app/alembic.ini revision --autogenerate -m "$(m)"