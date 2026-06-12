#!/usr/bin/env node
import { App, Stack, StackProps } from 'aws-cdk-lib'
import { Construct } from 'constructs'
import { Database } from '../stacks/database'
import { Secrets } from '../stacks/secrets'
import { Api } from '../stacks/api'
import { Frontend } from '../stacks/frontend'

// SSM SecureString parameter names. Create these once via the AWS CLI before
// deploying (see docs/deployment.md). They hold the only secret values.
const OPENAI_KEY_PARAM = '/miniglean/openai-api-key'
const DATABASE_URL_PARAM = '/miniglean/database-url'
const GITHUB_TOKEN_PARAM = '/miniglean/github-token'

/**
 * Single stack composing every MiniGlean construct: networking + database,
 * imported secrets, the FastAPI Lambda + HTTP API, and the Amplify frontend.
 */
class MinigleanStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)

    // Context overrides (passed with `cdk deploy -c key=value`).
    // frontendUrl defaults to "*" for the first deploy; tighten it once the
    // Amplify URL is known by re-deploying with -c frontendUrl=https://...
    const frontendUrl = (this.node.tryGetContext('frontendUrl') as string) ?? '*'
    const repoOwner = (this.node.tryGetContext('repoOwner') as string) ?? 'your-github-user'
    const repoName = (this.node.tryGetContext('repoName') as string) ?? 'miniglean'
    const branch = (this.node.tryGetContext('branch') as string) ?? 'main'

    const database = new Database(this, 'Database')

    const secrets = new Secrets(this, 'Secrets', {
      openAiKeyParam: OPENAI_KEY_PARAM,
      databaseUrlParam: DATABASE_URL_PARAM,
      githubTokenParam: GITHUB_TOKEN_PARAM,
    })

    const api = new Api(this, 'Api', {
      database,
      secrets,
      openAiKeyParam: OPENAI_KEY_PARAM,
      databaseUrlParam: DATABASE_URL_PARAM,
      frontendUrl,
    })

    new Frontend(this, 'Frontend', {
      repoOwner,
      repoName,
      branch,
      githubTokenParam: GITHUB_TOKEN_PARAM,
      apiUrl: api.httpApi.apiEndpoint,
    })
  }
}

const app = new App()

new MinigleanStack(app, 'MinigleanStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
})

app.synth()
