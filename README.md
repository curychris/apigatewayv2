# CI/CD Development
## Install Dependencies
`pip install -r requirements.txt`

## Setting Environments
AWS_ACCESS_KEY_ID=your aws access key<br/>
AWS_SECRET_ACCESS_KEY=your secret access key<br/>
AWS_SESSION_TOKEN=your sessions token<br/>
AWS_REGION=us-east-1<br/>
EFS_PATH=/mnt/efs/log/app.log<br/>
S3_BUCKET_NAME=your bucket name<br/>
API_GATEWAY_URL=your API Gateway URL<br/>
ECR_REPOSITORY=your name ECR<br/>
ECR_REGISTRY=your url image

## Environments For Local Test
MOCK_AWS=true<br/>
AWS_REGION=us-east-1<br/>
S3_BUCKET_NAME=dummy-bucket<br/>
API_GATEWAY_URL=http://localhost:5000/mock-api<br/>


# Build Docker image
docker build -t flask-app .

# Run Docker container
docker run -p 5000:5000 --env-file .env flask-app


## Running Apps
python app.py
