from aws_cdk import App

from cdk.stack import LambdaSqliteEfsStack


app = App()

LambdaSqliteEfsStack(
    app,
    "LambdaSqliteEfs",
    env={
        "account": "0123456789",
        "region": "us-east-1",
    },
)

app.synth()
