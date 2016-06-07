import os
import sys
import ftrack
import getpass
import logging


class UpdateRVComponent(ftrack.Action):

    label = 'Update RV Component'
    identifier = 'com.ftrack.updateRVComponent'

    def register(self):
        '''Register discover actions on logged in user.'''
        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                getpass.getuser()
            ),
            self.discover
        )

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.launch and source.user.username={0} '
            'and data.actionIdentifier={1}'.format(
                getpass.getuser(), self.identifier
            ),
            self.launch
        )

    def discover(self, event):
        '''Return action config if triggered on a single selection.'''
        selection = event['data'].get('selection', [])

        if not selection:
            return

        entityType = selection[0]['entityType']
        if entityType == 'assetversion':
            return {
                    'items': [{
                        'label': self.label,
                        'actionIdentifier': self.identifier
                    }]
                }
        else:
            return

    def launch(self, event):
        """
        Called when action is executed
        """
        selection = event['data'].get('selection', [])
        version = ftrack.AssetVersion(selection[0]['entityId'])
        metadata = version.getMeta()
        if 'source_file' in metadata:
            filename = metadata['source_file']
        else:
            filename = ''

        if 'values' in event['data']:
            values = event['data']['values']
            component = version.createComponent(name='movie', path=values['file_path'])
            version.publish()
            return {
                'success': True,
                'message': 'Action completed successfully'
            }

        return {
            'items': [{
                    'value': '##{0}##'.format('File Path'.capitalize()),
                    'type': 'label'
                }, {
                    'label': 'Name',
                    'type': 'text',
                    'value': filename,
                    'name': 'file_path'
                }]
            }


def register(registry, **kw):
    '''Register action. Called when used as an event plugin.'''
    logger = logging.getLogger(
        'com.ftrack.updateCompMeta'
    )

    # Validate that registry is an instance of ftrack.Registry. If not,
    # assume that register is being called from a new or incompatible API and
    # return without doing anything.
    if not isinstance(registry, ftrack.Registry):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack.Registry instance.'.format(registry)
        )
        return

    action = UpdateRVComponent()
    action.register()
