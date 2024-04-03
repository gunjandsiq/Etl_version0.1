import boto3
from botocore.config import Config
from models import database
import sentry_sdk
from sentry_sdk import capture_exception
from utils import models

sentry_sdk.init(
    dsn="https://9d8083968aee22403a4fa6a9896bfb4f@o4506800727523328.ingest.sentry.io/4506800763895808",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

class EC2_helper:

    def __init__(self):
        self.client_ec2 = boto3.client('ec2')

    # list of all the regions
    def available_regions(self):
        try:
            all_regions = self.client_ec2.describe_regions()
            regions =[]
            for items in all_regions["Regions"]:
                regions.append(items["RegionName"]) 
            # print (regions)
            return regions  
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def instance_response(self,response):
        try:
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    image_id = instance['ImageId']
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    key_name = instance['KeyName']
                    state = instance['Monitoring']['State']
                    status = instance['State']['Name']
                    tags = instance['Tags'] if 'Tags' in instance else []
                    for tag in tags:
                        instance_name = tag['Value']
                    out = {
                        'ImageId': image_id,
                        'InstanceId': instance_id,
                        'InstanceType': instance_type,
                        'KeyName': key_name,
                        'State': state,  
                        'Status': status,
                        'InstanceName': instance_name
                    }
                    instances.append(out)
            return instances  
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
      
    # Describes the specified instances or all instances
    def describe_ec2_instance(self,region=None,instance_ids=None):
        try:
            print("Describing EC2 instances")  

            if region and instance_ids:
                if not isinstance(instance_ids, list):
                    raise ValueError("Instance IDs must be provided as a list.")
                
                response = self.client_ec2.describe_instances(InstanceIds=instance_ids)
                instances = self.instance_response(response)

            elif region:
                my_config = Config(region_name=region)
                client_ec2 = boto3.client('ec2', config=my_config)
                response = self.client_ec2.describe_instances()
                instances = self.instance_response(response)

            elif instance_ids:
                if not isinstance(instance_ids, list):
                    raise ValueError("Instance IDs must be provided as a list.")
                
                response = self.client_ec2.describe_instances(InstanceIds=instance_ids)
                instances = self.instance_response(response)

            else:
                regions = self.available_regions()
                instances = []
                for reg in regions:
                    my_config = Config(region_name = reg)
                    client_ec2 = boto3.client('ec2',config=my_config)
                    response = client_ec2.describe_instances()
                    data = self.instance_response(response)
                    instances.extend(data)

            database.add_record('ec2','describe_ec2_instance',instances)
            print (instances)
            return instances
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # to create aws_ec2 instances  Launches the specified number of instances using an AMI for which we have permissions
    def create_ec2_instance(self,image_id,min_count,max_count,instance_type,key_name,instance_name):
        try:
            print("Creating EC2 instance")
            instance = self.client_ec2.run_instances(
                ImageId = image_id,                                                      # The ID of the AMI used to launch the instance.
                MinCount = min_count,                                                    # Minimum no. of instances to be launched
                MaxCount = max_count,                                                    # Maximum no. of instances to be launched
                InstanceType = instance_type,                                            # instance type
                KeyName = key_name,                                                      # name of the key pair
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags':[
                            {
                            'Key': 'Name',
                            'Value': instance_name
                            },
                        ]
                    },
                ]                                                      
            )
            response = {
                'ImageId':image_id,
                'InstanceId':instance['Instances'][0]['InstanceId'],
                'InstanceType':instance_type,
                'KeyName' : key_name,
                'InstanceName': instance_name
            }
            database.add_record('ec2','create_ec2_instance',response)
            print (response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def modify_ec2_instance_attribute(self,instance_id,instance_type):
        try:
            response = self.client_ec2.modify_instance_attribute(
                InstanceId = instance_id,
                InstanceType={
                    'Value': instance_type
                }
            )
            print(response)
            database.add_record('ec2','modify_ec2_instance_attribute',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def create_ec2_image(self, instance_id, image_name):
        try:
            response = self.client_ec2.create_image(
                InstanceId = instance_id,
                Name = image_name
            )
            print(response)
            database.add_record('ec2','create_ec2_image',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    # Describes the specified Elastic IP addresses or all Elastic IP addresses
    def describe_Ipaddress(self):
        try:
            response = self.client_ec2.describe_addresses()
            output = []
            for res in response['Addresses']:
                instanceId = (res['InstanceId'])
                publicIp = (res['PublicIp'])
                allocationId = (res['AllocationId'])
                associationId = (res['AssociationId'])
                domain =(res['Domain'])
                data = {
                    'InstanceId' : instanceId,
                    'PublicIp' : publicIp,
                    'AllocationId' : allocationId,
                    'AssociationId' : associationId,
                    'Domain' : domain
                }
                output.append(data)
            database.add_record('ec2','describe_Ipaddress',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    # Describes the specified key pairs or all key pairs   
    def describe_ec2_keyPairs(self):
        try:
            response= self.client_ec2.describe_key_pairs()
            output = []
            for res in response['KeyPairs']:
                keyPair_id = (res['KeyPairId'])
                keyName = (res['KeyName'])
                keyType = (res['KeyType'])
                data = {
                    'KeyPairId' : keyPair_id,
                    'KeyName' : keyName,
                    'KeyType' : keyType
                }
                output.append(data)
            database.add_record('ec2','describe_ec2_keyPairs',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Describes the Availability Zones, Local Zones, and Wavelength Zones that are available 
    def describe_available_zone(self):
        try:
            response= self.client_ec2.describe_availability_zones()
            output = []
            for res in response['AvailabilityZones']:
                state = (res['State'])
                regionName = (res['RegionName'])
                zoneName = (res['ZoneName'])
                zoneId = (res['ZoneId'])
                groupName = (res['GroupName'])
                data = {
                    'State' : state,
                    'RegionName' : regionName,
                    'ZoneName' : zoneName,
                    'ZoneId' : zoneId,
                    'GroupName' : groupName 
                }
                output.append(data)
            database.add_record("ec2","describe_available_zone",output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Allocates an Elastic IP address to AWS account  
    def allocate_Ipaddress(self):
        try:
            response = self.client_ec2.allocate_address()
            database.add_record('ec2','allocate_Ipaddress',response)
            return response  
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Associates an Elastic IP address
    def associate_Ipaddress(self,allocation_id,instance_id):
        try:
            response = self.client_ec2.associate_address(
                    AllocationId = allocation_id,                                                    # allocation id
                    InstanceId = instance_id,                                                        # the ID of the instance
            )
            database.add_record('ec2','associate_Ipaddress',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Releases the specified Elastic IP address
    def release_Ipaddress(self, allocation_id='', public_ip=''):
        try:
            if allocation_id or public_ip:
                response = self.client_ec2.release_address(
                    AllocationId = allocation_id,
                    PublicIp = public_ip
                )
                database.add_record('ec2','release_Ipaddress',response)
                print (response)
                return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return (str(e))


    # Disassociates an Elastic IP address from the instance
    def disassociate_Ipaddress(self, association_id='', public_ip=''):
        try:
            if association_id or public_ip:
                response = self.client_ec2.disassociate_address(
                    AssociationId = association_id,
                    PublicIp = public_ip  
                )
                database.add_record('ec2','disassociate_Ipaddress',response)
                return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Starts an Amazon EBS-backed instance
    def start_ec2_instance(self,instance_ids):
        try:
            if not isinstance(instance_ids, list):
                raise ValueError("Instance IDs must be provided as a list.")
            
            response = self.client_ec2.start_instances(InstanceIds = instance_ids)
            database.add_record('ec2','start_ec2_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Stops an Amazon EBS-backed instance
    def stop_ec2_instance(self,instance_ids):
        try:
            if not isinstance(instance_ids, list):
                raise ValueError("Instance IDs must be provided as a list.")
            
            response = self.client_ec2.stop_instances(InstanceIds = instance_ids)
            database.add_record('ec2','stop_ec2_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Shuts down the specified instances   
    def terminate_ec2_instance(self,instance_ids):
        try:
            if not isinstance(instance_ids, list):
                raise ValueError("Instance IDs must be provided as a list.")
            
            response = self.client_ec2.terminate_instances(InstanceIds = instance_ids)
            database.add_record('ec2','terminate_ec2_instance',response)
            print (response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Requests a reboot of the specified instances
    def reboot_ec2_instance(self,instance_ids):
        try:
            if not isinstance(instance_ids, list):
                raise ValueError("Instance IDs must be provided as a list.")
            
            response = self.client_ec2.reboot_instances(InstanceIds = instance_ids)
            database.add_record('ec2','reboot_ec2_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Creates an ED25519 or 2048-bit RSA key pair    
    def create_keyPair(self,key_name):
        try:
           response= self.client_ec2.create_key_pair(KeyName = key_name)
           database.add_record('ec2','create_keyPair',response)
           return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Deletes the specified key pair    
    def delete_keyPair(self,key_name):
        try:
           response= self.client_ec2.delete_key_pair(KeyName = key_name)
           database.add_record('ec2','delete_keyPair',response)
           return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Describes the specified EBS volumes or all EBS volumes
    def describe_ec2_volumes(self):
        try:
            response= self.client_ec2.describe_volumes()
            output = []
            for res in response['Volumes']:
                available_zone = (res['AvailabilityZone'])
                volume_id = (res['VolumeId'])
                size = (res['Size'])
                out = {
                        'AvailabilityZone':available_zone,
                        'VolumeId':volume_id,
                        'Size':size
                    }
                output.append(out)  
            database.add_record('ec2','describe_ec2_volumes',output) 
            return output 
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)       

    # Attaches an EBS volume to a running or stopped instance        
    def attach_ec2_volume(self,device,instance_id,volume_id):
        try:
            response = self.client_ec2.attach_volume(
                Device = device,
                InstanceId = instance_id,
                VolumeId = volume_id 
            )
            database.add_record('ec2','attach_ec2_volume',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Creates an EBS volume that can be attached to an instance in the same Availability Zone
    def create_ec2_volume(self,availability_zone,size,volume_type):
        try:
            response = self.client_ec2.create_volume(
                AvailabilityZone = availability_zone,
                Size = size,
                VolumeType = volume_type 
            )
            database.add_record('ec2','create_ec2_volume',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Deletes the specified EBS volume
    def delete_ec2_volume(self,volume_id):
        try:
            response = self.client_ec2.delete_volume(
                VolumeId = volume_id
            )
            database.add_record('ec2','delete_ec2_volume',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Detaches an EBS volume from an instance
    def detach_ec2_volume(self,volume_id, instance_id):
        try:
            response = self.client_ec2.detach_volume(
                VolumeId = volume_id,
                InstanceId = instance_id
            )
            database.add_record('ec2','detach_ec2_volume',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # modify several parameters of an existing EBS volume
    def modify_ec2_volume(self,volume_id, size):
        try:
            response = self.client_ec2.modify_volume(
                VolumeId = volume_id,
                Size = size
            )
            database.add_record('ec2','modify_ec2_volume',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
class Sqs_helper:

    def __init__(self):
        self.client_sqs = boto3.client('sqs')

    # Creates a new standard or FIFO queue.
    def create_sqs_queue(self,queue_name):
        try:
            response = self.client_sqs.create_queue(QueueName = queue_name)
            queueurl = response['QueueUrl']
            database.add_record('sqs','create_sqs_queue',queueurl)
            return queueurl
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Adds a permission to a queue, this allows sharing access to the queue
    def add_sqs_permission(self,queue_url,label, aws_account_ids, actions):
        try:
            response = self.client_sqs.add_permission(
                QueueUrl = queue_url,                                                        # The URL of the Amazon SQS queue to which permissions are added
                Label = label,                                                              # The unique identification of the permission. Maximum 80 characters
                AWSAccountIds = [aws_account_ids],                                           # The AWS account numbers to receive permission
                Actions = [actions]                                                         # The action the client wants to allow for the specified principal
            )
            database.add_record('sqs','add_sqs_permission',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Revokes any permissions in the queue   
    def remove_sqs_permission(self,queue_url, label):
        try:
            response = self.client_sqs.remove_permission(
                QueueUrl = queue_url,                                                        # The URL of the Amazon SQS queue from which permissions are removed
                Label = label                                                               # The identification of the permission to remove
            )
            database.add_record('sqs','remove_sqs_permission',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Deletes the queue
    def delete_sqs_queue(self,queue_url):
        try:
            response = self.client_sqs.delete_queue(QueueUrl = queue_url)
            database.add_record('sqs','delete_sqs_queue',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Delivers a message to the specified queue    
    def send_message(self,queue_url,message,msg_attributes,data_type):
        try:
            response = self.client_sqs.send_message(
                QueueUrl= queue_url,                                                # The URL of the Amazon SQS queue to which a message is sent
                MessageBody = message,                                              # The message to send
                MessageAttributes = {
                    'Message' : {
                        'StringValue': msg_attributes,
                        'DataType' : data_type
                    }
                },                                       
            )
            database.add_record('sqs','send_message',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Deletes the specified message from the specified queue
    def delete_message(self,queue_url,receipt_handle):
        try:
            response = self.client_sqs.delete_message(
                QueueUrl = queue_url,                                                # The URL of the Amazon SQS queue from which messages are deleted
                ReceiptHandle = receipt_handle                                       # The receipt handle associated with the message to delete
            )
            database.add_record('sqs','delete_message',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Retrieves one or more messages from the specified queue   
    def receive_message(self,queue_url):
        try:
            response = self.client_sqs.receive_message(
                QueueUrl = queue_url
            )
            database.add_record('sqs','receive_message',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Deletes available messages in a queue
    def purgue_sqs_queue(self,queue_url):
        try:
            response = self.client_sqs.purge_queue(
                QueueUrl = queue_url
            )
            database.add_record('sqs','purgue_sqs_queue',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Returns the URL of an existing Amazon SQS queue   
    def get_sqs_queueUrl(self,queue_name):
        try:
            response = self.client_sqs.get_queue_url(QueueName = queue_name)
            queueurl = response['QueueUrl']
            output = {"QueueUrl" : queueurl}
            database.add_record('sqs','get_sqs_queueUrl',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Returns a list of your queues in all the region    
    def list_sqs_queues(self):
        try:
            response = self.client_sqs.list_queues()
            queueurl = response['QueueUrls']
            output = {
                "QueueUrl" : queueurl
            }
            database.add_record('sqs','list_sqs_queue',output)
            # print (queueurl)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
class Sns_helper:

    def __init__(self):
        self.client_sns = boto3.client('sns')

    # Creates a topic to which notifications can be published. 
    def create_sns_topic(self,topic_name):
        try:
            response = self.client_sns.create_topic(
                Name = topic_name 
            )
            topic_arn = response['TopicArn']
            output = {
                'TopicArn' : topic_arn
            }
            database.add_record('sns','create_sns_topic',output)
            # print (output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)   

    # Adds a statement to a topic’s access control
    def add_sns_permission(self,topic_arn,label,aws_account_ids,action_name):
        try:
            response = self.client_sns.add_permission(
                TopicArn = topic_arn,
                Label = label,
                AWSAccountId = [aws_account_ids],
                ActionName = [action_name]
            )
            database.add_record('sns','add_sns_permission',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Removes a statement from a topic’s access control    
    def remove_sns_permission(self,topic_arn,label):
        try:
            response = self.client_sns.remove_permission(
                TopicArn = topic_arn,
                Label = label
            )
            database.add_record('sns','remove_sns_permission',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
         
    # Deletes a topic and all its subscriptions    
    def delete_sns_topic(self,topic_arn):
        try:
            response = self.client_sns.delete_topic(TopicArn = topic_arn)
            database.add_record('sns','delete_sns_topic',response)
            return f"{topic_arn} deleted successfully"
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)   
         
    # Returns a list of the requester’s topics    
    def list_sns_topic(self):
        try:
            response = self.client_sns.list_topics()
            topics = response['Topics']
            database.add_record('sns','list_sns_topic',topics)
            # print(topics)
            return topics
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Subscribes an endpoint to an Amazon SNS topic    
    def create_subscription(self,topic_arn,protocol,endpoint):
        try:
            response = self.client_sns.subscribe(
                TopicArn = topic_arn,
                Protocol = protocol,
                Endpoint = endpoint
            )
            subscriptionarn = response['SubscriptionArn']
            output = {
                'SubscriptionArn': subscriptionarn
            }
            database.add_record('sns','create_subscription',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Deletes a subscription
    def delete_subscription(self,subscription_arn):
        try:
            response = self.client_sns.unsubscribe(
                SubscriptionArn = subscription_arn
            )
            database.add_record('sns','delete_subscription',response)
            return f"Subscription {subscription_arn} deleted successfully"
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Sends a message to an Amazon SNS topic   
    def publish_topic(self,topic_arn,message):
        try:
            response = self.client_sns.publish(
                TopicArn = topic_arn,
                Message = message
            )
            messageId = response['MessageId']
            output = {
                'MessageId': messageId
            }
            database.add_record('sns','publish_topic',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Returns a list of the requester’s subscriptions    
    def list_subscription(self):
        try:
            subscription_list =[]
            response = self.client_sns.list_subscriptions()
            for res in response:
                subscription = res['Subscriptions']
                nextToken = res['NextToken']
                output = {
                    'Subscriptions': subscription,
                    'NextToken' : nextToken
                }
                subscription_list.append(output)
            database.add_record('sns','list_subscription',subscription_list)
            return subscription_list
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def confirm_http_subscription(self,topic_arn,token):
        try:
            response = self.client_sns.confirm_subscription(
                TopicArn = topic_arn,
                Token = token
            )
            database.add_record('sns','confirm_http_subscription',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Returns a list of the subscriptions to a specific topic    
    def list_subscription_by_topic(self,topic_arn):
        try:
            response = self.client_sns.list_subscriptions_by_topic(
                TopicArn = topic_arn
            )
            subscription = response['Subscriptions']
            nextToken = response['NextToken']
            output = {
                'Subscriptions': subscription,
                'NextToken' : nextToken
            }
            database.add_record('sns','list_subscription_by_topic',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
class Ses_helper:

    def __init__(self):
        self.client_ses = boto3.client('ses')

    # Creates an email template
    def create_ses_template(self,template_name,subject=None,text=None,html=None):
        try:
            template_data = {
                    'TemplateName': template_name,                                  # The name of the template
                    'SubjectPart': subject,                                         # The subject line of the email
                    'TextPart' : text,                                              # The email body that is visible to recipients
                    'HtmlPart' : html                                               # The HTML body of the email 
                }
            template_data = {key: value for key, value in template_data.items() if value is not None}
            response = self.client_ses.create_template(
                Template = template_data
            )
            database.add_record('ses','create_ses_template',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Updates an email template  
    def update_ses_template(self,template_name,subject=None,text=None,html=None):
        try:
            template_data = {
                    'TemplateName': template_name,                                  # The name of the template
                    'SubjectPart': subject,                                         # The subject line of the email
                    'TextPart' : text,                                              # The email body that is visible to recipients
                    'HtmlPart' : html                                               # The HTML body of the email 
                }
            template_data = {key: value for key, value in template_data.items() if value is not None}
            response = self.client_ses.update_template(
                Template = template_data
            )
            database.add_record('ses','update_ses_template',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    # Deletes an email template   
    def delete_ses_template(self,template_name):
        try:
            response = self.client_ses.delete_template(
                TemplateName = template_name
            )
            database.add_record('ses','delete_ses_template',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # To send email 
    def send_ses_email(self,source,destination,subject,body_text,body_html):
        try:
            response = self.client_ses.send_email(
                Source = source,                                                # sender's email address
                Destination = {  
                    'ToAddresses': [destination],
                    # 'CcAddresses': [cc],
                    # 'BccAddresses': [bcc]                      
                },
                Message = {
                    'Subject': {
                        'Data' : subject
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text
                        },
                        'Html':{
                            'Data': body_html
                        }
                    }
                }
            )
            database.add_record('ses','send_ses_email',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Adds an email address to the list of identities    
    def verify_email_identity(self,email):
        try:
            response = self.client_ses.verify_email_identity(
                EmailAddress = email
            )
            database.add_record('ses','verify_email_identity',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # verify email address    
    def verify_email_address(self,email):
        try:
            response = self.client_ses.verify_email_address(
                EmailAddress = email
            )
            database.add_record('ses','verify_email_address',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Lists the email templates     
    def ses_templates_list(self):
        try:
            response = self.client_ses.list_templates()
            templates_data = {
                'TemplatesMetadata': response['TemplatesMetadata'],
            }
            database.add_record('ses','ses_templates_list',templates_data)
            return templates_data
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Returns a list containing all of the identities   
    def identity_lists(self):
        try:
            identity_list =[]
            response = self.client_ses.list_identities()
            for res in response:
                identity = {
                    'Identities': res['Identities']
                }
                identity_list.append(identity)
            database.add_record('ses','identity_lists',identity_list)
            return identity_list
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    # Deletes the specified identity from the list    
    def delete_identity(self,identity):
        try:
            response = self.client_ses.delete_identity(
                Identity = identity
            ) 
            database.add_record('ses','delete_identity',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def get_ses_template(self,template_name):
        try:
            response = self.client_ses.get_template(
                TemplateName = template_name
            )
            template = {
                'Template' : response['Template']
            }
            database.add_record('ses','get_ses_template',template)
            return template
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
class S3_helper:

    def __init__(self):
        self.client_s3 = boto3.client('s3')

    # Returns a list of all buckets 
    def bucket_list_names(self):
        try:
            bucket_list = []
            response = self.client_s3.list_buckets()
            for bucket in response['Buckets']:
                bucket_list.append(bucket['Name'])
            database.add_record('s3','bucket_list_names',bucket_list)
            return bucket_list
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    def create_s3_bucket(self, bucket_name):
        try:
            response = self.client_s3.create_bucket(
                Bucket = bucket_name,
            )
            print(response)
            database.add_record('s3','create_s3_bucket',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def get_storage_class(self,bucket_name, file_key):
        try:
            response = self.client_s3.head_object(Bucket=bucket_name, Key=file_key)
            storage_class = response.get('StorageClass')
            database.add_record('s3','get_storage_class',storage_class)
            return storage_class
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Delete the object
    def delete_file_from_s3(self,bucket_name, file_key):
        try:
            response = self.client_s3.delete_object(Bucket=bucket_name, Key=file_key)
            database.add_record('s3','delete_file_from_s3',response)
            print(f"File '{file_key}' deleted successfully.")
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def filter_bucket(self,bucket_name, min_date=None, max_date=None,report_type=None):
        try:
            response = self.client_s3.list_objects_v2(Bucket=bucket_name)
            file_names = []
            for obj in response['Contents']:
                if obj['Key'].startswith("BelSkai"):
                    date = obj['Key'].split('_')[1].split('.')[0]
                    origanal_report_type=obj['Key'].split('_')[0].replace("BelSkai","")
                    # Check if date is within the specified range
                if (min_date is None or date >= min_date) and (max_date is None or date <= max_date) and (report_type is None or origanal_report_type == report_type):
                    file_names.append(obj['Key'])
                    # print(obj['Key'])
            database.add_record('s3','filter_bucket',file_names)       
            return file_names
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Creates a copy of an object that is already stored in s3   
    def change_storage_class(self,bucket_name, file_key, new_storage_class):
        try:
            copy_source = {
                'Bucket': bucket_name,
                'Key': file_key
            }
            self.client_s3.copy_object(
                Bucket=bucket_name,
                CopySource=copy_source,
                Key=file_key,
                StorageClass=new_storage_class
            )
            print(
                f"Storage class of {file_key} changed to {new_storage_class}")
        except self.client_s3.exceptions.InvalidObjectState as e:
            print(f"An error occurred: {e}. \n The object may be in a state like GLACIER or Deep Archive so that does not allow direct modification.")
        except Exception as e:  
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    # Returns all objects in a bucket   
    def objects_list(self,bucket_name): 
        try:
            response = self.client_s3.list_objects(
                Bucket = bucket_name
            )
            database.add_record('s3','objects_list',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Retrieves an object from s3    
    def get_object(self,bucket_name,file_key):
        try:
            response = self.client_s3.get_object(
                Bucket = bucket_name,
                Key = file_key 
            )
            database.add_record('s3','get_object',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Adds an object to a bucket    
    def put_object_in_s3(self,bucket_name,file_key):
        try:
            response = self.client_s3.put_object(
                Bucket = bucket_name,
                Key = file_key 
            )
            database.add_record('s3','put_object_in_s3',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Upload a file to an S3 object
    def upload_file_to_object(self,file_path,bucket_name,file_key):
        try:
            response = self.client_s3.upload_file(
                Filename = file_path,                                                 # The path to the file to upload
                Bucket = bucket_name,                                                 # The name of the bucket 
                Key = file_key                                                        # The name of the key
            )
            database.add_record('s3','upload_file_to_object',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Download an S3 object to a file    
    def download_object_to_file(self,bucket_name,file_key,file_path):
        try:
            response = self.client_s3.download_file(
                Bucket = bucket_name,                                                  # The name of the bucket to download from
                Key = file_key,                                                        # The name of the key
                Filename = file_path                                                   # The path to the file
            )
            database.add_record('s3','download_object_to_file',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

class Rds_helper:

    def __init__(self):
        self.client_rds = boto3.client('rds')

    def describe_db_cluster(self):
        try:
            response = self.client_rds.describe_db_clusters()
            db_clusters = []
            for res in response['DBClusters']:
                output = {
                    'DBClusterIdentifier': res['DBClusterIdentifier'],
                    'DatabaseName' : res['DatabaseName'],
                    'Status' : res['Status'],
                    'Engine' : res['Engine'],
                    'MasterUsername' : res['MasterUsername']
                }
                db_clusters.append(output)
            # print(db_clusters)
            database.add_record('rds','describe_db_clusters',db_clusters)
            return db_clusters
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def describe_db_instance(self):
        try:
            response = self.client_rds.describe_db_instances()
            db_instances = []
            for res in response['DBInstances']:
                output = {
                    'DBInstanceIdentifier' : res['DBInstanceIdentifier'],
                    'DBInstanceClass' : res['DBInstanceClass'],
                    'Engine' : res['Engine'],
                    'DBInstanceStatus' : res['DBInstanceStatus'],
                    'MasterUsername' : res['MasterUsername'],
                    'AvailabilityZone' : res['AvailabilityZone']
                }
                db_instances.append(output)
            print(db_instances)
            database.add_record('rds','describe_db_instance',db_instances)
            return db_instances
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    #PENDING
    def create_db_cluster(self, database_name, db_cluster_identifier, engine, user_name = None, user_password = None):
        try:
            response = self.client_rds.create_db_cluster(
                DatabaseName = database_name,
                DBClusterIdentifier = db_cluster_identifier,
                Engine = engine,
                MasterUsername = user_name if user_name else None,
                MasterUserPassword = user_password if user_password else None
            )
            print(response)
            database.add_record('rds','create_db_cluster',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)   
        
    #PENDING
    def modify_db_cluster(self, db_cluster_identifier, new_db_cluster_identifier, new_password):
        try:
            response = self.client_rds.modify_db_cluster(
                DBClusterIdentifier = db_cluster_identifier,
                NewDBClusterIdentifier  = new_db_cluster_identifier,
                MasterUserPassword = new_password
            )
            print(response)
            database.add_record('rds','modify_db_cluster',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def start_db_cluster(self, db_cluster_identifier):
        try:
            response = self.client_rds.start_db_cluster(
                DBClusterIdentifier = db_cluster_identifier
            )
            database.add_record('rds','start_db_cluster',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 

    def stop_db_cluster(self, db_cluster_identifier):
        try:
            response = self.client_rds.stop_db_cluster(
                DBClusterIdentifier = db_cluster_identifier
            )
            database.add_record('rds','stop_db_cluster',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 
        
    def reboot_db_cluster(self, db_cluster_identifier):
        try:
            response = self.client_rds.reboot_db_cluster(
                DBClusterIdentifier = db_cluster_identifier
            )
            database.add_record('rds','reboot_db_cluster',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def delete_db_cluster(self, db_cluster_identifier):
        try:
            response = self.client_rds.delete_db_cluster(
                DBClusterIdentifier = db_cluster_identifier
            ) 
            print(response)
            database.add_record('rds','delete_db_cluster',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    #PENDING
    # Creates a new DB instance
    def create_db_instance(self, db_instance_identifier, db_instance_class, engine,allocated_storage,user_name = None, user_password = None):
        try:
            response = self.client_rds.create_db_instance(
                DBInstanceIdentifier = db_instance_identifier,
                DBInstanceClass = db_instance_class,
                Engine = engine,
                AllocatedStorage = allocated_storage,                                                   # The amount of storage
                MasterUsername = user_name if user_name else None,
                MasterUserPassword = user_password if user_password else None
            )
            print(response)
            database.add_record('rds','create_db_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 
        
    def modify_db_instance(self, db_instance_identifier, db_instance_class, new_db_instance_identifier, new_password):
        try:
            response = self.client_rds.modify_db_instance(
                DBInstanceIdentifier = db_instance_identifier,
                DBInstanceClass = db_instance_class,
                NewDBInstanceIdentifier  = new_db_instance_identifier,
                MasterUserPassword = new_password
            )
            print(response)
            database.add_record('rds','modify_db_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def start_db_instance(self, db_instance_identifier):
        try:
            response = self.client_rds.start_db_instance(
                DBInstanceIdentifier = db_instance_identifier
            )
            database.add_record('rds','start_db_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def stop_db_instance(self, db_instance_identifier):
        try:
            response = self.client_rds.stop_db_instance(
                DBInstanceIdentifier = db_instance_identifier,
            )
            database.add_record('rds','stop_db_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def reboot_db_instance(self, db_instance_identifier):
        try:
            response = self.client_rds.reboot_db_instance(
                DBInstanceIdentifier = db_instance_identifier
            )
            database.add_record('rds','reboot_db_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def delete_db_instance(self, db_instance_identifier):
        try:
            response = self.client_rds.delete_db_instance(
                DBInstanceIdentifier = db_instance_identifier
            )
            print(response)
            database.add_record('rds','delete_db_instance',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Returns information about DB snapshots
    def describe_db_snapshot(self):
        try:
            db_snapshots = []
            response = self.client_rds.describe_db_snapshots()
            for res in response['DBSnapshots']:
                output = {
                   'DBSnapshotIdentifier' : res['DBSnapshotIdentifier'],
                   'DBInstanceIdentifier' : res['DBInstanceIdentifier'],
                   'Status' : res['Status'],
                   'AvailabilityZone' : res['AvailabilityZone'],
                   'SnapshotType' : res['SnapshotType'],
                   'DBSnapshotArn' : res['DBSnapshotArn'],
                   'VpcId' : res['VpcId'],
                }
                db_snapshots.append(output)
            print(db_snapshots)
            database.add_record('rds','describe_db_snapshot',db_snapshots)
            return db_snapshots
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  

    # Creates a snapshot of a DB instance    
    def create_db_snapshot(self, db_snapshot_identifier, db_instance_identifier):
        try:
            response = self.client_rds.create_db_snapshot(
                DBSnapshotIdentifier = db_snapshot_identifier,
                DBInstanceIdentifier = db_instance_identifier
            )
            database.add_record('rds','create_db_snapshot',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def modify_db_snapshot(self, db_snapshot_identifier, engine_version=None):
        try:
            response = self.client_rds.modify_db_snapshot(
                DBSnapshotIdentifier = db_snapshot_identifier,
                EngineVersion = engine_version
            )
            database.add_record('rds','modify_db_snapshot',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def delete_db_snapshot(self, db_snapshot_identifier):
        try:
            response = self.client_rds.delete_db_snapshot(
                DBSnapshotIdentifier = db_snapshot_identifier
            )
            print("Snapshot deleted")
            database.add_record('rds','delete_db_snapshot',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
class IAM_helper:

    def __init__(self):
        self.client_iam = boto3.client('iam')
    
    # Lists the IAM users 
    def iam_users_list(self):
        try:
            iam_users = []
            response = self.client_iam.list_users()
            for res in response['Users']:
                output = {
                    'Path' : res['Path'],
                    'UserName' : res['UserName'],
                    'UserId' : res['UserId'],
                    'UserArn' : res['Arn']
                }
                iam_users.append(output)
            print(iam_users)
            database.add_record('iam','iam_users_list',iam_users)
            return iam_users
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Lists the IAM groups    
    def iam_groups_list(self):
        try:
            iam_groups = []
            response = self.client_iam.list_groups()
            for res in response['Groups']:
                output = {
                    'Path' : res['Path'],
                    'GroupName' : res['GroupName'],
                    'GroupId' : res['GroupId'],
                    'GroupArn' : res['Arn']
                }
                iam_groups.append(output)
            print(iam_groups)
            database.add_record('iam','iam_groups_list',iam_groups)
            return iam_groups
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Lists the IAM roles   
    def iam_roles_list(self):
        try:
            iam_roles = []
            response = self.client_iam.list_roles()
            for res in response['Roles']:
                output = {
                    'Path' : res['Path'],
                    'RoleName' : res['RoleName'],
                    'RoleId' : res['RoleId'],
                    'RoleArn' : res['Arn'],
                }
                iam_roles.append(output)
            print(iam_roles)
            database.add_record('iam','iam_roles_list',iam_roles)
            return iam_roles
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Lists the IAM policies   
    def iam_policies_list(self):
        try:
            iam_policies = []
            response = self.client_iam.list_policies()
            for res in response['Policies']:
                output = {
                    'Path' : res['Path'],
                    'PolicyName' : res['PolicyName'],
                    'PolicyId' : res['PolicyId'],
                    'PolicyArn' : res['Arn']
                }
                iam_policies.append(output)
            print(iam_policies)
            database.add_record('iam','iam_policies_list',iam_policies)
            return iam_policies
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Creates a new IAM user for AWS account
    def create_iam_user(self, user_name):
        try:
            response = self.client_iam.create_user(
                UserName = user_name
            )
            print(response)
            database.add_record('iam','create_iam_user',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    # Creates a password for the specified IAM user
    def create_iam_login_profile(self, user_name, password):
        try:
            response = self.client_iam.create_login_profile(
                UserName = user_name,
                Password = password
            )
            print(response)
            database.add_record('iam','create_iam_login_profile',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Changes the password of the IAM user who is calling this operation
    def change_current_user_password(self, old_password, new_password):
        try:
            response = self.client_iam.change_password(
                OldPassword = old_password,
                NewPassword = new_password
            )
            print(response)
            database.add_record('iam','change_users_own_password',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Changes the password for the IAM user
    def change_iam_user_password(self, user_name, password):
        try:
            response = self.client_iam.update_login_profile(
                UserName = user_name,
                Password = password
            )
            print(response)
            database.add_record('iam','change_user_password',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Creates a new group for AWS account
    def create_iam_group(self, group_name):
        try:
            response = self.client_iam.create_group(
                GroupName = group_name
            )
            print(response)
            database.add_record('iam','create_iam_group',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  

    # Creates a new role for AWS account    
    def create_iam_role(self, role_name, role_policy_document, description=None):
        try:
            response = self.client_iam.create_role(
                RoleName = role_name,
                AssumeRolePolicyDocument = role_policy_document,                                                   # document that grants an entity permission to assume the role
                Description = description
            )
            print(response)
            database.add_record('iam','create_iam_role',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  

    # Creates a new managed policy for AWS account
    def create_iam_policy(self, policy_name, policy_document):
        try:
            response = self.client_iam.create_policy(
                PolicyName = policy_name,
                PolicyDocument = policy_document
            )
            print(response)
            database.add_record('iam','create_iam_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 

    # Creates a new AWS secret access key and access key ID    
    def create_user_access_key(self, user_name):
        try:
            response = self.client_iam.create_access_key(
                UserName = user_name
            )
            print(response)
            database.add_record('iam','create_user_access_key',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Attaches the specified managed policy to the specified user    
    def attach_user_policy(self, user_name, policy_arn):
        try:
            response = self.client_iam.attach_user_policy(
                UserName = user_name,
                PolicyArn = policy_arn
            )
            print(response)
            database.add_record('iam','attach_user_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Attaches the specified managed policy to the specified group    
    def attach_group_policy(self, group_name, policy_arn):
        try:
            response = self.client_iam.attach_group_policy(
                GroupName = group_name,
                PolicyArn = policy_arn
            )
            print(response)
            database.add_record('iam','attach_group_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Attaches the specified managed policy to the specified role    
    def attach_role_policy(self, role_name, policy_arn):
        try:
            response = self.client_iam.attach_role_policy(
                RoleName = role_name,
                PolicyArn = policy_arn
            )
            print(response)
            database.add_record('iam','attach_role_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Removes the specified managed policy from the specified user    
    def detach_user_policy(self, user_name, policy_arn):
        try:
            response = self.client_iam.detach_user_policy(
                UserName = user_name,
                PolicyArn = policy_arn
            )
            print(response)
            database.add_record('iam','detach_user_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Removes the specified managed policy from the specified group    
    def detach_group_policy(self, group_name, policy_arn):
        try:
            response = self.client_iam.detach_group_policy(
                GroupName = group_name,
                PolicyArn = policy_arn
            )
            print(response)
            database.add_record('iam','detach_group_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Removes the specified managed policy from the specified role    
    def detach_role_policy(self, role_name, policy_arn):
        try:
            response = self.client_iam.detach_role_policy(
                RoleName = role_name,
                PolicyArn = policy_arn
            )
            print(response)
            database.add_record('iam','detach_role_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def update_iam_user(self, user_name, new_user_name):
        try:
            response = self.client_iam.update_user(
                UserName = user_name,
                NewUserName = new_user_name
            )
            print(response)
            database.add_record('iam','update_iam_user',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def update_iam_group(self, group_name, new_group_name):
        try:
            response = self.client_iam.update_group(
                GroupName = group_name,
                NewGroupName = new_group_name
            )
            print(response)
            database.add_record('iam','update_iam_group',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def update_iam_role(self, role_name, description):
        try:
            response = self.client_iam.update_user(
                RoleName = role_name,
                Description = description
            )
            print(response)
            database.add_record('iam','update_iam_role',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Deletes the specified IAM user
    def delete_iam_user(self, user_name):
        try:
            response = self.client_iam.delete_user(
                UserName = user_name
            ) 
            print("User deleted successfully")
            database.add_record('iam','delete_iam_user',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)   
    
    # Deletes the specified IAM group
    def delete_iam_group(self, group_name):
        try:
            response = self.client_iam.delete_group(
                GroupName = group_name
            ) 
            print("Group deleted successfully")
            database.add_record('iam','delete_iam_group',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 

    # Deletes the specified IAM role
    def delete_iam_role(self, role_name):
        try:
            response = self.client_iam.delete_role(
                RoleName = role_name
            ) 
            print("Role deleted successfully")
            database.add_record('iam','delete_iam_role',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 

    # Deletes the specified IAM policy
    def delete_iam_policy(self, policy_arn):
        try:
            response = self.client_iam.delete_policy(
                PolicyArn = policy_arn
            ) 
            print("Policy deleted successfully")
            database.add_record('iam','delete_iam_policy',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)    
           
    def delete_user_access_key(self, user_name, access_key_id):
        try:
            response = self.client_iam.delete_access_key(
                UserName = user_name,
                AccessKeyId = access_key_id
            )
            print("Access key deleted Successfully")
            database.add_record('iam','delete_user_access_key',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 
        
    def delete_iam_login_profile(self, user_name):
        try:
            response = self.delete_login_profile(
                UserName = user_name
            )
            print("IAM user's password deleted Successfully")
            database.add_record('iam','delete_iam_login_profile',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Adds the specified user to the specified group   
    def add_user_to_group(self, group_name, user_name):
        try:
            response = self.client_iam.add_user_to_group(
                GroupName = group_name,
                UserName = user_name
            )
            print(response)
            database.add_record('iam','add_user_to_group',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 

    # Removes the specified user from the specified group   
    def remove_user_from_group(self, group_name, user_name):
        try:
            response = self.client_iam.remove_user_from_group(
                GroupName = group_name,
                UserName = user_name
            )
            print(response)
            database.add_record('iam','remove_user_from_group',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

class Elasticache_helper:

    def __init__(self):
        self.client_ec = boto3.client('elasticache')  

    # Returns a list of users
    def describe_ec_users(self):
        try:
            ec_users = []
            response = self.client_ec.describe_users()
            for res in response['Users']:
                output = {
                'UserId' : res['UserId'],
                'UserName' : res['UserName'],
                'Status' : res['Status'],
                'Engine' : res['Engine'],
                'MinEngineVersion' : res['MinimumEngineVersion'],
                'AccessString' : res['AccessString'],
                'Authentication' : res['Authentication'],
                'ARN' : res['ARN']
                }
                ec_users.append(output) 
            print(ec_users) 
            database.add_record('elasticache','describe_ec_users',ec_users)
            return ec_users
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)    

    # Returns information about all provisioned clusters
    def describe_cache_clusters(self, cache_cluster_id=None):
        try:
            if cache_cluster_id:
                response = self.client_ec.describe_cache_clusters(
                    CacheClusterId=cache_cluster_id
                )
            else:
                response = self.client_ec.describe_cache_clusters()

            output = {
                'CacheClusters': response['CacheClusters']
            }
            print(output)
            database.add_record('elasticache','describe_cache_clusters',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def describe_user_groups(self):
        try:
            response = self.client_ec.describe_user_groups()
            output = {
                'UserGroups': response['UserGroups']
            }
            print(output)
            database.add_record('elasticache','describe_user_groups',output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
       
    def describe_ec_snapshots(self):
        try:
            response = self.client_ec.describe_snapshots()
            output = {
                'Snapshots': response['Snapshots']
            }
            print(output)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
        
    def describe_serverless_cache(self):
        try:
            response = self.client_ec.describe_serverless_caches()
            output = {
                'ServerlessCaches' : response['ServerlessCaches']
            }
            print(output)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)  
         
    # Creates a Redis user
    def create_ec_user(self, user_id, user_name, engine, access_string):
        try:
            response = self.client_ec.create_user(
                UserId = user_id,
                UserName = user_name,
                Engine = engine,
                AccessString = access_string
            ) 
            print(response) 
            database.add_record('elasticache','create_ec_user',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 
        
    def create_user_group(self,user_group_id,engine):
        try:
            response = self.client_ec.create_user_group(
                UserGroupId = user_group_id,
                Engine = engine
            )
            print (response)
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 
        
    def create_cache_cluster(self, cache_cluster_id, cache_cluster_type, engine, num_nodes, limit):
        try:
            response = self.client_ec.create_cache_cluster(
                CacheClusterId = cache_cluster_id,                                  # The node group (shard) identifier
                CacheNodeType = cache_cluster_type,
                Engine = engine,                                                    # The name of the cache engine to be used for this cluster
                NumCacheNodes = num_nodes,                                          # The initial number of cache nodes that the cluster has , redis=1, mamecached=(1-40)
                SnapshotRetentionLimit = limit                                      # The number of days for which ElastiCache retains automatic snapshots before deleting them
            ) 
            print(response) 
            database.add_record('ec', 'create_cache_cluster', response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    def create_ec_snapshot(self,cache_cluster_id,snapshot_name):
        try:
            response = self.client_ec.create_snapshot(
                CacheClusterId = cache_cluster_id,
                SnapshotName = snapshot_name
            )
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)    
        
    def reboot_cache_cluster(self,cache_cluster_id,cache_node_ids):
        try:
            if not isinstance(cache_node_ids, list):
                raise ValueError("Cache Node ids must be provided as a list.")
            
            response = self.client_ec.reboot_cache_cluster(
                CacheClusterId = cache_cluster_id,
                CacheNodeIdsToReboot = cache_node_ids
            )
            print(response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Deletes a Elasticache User
    def delete_ec_user(self, user_id):
        try:
            response = self.client_ec.delete_user(
                UserId = user_id
            )
            database.add_record('elasticache','delete_ec_user',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
         
    def delete_user_group(self,user_group_id):
        try:
            response = self.client_ec.delete_user_group(
                UserGroupId = user_group_id
            )
            print ("User group deleted successfully")
            database.add_record('elasticache','delete_user_group',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    def delete_cache_cluster(self, cache_cluster_id):
        try:
            response = self.client_ec.delete_cache_cluster(
                CacheClusterId = cache_cluster_id
            )
            print("CacheCluster deleted successfully!")
            database.add_record('elasticache','delete_cache_cluster',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e) 
        
    def delete_ec_snapshot(self,snapshot_name):
        try:
            response = self.client_ec.delete_snapshot(
                SnapshotName = snapshot_name
            )
            print("elastiCache Snapshot deleted successfully!")
            database.add_record('elasticache','delete_ec_snapshot',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
# obj = Sqs_helper()
# obj.list_sqs_queue()
# obj1 = EC2_helper()
# obj1.release_Ipaddress("eipalloc-0a4b82e4113e89eb1")
# obj1.create_ec2_instance('ami-07833897a27c82251',1,1,'t3.micro','dsiqdevserver','LorealETL')
# obj1.terminate_ec2_instance(['i-0d93e01fceb25d607'])
# obj1.describe_ec2_instance()
# e = Sns_helper()
# e.list_sns_topic()
# e.delete_sns_topic("arn:aws:sns:us-east-2:054153502545:messages1")
# et = Ses_helper()
# et.list_identity()
# w = S3_helper()
# w.bucket_list_names()
# data = Rds_helper()
# # # data.describe_db_instance()
# data.create_db_instance('LorealETL','db.t3.large','postgres',5,'postgres','MaishaKanisha1819')
# l = IAM_helper()
# l.iam_policies_list()
# r = Elasticache_helper()
# r.describe_ec_users()
