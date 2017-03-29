# Copyright 2015 Google Inc. All Rights Reserved.
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

"""Constants for the dataproc tool."""

from googlecloudsdk.api_lib.compute import base_classes as compute_base
from googlecloudsdk.api_lib.compute import constants as compute_constants
from googlecloudsdk.api_lib.compute import utils as compute_utils
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute import scope_prompter
from googlecloudsdk.core import properties
from googlecloudsdk.core import resolvers


# Copy into dataproc for cleaner separation
SCOPE_ALIASES = compute_constants.SCOPES
SCOPE_ALIASES_FOR_HELP = compute_constants.ScopesForHelp()


def ExpandScopeAliases(scopes):
  """Replace known aliases in the list of scopes provided by the user."""
  scopes = scopes or []
  expanded_scopes = []
  for scope in scopes:
    if scope in SCOPE_ALIASES:
      expanded_scopes += SCOPE_ALIASES[scope]
    else:
      # Validate scopes server side.
      expanded_scopes.append(scope)
  return sorted(expanded_scopes)


def GetComputeResources(release_track, cluster_name):
  """Returns a resources object with resolved GCE zone and region."""
  holder = compute_base.ComputeApiHolder(release_track)
  project_prop = properties.VALUES.core.project
  region_prop = properties.VALUES.compute.region
  zone_prop = properties.VALUES.compute.zone
  project = project_prop.Get(required=True)
  resources = holder.resources
  resources.SetParamDefault(
      'compute', None, 'project', resolvers.FromProperty(project_prop))
  resources.SetParamDefault(
      'compute', None, 'zone', resolvers.FromProperty(zone_prop))
  resources.SetParamDefault(
      'compute', None, 'region', resolvers.FromProperty(region_prop))

  # Prompt for scope if necessary
  zone = properties.VALUES.compute.zone.Get()
  if not zone:
    _, zone = scope_prompter.PromptForScope(
        resource_name='cluster',
        underspecified_names=[cluster_name],
        scopes=[compute_scope.ScopeEnum.ZONE],
        default_scope=None,
        scope_lister=flags.GetDefaultScopeLister(
            holder.client, project))
    if not zone:
      # Still no zone, just raise error generated by this property.
      zone = properties.VALUES.compute.zone.Get(required=True)

  zone_ref = resources.Parse(zone, collection='compute.zones')
  zone_name = zone_ref.Name()
  zone_prop.Set(zone_name)
  region_name = compute_utils.ZoneNameToRegionName(zone_name)
  region_prop.Set(region_name)

  return resources