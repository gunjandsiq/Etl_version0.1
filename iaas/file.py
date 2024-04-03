import boto3

ec2 = boto3.client('ec2')
ec2_key = 'inst-ec2-key'
response = ec2.create_key_pair(KeyName=ec2_key)
private_key = response['KeyMaterial']

with open('ec2key.pem', 'w') as pem_file:
    pem_file.write(private_key)

print("PEM file created successfully.")

