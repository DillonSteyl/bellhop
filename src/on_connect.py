def lambda_handler(event, context):
    print("On connect event")
    print(event)
    return {
        'statusCode': 200,
    }
