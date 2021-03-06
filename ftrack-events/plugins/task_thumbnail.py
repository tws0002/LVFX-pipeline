import os
import ftrack
import getpass

shotHoldThumbnail = '/data/production/pipeline/linux/common/icons/JPEG/shotQuery.jpg'
shotCutThumbnail = '/data/production/pipeline/linux/common/icons/JPEG/shotProblem.jpg'


def callback(event):
    """ This plugin sets the task thumbnail from the task status update.
    """

    for entity in event['data'].get('entities', []):
        if entity.get('entityType') == 'task' and entity['action'] == 'update':

            if 'statusid' not in entity['keys']:
                return

            if 'statusid' in entity['changes']:
                newStatusId = entity['changes']['statusid']['new']
                status = ftrack.Status(newStatusId)
                thumbnail = None
                if status.getName() == 'Cut':
                    thumbnail = shotCutThumbnail
                elif status.getName() == 'On Hold':
                    thumbnail = shotHoldThumbnail
                try:
                    task = ftrack.Task(id=entity.get('entityId'))
                    task.createThumbnail(thumbnail)
                except:
                    return


# Subscribe to events with the update topic.
ftrack.setup()
ftrack.EVENT_HUB.subscribe('topic=ftrack.update', callback)
ftrack.EVENT_HUB.wait()
