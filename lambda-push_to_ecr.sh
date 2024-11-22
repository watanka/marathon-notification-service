aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 729742072816.dkr.ecr.ap-northeast-2.amazonaws.com
docker build -t runnersclub-lambda -f Dockerfile.awslambda .
docker tag runnersclub-lambda:latest 729742072816.dkr.ecr.ap-northeast-2.amazonaws.com/runnersclub-lambda:latest
docker push 729742072816.dkr.ecr.ap-northeast-2.amazonaws.com/runnersclub-lambda:latest