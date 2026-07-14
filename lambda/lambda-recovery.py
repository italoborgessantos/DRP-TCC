import time
import boto3
import json
from botocore.exceptions import ClientError

rds = boto3.client('rds', region_name='us-east-1')
backup = boto3.client('backup', region_name='us-east-1')
ssm = boto3.client('ssm', region_name='us-east-1')
ssm_cmd = boto3.client('ssm', region_name='us-east-1')
ec2 = boto3.client('ec2', region_name='us-east-1')

COOLDOWN_SECONDS = 15 * 60
LAST_RUN_PARAM = '/app/lambda/last_run'

original_instance_id = 'webshopdb'
resource_arn = 'arn:aws:rds:us-east-1:509399598717:db:webshopdb'
restore_db_instance_id = 'webshopdb-restaurado'
ec2_instance_id = 'i-08866d6ae981bfebb'
role_arn = 'arn:aws:iam::509399598717:role/service-role/AWSBackupDefaultServiceRole'


def get_last_run():
    try:
        response = ssm.get_parameter(Name=LAST_RUN_PARAM)
        return int(response['Parameter']['Value'])
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            return 0
        else:
            raise e


def update_last_run(timestamp):
    ssm.put_parameter(
        Name=LAST_RUN_PARAM,
        Value=str(timestamp),
        Type='String',
        Overwrite=True
    )


def wait_for_ec2_status_ok(instance_id, timeout_minutes=5):
    waiter = ec2.get_waiter('instance_status_ok')
    try:
        waiter.wait(
            InstanceIds=[instance_id],
            WaiterConfig={'Delay': 15, 'MaxAttempts': int(
                timeout_minutes * 60 / 15)}
        )
        return True
    except Exception as e:
        print(f"Timeout/Erro esperando EC2 status OK: {e}")
        return False


def lambda_handler(event, context):
    now = int(time.time())
    last_run = get_last_run()

    if now - last_run < COOLDOWN_SECONDS:
        print(
            f"Cooldown ativo. Última execução há {now - last_run} segundos. Saindo.")
        return {'statusCode': 200, 'body': f'Cooldown ativo.'}

    update_last_run(now)

    # --- REBOOT do EC2 ---
    try:
        print(f"Iniciando reboot do EC2 {ec2_instance_id}...")
        ec2.reboot_instances(InstanceIds=[ec2_instance_id])
    except ClientError as e:
        print(f"Falha ao pedir reboot da instância: {e}")
        raise

    if not wait_for_ec2_status_ok(ec2_instance_id, timeout_minutes=6):
        raise Exception(
            "EC2 não voltou ao estado OK dentro do tempo esperado.")

    print("EC2 reiniciado — prosseguindo...")

    # --- LISTAR BACKUPS ---
    backups_response = backup.list_recovery_points_by_backup_vault(
        BackupVaultName='Default',
        MaxResults=10
    )

    recovery_points = [
        r for r in backups_response['RecoveryPoints']
        if r['ResourceArn'] == resource_arn
    ]

    if not recovery_points:
        raise Exception("Nenhum backup encontrado!")

    recovery_points = sorted(
        recovery_points,
        key=lambda x: x['CreationDate'],
        reverse=True
    )

    SAFE_WINDOW_SECONDS = 2 * 60 * 60
    selected_recovery_point = None

    for i, rp in enumerate(recovery_points):
        creation_time = int(rp['CreationDate'].timestamp())
        diff = now - creation_time

        print(f"Backup {i}: criado há {diff} segundos")

        if diff > SAFE_WINDOW_SECONDS:
            selected_recovery_point = rp
            print(
                f"Selecionado backup fora da janela de risco (>{SAFE_WINDOW_SECONDS}s)")
            break

    # fallback (caso todos estejam dentro da janela)
    if not selected_recovery_point:
        print("Todos os backups estão dentro da janela de risco. Usando o mais antigo disponível.")
        selected_recovery_point = recovery_points[-1]

    recovery_point_arn = selected_recovery_point['RecoveryPointArn']
    print(f"Usando backup: {recovery_point_arn}")

    # --- RESTAURAÇÃO ---
    original_instance = rds.describe_db_instances(
        DBInstanceIdentifier=original_instance_id
    )['DBInstances'][0]

    sgp = [sg['VpcSecurityGroupId']
           for sg in original_instance['VpcSecurityGroups']]

    response = backup.start_restore_job(
        RecoveryPointArn=recovery_point_arn,
        Metadata={
            'DBInstanceIdentifier': restore_db_instance_id,
            'Engine': 'mysql',
            'DBInstanceClass': 'db.t3.micro',
            'MultiAZ': 'false',
            'PubliclyAccessible': 'false',
            'Port': '3306',
            'VpcSecurityGroupIds': json.dumps(sgp)
        },
        IamRoleArn=role_arn,
        IdempotencyToken=str(now)
    )

    restore_job_id = response['RestoreJobId']
    print(f"Restore iniciado: {restore_job_id}")

    max_wait_minutes = 13
    waited = 0

    while waited < max_wait_minutes * 60:
        status = backup.describe_restore_job(
            RestoreJobId=restore_job_id
        )['Status']

        print(f"Status do restore: {status}")

        if status in ['COMPLETED', 'FAILED', 'ABORTED']:
            break

        time.sleep(30)
        waited += 30

    if status != 'COMPLETED':
        failure_reason = backup.describe_restore_job(
            RestoreJobId=restore_job_id
        ).get('StatusMessage', 'Sem mensagem')

        raise Exception(
            f"Falha na restauração: {status}. Motivo: {failure_reason}")

    print("Restauração concluída. Aguardando disponibilidade...")

    waiter = rds.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=restore_db_instance_id)

    restored_instance = rds.describe_db_instances(
        DBInstanceIdentifier=restore_db_instance_id
    )['DBInstances'][0]

    new_endpoint = restored_instance['Endpoint']['Address']

    ssm.put_parameter(
        Name='/app/db/endpoint',
        Value=new_endpoint,
        Type='String',
        Overwrite=True
    )

    print(f"Novo endpoint atualizado: {new_endpoint}")

    ssm_cmd.send_command(
        InstanceIds=[ec2_instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={
            'commands': ['bash /home/ubuntu/shopee/restart_app.sh']
        },
    )

    print("Aplicação reiniciada no EC2.")

    return {
        'statusCode': 200,
        'body': f"Restauração concluída com sucesso, novo endpoint: {new_endpoint}"
    }
