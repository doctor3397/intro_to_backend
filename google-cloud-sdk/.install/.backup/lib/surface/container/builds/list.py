# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""List builds command."""

from apitools.base.py import list_pager

from googlecloudsdk.api_lib.cloudbuild import cloudbuild_util
from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


class List(base.ListCommand):
  """List builds."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
          to capture some information, but behaves like an ArgumentParser.
    """
    parser.add_argument(
        '--ongoing',
        help='Only list builds that are currently QUEUED or WORKING.',
        action='store_true')
    base.LIMIT_FLAG.SetDefault(parser, 50)

  def Collection(self):
    return 'cloudbuild.projects.builds'

  def GetUriFunc(self):
    registry = resources.REGISTRY.Clone()

    def _BuildToURI(build):
      build_ref = registry.Parse(
          None,
          params={
              'project': build.projectId,
              'id': build.id,
          },
          collection=self.Collection())
      return build_ref.SelfLink()
    return _BuildToURI

  # TODO(b/29048700): Until resolution of this bug, the error message
  # printed by gcloud (for 404s, eg) will be really terrible.
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """

    client = cloudbuild_util.GetClientInstance()
    messages = cloudbuild_util.GetMessagesModule()

    ongoing_filter = None
    if args.ongoing:
      ongoing_filter = 'status="WORKING" OR status="QUEUED"'

    return list_pager.YieldFromList(
        client.projects_builds,
        messages.CloudbuildProjectsBuildsListRequest(
            pageSize=args.page_size,
            projectId=properties.VALUES.core.project.Get(),
            filter=ongoing_filter),
        field='builds',
        batch_size=args.page_size,
        batch_size_attribute='pageSize')
