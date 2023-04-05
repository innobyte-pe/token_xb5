-- run Local
 docker-compose -f .\docker-compose-dev.yml up --build


-- deploy AWS

  git add .  ;
  git commit -m "deploy"  ;
  git push ; eb deploy
flask==1.1.2

-- recreate DB AWS (CAUTION: Elimina la base de datos)
eb ssh  =  login viertual instance
cd /var/app/current
docker-compose exec token python manage.py recreate_db