from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_eks as eks,
)
from constructs import Construct

class BackstageEksClusterStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
      
        existing_vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_name='default-vpc')
        vpc = existing_vpc

        #Create IAM role for EKS cluster 
        eks_role = iam.Role(self, "EksRole",
                            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
                            managed_policies=[
                                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy")
                            ])
        
        #Create cluster security group
        eks_sg = ec2.SecurityGroup(self, "BackStageEKSSG", vpc=vpc)
        eks_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_traffic()) # ALL Incoming traffic
        eks_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(8080))  # TCP 8080
        eks_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))   # TCP 443
        eks_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(10250)) # TCP 10250
        eks_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(5432))  # PostgreSQL TCP 5432
        eks_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.udp(53))    # UDP 53 for DNS
        eks_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(53))    # TCP 53 for DNS

        #Choose subnets for EKS cluster - public, private  subnets eu-west-1a  that already exist
        publicsubnet = ec2.Subnet.from_subnet_attributes(self,'publicsubnet', availability_zone = 'eu-west-1a', subnet_id = 'subnet-03e0b91b2ac696fd5')
        privatesubnet = ec2.Subnet.from_subnet_attributes(self,'privatesubnet', availability_zone = 'eu-west-1b', subnet_id = 'subnet-0609b8a74e5ed452a')
        subnets = ec2.SubnetSelection(subnets = [publicsubnet, privatesubnet])
#        subnets = ec2.SubnetSelection(subnet_ids=["subnet-0609b8a74e5ed452a", "subnet-03e0b91b2ac696fd5"])
       
        # Create the EKS cluster
        cluster = eks.Cluster(self, 'backStageCluster',
            version=eks.KubernetesVersion.V1_27,
            cluster_name='backstage-cluster',
            default_capacity=0,  # We will use Fargate profiles for managed nodes
            vpc=vpc,
            vpc_subnets=[subnets],
            masters_role=eks_role,
            security_group=eks_sg,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE
        )
        
        # Create Iam role for Fargate Profile
        fargate_role = iam.Role(self, "BackstageFargateRole",
                        assumed_by=iam.ServicePrincipal("eks-fargate-pods.amazonaws.com"),
                        managed_policies=[
                            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSFargatePodExecutionRolePolicy")
                        ])
        
        #Choose subnets for fargate - private subnets eu-west-1b that already exist
 #       fargate_subnets = ec2.SubnetSelection(subnets = [privatesubnet])
#       fargate_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE)
#       fargate_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType('PRIVATE'))
        # Create a Fargate profile for the cluster
        fargate_profile = cluster.add_fargate_profile('BackStageFargateProfile',
            pod_execution_role=fargate_role,
            selectors=[eks.Selector(namespace='default')],
#            vpc_subnets=fargate_subnets
        )

        # Output the cluster name and endpoint URL
        CfnOutput(self, 'ClusterName', value=cluster.cluster_name)
        CfnOutput(self, 'ClusterEndpoint', value=cluster.cluster_endpoint)

