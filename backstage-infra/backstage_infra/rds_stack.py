from aws_cdk import (
    # Duration,
    Stack,
    aws_rds,
    aws_ec2 as ec2,
    SecretValue,
    RemovalPolicy
    # aws_sqs as sqs,
)

from constructs import Construct

class BackstageRDSStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        existing_vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_name='default-vpc')
        vpc = existing_vpc

 #      RDS Config   
 #       rds.DatabaseInstance(
 #           self,
 #           'BackstageRdsInstance',
 #           engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13),
 #           instance_type=InstanceType.of(InstanceClass.BURSTABLE2, InstanceSize.SMALL),
 #           master_username='admin',
 #           master_user_password=SecretValue.plain_text('P@ssw0rd'),
 #           vpc=vpc,
 #           vpc_subnets=rds.SubnetSelection(subnet_type=rds.SubnetType.PRIVATE),
 #           removal_policy=RemovalPolicy.DESTROY,
 #       )

        privatesubnet1 = ec2.Subnet.from_subnet_attributes(self,'privatesubnet1', availability_zone = 'eu-west-1b', subnet_id = 'subnet-0609b8a74e5ed452a')
        privatesubnet2 = ec2.Subnet.from_subnet_attributes(self,'privatesubnet2', availability_zone = 'eu-west-1c', subnet_id = 'subnet-0b5d69bbc0a8a6a10')

        aws_rds.DatabaseCluster(
            self,
            'BackstageAuroraCluster',
            engine=aws_rds.DatabaseClusterEngine.aurora_postgres(
                version=aws_rds.AuroraPostgresEngineVersion.VER_15_3
            ),
            instances=2,  # Number of DB instances in the cluster
            instance_props=aws_rds.InstanceProps(
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.BURSTABLE2, 
                    ec2.InstanceSize.SMALL
                ),
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnets = [privatesubnet1, privatesubnet2]),
            ),
            credentials=aws_rds.Credentials.from_password(
                username='dbadmin', 
                password=SecretValue.plain_text('P@ssw0rd')
            ),
            removal_policy=RemovalPolicy.DESTROY
        )
