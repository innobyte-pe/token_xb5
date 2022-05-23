-- run Local
 docker-compose -f .\docker-compose-dev.yml up --build


-- deploy AWS

  git add .  ;
  git commit -m "deploy"  ;
  git push ; eb deploy


-- recreate DB