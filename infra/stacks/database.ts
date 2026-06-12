import { Construct } from 'constructs'
import { Duration, RemovalPolicy } from 'aws-cdk-lib'
import * as ec2 from 'aws-cdk-lib/aws-ec2'
import * as rds from 'aws-cdk-lib/aws-rds'

/**
 * Networking + Postgres for MiniGlean.
 *
 * A small VPC (2 AZs, a single NAT gateway) hosts an RDS Postgres 16 instance
 * with the pgvector extension. The database lives in isolated subnets and is
 * never publicly reachable; only resources in {@link lambdaSecurityGroup} may
 * connect. The single NAT gateway exists so Lambdas in the private-with-egress
 * subnets can reach the OpenAI API (it is the main recurring cost — roughly
 * ~$32/month — and is documented in docs/deployment.md).
 */
export class Database extends Construct {
  /** VPC shared with the API Lambda. */
  public readonly vpc: ec2.Vpc
  /** Postgres instance. */
  public readonly instance: rds.DatabaseInstance
  /** Security group attached to the database. */
  public readonly dbSecurityGroup: ec2.SecurityGroup
  /** Security group the Lambda must use to be granted DB ingress. */
  public readonly lambdaSecurityGroup: ec2.SecurityGroup
  /** Logical Postgres database name. */
  public readonly databaseName = 'miniglean'

  constructor(scope: Construct, id: string) {
    super(scope, id)

    this.vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        {
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: 'private-egress',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 24,
        },
        {
          name: 'isolated',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
          cidrMask: 24,
        },
      ],
    })

    this.dbSecurityGroup = new ec2.SecurityGroup(this, 'DbSecurityGroup', {
      vpc: this.vpc,
      description: 'MiniGlean RDS Postgres access',
      allowAllOutbound: false,
    })

    this.lambdaSecurityGroup = new ec2.SecurityGroup(this, 'LambdaSecurityGroup', {
      vpc: this.vpc,
      description: 'MiniGlean API Lambda',
      allowAllOutbound: true,
    })

    // Only the API Lambda may reach Postgres.
    this.dbSecurityGroup.addIngressRule(
      this.lambdaSecurityGroup,
      ec2.Port.tcp(5432),
      'Allow API Lambda to connect to Postgres',
    )

    // pgvector ships with RDS Postgres 16 but must be enabled per-database via
    // `CREATE EXTENSION IF NOT EXISTS vector;` — this runs in the first Alembic
    // migration (see docs/deployment.md), not here.
    const parameterGroup = new rds.ParameterGroup(this, 'ParameterGroup', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_16,
      }),
      description: 'MiniGlean Postgres 16 (pgvector enabled via migration)',
    })

    this.instance = new rds.DatabaseInstance(this, 'Postgres', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_16,
      }),
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.BURSTABLE4_GRAVITON,
        ec2.InstanceSize.MICRO,
      ),
      vpc: this.vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      securityGroups: [this.dbSecurityGroup],
      parameterGroup,
      databaseName: this.databaseName,
      // Generates a Secrets Manager secret for the master credentials.
      credentials: rds.Credentials.fromGeneratedSecret('miniglean'),
      multiAz: false,
      allocatedStorage: 20,
      maxAllocatedStorage: 50,
      backupRetention: Duration.days(7),
      deleteAutomatedBackups: true,
      publiclyAccessible: false,
      removalPolicy: RemovalPolicy.SNAPSHOT,
    })
  }
}
