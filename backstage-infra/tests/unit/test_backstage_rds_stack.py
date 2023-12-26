import pytest
from aws_cdk import Stack, rds, ec2, InstanceClass, InstanceSize, InstanceType, SecretValue, RemovalPolicy
from constructs import Construct

from backstage_infra.rds_stack import BackstageRDSStack

def test_backstage_rds_stack():
    # Create a mock VPC
    vpc = ec2.Vpc()

    # Create a test stack
    stack = Stack()

    # Instantiate the BackstageRDSStack
    backstage_rds_stack = BackstageRDSStack(stack, 'BackstageRDSStack', vpc)

    # Assert that the RDS instance is created with the correct properties
    rds_instance = backstage_rds_stack.node.find_child('BackstageRdsInstance')
    assert isinstance(rds_instance, rds.DatabaseInstance)
    assert rds_instance.engine == rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13)
    assert rds_instance.instance_type == InstanceType.of(InstanceClass.BURSTABLE2, InstanceSize.SMALL)
    assert rds_instance.master_username == 'admin'
    assert rds_instance.master_user_password == SecretValue.plain_text('P@ssw0rd')
    assert rds_instance.vpc == vpc
    assert rds_instance.vpc_subnets == rds.SubnetSelection(subnet_type=rds.SubnetType.PRIVATE)
    assert rds_instance.removal_policy == RemovalPolicy.DESTROY
