#!/usr/bin/env python3
import os
import aws_cdk as cdk

from backstage_infra.rds_stack import BackstageRDSStack
from backstage_infra.eks_infra import BackstageEksClusterStack

existing_vpc = cdk.ec2.Vpc.from_lookup( 'ExistingVpc', vpc_id='your-existing-vpc-id')
aws_account=cdk.Environment(account='123456789012', region='eu-west-1')
app = cdk.App()
BackstageEksClusterStack(app, description ='Sets up an EKS cluster and a fargate profile', vpc=existing_vpc, env=aws_account)
BackstageRDSStack(app, description = 'Sets up an Posgres RDS instance', vpc=existing_vpc, env=aws_account )
app.synth()
