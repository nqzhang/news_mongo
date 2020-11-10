for x in `supervisorctl status | grep news_mongo | awk '{print $1}'`;do supervisorctl restart $x;sleep 0.5;done
