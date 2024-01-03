#!/usr/bin/env python3
import os
import aws_cdk as cdk
from constructs import Construct

from backstage_infra.eks_infra import BackstageEksClusterStack

aws_account=cdk.Environment(account='938361207488', region='eu-west-1')
app = cdk.App()
BackstageEksClusterStack(scope=app, id="EKSCluster", description ='Sets up an EKS cluster and a fargate profile', env=aws_account)
app.synth()

