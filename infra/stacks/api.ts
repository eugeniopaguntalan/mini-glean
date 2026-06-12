import { Construct } from 'constructs'
import { Duration, CfnOutput } from 'aws-cdk-lib'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as ec2 from 'aws-cdk-lib/aws-ec2'
import * as events from 'aws-cdk-lib/aws-events'
import * as targets from 'aws-cdk-lib/aws-events-targets'
import { HttpApi, CorsHttpMethod, HttpMethod } from 'aws-cdk-lib/aws-apigatewayv2'
import { HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations'
import * as path from 'path'
import { Database } from './database'
import { Secrets } from './secrets'

export interface ApiProps {
  readonly database: Database
  readonly secrets: Secrets
  /** SSM parameter names passed to the Lambda so it can fetch secrets. */
  readonly openAiKeyParam: string
  readonly databaseUrlParam: string
  /** Allowed CORS origin for the frontend ("*" until the Amplify URL is known). */
  readonly frontendUrl: string
}

/**
 * The FastAPI backend running on Lambda (Python 3.12) behind an HTTP API.
 *
 * The Python source in apps/api is bundled with pip inside a Docker build so
 * native wheels (asyncpg, pdfplumber, tiktoken) match the Lambda runtime. A
 * scheduled EventBridge rule pings the function every 5 minutes with a warmer
 * event to mitigate cold starts.
 */
export class Api extends Construct {
  public readonly httpApi: HttpApi
  public readonly handler: lambda.Function

  constructor(scope: Construct, id: string, props: ApiProps) {
    super(scope, id)

    this.handler = new lambda.Function(this, 'Handler', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'lambda_handler.handler',
      memorySize: 512,
      timeout: Duration.seconds(30),
      code: lambda.Code.fromAsset(path.join(__dirname, '..', '..', 'apps', 'api'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash',
            '-c',
            [
              'pip install -r requirements.txt -t /asset-output',
              'cp -au . /asset-output',
            ].join(' && '),
          ],
        },
      }),
      vpc: props.database.vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      securityGroups: [props.database.lambdaSecurityGroup],
      environment: {
        ENVIRONMENT: 'production',
        LOG_LEVEL: 'INFO',
        ALLOWED_ORIGINS: props.frontendUrl,
        // Secret *names* only — never the values. Read at cold start via SSM.
        OPENAI_API_KEY_PARAM: props.openAiKeyParam,
        DATABASE_URL_PARAM: props.databaseUrlParam,
      },
    })

    // Allow the Lambda to read the runtime secrets from SSM.
    props.secrets.grantRuntimeRead(this.handler)

    this.httpApi = new HttpApi(this, 'HttpApi', {
      corsPreflight: {
        allowOrigins: [props.frontendUrl],
        allowMethods: [CorsHttpMethod.ANY],
        allowHeaders: ['Content-Type', 'Authorization'],
        maxAge: Duration.hours(1),
      },
    })

    this.httpApi.addRoutes({
      path: '/{proxy+}',
      methods: [HttpMethod.ANY],
      integration: new HttpLambdaIntegration('LambdaIntegration', this.handler),
    })

    // Warmer: ping the function every 5 minutes to keep it hot.
    new events.Rule(this, 'Warmer', {
      schedule: events.Schedule.rate(Duration.minutes(5)),
      targets: [
        new targets.LambdaFunction(this.handler, {
          event: events.RuleTargetInput.fromObject({ warmer: true }),
        }),
      ],
    })

    new CfnOutput(this, 'ApiUrl', {
      value: this.httpApi.apiEndpoint,
      description: 'Base URL of the MiniGlean HTTP API',
    })
  }
}
