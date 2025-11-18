from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    RemovalPolicy,
    Duration
)
from constructs import Construct

class SpaceXStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # 1. DynamoDB Table
        launches_table = dynamodb.Table(
            self, "SpaceXLaunchesTable",
            table_name="spacex-launches",
            partition_key=dynamodb.Attribute(
                name="launch_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="launch_date",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # 2. Lambda Function
        spacex_lambda = lambda_.Function(
            self, "SpaceXDataProcessor",
            function_name="spacex-data-processor",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("../lambda"),
            timeout=Duration.minutes(5),
            environment={
                "TABLE_NAME": launches_table.table_name
            }
        )
        
        # Permisos para Lambda
        launches_table.grant_read_write_data(spacex_lambda)
        
        # 3. EventBridge Rule (cada 6 horas)
        rule = events.Rule(
            self, "ScheduledRule",
            schedule=events.Schedule.rate(Duration.hours(6))
        )
        rule.add_target(targets.LambdaFunction(spacex_lambda))
        
        # 4. Setup ECS Infrastructure
        self._setup_ecs_infrastructure(launches_table)
        
        # Outputs
        from aws_cdk import CfnOutput
        CfnOutput(self, "TableName", value=launches_table.table_name)
        CfnOutput(self, "LambdaFunctionName", value=spacex_lambda.function_name)

    def _setup_ecs_infrastructure(self, table):
        """Configura la infraestructura ECS para la aplicación web"""
        
        # VPC
        vpc = ec2.Vpc(
            self, "AppVPC",
            max_azs=2,
            nat_gateways=0, 
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )
                
        # ECR Repository para el backend
        backend_repo = ecr.Repository(
            self, "BackendRepository",
            repository_name="spacex-backend",
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True
        )
        
        # ECR Repository para el frontend  
        frontend_repo = ecr.Repository(
            self, "FrontendRepository",
            repository_name="spacex-frontend",
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True
        )
        
        # ECS Cluster
        cluster = ecs.Cluster(
            self, "AppCluster",
            vpc=vpc,
            cluster_name="spacex-app-cluster"
        )
        
        # Task Execution Role
        task_execution_role = iam.Role(
            self, "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for ECS Task Execution",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )
        
        # Task Role para el backend (acceso a DynamoDB)
        backend_task_role = iam.Role(
            self, "BackendTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for Backend ECS Task"
        )
        table.grant_read_data(backend_task_role)
        
        # Backend Task Definition
        backend_task_definition = ecs.FargateTaskDefinition(
            self, "BackendTaskDefinition",
            execution_role=task_execution_role,
            task_role=backend_task_role,
            memory_limit_mib=512,
            cpu=256
        )
        
        # Backend Container
        backend_container = backend_task_definition.add_container(
            "BackendContainer",
            image=ecs.ContainerImage.from_asset("../backend"),
            environment={
                "TABLE_NAME": table.table_name,
                "DEBUG": "False",
                "AWS_DEFAULT_REGION": "us-east-1"
            },
            logging=ecs.LogDriver.aws_logs(stream_prefix="Backend")
        )
        
        backend_container.add_port_mappings(ecs.PortMapping(container_port=8000))
        
        # Frontend Task Definition
        frontend_task_definition = ecs.FargateTaskDefinition(
            self, "FrontendTaskDefinition", 
            execution_role=task_execution_role,
            memory_limit_mib=512,
            cpu=256
        )
        
        # Frontend Container
        frontend_container = frontend_task_definition.add_container(
            "FrontendContainer",
            image=ecs.ContainerImage.from_asset("../frontend"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="Frontend")
        )
        
        frontend_container.add_port_mappings(ecs.PortMapping(container_port=80))
        
        # Application Load Balancer
        lb = elbv2.ApplicationLoadBalancer(
            self, "LoadBalancer",
            vpc=vpc,
            internet_facing=True
        )
        
        # Backend Service
        backend_service = ecs.FargateService(
            self, "BackendService",
            cluster=cluster,
            task_definition=backend_task_definition,
            desired_count=1,
            assign_public_ip=True,
            health_check_grace_period=Duration.minutes(3),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )
        
        # Frontend Service
        frontend_service = ecs.FargateService(
            self, "FrontendService",
            cluster=cluster,
            task_definition=frontend_task_definition,
            desired_count=1,
            assign_public_ip=True,
            health_check_grace_period=Duration.minutes(2),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)

        )
        
        # Backend Target Group
        backend_target_group = elbv2.ApplicationTargetGroup(
            self, "BackendTargetGroup",
            port=8000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[backend_service],
            vpc=vpc,
            health_check=elbv2.HealthCheck(
                path="/health/",
                interval=Duration.seconds(60)
            )
        )
        
        # Frontend Target Group  
        frontend_target_group = elbv2.ApplicationTargetGroup(
            self, "FrontendTargetGroup",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[frontend_service],
            vpc=vpc
        )
        
        # Listeners
        lb.add_listener("BackendListener", 
            port=8000,
            default_target_groups=[backend_target_group]
        )
        
        lb.add_listener("FrontendListener",
            port=80, 
            default_target_groups=[frontend_target_group]
        )
        
        # Outputs
        from aws_cdk import CfnOutput
        CfnOutput(self, "BackendRepositoryUri", value=backend_repo.repository_uri)
        CfnOutput(self, "FrontendRepositoryUri", value=frontend_repo.repository_uri)
        CfnOutput(self, "LoadBalancerDNS", value=lb.load_balancer_dns_name)
        CfnOutput(self, "FrontendURL", value=f"http://{lb.load_balancer_dns_name}")
        CfnOutput(self, "BackendURL", value=f"http://{lb.load_balancer_dns_name}:8000")
        CfnOutput(self, "SwaggerURL", value=f"http://{lb.load_balancer_dns_name}:8000/swagger/")