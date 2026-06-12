import { Construct } from 'constructs'
import * as ssm from 'aws-cdk-lib/aws-ssm'
import * as iam from 'aws-cdk-lib/aws-iam'

/**
 * References to pre-provisioned SSM SecureString parameters.
 *
 * CloudFormation cannot *create* SecureString parameters, so these are created
 * out-of-band with the AWS CLI (see docs/deployment.md) and merely imported
 * here so we can grant read access to the things that need them. No secret
 * values ever appear in the CDK source or synthesized template.
 */
export interface SecretsProps {
  /** Parameter name holding the OpenAI API key. */
  readonly openAiKeyParam: string
  /** Parameter name holding the full Postgres connection string. */
  readonly databaseUrlParam: string
  /** Parameter name holding the GitHub token used by Amplify. */
  readonly githubTokenParam: string
}

export class Secrets extends Construct {
  public readonly openAiKey: ssm.IStringParameter
  public readonly databaseUrl: ssm.IStringParameter
  public readonly githubToken: ssm.IStringParameter

  private readonly paramNames: string[]

  constructor(scope: Construct, id: string, props: SecretsProps) {
    super(scope, id)

    this.openAiKey = ssm.StringParameter.fromSecureStringParameterAttributes(
      this,
      'OpenAiKey',
      { parameterName: props.openAiKeyParam },
    )
    this.databaseUrl = ssm.StringParameter.fromSecureStringParameterAttributes(
      this,
      'DatabaseUrl',
      { parameterName: props.databaseUrlParam },
    )
    this.githubToken = ssm.StringParameter.fromSecureStringParameterAttributes(
      this,
      'GithubToken',
      { parameterName: props.githubTokenParam },
    )

    this.paramNames = [
      props.openAiKeyParam,
      props.databaseUrlParam,
    ]
  }

  /**
   * Grant a principal permission to read (and decrypt) the runtime secrets the
   * API needs: the OpenAI key and the database URL.
   *
   * We grant explicitly rather than via `parameter.grantRead` because imported
   * SecureString parameters don't expose the KMS key, so the consumer also
   * needs `kms:Decrypt` on the account default SSM key.
   */
  public grantRuntimeRead(grantee: iam.IGrantable): void {
    const region = process.env.CDK_DEFAULT_REGION ?? '*'
    const account = process.env.CDK_DEFAULT_ACCOUNT ?? '*'

    grantee.grantPrincipal.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ['ssm:GetParameter', 'ssm:GetParameters'],
        resources: this.paramNames.map(
          (name) =>
            `arn:aws:ssm:${region}:${account}:parameter${
              name.startsWith('/') ? name : `/${name}`
            }`,
        ),
      }),
    )

    grantee.grantPrincipal.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ['kms:Decrypt'],
        resources: [`arn:aws:kms:${region}:${account}:alias/aws/ssm`],
      }),
    )
  }
}
