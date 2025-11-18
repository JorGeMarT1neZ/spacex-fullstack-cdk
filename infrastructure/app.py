#!/usr/bin/env python3
import aws_cdk as cdk
from stack.spacex_stack import SpaceXStack

app = cdk.App()

# Stack principal
SpaceXStack(
    app, "SpaceXFullStack",
    description="SpaceX Launches FullStack Application",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )
)

app.synth()
