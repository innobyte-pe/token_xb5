-- run Local
 docker-compose -f .\docker-compose-dev.yml up --build

 -- recreate DB
 docker-compose -f .\docker-compose-dev.yml exec token python manage.py recreate_db

 --<run in : http://localhost:5001/>

-- deploy AWS

  git add .  ;
  git commit -m "deploy"  ;
  git push ; eb deploy
flask==1.1.2

-- recreate DB AWS (CAUTION: Elimina la base de datos)
eb ssh  =  login viertual instance
cd /var/app/current
docker-compose exec token python manage.py recreate_db