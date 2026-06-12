import { Construct } from 'constructs'
import { SecretValue, CfnOutput } from 'aws-cdk-lib'
import * as amplify from '@aws-cdk/aws-amplify-alpha'
import { BuildSpec } from 'aws-cdk-lib/aws-codebuild'

export interface FrontendProps {
  /** owner/repo of the GitHub source, e.g. "your-user/miniglean". */
  readonly repoOwner: string
  readonly repoName: string
  /** Git branch Amplify builds and auto-deploys. */
  readonly branch: string
  /** SSM SecureString parameter name holding a GitHub PAT for Amplify. */
  readonly githubTokenParam: string
  /** Base URL of the deployed API, injected as NEXT_PUBLIC_API_URL. */
  readonly apiUrl: string
}

/**
 * Next.js frontend hosted on AWS Amplify (WEB_COMPUTE for App Router SSR).
 *
 * Amplify pulls from GitHub using a PAT stored in SSM. The monorepo lives under
 * apps/web, so the build spec cds into that workspace. NEXT_PUBLIC_API_URL is
 * wired to the API endpoint at deploy time — a one-way dependency
 * (frontend -> api) that avoids a circular reference with CORS.
 */
export class Frontend extends Construct {
  public readonly app: amplify.App

  constructor(scope: Construct, id: string, props: FrontendProps) {
    super(scope, id)

    const githubToken = SecretValue.ssmSecure(props.githubTokenParam)

    this.app = new amplify.App(this, 'App', {
      appName: 'miniglean-web',
      sourceCodeProvider: new amplify.GitHubSourceCodeProvider({
        owner: props.repoOwner,
        repository: props.repoName,
        oauthToken: githubToken,
      }),
      platform: amplify.Platform.WEB_COMPUTE,
      environmentVariables: {
        NEXT_PUBLIC_API_URL: props.apiUrl,
        AMPLIFY_MONOREPO_APP_ROOT: 'apps/web',
      },
      buildSpec: BuildSpec.fromObjectToYaml({
        version: 1,
        applications: [
          {
            appRoot: 'apps/web',
            frontend: {
              phases: {
                preBuild: { commands: ['npm ci'] },
                build: { commands: ['npm run build'] },
              },
              artifacts: {
                baseDirectory: '.next',
                files: ['**/*'],
              },
              cache: { paths: ['node_modules/**/*', '.next/cache/**/*'] },
            },
          },
        ],
      }),
    })

    this.app.addBranch(props.branch, { autoBuild: true })

    new CfnOutput(this, 'AmplifyAppId', {
      value: this.app.appId,
      description: 'Amplify App ID (find the live URL in the Amplify console)',
    })
  }
}
