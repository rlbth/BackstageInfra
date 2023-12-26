from aws_cdk import (
    # Duration,
    Stack,
    rds,
    ec2,
    InstanceClass,
    InstanceSize,
    InstanceType,
    SecretValue,
    RemovalPolicy
    # aws_sqs as sqs,
)
from constructs import Construct

class BackstageRDSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        rds.DatabaseInstance(
            self,
            'BackstageRdsInstance',
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13),
            instance_type=InstanceType.of(InstanceClass.BURSTABLE2, InstanceSize.SMALL),
            master_username='admin',
            master_user_password=SecretValue.plain_text('P@ssw0rd'),
            vpc=vpc,
            vpc_subnets=rds.SubnetSelection(subnet_type=rds.SubnetType.PRIVATE),
            removal_policy=RemovalPolicy.DESTROY,
        )
