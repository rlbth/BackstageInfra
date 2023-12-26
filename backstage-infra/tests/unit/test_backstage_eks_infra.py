import pytest
from aws_cdk import (
    Construct,
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_eks as eks,
)

from backstage_infra.eks_infra import BackstageEksClusterStack

@pytest.fixture
def stack():
    # Create a mocked VPC for testing
    vpc = ec2.Vpc.from_vpc_attributes(
        stack, 'MockVpc',
        vpc_id='mock-vpc-id',
        availability_zones=['eu-west-1a', 'eu-west-1b'],
        public_subnet_ids=['mock-subnet-id-1', 'mock-subnet-id-2']
    )

    # Create a stack instance
    stack = BackstageEksClusterStack(stack, 'MockEKSStack', vpc)

    return stack

def test_fargate_profile_creation(stack):
    # Assert that the Fargate profile is created with the correct selectors
    assert len(stack.node.find_all('AWS::EKS::FargateProfile')) == 1
    fargate_profile = stack.node.find_child('Profile')
    assert fargate_profile.selectors[0].namespace == 'default'

def test_cluster_outputs(stack):
    # Assert that the cluster name and endpoint are correctly outputted
    assert len(stack.node.find_all('AWS::CloudFormation::Output')) == 2
    cluster_name_output = stack.node.find_child('ClusterName')
    cluster_endpoint_output = stack.node.find_child('ClusterEndpoint')
    assert cluster_name_output.value == 'backstage-cluster'
    assert cluster_endpoint_output.value == 'https://<cluster-endpoint>'
