from typing import Any

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_efs as efs
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from constructs import Construct


EFS_MOUNT_PATH = "/mnt/datastore"


class LambdaSqliteEfsStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs: Any):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "Vpc", nat_gateways=0)

        file_system = efs.FileSystem(
            self,
            "FileSystem",
            vpc=vpc,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        access_point = file_system.add_access_point(
            "AccessPoint",
            path="/graphql-lambda",
            create_acl=efs.Acl(owner_uid="1001", owner_gid="1001", permissions="755"),
            posix_user=efs.PosixUser(uid="1001", gid="1001"),
        )

        bundling = cdk.BundlingOptions(
            image=cdk.DockerImage("public.ecr.aws/sam/build-python3.9"),
            command=[
                "bash",
                "-c",
                "pip install -r requirements.txt -t /asset-output/python"
                " && cp -au . /asset-output || true",
            ],
        )

        deps_layer = lambda_.LayerVersion(
            self,
            "ApiLayer",
            code=lambda_.Code.from_asset("lambdas/layer", bundling=bundling),
        )

        graphql_fn = lambda_.Function(
            self,
            "GraphQLFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambdas/graphql"),
            handler="package.main.handler",
            layers=[deps_layer],
            filesystem=lambda_.FileSystem.from_efs_access_point(
                access_point, EFS_MOUNT_PATH
            ),
            memory_size=1024,
            timeout=cdk.Duration.minutes(5),
            environment={
                "MOUNT_PATH": EFS_MOUNT_PATH,
            },
            log_retention=logs.RetentionDays.THREE_MONTHS,
            vpc=vpc,  # type: ignore
        )

        fn_url = lambda_.FunctionUrl(
            self,
            "GraphQLUrl",
            function=graphql_fn,  # type: ignore
            auth_type=lambda_.FunctionUrlAuthType.NONE,
        )

        load_fn = lambda_.Function(
            self,
            "LoadFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambdas/graphql"),
            handler="package.debug.load_handler",
            layers=[deps_layer],
            filesystem=lambda_.FileSystem.from_efs_access_point(
                access_point, EFS_MOUNT_PATH
            ),
            memory_size=1024,
            timeout=cdk.Duration.minutes(5),
            environment={
                "MOUNT_PATH": EFS_MOUNT_PATH,
            },
            log_retention=logs.RetentionDays.THREE_MONTHS,
            vpc=vpc,  # type: ignore
        )

        clear_fn = lambda_.Function(
            self,
            "ClearFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambdas/graphql"),
            handler="package.debug.clear_handler",
            layers=[deps_layer],
            filesystem=lambda_.FileSystem.from_efs_access_point(
                access_point, EFS_MOUNT_PATH
            ),
            memory_size=1024,
            timeout=cdk.Duration.minutes(5),
            environment={
                "MOUNT_PATH": EFS_MOUNT_PATH,
            },
            log_retention=logs.RetentionDays.THREE_MONTHS,
            vpc=vpc,  # type: ignore
        )

        cdk.CfnOutput(self, "FunctionUrl", value=fn_url.url)
        cdk.CfnOutput(self, "LoadFunctionName", value=load_fn.function_name)
        cdk.CfnOutput(self, "ClearFunctionName", value=clear_fn.function_name)
