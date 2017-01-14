from __future__ import print_function

import boto3
import json
import logging
import math
import random

AWS_REGION = 'eu-west-1'
TABLE_NAME = 'VoteApp'
VOTE_CHOICES = (
    'LOLWUT',
    'PCMR',
    'PEASANT',
)

dynamodb = boto3.client('dynamodb', AWS_REGION)
logger = logging.getLogger()


def lambda_handler(event, context):

    logger.setLevel(logging.INFO if context.invoked_function_arn.endswith('prd') else logging.DEBUG)

    logger.debug(json.dumps(event, indent=4, separators=(',', ': ')))

    voted_for = event.get('Vote', '').upper().strip()

    # Test that the vote received is a valid choice
    if voted_for in VOTE_CHOICES:

        # Add randomness to the value to help spread across partitions
        voted_for_hash = voted_for + '.' + str(math.floor((random.random() * 10) + 1))

        try:
            dynamodb.updateItem(
                TableName=TABLE_NAME,
                Key={
                    'VotedFor': {
                        'S': voted_for_hash,
                    }
                },
                UpdateExpression='add #vote :x',
                ExpressionAttributeNames={
                    '#vote': 'Votes',
                },
                ExpressionAttributeValues={
                    ':x': {
                        'N': '1',
                    },
                },
            )
        except Exception as e:
            logger.error('Error recording vote in ' + TABLE_NAME)
            logger.error(e)
            return {
                'status': 'error',
                'message': 'Oops, please try again',
            }
        else:
            logger.info('Vote received for ' + voted_for)
            return {
                'status': 'status',
            }

    else:
        logger.error('Invalid vote received: ' + voted_for)
        return {
            'status': 'error',
            'message': 'Oops, please try again',
        }