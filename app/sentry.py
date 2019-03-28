from suite.conf import settings


def before_send(event, hint):
    """Filtering"""
    for x in event['breadcrumbs']:
        if x['category'] == 'httplib':
            x['data']['url'] = x['data']['url'].replace(settings.BOT_TOKEN, '<BOT_TOKEN>')
            x['data']['url'] = x['data']['url'].replace(settings.DEVELOPER_BOT_TOKEN, '<DEVELOPER_BOT_TOKEN>')

    return event
