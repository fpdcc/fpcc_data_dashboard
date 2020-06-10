# FPCC Data Dashboard

 - Create .envrc

 - Add to file:

```
export FLASK_APP=dashapp
export FLASK_ENV=development
export DATABASE_URL=sqlite:///$PWD/app.db
export SECRET_KEY=secret_key_change_as_you_wish_make_it_long_123
```

- Then run

```bash
source .envrc
pip install -r requirements.txt

flask db init
flask db migrate -m 'init'
flask db upgrade
flask run
```

open in browser

This dashboard is based on work done by [okomarov](https://github.com/okomarov/dash_on_flask)
