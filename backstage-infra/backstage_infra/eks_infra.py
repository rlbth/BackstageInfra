from aws_cdk import (
    Construct,
    Stack,
    CfnOutput,
    iam,
    aws_ec2 as ec2,
    aws_eks as eks,
)

class BackstageEksClusterStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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

        #Choose subnets for EKS cluster - public subnets eu-west-1a and eu-west-1b that already exist
        subnets = ec2.SubnetSelection(subnet_ids=["subnet-0c0e0ae939a5c7288", "subnet-0c34ccdc84367324a"])
       
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
        
        #Choose subnets for fargate - private subnets eu-west-1a and eu-west-1b that already exist
        fargate_subnets = ec2.SubnetSelection(subnet_ids=["subnet-0c0e0ae939a5c7288", "subnet-0c34ccdc84367324a"])

        # Create a Fargate profile for the cluster
        fargate_profile = cluster.add_fargate_profile('BackStageFargateProfile',
            pod_execution_role=fargate_role,
            selectors=[eks.Selector(namespace='default')],
            vpc_subnets=fargate_subnets
        )

        # Output the cluster name and endpoint URL
        CfnOutput(self, 'ClusterName', value=cluster.cluster_name)
        CfnOutput(self, 'ClusterEndpoint', value=cluster.cluster_endpoint)

